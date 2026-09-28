"""Dual FEG: monotone L-Lipschitz operator, terminal squared residual."""

import sympy as sp

import pepflow as pf

L = pf.Parameter("L")
R = pf.Parameter("R")
A = pf.LipschitzMonotoneOperator(is_basis=True, tags=["A"], L=L)


def make_ctx_dual_feg(ctx_name: str, N, **kwargs) -> pf.PEPContext:
    ctx = pf.PEPContext(ctx_name).set_as_current()
    x = pf.Vector(is_basis=True, tags=["x_0"])
    A.set_zero_point("x_star")
    z = pf.Vector.zero().add_tag("z_0")
    for k in range(int(N)):
        t = sp.Integer(N - k)
        g = A(x)
        half = (x - z / L - g / L).add_tag(f"x_{k}_half")
        gh = A(half)
        x = (half - (t - 1) / t / L * (gh - g)).add_tag(f"x_{k + 1}")
        z = ((t - 1) / t * z - gh / t).add_tag(f"z_{k + 1}")
    A(x)
    return ctx


def get_pep_setup(N, params):
    ctx = make_ctx_dual_feg(f"dual_feg_{N}", N)
    pb = pf.PEPBuilder(ctx)
    pb.add_initial_constraint(
        ((ctx["x_0"] - ctx["x_star"]) ** 2).le(R**2, name="initial_condition")
    )
    pb.set_performance_metric(A(ctx[f"x_{N}"]) ** 2)
    return ctx, pb, A
