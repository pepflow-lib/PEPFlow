"""FEG for a monotone L-Lipschitz operator; squared residual metric."""

import sympy as sp

import pepflow as pf

L = pf.Parameter("L")
R = pf.Parameter("R")
A = pf.LipschitzMonotoneOperator(is_basis=True, tags=["A"], L=L)


def make_ctx_feg(ctx_name: str, N, **kwargs) -> pf.PEPContext:
    """Encode N steps, sharing x_0 and x_{1/2}."""
    ctx = pf.PEPContext(ctx_name).set_as_current()
    x0 = pf.Vector(is_basis=True, tags=["x_1/2", "x_0"])
    A.set_zero_point("x_star")
    x = x0
    for k in range(int(N)):
        anchor = x + sp.Rational(1, k + 1) * (x0 - x)
        if k == 0:
            half = x0
        else:
            half = anchor - sp.Rational(k, k + 1) / L * A(x)
            half.add_tag(f"x_{k + sp.Rational(1, 2)}")
        x = anchor - A(half) / L
        x.add_tag(f"x_{k + 1}")
    return ctx


def get_pep_setup(N, params):
    """Standard framework interface with radius R, not squared-radius R."""
    ctx = make_ctx_feg(f"ctx_{N}", N)
    pb = pf.PEPBuilder(ctx)
    pb.add_initial_constraint(
        ((ctx["x_0"] - ctx["x_star"]) ** 2).le(R**2, name="initial_condition")
    )
    pb.set_performance_metric(A(ctx[f"x_{N}"]) ** 2)
    return ctx, pb, A
