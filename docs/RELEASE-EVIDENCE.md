# Trustworthy release evidence

The actual Python evaluator consumes three inputs supplied by an authenticated reader: a workflow run, its same-run publication receipt and a fresh authoritative current-release observation. It performs no network requests itself. A caller must authenticate the evidence; JSON fields are not proof of origin on their own.

| Result | Meaning | Operator response |
| --- | --- | --- |
| Verified | Selected source/digest, same-run receipt and fresh current observation agree | Read the observation time and component scope |
| Unknown | Evidence is missing, failed, incomplete or cannot prove current state | Obtain the missing authenticated observation |
| Conflict | Receipt, source, artifact, run or destination identities disagree | Investigate the disagreement; do not relabel green |
| Stale | Previously consistent observation exceeds accepted age | Refresh authoritative evidence |

The evaluator validates the selected component, exact workflow/repository, run event/branch/attempt, source SHA and artifact SHA. It checks that a receipt belongs to the same run and uses authoritative current readback rather than a historical retained pin. A rollback can deploy an older source than the workflow runner's head; selected source and artifact are the relevant identities.

`scripts/demo.py` imports the original synthetic test fixture and intentionally shows all four outcomes. The displayed dates/run IDs and example repository are fictional. The public viewer does not query GitHub/Azure or expose a deployment control.

```bash
python -B scripts/demo.py
python -B -m unittest discover -s reference/releases -v
```

The TypeScript hosted release plugin and evidence-fetch adapters are not included as a complete application. These pure checks establish evaluation behavior, not live reader/provider acceptance.
