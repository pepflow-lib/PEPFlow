import importlib.util
import json
import hashlib
from pathlib import Path
spec = importlib.util.spec_from_file_location('runtime', Path(__file__).parent / 'helpers/runtime.py')
assert spec is not None and spec.loader is not None
runtime = importlib.util.module_from_spec(spec)
spec.loader.exec_module(runtime)
import numpy as np
import pepflow as pf
import sympy as sp
from pepflow.lyapunov_utils import ldl_decompose_with_reversed_basis
from certificates import acquire
from verify_certificate import verify_saved
from partial_sums import KEYS

root = runtime.ROOT
b2 = json.loads((root / 'state/feg_b2.json').read_text())
*_, dense = acquire(8)
(root / 'supplementary/feg_dense_N8.json').write_text(json.dumps(dense, indent=2))
n = 8
keep = {'initial_condition', f'A monotone:x_{n},x_star'}
keep |= {f'A monotone:x_{k},x_{k+1}' for k in range(1,n)}
keep |= {f'A Lipschitz:{"x_0" if k == 0 else f"x_{k}+1/2"},x_{k+1}' for k in range(n)}
dropped = [name for name in dense['named_dual_values'] if name not in keep]
assert keep.issubset(dense['named_dual_values'])
ctx, pb, obj, result, entries, data = acquire(8, dropped)
pm = pf.ExpressionManager(ctx, resolve_parameters={'L': sp.S(1), 'R': sp.S(1)})
D, ell = ldl_decompose_with_reversed_basis(result.get_gram_dual_matrix(), ctx.basis_vectors(), print_output=False)
E = np.asarray([pm.eval_vector(v).coords for v in ell], dtype=float)
data['numerical_decomposition'] = dict(method='reverse_ldl',D=D.tolist(),ell_coords=E.tolist(),basis_labels=data['basis_vectors'])
*_, checks = verify_saved(data, dense['opt_value'])
assert abs(data['opt_value']-4/n**2) < 1e-5
for key in ['algo_name','problem_type','obj_tag','performance_metric','initial_condition','conjectured_rate','setup_file','formula_status','lamb_code','S_code','closed_form_search']:
    data[key] = b2[key]
data['closed_form_search'] = dict(data['closed_form_search'], reused_from_certificate=b2['certificate_id'], applicability='Same recurrence, normalization, support recipe; unresolved analytic guesses not used for this numerical certificate')
data.update(numerical_checks=checks,numerical_certificate_verified=True,analytic_full_pep_verified=False,lyapunov_proof_verified=False,proof_valid=True,require_analytic_full_pep=False,S_decomp_type='ldl')
data['certificate_id'] = hashlib.sha256(json.dumps({k:data[k] for k in KEYS},sort_keys=True,separators=(',',':'),allow_nan=False).encode()).hexdigest()
(root / 'supplementary/feg_certificate_N8.json').write_text(json.dumps(data,indent=2,allow_nan=False))
print('N=8 dense objective', dense['opt_value'])
print('N=8 relaxed objective',data['opt_value'])
print('N=8 checks',checks)
print('N=8 certificate',data['certificate_id'])
