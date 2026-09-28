from itertools import combinations
from pepflow.lyapunov_utils import vectors_in_column_space, find_basis_with_sparsest_coefficients, find_symmetric_coefficient_matrix

f_obj = pf.get_func_or_oper_by_tag('f')
h_obj = pf.get_func_or_oper_by_tag('h')
assert isinstance(f_obj,pf.Function) and isinstance(h_obj,pf.Function)
x_star = ctx['x_star']
candidate_pairs = []
for j in range(N_int+1):
    candidate_pairs.append((f'x_{j}-x_star',ctx[f'x_{j}']-x_star))
    candidate_pairs.append((f'grad_h(x_{j})',h_obj.grad(ctx[f'x_{j}'])))
for j in range(1,N_int+1):
    candidate_pairs.append((f'sum_grad_f_1_to_{j}',sum((f_obj.grad(ctx[f'x_{i}']) for i in range(1,j+1)),pf.Vector.zero())))
for vector in ctx.basis_vectors():
    candidate_pairs.append((str(vector),vector))
for i,j in combinations(range(N_int+1),2):
    candidate_pairs.append((f'x_{i}-x_{j}',ctx[f'x_{i}']-ctx[f'x_{j}']))
unique_pairs, candidate_coords = [], []
for label,vector in candidate_pairs:
    coords=np.asarray(pm.eval_vector(vector).coords,dtype=float)
    if np.linalg.norm(coords)<1e-6 or any(np.allclose(coords,previous,atol=1e-7,rtol=0) for previous in candidate_coords):
        continue
    unique_pairs.append((label,vector))
    candidate_coords.append(coords)
candidates=[vector for _,vector in unique_pairs]
labels_by_id={id(vector):label for label,vector in unique_pairs}
spanning_by_k={}
for k in range(1,N_int+1):
    in_col=vectors_in_column_space(lyap[k],candidates,pep_context=ctx,resolve_parameters=params_sp,rtol=1e-4,atol=1e-4)
    spanning_by_k[k]=in_col
    print(f'V_{k} column-space candidates:')
    for vector in in_col:
        print('   '+labels_by_id[id(vector)])
