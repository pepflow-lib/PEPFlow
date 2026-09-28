"""Block 1: FGM at x_N, with the radius convention ||x_0-x_star|| <= R.

Derived from the current problem statement. No prior example code is reused.
The run's provenance limitation is recorded in supplementary/clean_room_report.md.
Theta coefficients use 50-digit arithmetic for the numerical SDP; exact=True
retains the nested radicals for subsequent symbolic work.
"""

import operator

import sympy as sp

import pepflow as pf

L = pf.Parameter("L")
R = pf.Parameter("R")
f = pf.SmoothConvexFunction(is_basis=True, tags=["f"], L=L)


def theta_sequence(N, *, exact=False, precision=50):
    """Return theta_0,...,theta_N, without a special terminal update."""
    N = operator.index(N)
    if N < 0:
        raise ValueError("N must be a nonnegative integer")
    theta = [sp.Integer(1)]
    for _ in range(N):
        previous = theta[-1] if exact else sp.N(theta[-1], precision)
        theta.append((1 + sp.sqrt(1 + 4 * previous**2)) / 2)
    return theta


def coefficient_rows(N, *, exact=False, precision=50):
    """Return h[i][j] in x_i=x_0-(1/L)*sum_{j<i} h[i][j] g_j."""
    theta = theta_sequence(N, exact=exact, precision=precision)
    rows = [[]]
    for k in range(N):
        inverse_next = 1 / theta[k + 1]
        row = [
            (1 - inverse_next) * rows[k][j] + inverse_next * theta[j] for j in range(k)
        ]
        row.append(1 + (theta[k] - 1) * inverse_next)
        rows.append(row)
    return rows


def conjectured_bound(N, L_value=1, R_value=1):
    """Return L R^2 / (2 (2 D_N + 1)), with D_N the final h-row sum."""
    D_N = sum(coefficient_rows(N)[-1], sp.Integer(0))
    return sp.sympify(L_value) * sp.sympify(R_value) ** 2 / (2 * (2 * D_N + 1))


def make_ctx_fgm_conjecture5_test3(ctx_name: str, N, **kwargs):
    """Encode the three-sequence algorithm exactly as stated in the prompt."""
    theta = theta_sequence(N)
    ctx = pf.PEPContext(ctx_name).set_as_current()
    x = pf.Vector(is_basis=True, tags=["x_0", "y_0", "z_0"])
    y = z = x
    f.set_stationary_point("x_star")
    for k in range(N):
        gradient = f.grad(x)
        y = x - (1 / L) * gradient
        y.add_tag(f"y_{k + 1}")
        z = z - (theta[k] / L) * gradient
        z.add_tag(f"z_{k + 1}")
        x = (1 - 1 / theta[k + 1]) * y + (1 / theta[k + 1]) * z
        x.add_tag(f"x_{k + 1}")
    return ctx


def get_pep_setup(N, params):
    """Standard pep_runner interface; R is a radius, not its square."""
    for name in ("L", "R"):
        if name in params:
            value = sp.sympify(params[name])
            if value.is_real is not True or (value <= 0 if name == "L" else value < 0):
                raise ValueError(
                    f"{name} must be real and {'positive' if name == 'L' else 'nonnegative'}"
                )
    ctx = make_ctx_fgm_conjecture5_test3(f"ctx_{N}", N)
    pb = pf.PEPBuilder(ctx)
    pb.add_initial_constraint(
        ((ctx["x_0"] - ctx["x_star"]) ** 2).le(R**2, name="initial_condition")
    )
    pb.set_performance_metric(f(ctx[f"x_{N}"]) - f(ctx["x_star"]))
    return ctx, pb, f
