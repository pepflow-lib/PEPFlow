def V_k_basis(k):
    if k==0:
        return []
    return [obj(ctx[f'x_{k}']),ctx[f'x_{k}']-ctx['x_0']]


def V_k_basis_labels(k):
    if k==0:
        return []
    return [f'A(x_{k})',f'x_{k}-x_0']
