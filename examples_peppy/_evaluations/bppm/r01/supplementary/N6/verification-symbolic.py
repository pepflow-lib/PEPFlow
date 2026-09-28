import hashlib
import numpy as np
import sympy as sp
from certificate import inventory

b1 = json.loads((notebook_dir / 'state/bppm_b1.json').read_text())
dense = json.loads((notebook_dir / 'supplementary/N6/dense.json').read_text())
certificate = json.loads((notebook_dir / 'supplementary/N6/relaxed-raw.json').read_text())
N = certificate['N_verify']
params_sp: dict[str, pf.NUMERICAL_TYPE] = {'alpha': sp.S(1), 'R': sp.S(1)}
ctx, pb, obj = get_pep_setup(N, params_sp)
ctx.set_as_current()
pb.set_relaxed_constraints(certificate['relaxed_constraints'])
entries = inventory(ctx, pb)
assert set(c.name for c, *_ in entries) == set(certificate['constraint_metadata'])
assert [str(v) for v in ctx.basis_vectors()] == certificate['basis_vectors']
assert [str(v) for v in ctx.basis_scalars()] == certificate['basis_scalars']
for rel, expected in certificate['certificate_provenance']['source_hashes'].items():
    assert hashlib.sha256((notebook_dir / rel).read_bytes()).hexdigest() == expected
pm = pf.ExpressionManager(ctx, resolve_parameters=params_sp)
basis = ctx.basis_vectors()
S_array = np.array(certificate['S_matrix'])
eigenvalues, eigenvectors = np.linalg.eigh(S_array)
D, E = np.diag(eigenvalues), eigenvectors.T
ell = [sum((float(c)*v for c,v in zip(row,basis)), pf.Vector.zero()) for row in E]
S_numeric = sum((float(D[i,i])*ell[i]*ell[i] for i in range(len(ell))), pf.Scalar.zero())
weighted = pf.Scalar.zero()
scalar_duals = []
for c, origin, owner, group in entries:
    meta = certificate['constraint_metadata'][c.name]
    value = certificate['named_dual_values'][c.name]
    assert meta['origin']==origin and meta['owner']==owner and meta['group']==group
    assert meta['kind']=='scalar' and meta['shape']==[] and meta['comparator']==c.cmp.value
    assert meta['relaxed'] == (c.name in pb.relaxed_constraints)
    if meta['relaxed']:
        assert value is None
        continue
    assert value is not None and np.isfinite(value)
    residual = c.lhs-c.rhs
    if c.cmp in (pf.Comparator.GE, pf.Comparator.SEQ):
        residual = -residual
    weighted += float(value)*(pf.Scalar.zero()+residual)
    if c.cmp != pf.Comparator.EQ:
        scalar_duals.append(value)
difference = pb.performance_metric-certificate['opt_value']-weighted+S_numeric
checked = pm.eval_scalar(difference)
def max_abs(values):
    return float(np.max(np.abs(np.asarray(values,dtype=float)), initial=0.0))
residuals = dict(identity_gram_max_abs=max_abs(checked.inner_prod_coords),identity_func_max_abs=max_abs(checked.func_coords),identity_offset_abs=max_abs(checked.offset),S_reconstruction_max_abs=max_abs(E.T@D@E-S_array),dense_relaxed_gap=abs(dense['opt_value']-certificate['opt_value']),minimum_scalar_inequality_dual=min(scalar_duals),minimum_S_eigenvalue=float(eigenvalues.min()),minimum_matrix_inequality_eigenvalue=0.0)
tolerances = dict(identity_atol=1e-5,identity_rtol=0.,reconstruction_atol=1e-4,reconstruction_rtol=1e-5,dual_tol=1e-6,psd_tol=1e-6,dense_opt_atol=1e-5)
assert certificate['certificate_provenance']['solver_status']=='optimal'
assert np.allclose(S_array,S_array.T,atol=1e-6,rtol=0)
assert all(residuals[key]<=1e-5 for key in ('identity_gram_max_abs','identity_func_max_abs','identity_offset_abs','dense_relaxed_gap'))
assert np.allclose(E.T@D@E,S_array,atol=1e-4,rtol=1e-5)
assert min(scalar_duals)>=-1e-6 and eigenvalues.min()>=-1e-6
assert abs(certificate['opt_value']-1/N)<1e-5
print('Numerical certificate residuals:',residuals)
pf.pprint_labeled_matrix(pf.MatrixWithNames(np.asarray(checked.inner_prod_coords,dtype=float), certificate['basis_vectors'], certificate['basis_vectors']))
print('Function residuals:',np.asarray(checked.func_coords,dtype=float))
print('Offset residual:',float(checked.offset))
print('S factor eigenvalues:',eigenvalues)
pf.pprint_labeled_matrix(pf.MatrixWithNames(S_array, certificate['basis_vectors'],certificate['basis_vectors']))

# Candidate formulas suggested by fractions and the proximal-gradient relation.
def candidate_duals(N, a):
    values = {'initial_condition':1/(a*N),f'h:x_star,x_{N}':1/(a*N)}
    for k in range(1,N+1):
        values[f'f:x_star,x_{k}']=sp.S(1)/N
        values[f'h:x_{k},x_{k-1}']=sp.S(k)/(a*N)
        if k>=2:
            values[f'f:x_{k-1},x_{k}']=sp.S(k-1)/N
            values[f'h:x_{k-1},x_{k}']=sp.S(k-1)/(a*N)
    return values
candidate = candidate_duals(N,sp.S(1))
active = {name:value for name,value in certificate['named_dual_values'].items() if value is not None}
assert set(active)==set(candidate)
lambda_error=max(abs(float(candidate[name])-value) for name,value in active.items())
assert lambda_error < 1e-4
candidate_weighted=sum((candidate[c.name]*(c.lhs-c.rhs) for c,*_ in entries if c.name in candidate),pf.Scalar.zero())
exact_sample=pm.eval_scalar(pb.performance_metric-sp.Rational(1,N)-candidate_weighted, sympy_mode=True)
assert all(sp.simplify(v)==0 for v in np.asarray(exact_sample.inner_prod_coords).flat)
assert all(sp.simplify(v)==0 for v in np.asarray(exact_sample.func_coords).flat)
assert sp.simplify(exact_sample.offset)==0
assert max_abs(S_array)<1e-4
for owner in ('f','h'):
    labels = sorted(set(tag for name in candidate if name.startswith(owner+':') for tag in name.split(':')[1].split(',')))
    matrix=np.array([[candidate.get(f'{owner}:{ri},{ci}',0) for ci in labels] for ri in labels],dtype=object)
    print(owner,'candidate multipliers:')
    pf.pprint_labeled_matrix(pf.MatrixWithNames(matrix,labels,labels))
print('Candidate lambda maximum discrepancy:',lambda_error)
print('Candidate S=0 maximum discrepancy:',max_abs(S_array))
print('Exact candidate identity at N=6, alpha=R=1: all coordinates zero.')
print('Analytic full-PEP status: candidate; arbitrary horizon and parameter proof not yet asserted.')


