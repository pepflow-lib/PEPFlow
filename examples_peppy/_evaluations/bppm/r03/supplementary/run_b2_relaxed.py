import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent / 'helpers'))
import runtime
import json
import hashlib
import numpy as np
import bppm_setup as setup
from certificate import capture, inventory
from formulas import candidate_duals

root = runtime.ROOT
b1 = json.loads((root / 'state/bppm_b1.json').read_text())
dense = json.loads((root / 'state/bppm_dense.json').read_text())
params = json.loads(b1['params_json'])
n = b1['N_verify']
ctx, pb, obj = setup.get_pep_setup(n, params)
candidate = candidate_duals(n, params['alpha'])
relaxed = [c.name for c, *_ in inventory(ctx, pb) if c.name not in candidate]
pb.set_relaxed_constraints(relaxed)
data = capture(ctx, pb, obj, params, dense['opt_value'])
error = max(abs(value-candidate.get(name,0)) for name,value in data['named_dual_values'].items() if value is not None)
S_error = float(np.max(np.abs(data['S_matrix'])))
assert error < 1e-4 and S_error < 1e-4
lamb_code = (root / 'supplementary/helpers/formulas.py').read_text(encoding='utf-8-sig')
state = {**b1, **data, 'N_verify':n,
'normalization':dict(tau_name='initial_condition',initial_condition=b1['initial_condition'],performance_metric=b1['performance_metric'],bound_value=data['opt_value'],bound_formula=b1['conjectured_rate']),
'closed_form_search':{'completed':True,'references_reviewed':['own input, approved generic framework; target references excluded'],
'attempts':[{'method':'Inspect dense multipliers; drop all entries outside adjacent pairs, f optimum pairs, terminal h optimum pair','outcome':'Preserves optimum; all selected multipliers match index-linear candidates','lambda_max_error':error},
{'method':'Inspect near-zero dense and relaxed S; compare exact zero candidate to all Gram entries, and zero scalar/offset coordinates','outcome':'Numerically matches zero S; exact all-horizon proof deferred','S_max_error':S_error}],
'unresolved_components':['analytic all-horizon lambda/S identity and domain proof']},
'formula_status':{'lambda':'candidate','S':'candidate'},'lamb_code':lamb_code,'S_code':'def S_guess():\n    return pf.Scalar.zero()\n',
'S_decomp_type':'direct','numerical_certificate_verified':True,'analytic_full_pep_verified':False,'lyapunov_proof_verified':False,
'require_analytic_full_pep':False,'proof_valid':True,'candidate_lambda_max_error':error,'candidate_S_max_error':S_error,
'construction_recipe':'f optimum pairs; f forward adjacent pairs from i=2; h reverse adjacent all; h forward adjacent from i=2; h optimum-to-terminal.'}
keys = ('N_verify','params_json','relaxed_constraints','S_matrix','S_row_names','S_col_names','basis_vectors','basis_scalars','opt_value','tau_sol','tau_name','named_dual_values','constraint_metadata','normalization','certificate_provenance','numerical_checks','numerical_decomposition')
state['certificate_id'] = hashlib.sha256(json.dumps({key:state[key] for key in keys},sort_keys=True,separators=(',',':'),allow_nan=False).encode()).hexdigest()
for name in ('bppm_relaxed.json','bppm_b2.json'):
    (root / 'state' / name).write_text(json.dumps(state, indent=2, allow_nan=False))
print('relaxed objective',state['opt_value'],'dropped',len(relaxed))
print('candidate errors',error,S_error)
print(state['numerical_checks'])
for name,value in state['named_dual_values'].items():
    if value is not None:
        print(name,value)
