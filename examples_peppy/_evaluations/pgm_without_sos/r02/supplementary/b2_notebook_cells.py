# %% Load the coherent selected certificate and rebuild its context without solving.
import hashlib
import json
from fractions import Fraction
import numpy as np
import sympy as sp
import pepflow as pf
from pepflow.constraint import ScalarConstraint
from pepflow.lyapunov_utils import ldl_decompose_with_reversed_basis
from pepflow.utils import Comparator

b1 = json.loads((notebook_dir / 'state/pgm_b1.json').read_text())
dense = json.loads((notebook_dir / 'state/pgm_dense.json').read_text())
selected = json.loads((notebook_dir / 'supplementary/b2-relaxation-001.json').read_text())
N = selected['N']
ctx, pb, obj = get_pep_setup(N, {'L': 1, 'R': 1})
pb.set_relaxed_constraints(selected['relaxed_constraints'])
for owner in ctx.func_to_triplets:
    owner.get_interpolation_constraints(ctx)
entries = [(c, 'initial', None, None) for c in pb.init_conditions]
for owner in ctx.func_to_triplets:
    groups = ctx.get_constraint_data(owner)
    entries.extend((c, 'interpolation', str(owner), str(group))
                   for group, cs in groups.sc_dict.items() for c in cs)
    entries.extend((c, 'interpolation', str(owner), str(group))
                   for group, c in groups.psd_dict.items())
metadata = selected['constraint_metadata']
duals = selected['named_dual_values']
assert set(metadata) == set(duals) == {c.name for c, *_ in entries}
for c, origin, owner, group in entries:
    assert isinstance(c, ScalarConstraint), 'Unexpected matrix constraint'
    assert metadata[c.name] == dict(origin=origin, owner=owner, group=group, kind='scalar',
        comparator=c.cmp.value, shape=[], relaxed=c.name in pb.relaxed_constraints)
for source, expected in selected['certificate_provenance']['source_hashes'].items():
    assert hashlib.sha256(Path(source).read_bytes()).hexdigest() == expected
pm = pf.ExpressionManager(ctx, resolve_parameters={'L': sp.S.One, 'R': sp.S.One})
basis = ctx.basis_vectors()
assert [str(v) for v in basis] == selected['basis_vectors'] == selected['S_row_names'] == selected['S_col_names']
assert [str(v) for v in ctx.basis_scalars()] == selected['basis_scalars']
print('Dense bound:', dense['opt_value'], 'Selected bound:', selected['opt_value'])
print('Basis:', selected['basis_vectors'])
for owner_name, group in sorted({(m['owner'],m['group']) for m in metadata.values() if m['owner'] is not None}):
    vals = [(name,v) for name,v in dense['named_dual_values'].items() if v is not None
            and metadata[name]['owner'] == owner_name and metadata[name]['group'] == group]
    active = [(name,round(v,6)) for name,v in vals if abs(v)>1e-6]
    print(owner_name, group, 'dense nonzero count at 1e-6:',len(active), 'largest:',sorted(active,key=lambda z:-abs(z[1]))[:6])
print('Dense S eigenvalues:',np.linalg.eigvalsh(np.asarray(dense['S_matrix'])))
print('Relaxation: retain star-to-iterate and consecutive forward pairs for both owners.')
print('Dropped constraints:', len(selected['relaxed_constraints']))
for name, value in duals.items():
    if value is not None:
        print(name, f'{value:.9f}', Fraction(value).limit_denominator(1000))

# %% Candidate multipliers inferred from fractions and scalar conservation.
def candidate_multiplier(name, horizon):
    n = sp.S(horizon)
    if name == 'initial_condition':
        return 1 / (4*n)
    owner, pair = name.split(':')
    first, second = pair.split(',')
    if second == 'x_star':
        return sp.S.Zero
    j = int(second[2:])
    def flow(index):
        if owner == 'f':
            return (index+1)/(2*n-index) if index >= 0 else sp.S.Zero
        return index/(2*n-index) if index >= 1 else sp.S.Zero
    if first == 'x_star':
        return 1-flow(horizon-1) if j == horizon else flow(j)-flow(j-1)
    i = int(first[2:])
    return flow(i) if j == i+1 else sp.S.Zero

lambda_error = max(abs(float(candidate_multiplier(name,N))-(value or 0)) for name,value in duals.items())
print('Candidate lambda max error:', lambda_error)
assert lambda_error <= 1e-4
for owner_tag, tags in [('f', ['x_star']+[f'x_{i}' for i in range(N+1)]),
                        ('g', ['x_star']+[f'x_{i}' for i in range(1,N+1)])]:
    matrix = np.array([[float(candidate_multiplier(f'{owner_tag}:{i},{j}',N)) if i != j else 0
                        for j in tags] for i in tags])
    print('Candidate', owner_tag, 'multipliers, numerically supported only:')
    pf.pprint_labeled_matrix(matrix, tags, precision=5)

