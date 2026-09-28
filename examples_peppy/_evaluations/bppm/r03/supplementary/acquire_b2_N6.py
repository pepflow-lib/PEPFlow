import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent/'helpers'))
import runtime
import json
import hashlib
import numpy as np
import bppm_setup as setup
from certificate import capture,inventory
from formulas import candidate_duals
root=runtime.ROOT
prior=json.loads((root/'state/bppm_b2.json').read_text())
params=json.loads(prior['params_json'])
n=6
ctx,pb,obj=setup.get_pep_setup(n,params)
dense=capture(ctx,pb,obj,params)
(root/'supplementary/b2-N6-dense.json').write_text(json.dumps(dense,indent=2))
ctx,pb,obj=setup.get_pep_setup(n,params)
candidate=candidate_duals(n,params['alpha'])
relaxed=[c.name for c,*_ in inventory(ctx,pb) if c.name not in candidate]
pb.set_relaxed_constraints(relaxed)
data=capture(ctx,pb,obj,params,dense['opt_value'])
error=max(abs(value-candidate.get(name,0)) for name,value in data['named_dual_values'].items() if value is not None)
s_error=float(np.max(np.abs(data['S_matrix'])))
assert error<=1e-4 and s_error<=1e-4
state={**prior,**data,'N_verify':n,'candidate_lambda_max_error':error,'candidate_S_max_error':s_error}
state['normalization']={**prior['normalization'],'bound_value':state['opt_value']}
state['closed_form_search']={**prior['closed_form_search'],'reused_from_certificate':prior['certificate_id'],'new_horizon_candidate_checks':{'N':n,'lambda_max_error':error,'S_max_error':s_error}}
keys=('N_verify','params_json','relaxed_constraints','S_matrix','S_row_names','S_col_names','basis_vectors','basis_scalars','opt_value','tau_sol','tau_name','named_dual_values','constraint_metadata','normalization','certificate_provenance','numerical_checks','numerical_decomposition')
state['certificate_id']=hashlib.sha256(json.dumps({key:state[key] for key in keys},sort_keys=True,separators=(',',':'),allow_nan=False).encode()).hexdigest()
(root/'supplementary/b2-N6-certificate.json').write_text(json.dumps(state,indent=2,allow_nan=False))
print('N6 dense',dense['opt_value'],'relaxed',state['opt_value'])
print('candidate errors',error,s_error)
print(state['numerical_checks']['residuals'])
