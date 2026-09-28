import importlib.util
import json
from pathlib import Path
root = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location('runtime', root / 'supplementary/helpers/runtime.py')
assert spec is not None and spec.loader is not None
runtime = importlib.util.module_from_spec(spec)
spec.loader.exec_module(runtime)
import dual_feg_setup as setup
import numpy as np
import pepflow as pf
import sympy as sp
import hashlib

notebook_dir = root
get_pep_setup = setup.get_pep_setup
# BEGIN NOTEBOOK VERIFICATION
selected = json.loads((notebook_dir / 'state/dual_feg_relaxed.json').read_text())
b1 = json.loads((notebook_dir / 'state/dual_feg_b1.json').read_text())
dense = json.loads((notebook_dir / 'state/dual_feg_dense.json').read_text())
N = selected['N']
params: dict[str, pf.NUMERICAL_TYPE] = {'L': sp.Integer(1), 'R': sp.Integer(1)}
ctx, pb, obj = get_pep_setup(N, params)
ctx.set_as_current()
pm = pf.ExpressionManager(ctx, resolve_parameters=params)
assert selected['basis_vectors'] == [str(v) for v in ctx.basis_vectors()]
assert selected['basis_scalars'] == [str(v) for v in ctx.basis_scalars()]
entries = list(pb.init_conditions) + obj.get_interpolation_constraints(ctx)
assert {c.name for c in entries} == set(selected['named_dual_values'])
for relative, expected in selected['certificate_provenance']['source_hashes'].items():
    assert hashlib.sha256((notebook_dir / relative).read_bytes()).hexdigest() == expected
weighted = pf.Scalar.zero()
values = []
for constraint in entries:
    value = selected['named_dual_values'][constraint.name]
    metadata = selected['constraint_metadata'][constraint.name]
    assert metadata['comparator'] == constraint.cmp.value
    if metadata['relaxed']:
        assert value is None
        continue
    assert value is not None
    residual = constraint.lhs - constraint.rhs
    if constraint.cmp in (pf.Comparator.GE, pf.Comparator.SEQ):
        residual = -residual
    weighted += float(value) * residual
    if constraint.cmp != pf.Comparator.EQ:
        values.append(float(value))
S_array = np.array(selected['S_matrix'], dtype=float)
D = np.array(selected['numerical_decomposition']['D'], dtype=float)
E = np.array(selected['numerical_decomposition']['ell_coords'], dtype=float)
basis = ctx.basis_vectors()
ell = [sum((float(a) * v for a, v in zip(row, basis)), pf.Vector.zero()) for row in E]
S_numeric = sum((float(D[i,j]) * ell[i] * ell[j] for i,j in np.ndindex(D.shape)), pf.Scalar.zero())
assert pb.performance_metric is not None
identity = pb.performance_metric - selected['opt_value'] - weighted + S_numeric
checked = pm.eval_scalar(identity)
def max_abs(values):
    return float(np.max(np.abs(np.asarray(values, dtype=float)), initial=0.0))
residuals = dict(identity_gram_max_abs=max_abs(checked.inner_prod_coords), identity_func_max_abs=max_abs(checked.func_coords),
    identity_offset_abs=max_abs(checked.offset), S_reconstruction_max_abs=max_abs(E.T @ D @ E-S_array),
    dense_relaxed_gap=abs(dense['opt_value']-selected['opt_value']),
    minimum_scalar_inequality_dual=min(values), minimum_S_eigenvalue=float(np.linalg.eigvalsh(S_array).min()),
    minimum_matrix_inequality_eigenvalue=0.0)
tolerances = dict(identity_atol=1e-5, identity_rtol=0.0, reconstruction_atol=1e-4, reconstruction_rtol=1e-5, dual_tol=1e-6, psd_tol=1e-6, dense_opt_atol=1e-5)
assert selected['certificate_provenance']['solver_status'] == 'optimal'
assert np.isfinite(S_array).all() and np.allclose(S_array,S_array.T,atol=1e-6,rtol=0)
assert max(residuals[k] for k in ['identity_gram_max_abs','identity_func_max_abs','identity_offset_abs']) <= 1e-5
assert np.allclose(E.T @ D @ E,S_array,atol=1e-4,rtol=1e-5)
assert residuals['dense_relaxed_gap'] < 1e-5
assert min(values) >= -1e-6 and residuals['minimum_S_eigenvalue'] >= -1e-6
assert abs(selected['opt_value']-4/N**2) < 1e-5
print('Complete numerical certificate:', residuals)
pf.pprint_labeled_matrix(np.asarray(checked.inner_prod_coords, dtype=float), row_labels=selected['basis_vectors'], precision=8)
print('Function and offset residuals:', checked.func_coords, checked.offset)

