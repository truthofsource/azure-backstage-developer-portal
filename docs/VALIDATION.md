# Local validation - November 6, 2026

**Terms used here:** A fixture is test data or a test setup used instead of real business records.

| Check | Observed result |
| --- | --- |
| Original release-evidence tests | 9 passed |
| Original startup readiness check tests | 10 passed on Linux |
| Public catalog/reference checks | 5 passed |
| Terraform initialization/format/validate | Passed, signed AzureRM 4.81.0 and AzAPI 2.13.0 |
| Terraform mocked plans | 2 passed; no Azure calls/apply |
| Compose boundary | Passed: edge-only 443, internal PostgreSQL, separate writer overlay |
| Linux shell syntax | All nine copied shell helpers passed after LF normalization |
| Actionlint | Passed; manual workflow not dispatched |
| Trivy secret scan | No findings in publishable source; not dependency/image clearance |
| Local browser | 16 catalog entities, all four evidence states, tabs and 390px layout passed |
| Browser isolation | Zero page errors and zero external requests |

There are 24 Python test cases plus two Terraform cases using simulated responses and the separate Compose contract assertions. The ten POSIX permission cases ran in an existing local Python 3.12 Linux container with no network and a read-only project mount. The Compose checks only rendered configuration; the four-service stack was not started.

The first public catalog seed failed JSON parsing after an incomplete target-list edit; it was rebuilt from the structured original and all five reference tests passed. The first enabled-VM mock rejected the short fictional SSH string; it now uses structurally valid public-only reference data with no private key, and both cases using simulated responses pass. These were public fixture issues, not live failures.

Screenshots show the new local reference viewer using actual catalog/evaluator source with fictional targets and evidence. They do not show a live Backstage session. No full Backstage workspace build, image scan, cloud publication, sign-in, dump/restore, VM start or Actions dispatch was performed for this project. Operational source excerpts require the complete privately configured environment.

[Machine-readable result](validation-results.json) records this exact scope. Tests do not authenticate the hypothetical evidence inputs; the real reader must do that separately.

A final bash syntax check caught retained Windows line endings in copied source. They were normalized to LF and protected with .gitattributes; the manual workflow now checks every copied shell helper without executing it.

## Strengths-focused presentation review — November 6

Reviewed identity policy, catalog/TechDocs publication, release evaluation, runtime startup, backups and growth guidance before updating the README and adding the engineering-strengths guide. The review changes presentation, not the runtime or Terraform.

The nine original release-evaluator tests and five public catalog checks were rerun: all 14 passed. The refreshed local viewer passed four-section navigation, 16 catalog entities, four release states, six strengths cards and a 390-pixel mobile layout, with zero page errors or external requests. Five reference screenshots were refreshed. The earlier Linux startup and Terraform results above remain dated evidence; they were not repeated for these presentation-only changes.

No Backstage stack, Azure VM, sign-in, backup/restore, cloud operation or hosted GitHub check was started. Repository-relative links and public labels were checked before publication.

## Wording and preview review - November 6, 2026

The supporting guides and preview labels received another plain-language review.
Screenshots were refreshed from the local fictional viewer. Desktop tabs loaded
without browser errors, and the 390-pixel mobile view had no horizontal page
overflow. External browser requests were blocked. HTML structure and embedded
scripts remained unchanged; this pass changed text and screenshots only.

These browser checks did not repeat cloud acceptance or the earlier code tests.
No Azure service, Gmail account, provider session or hosted Actions run was used.

## Plain-language review - November 7, 2026

The main overview now starts with the business problem, the solution and the
practical outcome. Technical commands and detailed results remain available in
expandable sections and linked guides. Links, heading anchors, formatting and
expandable sections were checked. Earlier code-test and cloud results remain
historical; this wording pass did not repeat those tests.

The fictional preview was also simplified, its screenshots refreshed, and its
desktop tabs and 390-pixel mobile layout checked locally. Browser requests were
restricted to the local preview; HTML structure and embedded scripts were unchanged.

## Troubleshooting documentation review — November 7, 2026

Added a README incident summary and a linked historical lessons guide, checking the account against the maintained source records. Documentation checks covered local links, complete incident fields, identifying-information patterns, whitespace and preservation of the existing four-step walkthrough. Shared incidents link to the relevant project details; unresolved causes remain explicit.

This was an editorial update. Application code, tests, Terraform, images, workflow definitions and cloud settings were not changed. Existing functional test counts and screenshots above retain their original scope and dates; no application suite, live scan, paid image request, recovery rehearsal or GitHub Actions run was executed for this documentation pass.
