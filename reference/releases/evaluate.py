"""Evaluate one production publication from separately collected read-only evidence.

This module does not fetch evidence, access Azure/GitHub, or infer a deployment
from a build commit. A future adapter must authenticate and supply each input.
"""

from datetime import datetime, timedelta, timezone
import re


REPOSITORY = "truthofsource/workforce-platform"
WORKFLOW = ".github/workflows/workforce-production-release.yml"
API_HOST = "func-example-workforce-api.azurewebsites.net"
WEB_HOST = "example-workforce.azurestaticapps.net"
COMPONENT_REFS = {
    "api": "component:default/workforce-api",
    "web": "component:default/workforce-web",
    "scanner": "component:default/workforce-document-scanner",
}
DIGEST_FIELDS = {"api": "apiSha256", "web": "webSha256", "scanner": "scannerSha256"}
SHA40 = re.compile(r"[0-9a-f]{40}\Z")
SHA64 = re.compile(r"[0-9a-f]{64}\Z")


def _time(value):
    if not isinstance(value, str):
        return None
    try:
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError:
        return None
    return parsed.astimezone(timezone.utc) if parsed.tzinfo else None


def _observation(component, state, *, observed_at=None, source=None,
                 digest=None, run_url=None):
    return {
        "schemaVersion": 1,
        "componentRef": COMPONENT_REFS[component],
        "environment": "production",
        "state": state,
        "observedAt": observed_at,
        "sourceSha": source,
        "artifactSha256": digest,
        "imageDigest": None,
        "runUrl": run_url,
    }


def evaluate(component, run, receipt, pin, *, now, max_age=timedelta(hours=24)):
    """Return a release-view observation; never treat incomplete evidence as verified.

    `run` is an authenticated GitHub Actions run with same-run artifact binding;
    GitHub may omit dispatch inputs from the run API. `receipt` is the
    publication artifact from that exact run.
    `pin` is a fresh authoritative current-release readback. Historical blobs
    under `pinned/active/` are retained and cannot establish current status.
    The caller must authenticate those sources before invoking this function.
    """
    if component not in COMPONENT_REFS:
        raise ValueError("Unreviewed release component")
    if not isinstance(now, datetime) or now.tzinfo is None or max_age <= timedelta(0):
        raise ValueError("A timezone-aware observation time and positive age are required")
    now = now.astimezone(timezone.utc)
    if not all(isinstance(item, dict) for item in (run, receipt, pin)):
        return _observation(component, "unknown")

    run_id = run.get("id")
    source = receipt.get("sourceSha")
    digest = receipt.get(DIGEST_FIELDS[component])
    if (not isinstance(run_id, int) or isinstance(run_id, bool) or run_id <= 0
            or not isinstance(source, str) or not SHA40.fullmatch(source)
            or not isinstance(digest, str) or not SHA64.fullmatch(digest)):
        return _observation(component, "unknown")
    run_url = f"https://github.com/{REPOSITORY}/actions/runs/{run_id}"

    # A failed or incomplete attempt cannot establish any new publication.
    if run.get("status") != "completed" or run.get("conclusion") != "success":
        return _observation(component, "unknown", run_url=run_url)
    if (run.get("receiptArtifactRunId") != run_id
            or run.get("receiptArtifactName") != f"workforce-production-publication-{run_id}"):
        return _observation(component, "conflict", run_url=run_url)
    selected = receipt.get("component")
    if selected not in (component, "both") or (selected == "both" and component == "scanner"):
        return _observation(component, "conflict", run_url=run_url)
    inputs = run.get("inputs")
    if inputs is not None:
        if not isinstance(inputs, dict):
            return _observation(component, "unknown", run_url=run_url)
        if (inputs.get("component") != selected
                or inputs.get("source_sha") != source
                or inputs.get(f"{component}_sha256") != digest):
            return _observation(component, "conflict", run_url=run_url)

    expected = {
        "repository": REPOSITORY,
        "workflowPath": WORKFLOW,
        "event": "workflow_dispatch",
        "headBranch": "main",
        "runAttempt": 1,
    }
    if any(run.get(key) != value for key, value in expected.items()):
        return _observation(component, "conflict", run_url=run_url)
    if (receipt.get("apiHost") != API_HOST
            or receipt.get("webHost") != WEB_HOST
            or receipt.get("defaultEndpointsVerified") is not True
            or receipt.get("activeReleasePinned") is not True):
        return _observation(component, "conflict", run_url=run_url)

    # A retained historical pin is insufficient: the reader must establish an
    # authoritative current pointer or independently verify the live runtime.
    if pin.get("isCurrent") is not True or pin.get("currentRunId") != run_id:
        return _observation(component, "unknown", run_url=run_url)
    read_at = _time(pin.get("observedAt"))
    if read_at is None:
        return _observation(component, "unknown", run_url=run_url)
    if read_at > now + timedelta(minutes=5):
        return _observation(component, "conflict", run_url=run_url)
    stamp = read_at.isoformat().replace("+00:00", "Z")
    if (pin.get("component") != component
            or pin.get("sourceSha") != source
            or pin.get("artifactSha256") != digest
            or pin.get("releaseClass") != "active"):
        return _observation(component, "conflict", observed_at=stamp, run_url=run_url)
    if now - read_at > max_age:
        return _observation(component, "stale", observed_at=stamp,
                            source=source, digest=digest, run_url=run_url)
    return _observation(component, "verified", observed_at=stamp,
                        source=source, digest=digest, run_url=run_url)
