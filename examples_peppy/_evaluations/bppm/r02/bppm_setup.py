"""Bregman proximal point setup; initial radius is R, not R squared."""

from numbers import Number
from typing import cast

import pepflow as pf

alpha = pf.Parameter("alpha")
R = pf.Parameter("R")
f = pf.ConvexFunction(is_basis=True, tags=["f"])
h = pf.ConvexFunction(is_basis=True, tags=["h"])


def make_ctx_bppm(ctx_name: str, N, **kwargs) -> pf.PEPContext:
    ctx = pf.PEPContext(ctx_name).set_as_current()
    x = pf.Vector(is_basis=True, tags=["x_0"])
    f.set_stationary_point("x_star")
    f(x)
    for k in range(int(N)):
        x = f.bregman_prox(x, cast(Number, alpha), h, tag=f"x_{k + 1}")
    return ctx


def get_pep_setup(N, params):
    ctx = make_ctx_bppm(f"ctx_{N}", N)
    x0, xs = ctx["x_0"], ctx["x_star"]
    divergence = h(xs) - h(x0) - h.grad(x0) * (xs - x0)
    pb = pf.PEPBuilder(ctx)
    pb.add_initial_constraint(divergence.le(R, name="initial_condition"))
    pb.set_performance_metric(f(ctx[f"x_{N}"]) - f(xs))
    return ctx, pb, f
