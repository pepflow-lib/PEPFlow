import json
from pathlib import Path
import numpy as np
import sympy as sp
import pepflow as pf

NOTEBOOK_DIR = Path.cwd()
b1 = json.loads((NOTEBOOK_DIR / 'state/pgm_b1.json').read_text())
dense = json.loads((NOTEBOOK_DIR / 'state/pgm_dense.json').read_text())
selected = json.loads((NOTEBOOK_DIR / 'supplementary/sparse-trial.json').read_text())
N = selected['N']
ctx, pb, obj = get_pep_setup(N, {'L': 1, 'R': 1})
pm = pf.ExpressionManager(ctx, resolve_parameters={'L': sp.Integer(1), 'R': sp.Integer(1)})
entries = list(pb.init_conditions)
for owner in ctx.func_to_triplets:
    entries.extend(owner.get_interpolation_constraints(ctx))
assert {c.name for c in entries} == set(selected['named_dual_values'])
basis = ctx.basis_vectors()
assert [str(v) for v in basis] == selected['basis_vectors']
assert [str(v) for v in ctx.basis_scalars()] == selected['basis_scalars']
S = np.asarray(selected['S_matrix'])
eigenvalues, eigenvectors = np.linalg.eigh(S)
D = np.diag(eigenvalues)
E = eigenvectors.T
S_numeric = sum((float(S[i,j]) * basis[i] * basis[j] for i,j in np.ndindex(S.shape)), pf.Scalar.zero())
weighted = pf.Scalar.zero()
for c in entries:
    value = selected['named_dual_values'][c.name]
    if value is not None:
        assert selected['constraint_metadata'][c.name]['comparator'] == 'LE'
        weighted += value * (c.lhs - c.rhs)
checked = pm.eval_scalar(pb.performance_metric - selected['opt_value'] - weighted + S_numeric)
def max_abs(a):
    return float(np.max(np.abs(np.asarray(a, dtype=float)), initial=0))
residuals = dict(identity_gram_max_abs=max_abs(checked.inner_prod_coords), identity_func_max_abs=max_abs(checked.func_coords), identity_offset_abs=max_abs(checked.offset), S_reconstruction_max_abs=max_abs(E.T @ D @ E-S), dense_relaxed_gap=abs(dense['opt_value']-selected['opt_value']), minimum_scalar_inequality_dual=min(v for v in selected['named_dual_values'].values() if v is not None), minimum_S_eigenvalue=float(eigenvalues.min()), minimum_matrix_inequality_eigenvalue=0.0)
assert selected['solver_status']=='optimal'
assert all(residuals[k]<=1e-5 for k in ('identity_gram_max_abs','identity_func_max_abs','identity_offset_abs','dense_relaxed_gap'))
assert np.allclose(E.T@D@E,S,atol=1e-4,rtol=1e-5)
assert eigenvalues.min()>=-1e-6
assert residuals['minimum_scalar_inequality_dual']>=-1e-6
print('Dense and sparse values:',dense['opt_value'],selected['opt_value'])
print('Basis:',selected['basis_vectors'])
print('Dense active counts:', {owner: sum(v is not None and v>1e-6 for name,v in dense['named_dual_values'].items() if name.startswith(owner+':')) for owner in ('f','g')})
print('Selected active multipliers:',{k:v for k,v in selected['named_dual_values'].items() if v is not None})
print('Complete numerical checks:',residuals)
pf.pprint_labeled_matrix(np.asarray(checked.inner_prod_coords),selected['basis_vectors'],precision=8)
pf.pprint_labeled_matrix(D,[f'eigenfactor_{j}' for j in range(len(D))],precision=6)
print('Selected decomposition S = E.T @ D @ E; E =',E)

# Initial closed-form search: cumulative forward weights and star differences.
def candidate_multiplier(name, n):
    if name=='initial_condition':
        return sp.Rational(1,4*n)
    owner,pair=name.split(':')
    left,right=pair.split(',')
    def forward(i):
        if owner=='f':
            return sp.Rational(i+1,2*n-i) if 0<=i<n else (sp.S.One if i==n else sp.S.Zero)
        return sp.Rational(i,2*n-i) if 0<=i<=n else sp.S.Zero
    if right=='x_star':
        return sp.S.Zero
    j=int(right[2:])
    if left=='x_star':
        return forward(j)-forward(j-1)
    i=int(left[2:])
    return forward(i) if j==i+1 else sp.S.Zero
candidate_values={c.name:candidate_multiplier(c.name,N) for c in entries}
err=max(abs(float(candidate_values[name])-float(value or 0)) for name,value in selected['named_dual_values'].items())
print('Candidate multiplier maximum error:',err)
assert err<1e-4
candidate_weighted=sum((candidate_values[c.name]*(c.lhs-c.rhs) for c in entries),pf.Scalar.zero())
S_candidate= -pb.performance_metric + sp.Rational(1,4*N) + candidate_weighted
candidate_eval=pm.eval_scalar(S_candidate)
candidate_error=max_abs(candidate_eval.inner_prod_coords-S)
assert candidate_error<1e-4
assert max_abs(candidate_eval.func_coords)<1e-10 and max_abs(candidate_eval.offset)<1e-10
print('Candidate S error:',candidate_error,'function/constant components',max_abs(candidate_eval.func_coords),max_abs(candidate_eval.offset))
for owner in ('f','g'):
    tags=['x_star']+[f'x_{i}' for i in range(0 if owner=='f' else 1,N+1)]
    matrix=np.array([[0 if a==b else float(candidate_multiplier(owner+':'+a+','+b,N)) for b in tags] for a in tags])
    pf.pprint_labeled_matrix(matrix,tags,precision=6)
pf.pprint_labeled_matrix(np.asarray(candidate_eval.inner_prod_coords),selected['basis_vectors'],precision=6)
print('Analytic status: candidate formulas only; all-horizon PSD/sign proof unresolved.')

