import sys
from pathlib import Path
root=Path(__file__).resolve().parent.parent
sys.path.insert(0,str(root/'supplementary/helpers'))
import runtime
import hashlib
import json
from certificates import acquire
from certificate_checks import verify_certificate, certificate_digest
from ogm_setup import get_pep_setup

previous=json.loads((root/'state/ogm_b2.json').read_text())
N=6
ctx,pb,obj=get_pep_setup(N,{'L':1,'R':1})
interpolation=obj.get_interpolation_constraints(ctx)
def index(tag):
    return 0 if tag=='z_0' else -1 if tag=='x_star' else int(tag.split('_')[1])
dropped=[]
for con in interpolation:
    left,right=con.name.split(':')[1].split(',')
    i,j=index(left),index(right)
    if not (i==-1 or j==i+1):
        dropped.append(con.name)
raw,ctx,pb,result,entries=acquire(N,dropped)
(root/'supplementary/b2-N6-raw.json').write_text(json.dumps(raw,indent=2))
state={**previous,**raw}
state['certificate_provenance']['source_hashes']['supplementary/helpers/certificate_checks.py']=hashlib.sha256((root/'supplementary/helpers/certificate_checks.py').read_bytes()).hexdigest()
ctx,pb,pm,checked,S_candidate,candidates,decomposition,checks=verify_certificate(state)
dense_row=next(row for row in previous['sweep_results'] if row['N']==N)
checks['residuals']['dense_relaxed_gap']=abs(dense_row['opt_value']-state['opt_value'])
assert checks['residuals']['dense_relaxed_gap']<1e-5
state['normalization']={**previous['normalization'],'bound_value':state['opt_value']}
state['numerical_checks']=checks
state['numerical_decomposition']=decomposition
state['closed_form_search']={**previous['closed_form_search'],'reused_from_certificate':previous['certificate_id'],'new_horizon_check':'Reused formulas and sparsity recipe checked against complete independent N=6 solve; residuals in numerical_checks.'}
state['certificate_id']=certificate_digest(state)
state['dense_reference']={'source':'state/ogm_b1.json','N':6,'opt_value':dense_row['opt_value'],'solver':dense_row['solver'],'options':dense_row['options']}
(root/'supplementary/ogm_b2_N6.json').write_text(json.dumps(state,indent=2,allow_nan=False))
print('N=6 certificate',state['certificate_id'])
print(json.dumps(checks,indent=2))
print('Selected main certificate remains N=4:',json.loads((root/'state/ogm_b2.json').read_text())['N_verify'])
