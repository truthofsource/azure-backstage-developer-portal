# Trustworthy release evidence

**Terms used here:** A digest is a file or container fingerprint used to confirm the exact version. An artifact is a file produced for a release, such as an application ZIP or container image.

The Python evaluator compares three records supplied by a trusted reader: the build run, the deployment record from that run and a fresh observation of the release currently running. It performs no network requests itself. A caller must authenticate the evidence; JSON fields are not proof of origin on their own.

| Result | Meaning | Operator response |
| --- | --- | --- |
| Verified | Selected source/digest, same-run receipt and fresh current observation agree | Read the observation time and component scope |
| Unknown | Evidence is missing, failed, incomplete or cannot prove current state | Obtain the missing authenticated observation |
| Conflict | Receipt, source, artifact, run or destination identities disagree | Investigate the disagreement; do not relabel green |
| Stale | Previously consistent observation exceeds accepted age | Refresh evidence from the system responsible for the result |

The evaluator validates the selected component, exact workflow/repository, run event/branch/attempt, source SHA and artifact SHA. It confirms that the deployment record belongs to the same run, then compares it with a current result from the system responsible for the release. A rollback can deploy an older source than the workflow runner's head; selected source and artifact are the relevant identities.

`scripts/demo.py` imports the original fictional test data and intentionally shows all four outcomes. The displayed dates/run IDs and example repository are fictional. The public viewer does not query GitHub/Azure or expose a deployment control.

```bash
python -B scripts/demo.py
python -B -m unittest discover -s reference/releases -v
```

The TypeScript hosted release plugin and evidence-fetch adapters are not included as a complete application. The local checks test the decision rules. They do not verify the live reader or its external services.
