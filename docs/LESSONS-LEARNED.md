# Troubleshooting lessons from the actual platform

These are historical engineering incidents summarized from maintained internal records. They are not newly reproduced tests, a fresh cloud inventory or instructions to repeat a consumed operation. Names, resource identifiers, private payloads and credentials are excluded.

## A successful backup command produced no new backup

**What happened.** An operating command could finish successfully without a newly saved dump.

**What the evidence showed.** The backup service condition and helper could legitimately skip a stopped session. Command exit status alone therefore did not establish that a fresh backup had been created.

**What changed and how it was checked.** Acceptance required evidence that the stack was active and a new timestamped dump, checksum and inventory existed. The recorded procedure also checked the actual installed helper path and guest output instead of treating Azure Run Command delivery as guest-script completion.

**What to carry forward.** Distinguish success, intentional skip, fresh backup creation and verified restore. Preserve the timestamp and content evidence needed to tell them apart rather than labeling every zero exit status as a current backup.

Source record: `docs/troubleshooting/backstage-engineering-portal.md — Backup says success but no new object; Handbook helper path and Run Command output`. These internal paths identify provenance; they are not public file links.

## A database listener appeared before restore readiness

**What happened.** The isolated recovery process could race database initialization even though PostgreSQL had already announced a listener.

**What the evidence showed.** Initialization used a temporary Unix socket before the final TCP service was ready. Testing the wrong readiness signal allowed the next recovery step to start too soon.

**What changed and how it was checked.** The recovery checks waited for the final loopback TCP server. Strict SQL execution and the saved inventory comparison were used to detect incomplete recovery; the live cluster was not used as the restore target.

**What to carry forward.** Wait for the exact interface and state required by the next operation. A process, socket or port being present is weaker evidence than a usable initialized database and a verified recovered result.

Source record: `docs/troubleshooting/backstage-engineering-portal.md — Hosted publication and recovery`. These internal paths identify provenance; they are not public file links.

## A template read reached a different GitHub permission boundary

**What happened.** A template-related read returned 403 even though ordinary repository content reads worked.

**What the evidence showed.** The stock template reader called /commits/main/status, a different endpoint from Contents. The failure did not establish that all repository reads were broken or that the existing reader needed broad write authority.

**What changed and how it was checked.** The reviewed path used fixed image-bundled template assets with equality tests against maintained skeletons. Catalog reads retained the original read-only integration and proposal writes retained their separate writer boundary.

**What to carry forward.** Trace the actual denied endpoint, not only the service name. Reducing a dependency can be safer than widening credentials; a created proposal is still separate from deployment or worker execution.

Source record: `docs/troubleshooting/backstage-engineering-portal.md — First triage: intentional pause versus failure`. These internal paths identify provenance; they are not public file links.

## A child process consumed the rest of a remote script

**What happened.** Transfers completed, but later shell steps did not run during a remote maintenance operation.

**What the evidence showed.** A child process could consume stdin from a script supplied with bash -s. Successful command delivery and a completed transfer did not establish completion of the later phases.

**What changed and how it was checked.** The procedure executed the script from a file, redirected transfer stdin from /dev/null and required a final phase receipt. Guest output was checked separately from the Azure Run Command submission result.

**What to carry forward.** Define and verify an explicit completion signal for multi-step automation. Do not repeat a possibly completed write merely because a later reporting or shell-transport phase failed.

Source record: `docs/troubleshooting/vulnerability-scanning.md — Transfers complete but later shell steps never execute`. These internal paths identify provenance; they are not public file links.

## Evidence and project boundaries

The local examples and screenshots in this repository remain separate from the dated hosted incidents above. A new documentation summary does not establish another successful deployment, restore, security scan or business transaction. Follow the repository’s existing validation guide for the commands and limits of the runnable reference.

The practical sequence is: identify the failing boundary, preserve safe correlation evidence, reconcile any uncertain result, apply only the relevant repair and verify the resulting state. A completed local command is not interchangeable with a completed cloud operation.
