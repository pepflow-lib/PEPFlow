import json, hashlib, datetime
from pathlib import Path
root=Path(__file__).resolve().parent
review=root.parent
original=Path('C:/Users/Jack/Documents/GitHub/PEPFlow/examples_peppy/_evaluations/20260923T140754Z_paper5_pgm_sos_6x5_isolation1/pgm_without_sos/r02')
hashes=json.loads((review/'submission-hashes.json').read_text())
results=[]
for relative,expected in hashes.items():
    p=original/relative
    actual=hashlib.sha256(Path('\\\\?\\'+str(p)).read_bytes()).hexdigest()
    results.append({'path':relative,'expected':expected,'actual':actual,'match':actual==expected})
(root/'original-integrity.json').write_text(json.dumps({'checked_at':datetime.datetime.now(datetime.timezone.utc).isoformat(),'count':len(results),'all_match':all(x['match'] for x in results),'files':results},indent=2))
print('Original hashes:',len(results),'all match:',all(x['match'] for x in results))
for skill in ['pep-implement','lyap-define','lyap-vectors','lyap-closed-form']:
    p=original/'supplementary/approved/plugins/pepflow-workflows/skills'/skill/'references/workflow.md'
    txt=Path('\\\\?\\'+str(p)).read_text(encoding='utf-8-sig')
    print('\nWORKFLOW',skill)
    for line in txt.splitlines():
        if any(x in line.lower() for x in ['toleran','optimal','atol','rtol','indep_tol','span_tol','n=1','n = 1','n=7','n = 7','pass','must','require']):
            print(line)
print('SAVED B2 CHECKS')
for rel in ['state/pgm_b2.json','supplementary/certificate-n6/pgm_b2.json']:
    d=json.loads((root/rel).read_text())
    print(rel,json.dumps(d['numerical_checks']))
    print('search',json.dumps(d['closed_form_search']))
