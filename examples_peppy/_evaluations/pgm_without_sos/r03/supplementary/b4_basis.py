def V_k_basis(k):
    if k==0:
        return []
    anchor=ctx['x_0']-ctx['x_star']
    if k==N_int:
        return [anchor]
    return [anchor,ctx[f'x_{k}']-ctx['x_star'],f.grad(ctx[f'x_{k}'])-f.grad(ctx['x_star']),f.grad(ctx['x_star'])]

def V_k_basis_labels(k):
    if k==0:
        return []
    if k==N_int:
        return ['x_0-x_star']
    return ['x_0-x_star','x_k-x_star','grad_f(x_k)-grad_f(x_star)','grad_f(x_star)']

for k in range(N_int+1):
    basis_k=V_k_basis(k)
    matrix=np.column_stack([pm.eval_vector(v).coords for v in basis_k]).astype(float) if basis_k else np.zeros((len(ctx.basis_vectors()),0))
    rank=int(np.linalg.matrix_rank(matrix,tol=1e-7)) if basis_k else 0
    assert rank==len(basis_k)==b3['rank_profile'][k]
    print(f'k={k}: rank {rank} basis {V_k_basis_labels(k)}')

