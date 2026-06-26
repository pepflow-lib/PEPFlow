"""
bppm setup module for pep_runner.py.

Algorithm: Bregman proximal point method with fixed step size alpha.
Performance metric: f(x_N) - f(x_star)
Initial condition: D_h(x_star, x_0) <= R, where x_star minimizes f.
Conjectured rate: R / (alpha * N)
"""

import pepflow as pf

# Module-level objects shared across get_pep_setup calls.
alpha = pf.Parameter("alpha")
R = pf.Parameter("R")
f = pf.ConvexFunction(is_basis=True, tags=["f"])
h = pf.ConvexFunction(is_basis=True, tags=["h"])


def make_ctx_bppm(ctx_name: str, N, **kwargs) -> pf.PEPContext:
    """Build the PEPContext encoding N steps of BPPM."""
    ctx = pf.PEPContext(ctx_name).set_as_current()
    x = pf.Vector(is_basis=True, tags=["x_0"])
    f.set_stationary_point("x_star")

    for k in range(int(N)):
        x = f.bregman_prox(x, alpha, h, tag=f"x_{k + 1}")

    return ctx


def get_pep_setup(N, params):
    """Standard interface for pep_runner.py."""
    ctx = make_ctx_bppm(f"ctx_{N}", N)
    pb = pf.PEPBuilder(ctx)
    x_0 = ctx["x_0"]
    x_star = ctx["x_star"]
    pb.add_initial_constraint(
        (h(x_star) - h(x_0) - h.grad(x_0) * (x_star - x_0)).le(
            R, name="initial_condition"
        )
    )
    pb.set_performance_metric(f(ctx[f"x_{N}"]) - f(x_star))
    return ctx, pb, f
