def V_k_basis(k):
    if k==0:
        return []
    kernel=next(owner for owner in ctx.func_to_triplets if str(owner)=='h')
    return [ctx['x_0']-ctx['x_star'],kernel.grad(ctx['x_0']),ctx[f'x_{k}']-ctx['x_star'],kernel.grad(ctx[f'x_{k}'])]


def V_k_basis_labels(k):
    return [] if k==0 else ['x_0-x_star','grad_h(x_0)',f'x_{k}-x_star',f'grad_h(x_{k})']


for k in range(N_int+1):
    basis_k=V_k_basis(k)
    matrix=np.column_stack([pm.eval_vector(v).coords for v in basis_k]).astype(float) if basis_k else np.zeros((len(ctx.basis_vectors()),0))
    basis_rank=int(np.linalg.matrix_rank(matrix,tol=1e-7)) if basis_k else 0
    assert basis_rank==len(basis_k)==ranks[k]
    print(f'k={k}: rank {basis_rank} basis {V_k_basis_labels(k)}')