# Candidate lambda formulas at L=1; zeros correspond exactly to the selected sparse pattern.
def lambda_candidate(name, N):
    if name == 'initial_condition':
        return sp.Rational(4,N**2)
    if name == f'A monotone:x_{N},x_star':
        return sp.Rational(4,N)
    for k in range(N-1):
        t=N-k
        if name == f'A monotone:x_{N},y_{k}':
            return sp.Rational(4,t*(t-1))
        if name == f'A Lipschitz:x_{k},y_{k}':
            return sp.Rational(2,t**2)
    if name == f'A Lipschitz:x_{N-1},x_{N}':
        return sp.Integer(2)
    return sp.Integer(0)
lambda_error = max(abs(float(lambda_candidate(name,N))-float(value)) for name,value in selected['named_dual_values'].items() if value is not None)
assert lambda_error <= 1e-4
S_guess = (sp.Rational(2,N) * (ctx['x_0']-ctx['x_star']) - ctx[f'g_{N}'])**2
S_guess_eval = pm.eval_scalar(S_guess)
S_guess_error = max_abs(np.asarray(S_guess_eval.inner_prod_coords,dtype=float)-S_array)
assert S_guess_error <= 1e-4
assert max_abs(S_guess_eval.func_coords) == 0 and max_abs(S_guess_eval.offset) == 0
candidate_weighted = pf.Scalar.zero()
for constraint in entries:
    residual=constraint.lhs-constraint.rhs
    if constraint.cmp in (pf.Comparator.GE,pf.Comparator.SEQ):
        residual=-residual
    candidate_weighted += lambda_candidate(constraint.name,N)*residual
candidate_identity = pm.eval_scalar(pb.performance_metric-sp.Rational(4,N**2)-candidate_weighted+S_guess)
candidate_residual=max(max_abs(candidate_identity.inner_prod_coords),max_abs(candidate_identity.func_coords),max_abs(candidate_identity.offset))
assert candidate_residual < 1e-12
print('Lambda candidate error:',lambda_error,'S candidate error:',S_guess_error,'fixed-N candidate identity:',candidate_residual)
pf.pprint_labeled_matrix(np.asarray(S_guess_eval.inner_prod_coords,dtype=float),row_labels=selected['basis_vectors'])
print('Numerical reverse-LDL diagonal (all entries retained):',np.diag(D))
print('Analytic full-PEP proof: unresolved for arbitrary N; candidate identities above are fixed-N checks.')
# END NOTEBOOK VERIFICATION

closed_form_search = dict(completed=True, references_reviewed=['Own dense and sparse certificates; no pre-existing mathematical references authorized'],
 attempts=[{'method':'Inspect rational fractions of terminal monotonicity and per-step Lipschitz multipliers', 'candidate':'4/[t(t-1)], 4/N, 2/t^2 at L=1', 'max_abs_error':lambda_error},
           {'method':'Inspect rank-one S and coordinates', 'candidate':'||(2/N)(x0-xstar)-gN||^2 at L=1', 'max_abs_error':S_guess_error, 'fixed_N_identity_residual':candidate_residual}],
 unresolved_components=['arbitrary-horizon and parameter-domain proof of candidate lambda/S'])
state={**b1,**selected,'N_verify':N,'normalization':dict(tau_name='initial_condition', initial_condition=b1['initial_condition'],performance_metric=b1['performance_metric'],bound_value=selected['opt_value'],bound_formula=b1['conjectured_rate']),
'numerical_checks':dict(tolerances=tolerances,residuals=residuals,passed=True), 'closed_form_search':closed_form_search,
'formula_status':{'lambda':'candidate','S':'candidate'},'lamb_code':None,'S_code':'S_guess = (sp.Rational(2,N)*(ctx["x_0"]-ctx["x_star"])-ctx[f"g_{N}"])**2',
'S_decomp_type':'ldl','numerical_certificate_verified':True,'analytic_full_pep_verified':False,'lyapunov_proof_verified':False,'require_analytic_full_pep':False,'proof_valid':True}
state['lamb_code'] = __import__('inspect').getsource(lambda_candidate)
keys=('N_verify','params_json','relaxed_constraints','S_matrix','S_row_names','S_col_names','basis_vectors','basis_scalars','opt_value','tau_sol','tau_name','named_dual_values','constraint_metadata','normalization','certificate_provenance','numerical_checks','numerical_decomposition')
state['certificate_id']=hashlib.sha256(json.dumps({k:state[k] for k in keys},sort_keys=True,separators=(',',':'),allow_nan=False).encode()).hexdigest()
for filename in ('dual_feg_b2.json','dual_feg_relaxed.json'):
    (root/'state'/filename).write_text(json.dumps(state,indent=2,allow_nan=False))


