def V_k_basis(k):
    assert isinstance(h_obj,pf.Function)
    if k==0:
        return []
    return [ctx[f'x_{k}']-ctx['x_star'], h_obj.grad(ctx[f'x_{k}']), ctx['x_0']-ctx['x_star'], h_obj.grad(ctx['x_0'])]


def V_k_basis_labels(k):
    return [] if k==0 else [f'x_{k}-x_star',f'grad_h(x_{k})','x_0-x_star','grad_h(x_0)']

