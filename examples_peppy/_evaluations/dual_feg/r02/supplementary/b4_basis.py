def V_k_basis(k):
    if k==0:
        return []
    if k==N_int:
        return [ctx[f'g_{N_int}'],ctx[f'x_{N_int}']-ctx['x_0']]
    return [ctx[f'g_{N_int}'],ctx[f'z_{k}'],ctx[f'x_{k}']-ctx['x_0'],ctx[f'x_{N_int}']-ctx['x_0']]

def V_k_basis_labels(k):
    if k==0:
        return []
    if k==N_int:
        return ['g_N','x_N-x_0']
    return ['g_N',f'z_{k}',f'x_{k}-x_0','x_N-x_0']
