"""Check reviewed VM inputs without starting containers or reading secret values."""

import argparse
import ipaddress
import re
import stat
import sys
from pathlib import Path
from urllib.parse import urlsplit
from uuid import UUID


REQUIRED = {
    "BACKSTAGE_POSTGRES_IMAGE", "BACKSTAGE_IMAGE", "BACKSTAGE_OAUTH_IMAGE",
    "BACKSTAGE_CADDY_IMAGE", "BACKSTAGE_DOMAIN", "BACKSTAGE_TENANT_ID",
    "BACKSTAGE_ENTRA_CLIENT_ID", "BACKSTAGE_INGRESS_CLIENT_ID",
    "BACKSTAGE_ENGINEER_GROUP_ID", "BACKSTAGE_CATALOG_URL",
    "BACKSTAGE_ENGINEER_ROSTER_FILE", "BACKSTAGE_ENGINEER_USER_REFS",
    "BACKSTAGE_GITHUB_APP_ID", "BACKSTAGE_GITHUB_APP_CLIENT_ID",
    "BACKSTAGE_SECRET_DIR",
}
SECRETS = (
    "postgres_password", "postgres_admin_password", "backstage_entra_client_secret", "github_app_client_secret",
    "github_app_private_key", "github_app_webhook_secret", "ingress_client_secret",
    "ingress_cookie_secret",
)
OPTIONAL = {
    "BACKSTAGE_API_PROOF_ENABLED", "BACKSTAGE_WEB_PROOF_ENABLED", "BACKSTAGE_SCANNER_PROOF_ENABLED",
    "BACKSTAGE_TEMPLATES_ENABLED", "BACKSTAGE_TEMPLATE_APP_ID",
    "BACKSTAGE_TEMPLATE_INSTALLATION_ID", "BACKSTAGE_TEMPLATE_REPOSITORY_ID",
    "BACKSTAGE_TEMPLATE_MAINTAINERS",
}
IMAGE = re.compile(r"^[a-z0-9][a-z0-9./_-]*@sha256:[a-f0-9]{64}$")
DOMAIN = re.compile(r"^(?=.{1,253}$)(?:[a-z0-9](?:[a-z0-9-]{0,61}[a-z0-9])?\.)+[a-z]{2,63}$")
USER_REF = re.compile(r"^user:default/[a-z0-9][a-z0-9_-]*$")


def load_env(path: Path) -> dict[str, str]:
    values: dict[str, str] = {}
    for line_number, raw in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
        line = raw.strip()
        if not line or line.startswith("#"):
            continue
        if "=" not in line:
            raise ValueError(f"Line {line_number}: expected KEY=value")
        key, value = line.split("=", 1)
        if key not in REQUIRED | OPTIONAL or key in values or not value or value != value.strip():
            raise ValueError(f"Line {line_number}: unknown, duplicate or invalid setting {key}")
        if any(char in value for char in ("'", '"', "$", "`")):
            raise ValueError(f"Line {line_number}: use literal unquoted values for {key}")
        values[key] = value
    missing = REQUIRED - values.keys()
    if missing:
        raise ValueError("Missing settings: " + ", ".join(sorted(missing)))
    return values


def require_uuid(value: str, label: str) -> None:
    try:
        parsed = UUID(value)
    except ValueError as exc:
        raise ValueError(f"{label} must be a UUID") from exc
    if str(parsed) != value or parsed.int == 0:
        raise ValueError(f"{label} must be a nonzero lowercase UUID")


def require_https(value: str, label: str) -> None:
    parsed = urlsplit(value)
    try:
        host = parsed.hostname
        port = parsed.port
    except ValueError as exc:
        raise ValueError(f"{label} must be a reviewed HTTPS URL") from exc
    if (parsed.scheme != "https" or not host or not DOMAIN.fullmatch(host)
            or parsed.username or parsed.password or port or parsed.fragment
            or host.endswith(".example.org") or host.endswith(".example.com")):
        raise ValueError(f"{label} must be a reviewed HTTPS URL")


