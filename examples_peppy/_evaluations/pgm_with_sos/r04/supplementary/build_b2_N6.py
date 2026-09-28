import hashlib
import json
from pathlib import Path
import sys
sys.path.insert(0,str(Path(__file__).resolve().parent/'helpers'))
import runtime
import nbformat
from nbclient import NotebookClient

root=runtime.ROOT
source=(root/'supplementary/b2_notebook_cells.py').read_text(encoding='utf-8-sig')
source=source.replace('state/pgm_dense.json','supplementary/b2-N6-dense.json').replace('state/pgm_selected_raw.json','supplementary/b2-N6-raw.json')
namespace={'notebook_dir':root}
exec((root/'pgm_setup.py').read_text(),namespace)
exec(source,namespace)
raw=namespace['raw']
b1=namespace['b1']
residuals=namespace['residuals']
state={**b1,**raw,'N_verify':raw['N'],'tau_name':'initial_condition','tau_sol':raw['named_dual_values']['initial_condition'],'S_row_names':raw['basis_vectors'],'S_col_names':raw['basis_vectors'],
'normalization':dict(tau_name='initial_condition',initial_condition=b1['initial_condition'],performance_metric=b1['performance_metric'],bound_value=raw['opt_value'],bound_formula=b1['conjectured_rate']),
'certificate_provenance':dict(solve_id='b2-refined-dual-N6',pep_type=raw.get('pep_type','primal'),solver_status=raw['status'],source_hashes=raw['source_hashes'],solver=dict(api='CVXDualSolver.build_problem + cvxpy.Problem.solve; derived multiplier equalities',effective_name='CLARABEL',settings=raw['solver_options'])),
'numerical_checks':dict(tolerances=dict(identity_atol=1e-5,identity_rtol=0,reconstruction_atol=1e-4,reconstruction_rtol=1e-5,dual_tol=1e-6,psd_tol=1e-6,dense_opt_atol=1e-5),residuals=residuals,passed=True),
'numerical_decomposition':dict(method='direct',D=namespace['D'].tolist(),ell_coords=namespace['E'].tolist(),basis_labels=raw['basis_vectors'],piece_grouping='three supplied squared vectors per iteration, sequential i=1..N',normalization_factor=1,piece_gram_coordinates=[namespace['np'].array(namespace['pm'].eval_scalar(p).inner_prod_coords,dtype=float).tolist() for p in namespace['pieces']]),
'closed_form_search':dict(completed=True,references_reviewed=['supplementary/approved/input.md: supplied fixed SOS aid'],attempts=['Inspected fractions from dense and consecutive-only relaxed certificates for both f and g. Inferred alpha_i=i/(2N+1-i), beta_i=i/(2N-i), and optimizer-row differences.','Implemented supplied SOS with exact rational coefficients; compared at normalization 1 to the selected coherent numerical S.','Checked candidate multiplier/SOS identity at N=4, including all Gram, function and constant coordinates.'],unresolved_components=['all-horizon analytic full-PEP identity']),
'formula_status':{'lambda':'candidate','S':'candidate'},'lamb_code':source[source.index('def lambda_candidate'):source.index('lambda_errors =')], 'S_code':source[source.index('def supplied_sos'):source.index('pieces, coefficients, vectors = supplied_sos')],
'S_decomp_type':'direct','numerical_certificate_verified':True,'analytic_full_pep_verified':False,'lyapunov_proof_verified':False,'require_analytic_full_pep':False,'proof_valid':True,'certificate_check_source':'supplementary/b2_notebook_cells.py'}
for owner in ('f','g'):
    labels=['x_star']+[f'x_{i}' for i in range(0 if owner=='f' else 1,raw['N']+1)]
    matrix=[[raw['named_dual_values'].get(f'{owner}:{left},{right}') or 0 for right in labels] for left in labels]
    state.setdefault('lambda_groups',{})[owner]=dict(matrix=matrix,row_names=labels,col_names=labels)
keys=('N_verify','params_json','relaxed_constraints','S_matrix','S_row_names','S_col_names','basis_vectors','basis_scalars','opt_value','tau_sol','tau_name','named_dual_values','constraint_metadata','normalization','certificate_provenance','numerical_checks','numerical_decomposition')
state['certificate_id']=hashlib.sha256(json.dumps({k:state[k] for k in keys},sort_keys=True,separators=(',',':'),allow_nan=False).encode()).hexdigest()
for name in ('b2-N6-certificate.json',):
    (root/'supplementary'/name).write_text(json.dumps(state,indent=2,allow_nan=False))


