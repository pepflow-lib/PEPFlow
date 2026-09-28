# %%
import hashlib
import numpy as np
from pepflow.utils import Comparator

b1 = json.loads((notebook_dir / 'state/ogm_b1.json').read_text())
dense = json.loads((notebook_dir / 'state/ogm_dense.json').read_text())
selected = json.loads((notebook_dir / 'supplementary/b2-chain-certificate.json').read_text())
N = selected['N']
params = json.loads(b1['params_json'])
assert N == b1['N_verify']
for path, expected in selected['certificate_provenance']['source_hashes'].items():
    assert hashlib.sha256(Path(path).read_bytes()).hexdigest() == expected
print('Dense objective:', dense['opt_value'])
print('Basis:', dense['basis_vectors'])
print('Dense S eigenvalues:', np.linalg.eigvalsh(np.asarray(dense['S_matrix'])))
print('Dense active multipliers (>1e-6):')
for name, value in dense['named_dual_values'].items():
    if value is not None and value > 1e-6:
        print(name, value)
points = ['z_0'] + [f'x_{i}' for i in range(1, N+1)]
keep = {f'f:x_star,{p}' for p in points} | {f'f:{a},{b}' for a,b in zip(points[:-1],points[1:])} | {'initial_condition'}
relaxed = [name for name in dense['named_dual_values'] if name not in keep]
assert relaxed == selected['relaxed_constraints']
print('Relaxation retains optimizer-to-iterate and forward consecutive pairs.')
print('Selected objective:', selected['opt_value'])
assert abs(selected['opt_value']-dense['opt_value']) < 1e-5
print('Preserved optimum:', abs(selected['opt_value']-dense['opt_value']))
print('Solve provenance:', selected['certificate_provenance']['solver'])
# %%
ctx, pb, obj = get_pep_setup(N, params)
ctx.set_as_current()
pm = pf.ExpressionManager(ctx, resolve_parameters=params)
assert [str(v) for v in ctx.basis_vectors()] == selected['basis_vectors']
assert [str(v) for v in ctx.basis_scalars()] == selected['basis_scalars']
pb.set_relaxed_constraints(relaxed)
groups = ctx.get_constraint_data(obj)
assert not groups.psd_dict
entries = [(c, 'initial', None, None) for c in pb.init_conditions]
entries.extend((c, 'interpolation', str(obj), str(group)) for group, constraints in groups.sc_dict.items() for c in constraints)
assert len({c.name for c, *_ in entries}) == len(entries)
assert {c.name for c, *_ in entries} == set(selected['named_dual_values']) == set(selected['constraint_metadata'])
for c, origin, owner, group in entries:
    meta = selected['constraint_metadata'][c.name]
    assert meta == dict(origin=origin, owner=owner, group=group, kind='scalar', comparator=c.cmp.value, shape=[], relaxed=c.name in relaxed)
    value = selected['named_dual_values'][c.name]
    assert (value is None) == (c.name in relaxed)
    if value is not None:
        assert np.isfinite(value)
        print(c.name, value)
# %%
theta = theta_sequence(N)


def lamb_candidate(ri, ci):
    if ri == 'x_star' and ci in points:
        j = points.index(ci)
        return 2*theta[j]/theta[N]**2 if j < N else 1/theta[N]
    if ri in points[:-1] and ci == points[points.index(ri)+1]:
        i = points.index(ri)
        return 2*theta[i]**2/theta[N]**2
    return 0.0


candidate_lambda = np.array([[lamb_candidate(ri, ci) for ci in selected['lambda_col_names']] for ri in selected['lambda_row_names']])
numeric_lambda = np.array(selected['lambda_matrix'])
lambda_error = float(np.max(np.abs(candidate_lambda-numeric_lambda)))
assert lambda_error <= 1e-4
pf.pprint_labeled_matrix(candidate_lambda, selected['lambda_row_names'], selected['lambda_col_names'])
print('Candidate lambda max discrepancy:', lambda_error)
q = ctx[f'z_{N}'] - ctx['x_star'] - theta[N]/params['L']*ctx[f'g_{N}']
q_coords = np.asarray(pm.eval_vector(q).coords, dtype=float)
E = q_coords.reshape(1, -1)
D = np.array([[float(selected['tau_sol'])]])
S_numeric = float(D[0,0]) * q**2
S_array = np.asarray(selected['S_matrix'], dtype=float)
S_reconstructed = E.T @ D @ E
S_candidate = params['L']/(2*theta[N]**2)*q**2
candidate_eval = pm.eval_scalar(S_candidate)
S_formula_error = float(np.max(np.abs(np.asarray(candidate_eval.inner_prod_coords,dtype=float)-S_array)))
assert S_formula_error <= 1e-4
assert np.allclose(candidate_eval.func_coords, 0, atol=1e-4, rtol=0)
assert abs(float(candidate_eval.offset)) <= 1e-4
pf.pprint_labeled_matrix(S_reconstructed, selected['basis_vectors'])
print('Direct factor D:', D)
print('q coordinates in saved basis:', E)
print('S formula max discrepancy:', S_formula_error)
print('Formula status: candidate only; arbitrary-horizon proof pending.')
# %%
weighted_constraints = pf.Scalar.zero()
scalar_inequality_values = []
for c, *_ in entries:
    value = selected['named_dual_values'][c.name]
    if c.name in relaxed:
        assert value is None
        continue
    residual = c.lhs-c.rhs
    if c.cmp in (Comparator.GE, Comparator.SEQ):
        residual = -residual
    weighted_constraints += float(value) * (pf.Scalar.zero()+residual)
    if c.cmp != Comparator.EQ:
        scalar_inequality_values.append(float(value))
