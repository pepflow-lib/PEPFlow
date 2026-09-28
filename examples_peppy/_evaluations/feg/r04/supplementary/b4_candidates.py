from itertools import combinations
from pepflow.lyapunov_utils import vectors_in_column_space, find_basis_with_sparsest_coefficients, find_symmetric_coefficient_matrix

candidate_pairs = []
# Favor meaningful operator and anchor-gap labels before incidental differences.
for j in range(N_int+1):
    candidate_pairs.append((f'A(x_{j})',obj(ctx[f'x_{j}'])))
    candidate_pairs.append((f'x_{j}-x_0',ctx[f'x_{j}']-ctx['x_0']))
    candidate_pairs.append((f'x_{j}-x_star',ctx[f'x_{j}']-ctx['x_star']))
base_pairs = [(str(v),v) for v in ctx.basis_vectors()]
base_pairs += [(f'x_{j}',ctx[f'x_{j}']) for j in range(N_int+1)]
base_pairs += [(f'x_{2*j+1}/2',ctx[f'x_{2*j+1}/2']) for j in range(N_int)]
candidate_pairs += base_pairs
candidate_pairs += [(f'({a})-({b})',u-v) for (a,u),(b,v) in combinations(base_pairs,2)]
unique_candidates, candidate_coordinates = [], []
for label,vector in candidate_pairs:
    coord=np.asarray(pm.eval_vector(vector).coords,dtype=float)
    if np.linalg.norm(coord)<=1e-6 or any(np.allclose(coord,previous,atol=1e-10,rtol=0) for previous in candidate_coordinates):
        continue
    unique_candidates.append((label,vector))
    candidate_coordinates.append(coord)
candidates=[v for _,v in unique_candidates]
labels_by_id={id(v):label for label,v in unique_candidates}
print('Distinct nonzero candidates:',len(candidates))
