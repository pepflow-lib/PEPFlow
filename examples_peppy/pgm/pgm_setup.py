"""
pgm setup module for pep_runner.py.

Algorithm: Proximal gradient descent with fixed step size 1/L.
Performance metric: h(x_N) - h(x_star), where h = f + g.
Initial condition: ||x_0 - x_star||^2 <= R^2.
Conjectured rate: L * R^2 / (4 * N).
"""

import pepflow as pf

# Module-level objects shared across get_pep_setup calls.
L = pf.Parameter("L")
R = pf.Parameter("R")
f = pf.SmoothConvexFunction(is_basis=True, tags=["f"], L=L)
g = pf.ConvexFunction(is_basis=True, tags=["g"])
h = (f + g).add_tag("h")


def make_ctx_pgm(ctx_name: str, N, **kwargs) -> pf.PEPContext:
    """Build the PEPContext encoding N steps of proximal gradient descent."""
    ctx = pf.PEPContext(ctx_name).set_as_current()
    x = pf.Vector(is_basis=True, tags=["x_0"])
    h.set_stationary_point("x_star")

    for k in range(int(N)):
        y = x - (1 / L) * f.grad(x)
        y.add_tag(f"y_{k + 1}")
        x = g.prox(y, 1 / L, tag=f"x_{k + 1}")

    return ctx


def get_pep_setup(N, params):
    """Standard interface for pep_runner.py."""
    ctx = make_ctx_pgm(f"ctx_{N}", N)
    pb = pf.PEPBuilder(ctx)
    pb.add_initial_constraint(
        ((ctx["x_0"] - ctx["x_star"]) ** 2).le(R**2, name="initial_condition")
    )
    pb.set_performance_metric(h(ctx[f"x_{N}"]) - h(ctx["x_star"]))
    return ctx, pb, f