diff = pb.performance_metric-float(selected['opt_value'])-weighted_constraints+S_numeric
checked = pm.eval_scalar(diff)


def max_abs(values):
    return float(np.max(np.abs(np.asarray(values,dtype=float)), initial=0.0))


tolerances = dict(identity_atol=1e-5, identity_rtol=0.0, reconstruction_atol=1e-4, reconstruction_rtol=1e-5, dual_tol=1e-6, psd_tol=1e-6, dense_opt_atol=1e-5)
residuals = dict(identity_gram_max_abs=max_abs(checked.inner_prod_coords), identity_func_max_abs=max_abs(checked.func_coords), identity_offset_abs=max_abs(checked.offset), S_reconstruction_max_abs=max_abs(S_reconstructed-S_array), dense_relaxed_gap=abs(dense['opt_value']-selected['opt_value']), minimum_scalar_inequality_dual=min(scalar_inequality_values), minimum_S_eigenvalue=float(np.linalg.eigvalsh((S_array+S_array.T)/2).min()), minimum_matrix_inequality_eigenvalue=0.0)
assert selected['certificate_provenance']['solver_status']=='optimal'
assert np.all(np.isfinite(S_array))
assert np.allclose(S_array,S_array.T,atol=1e-6,rtol=0)
assert all(residuals[key]<=1e-5 for key in ('identity_gram_max_abs','identity_func_max_abs','identity_offset_abs'))
assert np.allclose(S_reconstructed,S_array,atol=1e-4,rtol=1e-5)
assert residuals['dense_relaxed_gap']<1e-5
assert residuals['minimum_scalar_inequality_dual']>=-1e-6
assert residuals['minimum_S_eigenvalue']>=-1e-6
assert abs(selected['opt_value']-params['L']*params['R']**2/(2*theta[N]**2))<=1e-5
pf.pprint_labeled_matrix(np.asarray(checked.inner_prod_coords,dtype=float), selected['basis_vectors'])
pf.pprint_labeled_matrix(np.asarray(checked.func_coords,dtype=float).reshape(1,-1), ['function residual'], selected['basis_scalars'])
print('Constant residual:', checked.offset)
print('Numerical checks:', residuals)
print('Numerical certificate verified. Analytic full-PEP and Lyapunov proof not yet verified.')
# %%
lamb_code = '''def lamb(ri, ci, theta, N):
    points = ['z_0'] + [f'x_{k}' for k in range(1, N+1)]
    if ri == 'x_star' and ci in points:
        j = points.index(ci)
        return 2*theta[j]/theta[N]**2 if j<N else 1/theta[N]
    if ri in points[:-1] and ci == points[points.index(ri)+1]:
        i = points.index(ri)
        return 2*theta[i]**2/theta[N]**2
    return 0
'''
S_code = '''def S_guess(ctx, theta, N, L):
    q = ctx[f'z_{N}']-ctx['x_star']-theta[N]/L*ctx[f'g_{N}']
    return L/(2*theta[N]**2)*q**2
'''
closed_form_search = dict(completed=True, references_reviewed=['Own input and approved generic framework only; target reference examples excluded by clean-room rules.'], attempts=[dict(method='Scale optimizer-row multipliers by theta_N^2 and compare with 2 theta_i, terminal theta_N; compare consecutive multipliers with 2 theta_i^2.', outcome='candidate', max_error=lambda_error),dict(method='Rank-one S suggests shifted z_N; test q=z_N-x_star-theta_N/L*g_N and L/(2 theta_N^2) q^2.', outcome='candidate', max_error=S_formula_error)], unresolved_components=['arbitrary-horizon analytic verification of lambda and S identity'])
normalization = dict(tau_name='initial_condition',initial_condition=b1['initial_condition'],performance_metric=b1['performance_metric'],bound_value=selected['opt_value'],bound_formula=b1['conjectured_rate'])
b2 = {**b1, **selected, 'normalization':normalization,'numerical_checks':dict(tolerances=tolerances,residuals=residuals,passed=True),'numerical_decomposition':dict(method='direct',D=D.tolist(),ell_coords=E.tolist(),basis_labels=selected['basis_vectors'],factor_expression='z_N-x_star-theta_N/L*g_N',omission_note='Small numerical remainder is omitted only after full S reconstruction and certificate coordinate checks.'),'closed_form_search':closed_form_search,'formula_status':{'lambda':'candidate','S':'candidate'},'lamb_code':lamb_code,'S_code':S_code,'S_decomp_type':'direct','numerical_certificate_verified':True,'analytic_full_pep_verified':False,'lyapunov_proof_verified':False,'require_analytic_full_pep':False,'proof_valid':True}
certificate_keys = ('N_verify','params_json','relaxed_constraints','S_matrix','S_row_names','S_col_names','basis_vectors','basis_scalars','opt_value','tau_sol','tau_name','named_dual_values','constraint_metadata','normalization','certificate_provenance','numerical_checks','numerical_decomposition')
b2['certificate_id'] = hashlib.sha256(json.dumps({key:b2[key] for key in certificate_keys},sort_keys=True,separators=(',',':'),allow_nan=False).encode()).hexdigest()
for name in ('ogm_b2.json','ogm_relaxed.json'):
    (notebook_dir/'state'/name).write_text(json.dumps(b2,indent=2,allow_nan=False))
print('Selected certificate ID:',b2['certificate_id'])
print('Initial closed-form search:',closed_form_search)
