"""Bregman proximal point method; radius is D_h(x_star,x_0) <= R."""

import pepflow as pf

f = pf.ConvexFunction(is_basis=True, tags=["f"])
h = pf.ConvexFunction(is_basis=True, tags=["h"])
alpha = pf.Parameter("alpha")
R = pf.Parameter("R")


def bregman(u, v):
    return h(u) - h(v) - h.grad(v) * (u - v)


def make_ctx_bppm(ctx_name: str, N, stepsize) -> pf.PEPContext:
    ctx = pf.PEPContext(ctx_name).set_as_current()
    x = pf.Vector(is_basis=True, tags=["x_0"])
    f.set_stationary_point("x_star")
    for k in range(int(N)):
        x = f.bregman_prox(x, stepsize, h, tag=f"x_{k + 1}")
    return ctx


def get_pep_setup(N, params):
    ctx = make_ctx_bppm(f"ctx_{N}", N, alpha)
    pb = pf.PEPBuilder(ctx)
    pb.add_initial_constraint(
        bregman(ctx["x_star"], ctx["x_0"]).le(R, name="initial_condition")
    )
    pb.set_performance_metric(f(ctx[f"x_{N}"]) - f(ctx["x_star"]))
    return ctx, pb, f