# %% Selected numerical reverse-LDL decomposition; retain every factor.
S_array = np.asarray(selected['S_matrix'],dtype=float)
S_labeled = pf.MatrixWithNames(matrix=S_array, row_names=selected['S_row_names'], col_names=selected['S_col_names'])
D, ell = ldl_decompose_with_reversed_basis(S_labeled, basis, print_output=False)
D = np.asarray(D,dtype=float)
E = np.asarray([pm.eval_vector(v).coords for v in ell],dtype=float)
S_numeric = sum((float(D[i,j])*ell[i]*ell[j] for i,j in np.ndindex(D.shape)),pf.Scalar.zero())
print('Reverse-LDL diagonal:',np.diag(D))
pf.pprint_labeled_matrix(E, [f'ell_{i}' for i in range(len(E))],selected['basis_vectors'],precision=4)
print('Full D retained, including tiny pivots; off-diagonal maximum:',np.max(np.abs(D-np.diag(np.diag(D)))))
S_reconstructed = E.T@D@E

# %% All-coordinate numerical identity and cone checks.
weighted = pf.Scalar.zero()
weighted_candidate = pf.Scalar.zero()
scalar_inequalities = []
for c, *_ in entries:
    residual = c.lhs-c.rhs
    if c.cmp in (Comparator.GE,Comparator.SEQ):
        residual = -residual
    weighted_candidate += candidate_multiplier(c.name,N)*(pf.Scalar.zero()+residual)
    value = duals[c.name]
    if metadata[c.name]['relaxed']:
        assert value is None
        continue
    assert value is not None and np.isfinite(value)
    weighted += value*(pf.Scalar.zero()+residual)
    if c.cmp != Comparator.EQ:
        scalar_inequalities.append(value)
diff = pb.performance_metric-selected['opt_value']-weighted+S_numeric
checked = pm.eval_scalar(diff)
def max_abs(array):
    return float(np.max(np.abs(np.asarray(array,dtype=float)),initial=0))
S_eigs = np.linalg.eigvalsh((S_array+S_array.T)/2)
residuals = dict(identity_gram_max_abs=max_abs(checked.inner_prod_coords),
    identity_func_max_abs=max_abs(checked.func_coords), identity_offset_abs=max_abs(checked.offset),
    S_reconstruction_max_abs=max_abs(S_reconstructed-S_array),
    dense_relaxed_gap=abs(dense['opt_value']-selected['opt_value']),
    conjecture_gap=abs(selected['opt_value']-1/(4*N)),
    minimum_scalar_inequality_dual=min(scalar_inequalities,default=0),
    minimum_S_eigenvalue=float(S_eigs.min()), minimum_matrix_inequality_eigenvalue=0.0)
tolerances = dict(identity_atol=1e-5,identity_rtol=0,reconstruction_atol=1e-4,
                  reconstruction_rtol=1e-5,dual_tol=1e-6,psd_tol=1e-6,dense_opt_atol=1e-5)
passed = (selected['certificate_provenance']['solver_status']=='optimal'
          and np.isfinite(S_array).all() and np.allclose(S_array,S_array.T,atol=1e-6,rtol=0)
          and all(residuals[key]<=1e-5 for key in ['identity_gram_max_abs','identity_func_max_abs','identity_offset_abs'])
          and np.allclose(S_reconstructed,S_array,atol=1e-4,rtol=1e-5)
          and residuals['dense_relaxed_gap']<1e-5 and residuals['conjecture_gap']<1e-5
          and residuals['minimum_scalar_inequality_dual']>=-1e-6 and residuals['minimum_S_eigenvalue']>=-1e-6)
print('Numerical certificate verified:',bool(passed))
print(json.dumps(residuals,indent=2))
pf.pprint_labeled_matrix(np.asarray(checked.inner_prod_coords,dtype=float),selected['basis_vectors'],precision=9)
assert passed

# %% Initial S formula search: assemble the candidate residual and compare all components.
S_candidate = weighted_candidate-pb.performance_metric+sp.Rational(1,4*N)
S_candidate_coords = pm.eval_scalar(S_candidate,sympy_mode=True)
S_candidate_error = max_abs(S_candidate_coords.inner_prod_coords-S_array)
print('Candidate S Gram error:',S_candidate_error)
print('Candidate S scalar/offset:',max_abs(S_candidate_coords.func_coords),max_abs(S_candidate_coords.offset))
assert S_candidate_error <= 1e-4
assert max_abs(S_candidate_coords.func_coords)==0 and max_abs(S_candidate_coords.offset)==0
print('Candidate S eigenvalues:',np.linalg.eigvalsh(np.asarray(S_candidate_coords.inner_prod_coords,dtype=float)))
print('Global S positivity and arbitrary-horizon identities remain unresolved; numerical continuation is permitted.')

