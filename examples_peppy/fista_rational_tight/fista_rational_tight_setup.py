"""Composite FISTA with momentum k/(k+3) and a radius R distance bound."""

import sympy as sp

import pepflow as pf

L = pf.Parameter("L")
R = pf.Parameter("R")
f = pf.SmoothConvexFunction(is_basis=True, tags=["f"], L=L)
g = pf.ConvexFunction(is_basis=True, tags=["g"])
F = f + g


def make_ctx_fista_rational_tight(ctx_name, N, **kwargs):
    """Encode every proximal point; never evaluate g at the initial point."""
    ctx = pf.PEPContext(ctx_name).set_as_current()
    x = pf.Vector(is_basis=True, tags=["x_0", "y_0"])
    F.set_stationary_point("x_star")
    y = x
    for k in range(int(N)):
        y_next = g.prox(x - f.grad(x) / L, 1 / L, tag=f"y_{k + 1}")
        f(y_next)
        if k == 0:
            x_next = y_next
        else:
            x_next = y_next + sp.Rational(k, k + 3) * (y_next - y)
        x_next.add_tag(f"x_{k + 1}")
        x, y = x_next, y_next
    return ctx


def get_pep_setup(N, params):
    ctx = make_ctx_fista_rational_tight(f"fista_{N}", N)
    pb = pf.PEPBuilder(ctx)
    pb.add_initial_constraint(
        ((ctx["x_0"] - ctx["x_star"]) ** 2).le(R**2, name="initial_condition")
    )
    pb.set_performance_metric(F(ctx[f"y_{N}"]) - F(ctx["x_star"]))
    return ctx, pb, f
