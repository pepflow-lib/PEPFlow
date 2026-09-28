"""Block 1 PEP for FGM with step 1/L and momentum k/(k+3).

Metric: f(y_N) - f(x_star). Initial radius: ||x_0-x_star|| <= R.
Conjecture: 2*L*R**2 / ((N+2)*(N+3)), for N >= 1.
Derived from the current task statement; see supplementary/clean_room_report.md
for the path-discovery contamination disclosure.
"""

import sympy as sp

import pepflow as pf

L = pf.Parameter("L")
R = pf.Parameter("R")
f = pf.SmoothConvexFunction(is_basis=True, tags=["f"], L=L)


def make_ctx_fgm_rational_test(ctx_name: str, N, **kwargs) -> pf.PEPContext:
    """Encode the stated recursion with exact rational momentum coefficients."""
    if not sp.sympify(N).is_Integer or N < 1:
        raise ValueError("N must be an integer >= 1")
    ctx = pf.PEPContext(ctx_name).set_as_current()
    x = pf.Vector(is_basis=True, tags=["y_0", "x_0"])
    y = x
    f.set_stationary_point("x_star")
    for k in range(int(N)):
        y_next = x - f.grad(x) / L
        y_next.add_tag(f"y_{k + 1}")
        # At k=0 these are the same point; preserve its oracle identity.
        x_next = y_next if k == 0 else y_next + sp.Rational(k, k + 3) * (y_next - y)
        x_next.add_tag(f"x_{k + 1}")
        x, y = x_next, y_next
    return ctx


def get_pep_setup(N, params):
    """Return the standard (context, builder, function) runner interface."""
    for name, value in params.items():
        if name == "L" and sp.sympify(value) <= 0:
            raise ValueError("L must be positive")
        if name == "R" and sp.sympify(value) < 0:
            raise ValueError("R must be nonnegative")
    ctx = make_ctx_fgm_rational_test(f"ctx_{N}", N)
    pb = pf.PEPBuilder(ctx)
    pb.add_initial_constraint(
        ((ctx["x_0"] - ctx["x_star"]) ** 2).le(R**2, name="initial_condition")
    )
    pb.set_performance_metric(f(ctx[f"y_{N}"]) - f(ctx["x_star"]))
    return ctx, pb, f
