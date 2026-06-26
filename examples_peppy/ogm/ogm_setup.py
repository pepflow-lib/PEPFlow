"""
ogm setup module for pep_runner.py.

Algorithm: Optimized gradient method with fixed step size 1/L.
Performance metric: f(x_N) - f(x_star)
Initial condition: ||x_0 - x_star|| <= R, encoded as ||x_0 - x_star||^2 <= R^2.
Conjectured rate: L * R^2 / (2 * theta_N^2)
"""

from functools import cache

import numpy as np

import pepflow as pf

# Module-level objects shared across get_pep_setup calls.
L = pf.Parameter("L")
R = pf.Parameter("R")
f = pf.SmoothConvexFunction(is_basis=True, tags=["f"], L=L)


@cache
def theta_ogm_value(i: int, N: int) -> float:
    """Return the fixed-horizon OGM theta_i value."""
    if i == -1:
        return 0.0
    if i == N:
        return 0.5 * (1 + np.sqrt(8 * theta_ogm_value(N - 1, N) ** 2 + 1))
    return 0.5 * (1 + np.sqrt(4 * theta_ogm_value(i - 1, N) ** 2 + 1))


def theta_resolve_parameters(N: int, L_value=1, R_value=1):
    """Resolve L, R, and theta parameters for a fixed horizon."""
    params = {"L": L_value, "R": R_value}
    params.update({f"theta_{i}": theta_ogm_value(i, N) for i in range(N + 1)})
    return params


def make_ctx_ogm(ctx_name: str, N, **kwargs) -> pf.PEPContext:
    """Build the PEPContext encoding N steps of OGM."""
    N_int = int(N)
    ctx = pf.PEPContext(ctx_name).set_as_current()
    theta = [pf.Parameter(f"theta_{i}") for i in range(N_int + 1)]

    x = pf.Vector(is_basis=True, tags=["x_0"])
    z = x
    f.set_stationary_point("x_star")

    for k in range(N_int):
        y = x - (1 / L) * f.grad(x)
        y.add_tag(f"y_{k}")
        z = z - (2 / L) * theta[k] * f.grad(x)
        z.add_tag(f"z_{k + 1}")
        x = (1 - 1 / theta[k + 1]) * y + (1 / theta[k + 1]) * z
        x.add_tag(f"x_{k + 1}")

    return ctx


def get_pep_setup(N, params):
    """Standard interface for pep_runner.py."""
    N_int = int(N)
    params.update({f"theta_{i}": theta_ogm_value(i, N_int) for i in range(N_int + 1)})
    ctx = make_ctx_ogm(f"ctx_{N}", N)
    pb = pf.PEPBuilder(ctx)
    pb.add_initial_constraint(
        ((ctx["x_0"] - ctx["x_star"]) ** 2).le(R**2, name="initial_condition")
    )
    pb.set_performance_metric(f(ctx[f"x_{N}"]) - f(ctx["x_star"]))
    return ctx, pb, f
