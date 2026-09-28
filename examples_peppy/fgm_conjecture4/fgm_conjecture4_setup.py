"""Fresh Block 1 implementation from the supplied FGM recurrence.

Provenance: parent run is CONTAMINATED by a prohibited filename search.
No pre-existing example contents were consulted. See supplementary/audit.md.
Numerical evidence does not establish the conjectured all-horizon upper bound.
"""

import sympy as sp

import pepflow as pf

L = pf.Parameter("L")
R = pf.Parameter("R")
f = pf.SmoothConvexFunction(is_basis=True, tags=["f"], L=L)


def theta_sequence(N, digits=50):
    """Evaluate the stated recurrence; digits=None retains exact radicals."""
    N = int(N)
    if N < 0:
        raise ValueError("N must be nonnegative")
    theta = [sp.Integer(1)]
    for _ in range(N):
        value = (1 + sp.sqrt(1 + 4 * theta[-1] ** 2)) / 2
        theta.append(value if digits is None else sp.N(value, digits))
    return theta


def coefficient_rows(N, digits=50):
    """h[i][j] in x_i = x_0 - sum_{j<i} h[i][j] g_j / L."""
    theta = theta_sequence(N, digits)
    rows = [[]]
    for k in range(int(N)):
        t = theta[k + 1]
        rows.append(
            [(1 - 1 / t) * rows[k][j] + theta[j] / t for j in range(k)]
            + [1 + (theta[k] - 1) / t]
        )
    return rows


def conjectured_rate(N, L_value=1, R_value=1):
    """Candidate LR^2/[2(2 C_N+1)], not an established upper bound."""
    if int(N) != N or N < 1:
        raise ValueError("The supplied conjecture is defined for integer N >= 1")
    C_N = 1 + sum(coefficient_rows(N - 1)[N - 1], sp.Integer(0))
    return sp.sympify(L_value) * sp.sympify(R_value) ** 2 / (2 * (2 * C_N + 1))


def make_ctx_fgm_c4_study_20260916_contaminated(ctx_name, N, **kwargs):
    """Encode the three sequences exactly as specified, with 50-digit theta."""
    if int(N) != N or N < 1:
        raise ValueError("N must be an integer >= 1")
    N = int(N)
    theta = theta_sequence(N)
    ctx = pf.PEPContext(ctx_name).set_as_current()
    x = pf.Vector(is_basis=True, tags=["x_0", "y_0", "z_0"])
    y = z = x
    f.set_stationary_point("x_star")
    for k in range(N):
        g = f.grad(x)
        y = x - (1 / L) * g
        y.add_tag(f"y_{k + 1}")
        z = z - (theta[k] / L) * g
        z.add_tag(f"z_{k + 1}")
        x = (1 - 1 / theta[k + 1]) * y + (1 / theta[k + 1]) * z
        x.add_tag(f"x_{k + 1}")
    return ctx


def get_pep_setup(N, params):
    """Standard pepflow.pep_runner interface; R denotes radius, not R squared."""
    for name, default in (("L", 1), ("R", 1)):
        value = sp.sympify(params.get(name, default))
        if not value.is_real or (value <= 0 if name == "L" else value < 0):
            raise ValueError("Require L > 0 and R >= 0")
    ctx = make_ctx_fgm_c4_study_20260916_contaminated(f"ctx_{N}", N)
    pb = pf.PEPBuilder(ctx)
    pb.add_initial_constraint(
        ((ctx["x_0"] - ctx["x_star"]) ** 2).le(R**2, name="initial_condition")
    )
    pb.set_performance_metric(f(ctx[f"y_{int(N)}"]) - f(ctx["x_star"]))
    return ctx, pb, f
