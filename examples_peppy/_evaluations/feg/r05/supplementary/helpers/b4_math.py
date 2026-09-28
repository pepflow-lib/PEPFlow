# REPLAY
import json
from itertools import combinations
import numpy as np
import sympy as sp
import pepflow as pf
from pepflow.lyapunov_utils import vectors_in_column_space, find_basis_with_sparsest_coefficients, find_symmetric_coefficient_matrix
from partial_sums import partial_sums as replay_partial_sums
from pepflow.utils import NUMERICAL_TYPE
import runtime

b3 = json.loads((runtime.ROOT/'state/feg_b3.json').read_text())
dense = json.loads((runtime.ROOT/'state/feg_dense.json').read_text())
ctx, pb, obj, pm, lyap, observation = replay_partial_sums(b3, dense['opt_value'])
params_sp: dict[str, NUMERICAL_TYPE] = {'L': sp.S(1), 'R': sp.S(1)}
n = b3['N_verify']
rank_evidence = json.loads((runtime.ROOT/b3['rank_search']['evidence_path']).read_text())
assert rank_evidence['summary'] == b3['rank_search']
assert observation['rank_profile'] == b3['rank_profile']
for key in ['lyap_inner_prod_coords','lyap_func_coords','lyap_offsets']:
    assert np.allclose(np.asarray(observation[key]), np.asarray(b3[key]), atol=1e-5, rtol=0)

# CANDIDATES
candidate_pairs = []
for k in range(1,n+1):
    candidate_pairs += [(f'g_{k}',obj(ctx[f'x_{k}'])), (f'q_{k}',ctx[f'x_{k}']-ctx['x_0'])]
base = [(str(v),v) for v in ctx.basis_vectors()]
base += [(f'x_{k}',ctx[f'x_{k}']) for k in range(n+1)]
base += [(f'x_{k}+1/2',ctx[f'x_{k}+1/2']) for k in range(1,n)]
candidate_pairs += base
candidate_pairs += [(f'({la})-({lb})',va-vb) for (la,va),(lb,vb) in combinations(base,2)]
unique_pairs = []
unique_coords = []
for label,v in candidate_pairs:
    coords = np.asarray(pm.eval_vector(v).coords,dtype=float)
    if np.linalg.norm(coords) <= 1e-6:
        continue
    if any(np.allclose(coords,c,atol=1e-7,rtol=0) or np.allclose(coords,-c,atol=1e-7,rtol=0) for c in unique_coords):
        continue
    unique_pairs.append((label,v))
    unique_coords.append(coords)
candidates = [v for label,v in unique_pairs]
labels_by_id = {id(v):label for label,v in unique_pairs}
print('Distinct nonzero candidates:',len(candidates))

# FILTER
in_column = {}
for k in range(1,n+1):
    in_column[k] = vectors_in_column_space(lyap[k],candidates,pep_context=ctx,resolve_parameters=params_sp,rtol=1e-4,atol=1e-4)
    print(f'V_{k} column-space candidates:')
    for v in in_column[k]:
        print('  ',labels_by_id[id(v)])

# SEARCH
searched = {}
for k in range(1,n+1):
    basis,C = find_basis_with_sparsest_coefficients(lyap[k],in_column[k],pep_context=ctx,resolve_parameters=params_sp,zero_tol=1e-6,indep_tol=1e-7,span_tol=1e-5)
    assert len(basis)==b3['rank_profile'][k]==2
    searched[k] = {'labels':[labels_by_id[id(v)] for v in basis],'C':C.tolist()}
    print(f'k={k}, rank 2; sparse basis: {searched[k]["labels"]}; zero coefficients: {int(np.sum(np.abs(C)<1e-6))}/{C.size}')

# BASIS
# Adopt the same direct algorithmic basis at every noninitial index.
def V_k_basis(k):
    if k == 0:
        return []
    return [obj(ctx[f'x_{k}']),ctx[f'x_{k}']-ctx['x_0']]


def V_k_basis_labels(k):
    return [] if k == 0 else [f'g_{k}',f'q_{k}']


for k in range(n+1):
    basis = V_k_basis(k)
    rank = 0 if not basis else np.linalg.matrix_rank(np.column_stack([pm.eval_vector(v).coords for v in basis]).astype(float),tol=1e-7)
    assert rank == len(basis) == b3['rank_profile'][k]
    print(f'k={k}: rank {rank} basis {V_k_basis_labels(k)}')

# COEFFICIENTS
coeff_by_k = {}
quadratic_residuals = {}
component_residuals = {}
for k in range(n+1):
    basis = V_k_basis(k)
    target = pm.eval_scalar(lyap[k])
    matrix = np.asarray(target.inner_prod_coords,dtype=float)
    if basis:
        C = find_symmetric_coefficient_matrix(lyap[k],basis,pep_context=ctx,resolve_parameters=params_sp,indep_tol=1e-7,span_tol=1e-5)
        B = np.column_stack([pm.eval_vector(v).coords for v in basis]).astype(float)
        residual = float(np.linalg.norm(B@C@B.T-matrix,ord='fro'))
    else:
        C = np.zeros((0,0))
        residual = float(np.linalg.norm(matrix,ord='fro'))
    assert residual <= 1e-5*max(1.0,float(np.linalg.norm(matrix,ord='fro')))
    assert np.array_equal(C,C.T)
    assert np.allclose(target.func_coords,0,atol=1e-5,rtol=0) and abs(float(target.offset))<=1e-5
    coeff_by_k[k] = C
    quadratic_residuals[str(k)] = residual
    print(f'k={k}: reconstruction residual {residual:.3g}; function terms {target.func_coords}; offset {target.offset}')
    if basis:
        pf.pprint_labeled_matrix(C,V_k_basis_labels(k),V_k_basis_labels(k),precision=8)

# STRUCTURE
def V_k_structure(k):
    vectors = V_k_basis(k)
    C = coeff_by_k[k]
    return sum((float(C[i,j])*vectors[i]*vectors[j] for i,j in np.ndindex(C.shape)),pf.Scalar.zero())


for k in range(n+1):
    difference = pm.eval_scalar(V_k_structure(k)-lyap[k])
    target = pm.eval_scalar(lyap[k])
    component_residuals[str(k)] = {}
    for name,coords,target_coords in [('gram',difference.inner_prod_coords,target.inner_prod_coords),('function',difference.func_coords,target.func_coords),('offset',difference.offset,target.offset)]:
        err=float(np.max(np.abs(np.asarray(coords,dtype=float)),initial=0))
        scale=float(np.max(np.abs(np.asarray(target_coords,dtype=float)),initial=0))
        assert err <= 1e-4+1e-5*scale
        component_residuals[str(k)][name]=err
print('All indices 0..N independently reconstructed in every scalar component.')

