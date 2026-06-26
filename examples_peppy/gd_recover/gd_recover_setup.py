"""
gd_recover setup module for pep_runner.py.

Algorithm: Gradient descent with fixed step size 1/L.
Performance metric: f(x_N) - f(x_star)
Initial condition: ||x_0 - x_star|| <= R, encoded as ||x_0 - x_star||^2 <= R^2.
Conjectured rate: L * R^2 / (4 * N + 2)
"""

import pepflow as pf

# Module-level objects shared across get_pep_setup calls.
L = pf.Parameter("L")
R = pf.Parameter("R")
f = pf.SmoothConvexFunction(is_basis=True, tags=["f"], L=L)


def make_ctx_gd_recover(ctx_name: str, N, **kwargs) -> pf.PEPContext:
    """Build the PEPContext encoding N steps of gradient descent."""
    ctx = pf.PEPContext(ctx_name).set_as_current()
    x = pf.Vector(is_basis=True, tags=["x_0"])
    f.set_stationary_point("x_star")

    for k in range(int(N)):
        x = x - (1 / L) * f.grad(x)
        x.add_tag(f"x_{k + 1}")

    return ctx


def get_pep_setup(N, params):
    """Standard interface for pep_runner.py."""
    ctx = make_ctx_gd_recover(f"ctx_{N}", N)
    pb = pf.PEPBuilder(ctx)
    pb.add_initial_constraint(
        ((ctx["x_0"] - ctx["x_star"]) ** 2).le(R**2, name="initial_condition")
    )
    pb.set_performance_metric(f(ctx[f"x_{N}"]) - f(ctx["x_star"]))
    return ctx, pb, f
