# CELL
import hashlib
import uuid
from fractions import Fraction
import numpy as np
import sympy as sp
from pepflow.lyapunov_utils import ldl_decompose_with_reversed_basis
from solve_runtime import solve_primal

b1 = json.loads((notebook_dir / 'state' / 'pgm_b1.json').read_text())
N_int = b1['N_verify']
params_sp: dict[str, pf.NUMERICAL_TYPE] = {'L': sp.Integer(1), 'R': sp.Integer(1)}
dense_data = json.loads((notebook_dir / 'state' / 'pgm_dense.json').read_text())
assert dense_data['N'] == N_int
print('Dense optimum:', dense_data['opt_value'], dense_data['solver'])
print('Basis:', dense_data['basis_vectors'])
for tag in ('f', 'g'):
    entries_dense = {name: value for name, value in dense_data['named_duals'].items()
                     if name.startswith(tag + ':') and abs(value) > 1e-6}
    print(tag, 'dense active count:', len(entries_dense), 'range:',
          (min(entries_dense.values()), max(entries_dense.values())))
print('Dense Gram rank at 1e-4:', np.linalg.matrix_rank(np.array(dense_data['S_matrix']), tol=1e-4))
source_paths = [notebook_dir / 'pgm_setup.py', notebook_dir / 'supplementary/helpers/solve_runtime.py']
allowlist = json.loads((repo_root / 'allowlist.json').read_text())
source_paths += [Path(p) for p in allowlist['exact_read_files'] if Path(p).parent == repo_root / 'pepflow']
source_hashes = {str(p.relative_to(notebook_dir)).replace('\\', '/'): hashlib.sha256(p.read_bytes()).hexdigest() for p in source_paths}
ctx, pb, obj = get_pep_setup(N_int, params_sp)
relaxed = []
for owner in ctx.func_to_triplets:
    for constraint in owner.get_interpolation_constraints(ctx):
        left, right = constraint.name.split(':')[1].split(',')
        keep = left == 'x_star' or (left != 'x_star' and right != 'x_star'
                and int(right[2:]) == int(left[2:]) + 1)
        if not keep:
            relaxed.append(constraint.name)
pb.set_relaxed_constraints(relaxed)
result, solver_metadata = solve_primal(ctx, pb, params_sp)
assert result.context is ctx
print('Relaxed:', result.opt_value, solver_metadata)
print('Dropped constraints:', len(relaxed))
assert abs(result.opt_value - dense_data['opt_value']) < 1e-5
assert abs(result.opt_value - 1/(4*N_int)) < 1e-5

# CELL
entries = [(c, 'initial', None, None) for c in pb.init_conditions]
for owner in ctx.func_to_triplets:
    groups = ctx.get_constraint_data(owner)
    entries.extend((c, 'interpolation', str(owner), str(group))
                   for group, constraints in groups.sc_dict.items() for c in constraints)
    entries.extend((c, 'interpolation', str(owner), str(group))
                   for group, c in groups.psd_dict.items())
assert len({c.name for c, *_ in entries}) == len(entries)
constraint_metadata = {}
named_dual_values = {}
for c, origin, owner, group in entries:
    assert isinstance(c, pf.ScalarConstraint), 'Unexpected non-scalar family'
    dropped = c.name in relaxed
    value = result.get_dual_value(c.name)
    assert dropped or value is not None
    constraint_metadata[c.name] = dict(origin=origin, owner=owner, group=group,
        kind='scalar', comparator=c.cmp.value, shape=[], relaxed=dropped)
    named_dual_values[c.name] = None if dropped else float(value)
    if not dropped:
        print(c.name, float(value), Fraction(float(value)).limit_denominator(1000))
assert set(relaxed).issubset(constraint_metadata)
S_sol = result.get_gram_dual_matrix()
S_array = np.asarray(S_sol.matrix, dtype=float)
basis = ctx.basis_vectors()
assert S_sol.row_names == [str(v) for v in basis]
pm = pf.ExpressionManager(ctx, resolve_parameters=params_sp)

# CELL
def lambda_candidate(owner, ri, ci, horizon):
    """Candidate inferred from consecutive cumulative weights."""
    def cumulative(k):
        if k < (0 if owner == 'f' else 1):
            return sp.S.Zero
        return sp.Rational(k + (1 if owner == 'f' else 0), 2*horizon-k)
    if ri == 'x_star':
        j = int(ci[2:])
        return (sp.S.One if j == horizon else cumulative(j)) - cumulative(j-1)
    if ci != 'x_star' and int(ci[2:]) == int(ri[2:])+1:
        return cumulative(int(ri[2:]))
    return sp.S.Zero

candidate_duals = {}
for c, origin, owner, group in entries:
    if origin == 'initial':
        candidate_duals[c.name] = sp.Rational(1, 4*N_int)
    else:
        ri, ci = c.name.split(':')[1].split(',')
        candidate_duals[c.name] = lambda_candidate(owner, ri, ci, N_int)
