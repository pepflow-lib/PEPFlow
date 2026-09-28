def V_k_basis(k):
    if k==0:
        return []
    return [obj(ctx[f'x_{k}']),ctx[f'x_{k}']-ctx['x_0']]


def V_k_basis_labels(k):
    return [] if k==0 else [f'A(x_{k})',f'x_{k}-x_0']


for k in range(N_int+1):
    chosen=V_k_basis(k)
    matrix=np.column_stack([pm.eval_vector(v).coords for v in chosen]).astype(float) if chosen else np.zeros((len(ctx.basis_vectors()),0))
    assert int(np.linalg.matrix_rank(matrix,tol=1e-7))==len(chosen)==ranks[k]
    print(f'k={k}: rank {ranks[k]} basis {V_k_basis_labels(k)}')
