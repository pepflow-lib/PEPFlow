# Construct, filter and search the actual candidate vectors.
from pepflow.lyapunov_utils import vectors_in_column_space, find_basis_with_sparsest_coefficients, find_symmetric_coefficient_matrix

candidate_pairs = []
for i in range(N_int+1):
    candidate_pairs.extend([(f'a_{i}=x_star-x_{i}', ctx['x_star']-ctx[f'x_{i}']),
                            (f'q_{i}=grad_h(x_{i})', h.grad(ctx[f'x_{i}'])),
                            (f'q_0-q_{i}', h.grad(ctx['x_0'])-h.grad(ctx[f'x_{i}'])),
                            (f'x_{i}-x_0', ctx[f'x_{i}']-ctx['x_0'])])
for v in ctx.basis_vectors():
    candidate_pairs.append((str(v),v))
for i in range(N_int+1):
    for j in range(i):
        candidate_pairs.append((f'x_{i}-x_{j}', ctx[f'x_{i}']-ctx[f'x_{j}']))
unique_pairs=[]
unique_coords=[]
for label, vector in candidate_pairs:
    coords=np.asarray(pm.eval_vector(vector).coords,dtype=float)
    if np.linalg.norm(coords)<1e-7:
        continue
    if any(np.allclose(coords,prior,atol=1e-7,rtol=0) for prior in unique_coords):
        continue
    unique_pairs.append((label,vector))
    unique_coords.append(coords)
candidates=[v for _,v in unique_pairs]
candidate_labels={id(v):label for label,v in unique_pairs}
spanning_by_k={}
for k in range(1,N_int+1):
    in_col=vectors_in_column_space(lyap[k],candidates,pep_context=ctx,resolve_parameters=params_sp,rtol=1e-4,atol=1e-4)
    spanning_by_k[k]=in_col
    print(f'V_{k} column-space candidates:')
    for v in in_col:
        print('  ',candidate_labels[id(v)])

sparse_basis_by_k={}
sparse_coeff_by_k={}
for k in range(1,N_int+1):
    chosen,C=find_basis_with_sparsest_coefficients(lyap[k],spanning_by_k[k],pep_context=ctx,
        resolve_parameters=params_sp,zero_tol=1e-6,indep_tol=1e-7,span_tol=1e-5)
    assert len(chosen)==ranks[k]
    sparse_basis_by_k[k]=chosen
    sparse_coeff_by_k[k]=C
    print(f'k={k}, rank={ranks[k]}')
    print('sparse basis:',[candidate_labels[id(v)] for v in chosen])
    print('zero coefficients:',int(np.sum(np.abs(C)<1e-6)),'/',C.size)