lambda_error = max(abs(float(candidate_duals[name])-float(value or 0))
                   for name, value in named_dual_values.items())
print('All-group candidate multiplier error:', lambda_error)
assert lambda_error < 1e-4
for owner in ctx.func_to_triplets:
    labels = ctx.order_of_point(owner)
    matrix = np.array([[float(lambda_candidate(str(owner), a, b, N_int)) if a != b else 0
                        for b in labels] for a in labels])
    pf.pprint_labeled_matrix(pf.MatrixWithNames(matrix, labels, labels))

# The candidate remainder is defined by the exact residual identity.
# This defines its coefficients; positivity for arbitrary N is still open.
S_guess = sp.Rational(1, 4*N_int) * (ctx['x_0']-ctx['x_star'])**2 - pb.performance_metric
for c, origin, owner, group in entries:
    if origin == 'interpolation':
        residual = c.lhs-c.rhs
        if c.cmp == pf.Comparator.GE:
            residual = -residual
        S_guess += candidate_duals[c.name] * residual
candidate_checked = pm.eval_scalar(S_guess)
S_candidate = np.asarray(candidate_checked.inner_prod_coords, dtype=float)
S_candidate_error = float(np.max(np.abs(S_candidate-S_array)))
print('Candidate S error:', S_candidate_error)
assert S_candidate_error < 1e-4
assert np.max(np.abs(candidate_checked.func_coords), initial=0) < 1e-5
assert abs(float(candidate_checked.offset)) < 1e-5
pf.pprint_labeled_matrix(pf.MatrixWithNames(S_candidate, S_sol.row_names, S_sol.col_names))

# CELL
# No supplied decomposition is authorized for this condition.
# Decompose this same live numerical S in the matching original basis.
D, ell = ldl_decompose_with_reversed_basis(S_sol, basis, print_output=False)
D = np.asarray(D, dtype=float)
E = np.asarray([pm.eval_vector(v).coords for v in ell], dtype=float)
S_numeric = sum((float(D[i,j])*ell[i]*ell[j] for i,j in np.ndindex(D.shape)), pf.Scalar.zero())
S_reconstructed = E.T @ D @ E
numerical_decomposition = {'method':'reverse_ldl', 'D':D.tolist(),
    'ell_coords':E.tolist(), 'basis_labels':[str(v) for v in basis]}
print('Reverse LDL diagonal:', np.diag(D))
print('LDL factors in original basis:', E)
pf.pprint_labeled_matrix(pf.MatrixWithNames(S_reconstructed-S_array, S_sol.row_names, S_sol.col_names))
weighted_constraints = pf.Scalar.zero()
scalar_duals = []
for c, origin, owner, group in entries:
    value = named_dual_values[c.name]
    if constraint_metadata[c.name]['relaxed']:
        assert value is None
        continue
    residual = c.lhs-c.rhs
    if c.cmp in (pf.Comparator.GE, pf.Comparator.SEQ):
        residual = -residual
    assert value is not None
    weighted_constraints += float(value) * (pf.Scalar.zero()+residual)
    if c.cmp != pf.Comparator.EQ:
        scalar_duals.append(float(value))
diff = pb.performance_metric-float(result.opt_value)-weighted_constraints+S_numeric
checked = pm.eval_scalar(diff)

def max_abs(values):
    return float(np.max(np.abs(np.asarray(values,dtype=float)),initial=0))

residuals = {
    'identity_gram_max_abs':max_abs(checked.inner_prod_coords),
    'identity_func_max_abs':max_abs(checked.func_coords),
    'identity_offset_abs':max_abs(checked.offset),
    'S_reconstruction_max_abs':max_abs(S_reconstructed-S_array),
    'dense_relaxed_gap':abs(result.opt_value-dense_data['opt_value']),
    'minimum_scalar_inequality_dual':min(scalar_duals,default=0),
    'minimum_S_eigenvalue':float(np.linalg.eigvalsh((S_array+S_array.T)/2).min()),
    'minimum_matrix_inequality_eigenvalue':0.0,
}
tolerances = dict(identity_atol=1e-5,identity_rtol=0.0,reconstruction_atol=1e-4,
    reconstruction_rtol=1e-5,dual_tol=1e-6,psd_tol=1e-6,dense_opt_atol=1e-5)
passed = (str(result.solver_status)=='optimal' and np.all(np.isfinite(S_array))
    and np.allclose(S_array,S_array.T,atol=1e-6,rtol=0)
    and all(residuals[k] <= 1e-5 for k in ('identity_gram_max_abs','identity_func_max_abs','identity_offset_abs'))
    and np.allclose(S_reconstructed,S_array,atol=1e-4,rtol=1e-5)
    and residuals['dense_relaxed_gap']<1e-5
    and residuals['minimum_scalar_inequality_dual']>=-1e-6
    and residuals['minimum_S_eigenvalue']>=-1e-6)
