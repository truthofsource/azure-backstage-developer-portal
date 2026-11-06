# Local validation â€” November 6, 2026

| Check | Observed result |
| --- | --- |
| Original release-evidence tests | 9 passed |
| Original startup preflight tests | 10 passed on Linux |
| Public catalog/reference checks | 5 passed |
| Terraform initialization/format/validate | Passed, signed AzureRM 4.81.0 and AzAPI 2.13.0 |
| Terraform mocked plans | 2 passed; no Azure calls/apply |
| Compose boundary | Passed: edge-only 443, internal PostgreSQL, separate writer overlay |
| Linux shell syntax | All nine copied shell helpers passed after LF normalization |
| Actionlint | Passed; manual workflow not dispatched |
| Trivy secret scan | No findings in publishable source; not dependency/image clearance |
| Local browser | 16 catalog entities, all four evidence states, tabs and 390px layout passed |
| Browser isolation | Zero page errors and zero external requests |

There are 24 Python test cases plus two Terraform mock cases and the separate Compose contract assertions. The ten POSIX permission cases ran in an existing local Python 3.12 Linux container with no network and a read-only project mount. The Compose checks only rendered configuration; the four-service stack was not started.

The first public catalog seed failed JSON parsing after an incomplete target-list edit; it was rebuilt from the structured original and all five reference tests passed. The first enabled-VM mock rejected the short fictional SSH string; it now uses structurally valid public-only reference data with no private key, and both mock cases pass. These were public fixture issues, not live failures.

Screenshots show the new local reference viewer using actual catalog/evaluator source with fictional targets and evidence. They do not show a live Backstage session. No full Backstage workspace build, image scan, cloud publication, sign-in, dump/restore, VM start or Actions dispatch was performed for this project. Operational source excerpts require the complete privately configured environment.

[Machine-readable result](validation-results.json) records this exact scope. Tests do not authenticate the hypothetical evidence inputs; the real reader must do that separately.

A final bash syntax check caught retained Windows line endings in copied source. They were normalized to LF and protected with .gitattributes; the manual workflow now checks every copied shell helper without executing it.
