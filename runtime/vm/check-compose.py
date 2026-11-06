"""Validate the inert VM Compose boundary without starting any service."""

import json
import os
from pathlib import Path
import re
import subprocess


ROOT = Path(__file__).resolve().parent
SHA = "0" * 64
env = os.environ.copy()
env.update(
    BACKSTAGE_POSTGRES_IMAGE=f"docker.io/library/postgres@sha256:{SHA}",
    BACKSTAGE_IMAGE=f"example.azurecr.io/backstage/portal@sha256:{SHA}",
    BACKSTAGE_OAUTH_IMAGE=f"quay.io/oauth2-proxy/oauth2-proxy@sha256:{SHA}",
    BACKSTAGE_CADDY_IMAGE=f"docker.io/library/caddy@sha256:{SHA}",
    BACKSTAGE_DOMAIN="backstage.example.org",
    BACKSTAGE_TENANT_ID="11111111-1111-1111-1111-111111111111",
    BACKSTAGE_ENTRA_CLIENT_ID="22222222-2222-2222-2222-222222222222",
    BACKSTAGE_INGRESS_CLIENT_ID="33333333-3333-3333-3333-333333333333",
    BACKSTAGE_ENGINEER_GROUP_ID="44444444-4444-4444-4444-444444444444",
    BACKSTAGE_CATALOG_URL="https://example.org/catalog.yaml",
    BACKSTAGE_ENGINEER_ROSTER_FILE="/tmp/backstage-compose-test-roster.yaml",
    BACKSTAGE_ENGINEER_USER_REFS="user:default/engineer",
    BACKSTAGE_GITHUB_APP_ID="1234",
    BACKSTAGE_GITHUB_APP_CLIENT_ID="Iv1.example",
    BACKSTAGE_SECRET_DIR="/tmp/backstage-compose-test-secrets",
    BACKSTAGE_SCANNER_PROOF_ENABLED="false",
)
result = subprocess.run(
    ["docker", "compose", "-f", str(ROOT / "compose.yaml"), "config", "--format", "json"],
    env=env,
    check=True,
    capture_output=True,
    text=True,
)
config = json.loads(result.stdout)
services = config["services"]
assert set(services) == {"postgres", "backstage", "oauth2-proxy", "caddy"}
for name, service in services.items():
    assert re.search(r"@sha256:[a-f0-9]{64}$", service["image"]), name
    assert not service.get("privileged"), name
    if name != "caddy":
        assert not service.get("ports"), f"{name} unexpectedly publishes a port"
assert {int(port["target"]) for port in services["caddy"]["ports"]} == {443}
assert services["backstage"]["environment"]["BACKSTAGE_SCANNER_PROOF_ENABLED"] == "false"
assert set(services["caddy"]["networks"]) == {"edge"}
assert set(services["oauth2-proxy"]["networks"]) == {"edge"}
assert set(services["postgres"]["networks"]) == {"database"}
assert set(services["backstage"]["networks"]) == {"edge", "database"}
assert config["networks"]["database"]["internal"] is True
assert "--allowed-group=44444444-4444-4444-4444-444444444444" in services["oauth2-proxy"]["command"]
assert "--cookie-secure=true" in services["oauth2-proxy"]["command"]
assert "--reverse-proxy=true" in services["oauth2-proxy"]["command"]
assert not any(flag.startswith(("--trusted-ip=", "--trusted-proxy-ip=")) for flag in services["oauth2-proxy"]["command"])
edge_ipam = config["networks"]["edge"]["ipam"]["config"][0]
assert edge_ipam["ip_range"] == "172.30.80.128/25", "Reserve static proxy addresses outside dynamic allocation"
assert edge_ipam["gateway"] == "172.30.80.1"
assert "/app/start-vm.sh" in services["backstage"]["command"]
assert any(mount.get("target") == "/app/engineers.yaml" and mount.get("read_only") is True
           for mount in services["backstage"]["volumes"]), "Private roster must be mounted read-only"
assert any(mount.get("target") == "/var/lib/backstage/techdocs" and mount.get("read_only") is True
           for mount in services["backstage"]["volumes"]), "Externally published handbook must be read-only to the backend"
for name in ("postgres", "backstage", "oauth2-proxy"):
    assert services[name].get("secrets"), f"{name} lacks secret mounts"
caddyfile = (ROOT / "Caddyfile").read_text()
assert "handle /oauth2/*" in caddyfile
assert "forward_auth oauth2-proxy:4180" in caddyfile
assert "reverse_proxy backstage:7007" in caddyfile
assert "disable_http_challenge" in caddyfile
assert "auto_https disable_redirects" in caddyfile
print("VM Compose boundary passed: only Caddy publishes 443; database is internal; Entra group gate is present.")
env.update(BACKSTAGE_TEMPLATES_ENABLED="true", BACKSTAGE_TEMPLATE_APP_ID="5678",
           BACKSTAGE_TEMPLATE_INSTALLATION_ID="987", BACKSTAGE_TEMPLATE_REPOSITORY_ID="765",
           BACKSTAGE_TEMPLATE_MAINTAINERS="user:default/engineer")
writer = subprocess.run(["docker", "compose", "-f", str(ROOT / "compose.yaml"),
    "-f", str(ROOT / "compose.templates.yaml"), "config", "--format", "json"],
    env=env, check=True, capture_output=True, text=True)
writer_config = json.loads(writer.stdout)
assert set(writer_config["services"]) == set(services)
mounts = writer_config["services"]["backstage"]["secrets"]
assert any(item["source"] == "template_github_private_key" for item in mounts)
assert not any(item["source"] == "template_github_private_key" for item in services["backstage"]["secrets"])
assert writer_config["services"]["backstage"]["environment"]["BACKSTAGE_TEMPLATE_APP_ID"] == "5678"
print("Writer overlay passed: only Backstage receives its separate key; default stack has no writer mount.")