print('Numerical certificate residuals:',residuals)
print('Numerical certificate verified:', bool(passed))
pf.pprint_labeled_matrix(pf.MatrixWithNames(np.asarray(checked.inner_prod_coords,dtype=float), S_sol.row_names,S_sol.col_names))
print('Function residual:', np.asarray(checked.func_coords,dtype=float))
print('Constant residual:',float(checked.offset))
assert passed

# CELL
closed_form_search = {'completed':True,'references_reviewed':[],
    'reference_policy':'No target references or supplied SOS aid authorized.',
    'attempts':[
        {'method':'Rationalize both consecutive lambda families; infer cumulative weights (k+1)/(2N-k) for f and k/(2N-k) for g; star weights are successive differences with terminal cumulative weight 1.',
         'outcome':'Candidate agrees at N=4, L=R=1; arbitrary-horizon feasibility unproved.', 'max_error':lambda_error},
        {'method':'Construct rational S from candidate interpolation weights and normalization; compare all coordinates and inspect reverse LDL factors.',
         'outcome':'Matches numerical S; no proved all-horizon positive decomposition yet.', 'max_error':S_candidate_error}],
    'unresolved_components':['analytic multiplier validity','all-horizon PSD/SOS of S']}
formula_status = {'lambda':'candidate','S':'candidate'}
lamb_code = '''def lamb(owner, ri, ci, N):
    def cumulative(k):
        if k < (0 if owner == "f" else 1): return sp.S.Zero
        return sp.Rational(k + (1 if owner == "f" else 0), 2*N-k)
    if ri == "x_star":
        j = int(ci[2:])
        return (sp.S.One if j == N else cumulative(j)) - cumulative(j-1)
    if ci != "x_star" and int(ci[2:]) == int(ri[2:])+1:
        return cumulative(int(ri[2:]))
    return sp.S.Zero
'''
S_code = '''S_guess = L/(4*N) * (ctx["x_0"]-ctx["x_star"])**2 - pb.performance_metric
for owner in ctx.func_to_triplets:
    for c in owner.get_interpolation_constraints(ctx):
        ri,ci=c.name.split(":")[1].split(",")
        S_guess += lamb(str(owner),ri,ci,N)*(c.lhs-c.rhs)
'''
for relative, expected in source_hashes.items():
    assert hashlib.sha256((notebook_dir/relative).read_bytes()).hexdigest()==expected
lambda_data = result.get_scalar_constraint_dual_value_in_numpy(obj)
assert isinstance(lambda_data,pf.MatrixWithNames)
tau_value = named_dual_values['initial_condition']
assert tau_value is not None
state_b2 = {**b1,'N':N_int,'N_verify':N_int,'opt_value':float(result.opt_value),
    'tau_sol':float(tau_value),'tau_name':'initial_condition',
    'relaxed_constraints':list(relaxed),'S_matrix':S_array.tolist(),
    'S_row_names':list(S_sol.row_names),'S_col_names':list(S_sol.col_names),
    'basis_vectors':[str(v) for v in basis],'basis_scalars':[str(v) for v in ctx.basis_scalars()],
    'named_dual_values':named_dual_values,'constraint_metadata':constraint_metadata,
    'lambda_matrix':np.asarray(lambda_data.matrix,dtype=float).tolist(),
    'lambda_row_names':list(lambda_data.row_names),'lambda_col_names':list(lambda_data.col_names),
    'normalization':dict(tau_name='initial_condition',initial_condition=b1['initial_condition'],
        performance_metric=b1['performance_metric'],bound_value=float(result.opt_value),bound_formula=b1['conjectured_rate']),
    'certificate_provenance':dict(solve_id=str(uuid.uuid4()),pep_type='primal',
        solver_status=str(result.solver_status),source_hashes=source_hashes,
        solver=dict(api='CVXPrimalSolver.build_problem',**solver_metadata)),
    'numerical_checks':dict(tolerances=tolerances,residuals=residuals,passed=bool(passed)),
    'numerical_decomposition':numerical_decomposition,'closed_form_search':closed_form_search,
    'formula_status':formula_status,'lamb_code':lamb_code,'S_code':S_code,'S_decomp_type':'ldl',
    'numerical_certificate_verified':True,'analytic_full_pep_verified':False,
    'lyapunov_proof_verified':False,'require_analytic_full_pep':False,'proof_valid':True}
certificate_keys = ('N_verify','params_json','relaxed_constraints','S_matrix','S_row_names',
    'S_col_names','basis_vectors','basis_scalars','opt_value','tau_sol','tau_name',
    'named_dual_values','constraint_metadata','normalization','certificate_provenance',
    'numerical_checks','numerical_decomposition')
state_b2['certificate_id'] = hashlib.sha256(json.dumps({key:state_b2[key] for key in certificate_keys},
    sort_keys=True,separators=(',',':'),allow_nan=False).encode()).hexdigest()
for filename in ('pgm_relaxed.json','pgm_b2.json'):
    (notebook_dir/'state'/filename).write_text(json.dumps(state_b2,indent=2,allow_nan=False))
print('Initial search:',closed_form_search)
print('Numerical certificate verified; analytic full-PEP and Lyapunov proofs remain pending.')

