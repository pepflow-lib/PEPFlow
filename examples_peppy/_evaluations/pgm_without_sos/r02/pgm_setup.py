"""PGM setup: composite objective gap with squared-distance initialization."""

import pepflow as pf

L = pf.Parameter("L")
R = pf.Parameter("R")
f = pf.SmoothConvexFunction(is_basis=True, tags=["f"], L=L)
g = pf.ConvexFunction(is_basis=True, tags=["g"])
h = f + g
h.add_tag("h")


def make_ctx_pgm(ctx_name: str, N, **kwargs) -> pf.PEPContext:
    ctx = pf.PEPContext(ctx_name).set_as_current()
    x = pf.Vector(is_basis=True, tags=["x_0"])
    h.set_stationary_point("x_star")
    for k in range(N):
        x = g.prox(x - f.grad(x) / L, 1 / L, tag=f"x_{k + 1}")
    f(x)
    return ctx


def get_pep_setup(N, params):
    ctx = make_ctx_pgm(f"pgm_{N}", N)
    pb = pf.PEPBuilder(ctx)
    pb.add_initial_constraint(
        ((ctx["x_0"] - ctx["x_star"]) ** 2).le(R**2, name="initial_condition")
    )
    pb.set_performance_metric(h(ctx[f"x_{N}"]) - h(ctx["x_star"]))
    return ctx, pb, f
