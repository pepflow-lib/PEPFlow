import runpy
from pathlib import Path
runpy.run_path(str(Path(__file__).with_name('runtime.py')))
import json
import hashlib
import numpy as np
from feg_setup import get_pep_setup

notebook_dir = Path(__file__).resolve().parents[1]
exec((notebook_dir/'supplementary/N8/check_cell.py').read_text(encoding='utf-8-sig'))
exec((notebook_dir/'supplementary/b2_search_cell.py').read_text(encoding='utf-8-sig'))
allowlist = json.loads((notebook_dir/'supplementary/approved/allowlist.json').read_text())
paths = [Path(p) for p in allowlist['exact_read_files'] if Path(p).parent == notebook_dir/'supplementary/approved/pepflow']
paths += [notebook_dir/'feg_setup.py']
source_hashes = {str(p.relative_to(notebook_dir)).replace('\\','/'):hashlib.sha256(p.read_bytes()).hexdigest() for p in paths}
state = {**b1,**selected}
state.update(numerical_certificate_verified=True,analytic_full_pep_verified=False,lyapunov_proof_verified=False,proof_valid=True,require_analytic_full_pep=False,lamb_code=None,S_code=None,S_decomp_type='ldl',formula_status={'lambda':'unresolved','S':'unresolved'},normalization=dict(tau_name='initial_condition',initial_condition=b1['initial_condition'],performance_metric=b1['performance_metric'],bound_value=selected['opt_value'],bound_formula=b1['conjectured_rate']),certificate_provenance=dict(solve_id=selected['solve_id'],pep_type='primal',solver_status=selected['solver_status'],source_hashes=selected['source_hashes_before_and_after_solve'],solver=dict(api='CVXPrimalSolver.build_problem and cvxpy.Problem.solve',effective_name='CLARABEL',settings={'solver':'CLARABEL'})),numerical_checks=dict(tolerances=json.loads((notebook_dir/'supplementary/approved/settings.json').read_text())['tolerances'],residuals=residuals,passed=True),numerical_decomposition=dict(method='reverse_ldl',D=np.asarray(D).tolist(),ell_coords=E.tolist(),basis_labels=selected['basis_vectors']),closed_form_search=dict(completed=True,references_reviewed=['Own input and approved generic framework; target references prohibited'],attempts=[dict(method='Rational inspection: monotone 4k(k+1)/N^2, endpoint 4/N; Lipschitz 2(k+1)^2/N^2',max_error=lambda_error,matched=lambda_error<=1e-4),dict(method='Rank-one candidate (2(x0-xstar)/N-A(xN))^2',max_error=S_guess_error,matched=S_guess_error<=1e-4)],unresolved_components=['lambda','S']))
keys=('N_verify','params_json','relaxed_constraints','S_matrix','S_row_names','S_col_names','basis_vectors','basis_scalars','opt_value','tau_sol','tau_name','named_dual_values','constraint_metadata','normalization','certificate_provenance','numerical_checks','numerical_decomposition')
state['certificate_id']=hashlib.sha256(json.dumps({k:state[k] for k in keys},sort_keys=True,separators=(',',':'),allow_nan=False).encode()).hexdigest()
for name in ('feg_b2.json','feg_relaxed.json'):
    (notebook_dir/'supplementary/N8'/name).write_text(json.dumps(state,indent=2))
print('B2 state saved')