def validate(values: dict[str, str], check_files: bool = True) -> None:
    for key in ("BACKSTAGE_POSTGRES_IMAGE", "BACKSTAGE_IMAGE",
                "BACKSTAGE_OAUTH_IMAGE", "BACKSTAGE_CADDY_IMAGE"):
        if not IMAGE.fullmatch(values[key]):
            raise ValueError(f"{key} must be an immutable repository@sha256 digest")
    if not values["BACKSTAGE_POSTGRES_IMAGE"].startswith("docker.io/library/postgres@"):
        raise ValueError("BACKSTAGE_POSTGRES_IMAGE must use the reviewed PostgreSQL repository")
    if not values["BACKSTAGE_IMAGE"].startswith("examplehubregistry001.azurecr.io/backstage/portal@"):
        raise ValueError("BACKSTAGE_IMAGE must use the scoped Backstage ACR repository")
    if not values["BACKSTAGE_OAUTH_IMAGE"].startswith("quay.io/oauth2-proxy/oauth2-proxy@"):
        raise ValueError("BACKSTAGE_OAUTH_IMAGE must use the reviewed OAuth2 Proxy repository")
    if not values["BACKSTAGE_CADDY_IMAGE"].startswith("docker.io/library/caddy@"):
        raise ValueError("BACKSTAGE_CADDY_IMAGE must use the reviewed Caddy repository")
    domain = values["BACKSTAGE_DOMAIN"]
    if not DOMAIN.fullmatch(domain) or domain.endswith((".example.org", ".example.com")):
        raise ValueError("BACKSTAGE_DOMAIN must be a reviewed public DNS name")
    try:
        ipaddress.ip_address(domain)
    except ValueError:
        pass
    else:
        raise ValueError("BACKSTAGE_DOMAIN must be a DNS name")
    for key in ("BACKSTAGE_TENANT_ID", "BACKSTAGE_ENTRA_CLIENT_ID",
                "BACKSTAGE_INGRESS_CLIENT_ID", "BACKSTAGE_ENGINEER_GROUP_ID"):
        require_uuid(values[key], key)
    if values["BACKSTAGE_ENTRA_CLIENT_ID"] == values["BACKSTAGE_INGRESS_CLIENT_ID"]:
        raise ValueError("Ingress and Backstage must use separate Entra applications")
    require_https(values["BACKSTAGE_CATALOG_URL"], "BACKSTAGE_CATALOG_URL")
    roster = Path(values["BACKSTAGE_ENGINEER_ROSTER_FILE"])
    if not roster.is_absolute():
        raise ValueError("Engineer roster must use an absolute private file path")
    refs = values["BACKSTAGE_ENGINEER_USER_REFS"].split(",")
    if not refs or any(not USER_REF.fullmatch(ref) for ref in refs) or len(refs) != len(set(refs)):
        raise ValueError("BACKSTAGE_ENGINEER_USER_REFS must be distinct exact user:default/name refs")
    if not values["BACKSTAGE_GITHUB_APP_ID"].isdigit() or int(values["BACKSTAGE_GITHUB_APP_ID"]) == 0:
        raise ValueError("BACKSTAGE_GITHUB_APP_ID must be a nonzero number")
    if not re.fullmatch(r"[a-zA-Z0-9][a-zA-Z0-9.]{5,99}", values["BACKSTAGE_GITHUB_APP_CLIENT_ID"]):
        raise ValueError("BACKSTAGE_GITHUB_APP_CLIENT_ID must be a GitHub App client ID")
    secret_dir = Path(values["BACKSTAGE_SECRET_DIR"])
    if not secret_dir.is_absolute() or secret_dir == Path("/"):
        raise ValueError("BACKSTAGE_SECRET_DIR must be an absolute dedicated directory")
    for key in ("BACKSTAGE_API_PROOF_ENABLED", "BACKSTAGE_WEB_PROOF_ENABLED",
                "BACKSTAGE_SCANNER_PROOF_ENABLED", "BACKSTAGE_TEMPLATES_ENABLED"):
        if values.get(key, "false") not in ("true", "false"):
            raise ValueError(f"{key} must be true or false")
    templates = values.get("BACKSTAGE_TEMPLATES_ENABLED", "false") == "true"
    if templates:
        for key in ("BACKSTAGE_TEMPLATE_APP_ID", "BACKSTAGE_TEMPLATE_INSTALLATION_ID", "BACKSTAGE_TEMPLATE_REPOSITORY_ID"):
            if not values.get(key, "").isdigit() or int(values[key]) <= 0:
                raise ValueError(f"{key} must be a positive integer")
        if values["BACKSTAGE_TEMPLATE_APP_ID"] == values["BACKSTAGE_GITHUB_APP_ID"]:
            raise ValueError("Template writer must be separate from the reader App")
        maintainers = values.get("BACKSTAGE_TEMPLATE_MAINTAINERS", "").split(",")
        if not maintainers or any(ref not in refs for ref in maintainers) or len(set(maintainers)) != len(maintainers):
            raise ValueError("Template maintainers must be distinct approved engineer refs")
    if not check_files:
        return
    if roster.is_symlink() or not roster.is_file() or roster.stat().st_size == 0:
        raise ValueError("Private engineer roster is missing, empty or a symlink")
    if roster.stat().st_mode & stat.S_IROTH:
        raise ValueError("Private engineer roster must not be world-readable")
    if secret_dir.is_symlink() or not secret_dir.is_dir():
        raise ValueError("Secret directory is missing or is a symlink")
    if secret_dir.stat().st_mode & stat.S_IWOTH:
        raise ValueError("Secret directory must not be writable by other users")
    for name in SECRETS + (("template_github_private_key",) if templates else ()):
        path = secret_dir / name
        if path.is_symlink() or not path.is_file() or path.stat().st_size == 0:
            raise ValueError(f"Secret file {name} is missing, empty or a symlink")
        if path.stat().st_mode & stat.S_IROTH:
            raise ValueError(f"Secret file {name} must not be world-readable")
    if (secret_dir / "ingress_cookie_secret").stat().st_size != 32:
        raise ValueError("ingress_cookie_secret must contain exactly 32 raw bytes")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("env_file", type=Path, help="Reviewed VM environment file")
    args = parser.parse_args()
    try:
        if args.env_file.is_symlink() or not args.env_file.is_file():
            raise ValueError("Environment file is missing or is a symlink")
        if args.env_file.stat().st_mode & (stat.S_IRGRP | stat.S_IROTH):
            raise ValueError("Environment file must not be group/world-readable")
        validate(load_env(args.env_file))
    except (OSError, ValueError) as exc:
        print(f"VM preflight failed: {exc}", file=sys.stderr)
        return 2
    print("VM preflight passed: reviewed settings and secret files are present; no service was started.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
