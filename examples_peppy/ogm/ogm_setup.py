"""
ogm setup module for pep_runner.py.

Algorithm: Optimized gradient method with fixed stepsize 1/L.
Performance metric: f(x_N) - f(x_star)
Initial condition: ||x_0 - x_star||^2 <= R^2, where grad f(x_star)=0.
Conjectured rate: to be determined
"""

import sympy as sp

import pepflow as pf

# Module-level objects shared across get_pep_setup calls.
L = pf.Parameter("L")
R = pf.Parameter("R")
f = pf.SmoothConvexFunction(is_basis=True, tags=["f"], L=L)


def ogm_theta_sequence(N):
    """Return theta_0, ..., theta_N for the fixed-horizon OGM schedule."""
    N_int = int(N)
    theta_prev = sp.S(0)
    theta = []

    for _ in range(N_int):
        theta_k = sp.Rational(1, 2) * (1 + sp.sqrt(4 * theta_prev**2 + 1))
        theta.append(theta_k)
        theta_prev = theta_k

    theta_N = sp.Rational(1, 2) * (1 + sp.sqrt(8 * theta_prev**2 + 1))
    theta.append(theta_N)
    return theta


def make_ctx_ogm(ctx_name: str, N, **kwargs) -> pf.PEPContext:
    """Build the PEPContext encoding N steps of OGM."""
    del kwargs
    N_int = int(N)
    ctx = pf.PEPContext(ctx_name).set_as_current()

    x = pf.Vector(is_basis=True, tags=["x_0"])
    z = x
    z.add_tag("z_0")
    f.set_stationary_point("x_star")
    theta = ogm_theta_sequence(N_int)

    for k in range(N_int):
        grad_x = f.grad(x)
        y = x - (sp.S(1) / L) * grad_x
        y.add_tag(f"y_{k}")

        z = z - (sp.S(2) / L) * theta[k] * grad_x
        z.add_tag(f"z_{k + 1}")

        x = (1 - sp.S(1) / theta[k + 1]) * y + (sp.S(1) / theta[k + 1]) * z
        x.add_tag(f"x_{k + 1}")

    return ctx


def get_pep_setup(N, params):
    """Standard interface for pep_runner.py."""
    del params
    ctx = make_ctx_ogm(f"ctx_{N}", N)
    pb = pf.PEPBuilder(ctx)
    pb.add_initial_constraint(
        ((ctx["x_0"] - ctx["x_star"]) ** 2).le(R**2, name="initial_condition")
    )
    pb.set_performance_metric(f(ctx[f"x_{N}"]) - f(ctx["x_star"]))
    return ctx, pb, f
