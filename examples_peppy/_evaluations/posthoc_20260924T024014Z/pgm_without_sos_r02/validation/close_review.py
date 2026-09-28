import json, hashlib, datetime
from pathlib import Path
v=Path(__file__).resolve().parent
r=v.parent
o=Path('C:/Users/Jack/Documents/GitHub/PEPFlow/examples_peppy/_evaluations/20260923T140754Z_paper5_pgm_sos_6x5_isolation1/pgm_without_sos/r02')
h=json.loads((r/'submission-hashes.json').read_text())
assert all(hashlib.sha256(Path('\\\\?\\'+str(o/p)).read_bytes()).hexdigest()==x for p,x in h.items())
d=json.loads((r/'review.json').read_text())
assert d['mathematical_verdict']=='PASS' and [x['block_id'] for x in d['blocks']]==['B1','B2','B3','B4','B5']
assert json.loads((v/'execution-status.json').read_text())['returncode']==0
for c in d['checks']:
    p=Path(c['evidence_ref'])
    assert (p if p.is_absolute() else r/p).is_file(),p
integrity=json.loads((v/'original-integrity.json').read_text())
integrity['closing_verified_at']=datetime.datetime.now(datetime.timezone.utc).isoformat()
(v/'original-integrity.json').write_text(json.dumps(integrity,indent=2))
d['review_stopped_at']=integrity['closing_verified_at']
(r/'review.json').write_text(json.dumps(d,indent=2))
print('Review schema essentials, evidence references, exit code and all',len(h),'closing original hashes verified.')
