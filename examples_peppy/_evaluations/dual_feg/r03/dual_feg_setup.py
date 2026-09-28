"""Dual-FEG with candidate performance metric ||A(x_N)||^2."""

import sympy as sp

import pepflow as pf

L = pf.Parameter("L")
R = pf.Parameter("R")
A = pf.LipschitzMonotoneOperator(is_basis=True, tags=["A"], L=L)


def make_ctx_dual_feg(ctx_name: str, N, **kwargs) -> pf.PEPContext:
    """Encode the supplied fixed-horizon recurrence using exact ratios."""
    N = int(N)
    if N < 1:
        raise ValueError("N must be positive")
    ctx = pf.PEPContext(ctx_name).set_as_current()
    x = pf.Vector(is_basis=True, tags=["x_0"])
    A.set_zero_point("x_star")
    z = pf.Vector.zero().add_tag("z_0")
    for k in range(N):
        ax = A(x).add_tag(f"g_{k}")
        half = (x - z / L - ax / L).add_tag(f"x_half_{k}")
        ahalf = A(half).add_tag(f"h_{k}")
        ratio = sp.Rational(N - k - 1, N - k)
        x = (half - ratio * (ahalf - ax) / L).add_tag(f"x_{k + 1}")
        z = (ratio * z - ahalf / (N - k)).add_tag(f"z_{k + 1}")
    A(x).add_tag(f"g_{N}")
    return ctx


def get_pep_setup(N, params):
    """Standard setup interface, with R interpreted as a distance radius."""
    ctx = make_ctx_dual_feg(f"dual_feg_{N}", N)
    pb = pf.PEPBuilder(ctx)
    pb.add_initial_constraint(
        ((ctx["x_0"] - ctx["x_star"]) ** 2).le(R**2, name="initial_condition")
    )
    pb.set_performance_metric(A(ctx[f"x_{N}"]) ** 2)
    return ctx, pb, A
