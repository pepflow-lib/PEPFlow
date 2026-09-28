import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent/'helpers'))
import runtime
import json
from certificate import acquire, digest

root=runtime.ATTEMPT
prior=json.loads((root/'state/feg_b2.json').read_text())
dense=acquire(4)
(root/'supplementary/b2-dense-N4.json').write_text(json.dumps(dense,indent=2,allow_nan=False))
def keep(name,n):
    if name=='initial_condition':
        return True
    family,pair=name.split(':')
    points=set(pair.split(','))
    if family=='A monotone':
        return points=={f'x_{n}','x_star'} or any(points=={f'x_{k}',f'x_{k+1}'} for k in range(1,n))
    if family=='A Lipschitz':
        return any(points=={f'x_{j}',f'x_{2*j-1}/2'} for j in range(1,n+1))
    return False
relaxed=[name for name in dense['named_dual_values'] if not keep(name,4)]
data=acquire(4,relaxed,dense['opt_value'])
assert data['numerical_checks']['passed']
for key in ('closed_form_search','formula_status','lamb_code','S_code','require_analytic_full_pep','sparsity_recipe'):
    data[key]=prior[key]
data['closed_form_search']={**data['closed_form_search'],'reused_from_certificate_id':prior['certificate_id'],'reuse_note':'Initial search completed at N=6; analytic candidates remain separate and are not used to replace this N=4 numerical certificate.'}
data['S_decomp_type']='ldl'
data['proof_valid']=True
data['certificate_id']=digest(data)
(root/'supplementary/b2-certificate-N4.json').write_text(json.dumps(data,indent=2,allow_nan=False))
print(json.dumps({'N':4,'dense':dense['opt_value'],'relaxed':data['opt_value'],'certificate_id':data['certificate_id'],'checks':data['numerical_checks']},indent=2))
