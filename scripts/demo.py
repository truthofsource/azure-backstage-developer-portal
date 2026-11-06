"""Print actual release-evaluator outcomes using fictional same-run evidence."""
from pathlib import Path
import sys,json
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'reference/releases'))
from evaluate import evaluate
from test_evaluate import evidence,NOW
def results():
    rows=[]
    for label,scenario in [('Current publication','verified'),('Missing current readback','unknown'),('Artifact mismatch','conflict'),('Old current observation','stale')]:
        run,receipt,pin=evidence()
        if scenario=='unknown':pin['isCurrent']=False
        elif scenario=='conflict':pin['artifactSha256']='e'*64
        elif scenario=='stale':pin['observedAt']='2026-10-10T11:55:00Z'
        outcome=evaluate('api',run,receipt,pin,now=NOW)
        assert outcome['state']==scenario
        rows.append({'scenario':label,**outcome})
    return rows
if __name__=='__main__': print(json.dumps(results(),indent=2))
