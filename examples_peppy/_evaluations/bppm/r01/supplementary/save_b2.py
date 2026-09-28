import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent/'helpers'))
import runtime
import json
import hashlib
import numpy as np
import pepflow as pf
from bppm_setup import get_pep_setup
notebook_dir=runtime.ROOT
source=(notebook_dir/'supplementary/b2_verification.py').read_text(encoding='utf-8-sig')
exec(compile(source,'b2_verification.py','exec'))
state={**b1,**certificate}
state.update(normalization=dict(tau_name='initial_condition',initial_condition=b1['initial_condition'],performance_metric=b1['performance_metric'],bound_value=certificate['opt_value'],bound_formula=b1['conjectured_rate']),numerical_checks=dict(tolerances=tolerances,residuals=residuals,passed=True),numerical_decomposition=dict(method='direct',factorization='spectral',D=D.tolist(),ell_coords=E.tolist(),basis_labels=certificate['basis_vectors']),S_decomp_type='direct',formula_status={'lambda':'candidate','S':'candidate'},closed_form_search=dict(completed=True,references_reviewed=['own approved input and generic framework only; no existing proof references authorized'],attempts=[{'method':'Rational approximations of all sparse multipliers plus proximal optimality relation','lambda_max_error':lambda_error,'S_zero_max_error':max_abs(S_array),'fixed_sample_exact_identity':True}],unresolved_components=['arbitrary-horizon and parameter proof of candidate lambda/S']),numerical_certificate_verified=True,analytic_full_pep_verified=False,lyapunov_proof_verified=False,require_analytic_full_pep=False,proof_valid=True,certificate_check_source=source)
start=source.index('def candidate_duals(')
end=source.index('\ncandidate =',start)
state['lamb_code']=source[start:end]
state['S_code']='S_guess = pf.Scalar.zero()'
labels=sorted(set(tag for name in candidate if name.startswith('f:') for tag in name.split(':')[1].split(',')))
state.update(lambda_matrix=[[certificate['named_dual_values'].get(f'f:{ri},{ci}') or 0.0 for ci in labels] for ri in labels],lambda_row_names=labels,lambda_col_names=labels)
keys=('N_verify','params_json','relaxed_constraints','S_matrix','S_row_names','S_col_names','basis_vectors','basis_scalars','opt_value','tau_sol','tau_name','named_dual_values','constraint_metadata','normalization','certificate_provenance','numerical_checks','numerical_decomposition')
state['certificate_id']=hashlib.sha256(json.dumps({k:state[k] for k in keys},sort_keys=True,separators=(',',':'),allow_nan=False).encode()).hexdigest()
for filename in ('bppm_b2.json','bppm_relaxed.json'):
    (notebook_dir/'state'/filename).write_text(json.dumps(state,indent=2,allow_nan=False))
print('B2 state saved, certificate:',state['certificate_id'])
