"""OGM from the 2026-09-16 2 AM prompt; Block 1 numerical setup.

Class: convex, L-smooth, L > 0. Radius R >= 0 is a distance, not its square.
Metric: f(y_N) - f(x_star). Initial condition: ||x_0-x_star||^2 <= R^2.
Candidate: L*R^2 / (2*(2*theta[N-1]^2+1)). No analytic proof is asserted.
See supplementary/clean_room_audit.md for the initial filename exposure.
"""

import sympy as sp

import pepflow as pf

L = pf.Parameter("L")
R = pf.Parameter("R")
f = pf.SmoothConvexFunction(is_basis=True, tags=["f"], L=L)


def theta_sequence(N, *, exact=False):
    """Return theta_0,...,theta_N; numerical coefficients use 50 digits.

    exact=True preserves nested radicals for later symbolic investigations.
    The SDP solver ultimately uses double precision in either case.
    """
    if isinstance(N, bool) or int(N) != N or N < 1:
        raise ValueError("N must be a positive integer")
    N = int(N)
    theta = [sp.Integer(1)]
    for k in range(N):
        factor = 8 if k == N - 1 else 4
        next_theta = (1 + sp.sqrt(1 + factor * theta[-1] ** 2)) / 2
        theta.append(next_theta if exact else next_theta.evalf(50))
    return theta


def conjectured_rate(N, L_value=1, R_value=1):
    theta = theta_sequence(N)
    return (
        sp.sympify(L_value)
        * sp.sympify(R_value) ** 2
        / (2 * (2 * theta[N - 1] ** 2 + 1))
    )


def make_ctx_ogm_conjecture4_test_20260916_2am(ctx_name, N, **kwargs):
    """Encode all supplied updates, including the terminal x_N update."""
    theta = theta_sequence(N, exact=kwargs.get("exact", False))
    N = int(N)
    ctx = pf.PEPContext(ctx_name).set_as_current()
    # Last tag remains x_0 so oracle names consistently use x_k.
    x = pf.Vector(is_basis=True, tags=["y_0", "x_0"])
    y = x
    f.set_stationary_point("x_star")
    for k in range(N):
        y_next = x - (1 / L) * f.grad(x)
        y_next.add_tag(f"y_{k + 1}")
        x_next = (
            y_next
            + ((theta[k] - 1) / theta[k + 1]) * (y_next - y)
            + (theta[k] / theta[k + 1]) * (y_next - x)
        )
        x_next.add_tag(f"x_{k + 1}")
        x, y = x_next, y_next
    return ctx


def get_pep_setup(N, params):
    """Standard pepflow.pep_runner interface; parameters resolve at solve time."""
    if "L" in params and float(params["L"]) <= 0:
        raise ValueError("L must be positive")
    if "R" in params and float(params["R"]) < 0:
        raise ValueError("R must be nonnegative")
    ctx = make_ctx_ogm_conjecture4_test_20260916_2am(f"ctx_{N}", N)
    pb = pf.PEPBuilder(ctx)
    pb.add_initial_constraint(
        ((ctx["x_0"] - ctx["x_star"]) ** 2).le(R**2, name="initial_condition")
    )
    pb.set_performance_metric(f(ctx[f"y_{N}"]) - f(ctx["x_star"]))
    return ctx, pb, f
