"""Focused refusal cases for the VM startup preflight."""

import os
import tempfile
import unittest
from pathlib import Path

from preflight import SECRETS, load_env, validate


SHA = "a" * 64


@unittest.skipUnless(os.name == "posix", "VM secret/roster permissions require Linux; checked in Backstage CI")
class PreflightTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        root = Path(self.temporary.name)
        self.roster = root / "engineers.yaml"
        self.roster.write_text("apiVersion: backstage.io/v1alpha1\nkind: User\n")
        self.roster.chmod(0o600)
        self.secret_dir = root / "secrets"
        self.secret_dir.mkdir(mode=0o700)
        for name in SECRETS:
            file = self.secret_dir / name
            file.write_bytes(b"x" * (32 if name == "ingress_cookie_secret" else 8))
            file.chmod(0o600)
        self.values = {
            "BACKSTAGE_POSTGRES_IMAGE": f"docker.io/library/postgres@sha256:{SHA}",
            "BACKSTAGE_IMAGE": f"examplehubregistry001.azurecr.io/backstage/portal@sha256:{SHA}",
            "BACKSTAGE_OAUTH_IMAGE": f"quay.io/oauth2-proxy/oauth2-proxy@sha256:{SHA}",
            "BACKSTAGE_CADDY_IMAGE": f"docker.io/library/caddy@sha256:{SHA}",
            "BACKSTAGE_DOMAIN": "portal.workforce.invalid",
            "BACKSTAGE_TENANT_ID": "11111111-1111-1111-1111-111111111111",
            "BACKSTAGE_ENTRA_CLIENT_ID": "22222222-2222-2222-2222-222222222222",
            "BACKSTAGE_INGRESS_CLIENT_ID": "33333333-3333-3333-3333-333333333333",
            "BACKSTAGE_ENGINEER_GROUP_ID": "44444444-4444-4444-4444-444444444444",
            "BACKSTAGE_CATALOG_URL": "https://raw.githubusercontent.com/truthofsource/repo/main/catalog.yaml",
            "BACKSTAGE_ENGINEER_ROSTER_FILE": str(self.roster),
            "BACKSTAGE_ENGINEER_USER_REFS": "user:default/engineer",
            "BACKSTAGE_GITHUB_APP_ID": "1234",
            "BACKSTAGE_GITHUB_APP_CLIENT_ID": "Iv1.abc123",
            "BACKSTAGE_SECRET_DIR": str(self.secret_dir),
        }

    def test_valid_configuration(self):
        validate(self.values)

    def test_scanner_proof_requires_boolean_switch(self):
        self.values["BACKSTAGE_SCANNER_PROOF_ENABLED"] = "yes"
        with self.assertRaisesRegex(ValueError, "BACKSTAGE_SCANNER_PROOF_ENABLED"):
            validate(self.values, check_files=False)
        self.values["BACKSTAGE_SCANNER_PROOF_ENABLED"] = "false"
        validate(self.values)

    def test_rejects_mutable_image(self):
        self.values["BACKSTAGE_IMAGE"] = "examplehubregistry001.azurecr.io/backstage/portal:latest"
        with self.assertRaisesRegex(ValueError, "immutable"):
            validate(self.values)

    def test_rejects_exposed_roster(self):
        self.roster.chmod(0o644)
        with self.assertRaisesRegex(ValueError, "world-readable"):
            validate(self.values)

    def test_rejects_shared_signin_app(self):
        self.values["BACKSTAGE_INGRESS_CLIENT_ID"] = self.values["BACKSTAGE_ENTRA_CLIENT_ID"]
        with self.assertRaisesRegex(ValueError, "separate Entra"):
            validate(self.values)

    def test_rejects_world_readable_secret(self):
        (self.secret_dir / "postgres_password").chmod(0o644)
        with self.assertRaisesRegex(ValueError, "world-readable"):
            validate(self.values)

    def test_rejects_cookie_secret_with_wrong_length(self):
        (self.secret_dir / "ingress_cookie_secret").write_bytes(b"short")
        with self.assertRaisesRegex(ValueError, "32 raw bytes"):
            validate(self.values)

    def test_rejects_unknown_env_setting(self):
        file = Path(self.temporary.name) / "vm.env"
        file.write_text("BACKSTAGE_DOMAIN=portal.workforce.invalid\nEXTRA_SETTING=value\n")
        with self.assertRaisesRegex(ValueError, "unknown"):
            load_env(file)

    def test_writer_requires_separate_app_and_private_key(self):
        self.values.update(BACKSTAGE_TEMPLATES_ENABLED="true", BACKSTAGE_TEMPLATE_APP_ID="5678",
                           BACKSTAGE_TEMPLATE_INSTALLATION_ID="987", BACKSTAGE_TEMPLATE_REPOSITORY_ID="765",
                           BACKSTAGE_TEMPLATE_MAINTAINERS=self.values["BACKSTAGE_ENGINEER_USER_REFS"])
        with self.assertRaisesRegex(ValueError, "template_github_private_key"):
            validate(self.values)
        key = self.secret_dir / "template_github_private_key"
        key.write_bytes(b"synthetic-key")
        key.chmod(0o600)
        validate(self.values)
        self.values["BACKSTAGE_TEMPLATE_APP_ID"] = self.values["BACKSTAGE_GITHUB_APP_ID"]
        with self.assertRaisesRegex(ValueError, "separate"):
            validate(self.values)

    def test_writer_maintainer_must_be_engineer(self):
        self.values.update(BACKSTAGE_TEMPLATES_ENABLED="true", BACKSTAGE_TEMPLATE_APP_ID="5678",
                           BACKSTAGE_TEMPLATE_INSTALLATION_ID="987", BACKSTAGE_TEMPLATE_REPOSITORY_ID="765",
                           BACKSTAGE_TEMPLATE_MAINTAINERS="user:default/unlisted")
        with self.assertRaisesRegex(ValueError, "approved engineer"):
            validate(self.values, check_files=False)


if __name__ == "__main__":
    unittest.main()
