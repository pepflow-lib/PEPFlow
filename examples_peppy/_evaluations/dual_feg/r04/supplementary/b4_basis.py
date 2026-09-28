def V_k_basis(k):
    if k == 0:
        return []
    if k == N_int:
        return [obj(ctx[f'x_{N_int}']), ctx['x_0'] - ctx[f'x_{N_int}']]
    return [obj(ctx[f'x_{N_int}']), ctx['x_0'] - ctx[f'x_{N_int}'],
            ctx[f'x_{k}'] - ctx[f'x_{N_int}'], ctx[f'z_{k}']]


def V_k_basis_labels(k):
    if k == 0:
        return []
    if k == N_int:
        return ['A(x_N)', 'x_0-x_N']
    return ['A(x_N)', 'x_0-x_N', f'x_{k}-x_N', f'z_{k}']
