"""Release evidence checks; all values are synthetic and non-operational."""

from datetime import datetime, timedelta, timezone
import unittest

from evaluate import evaluate


NOW = datetime(2026, 10, 12, 12, 0, tzinfo=timezone.utc)
SOURCE = "a" * 40
API_DIGEST = "b" * 64
WEB_DIGEST = "c" * 64


def evidence(component="api", selected=None):
    selected = selected or component
    run = {
        "id": 123456,
        "repository": "truthofsource/workforce-platform",
        "workflowPath": ".github/workflows/workforce-production-release.yml",
        "event": "workflow_dispatch",
        "headBranch": "main",
        "runAttempt": 1,
        "status": "completed",
        "conclusion": "success",
        "receiptArtifactRunId": 123456,
        "receiptArtifactName": "workforce-production-publication-123456",
        # The source can differ from the workflow runner's head SHA.
        "headSha": "d" * 40,
        "inputs": {
            "component": selected,
            "source_sha": SOURCE,
            "api_sha256": API_DIGEST,
            "web_sha256": WEB_DIGEST,
        },
    }
    receipt = {
        "sourceSha": SOURCE,
        "component": selected,
        "apiSha256": API_DIGEST if selected in ("api", "both") else "",
        "webSha256": WEB_DIGEST if selected in ("web", "both") else "",
        "scannerSha256": "",
        "apiHost": "func-example-workforce-api.azurewebsites.net",
        "webHost": "example-workforce.azurestaticapps.net",
        "defaultEndpointsVerified": True,
        "activeReleasePinned": True,
    }
    pin = {
        "component": component,
        "sourceSha": SOURCE,
        "artifactSha256": API_DIGEST if component == "api" else WEB_DIGEST,
        "releaseClass": "active",
        "isCurrent": True,
        "currentRunId": 123456,
        "observedAt": "2026-10-12T11:55:00Z",
    }
    return run, receipt, pin


class ReleaseEvidenceTests(unittest.TestCase):
    def check(self, component="api", selected=None, *, now=NOW, max_age=timedelta(hours=24),
              change=None):
        run, receipt, pin = evidence(component, selected)
        if change:
            change(run, receipt, pin)
        return evaluate(component, run, receipt, pin, now=now, max_age=max_age)

    def test_exact_api_publication_and_rollback_source(self):
        result = self.check()
        self.assertEqual(result["state"], "verified")
        self.assertEqual(result["sourceSha"], SOURCE)
        self.assertNotEqual(result["sourceSha"], "d" * 40)
        self.assertEqual(result["artifactSha256"], API_DIGEST)

    def test_combined_release_produces_distinct_components(self):
        self.assertEqual(self.check("api", "both")["artifactSha256"], API_DIGEST)
        self.assertEqual(self.check("web", "both")["artifactSha256"], WEB_DIGEST)

    def test_component_only_release_does_not_update_other_component(self):
        self.assertEqual(self.check("web", "api")["state"], "unknown")

    def test_failed_and_incomplete_runs_never_verify(self):
        for status, conclusion in (("completed", "failure"), ("in_progress", None)):
            result = self.check(change=lambda r, _p, _a: r.update(
                status=status, conclusion=conclusion))
            self.assertEqual(result["state"], "unknown")

    def test_missing_receipt_or_current_readback_never_verifies(self):
        run, receipt, pin = evidence()
        for candidate in ((run, None, pin), (run, receipt, None)):
            self.assertEqual(evaluate("api", *candidate, now=NOW)["state"], "unknown")

    def test_run_api_without_inputs_uses_same_run_artifact(self):
        self.assertEqual(self.check(change=lambda r, _p, _a: r.update(
            inputs=None))["state"], "verified")

    def test_retained_historical_pin_does_not_prove_current_release(self):
        self.assertEqual(self.check(change=lambda _r, _p, a: a.update(
            isCurrent=False))["state"], "unknown")
        self.assertEqual(self.check(change=lambda _r, _p, a: a.update(
            currentRunId=123455))["state"], "unknown")

    def test_conflicting_source_digest_pin_or_run_identity(self):
        cases = (
            lambda r, p, a: r["inputs"].update(source_sha="e" * 40),
            lambda r, p, a: p.update(apiSha256="e" * 64),
            lambda r, p, a: p.update(webHost="unreviewed.example"),
            lambda r, p, a: a.update(artifactSha256="e" * 64),
            lambda r, p, a: r.update(repository="unreviewed/repository"),
            lambda r, p, a: r.update(runAttempt=2),
            lambda r, p, a: r.update(receiptArtifactRunId=123455),
            lambda r, p, a: r.update(receiptArtifactName="wrong-artifact"),
            lambda r, p, a: p.update(activeReleasePinned=False),
        )
        for change in cases:
            with self.subTest(change=change):
                self.assertEqual(self.check(change=change)["state"], "conflict")

    def test_stale_and_future_pin_readbacks(self):
        self.assertEqual(self.check(now=NOW + timedelta(days=2))["state"], "stale")
        self.assertEqual(self.check(change=lambda _r, _p, a: a.update(
            observedAt="2026-10-12T12:06:00Z"))["state"], "conflict")


if __name__ == "__main__":
    unittest.main()
