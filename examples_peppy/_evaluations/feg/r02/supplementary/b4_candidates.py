from itertools import combinations
from pepflow.lyapunov_utils import vectors_in_column_space, find_basis_with_sparsest_coefficients, find_symmetric_coefficient_matrix

candidate_pairs=[]
for k in range(1,N_int+1):
    candidate_pairs.extend([(f'A(x_{k})',obj(ctx[f'x_{k}'])),(f'x_{k}-x_0',ctx[f'x_{k}']-ctx['x_0'])])
base=list(ctx.basis_vectors())+[ctx[f'x_{k}'] for k in range(N_int+1)]+[ctx['x_star']]+[ctx[f'x_{k}+1/2'] for k in range(1,N_int)]
candidate_pairs.extend((str(v),v) for v in base)
candidate_pairs.extend((f'({u})-({v})',u-v) for u,v in combinations(base,2))
candidates=[]
labels_by_id={}
seen_coords=[]
for label,vector in candidate_pairs:
    coords=np.asarray(pm.eval_vector(vector).coords,dtype=float)
    if np.linalg.norm(coords)<=1e-6 or any(np.allclose(coords,old,atol=1e-8,rtol=0) for old in seen_coords):
        continue
    candidates.append(vector)
    labels_by_id[id(vector)]=label
    seen_coords.append(coords)
print('Deduplicated nonzero candidates:',len(candidates))
