"""Dual FEG: final squared operator residual under a radius bound."""
import pepflow as pf
import sympy as sp

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
        g = A(x).add_tag(f"g_{k}")
        y = (x - (z + g) / L).add_tag(f"y_{k}")
        h = A(y).add_tag(f"h_{k}")
        x = (y - (t - 1) / t / L * (h - g)).add_tag(f"x_{k + 1}")
        z = ((t - 1) / t * z - h / t).add_tag(f"z_{k + 1}")
    A(x).add_tag(f"g_{N}")
    return ctx


def get_pep_setup(N, params):
    ctx = make_ctx_dual_feg(f"ctx_{N}", N)
    pb = pf.PEPBuilder(ctx)
    pb.add_initial_constraint(
        ((ctx["x_0"] - ctx["x_star"]) ** 2).le(R**2, name="initial_condition")
    )
    pb.set_performance_metric(A(ctx[f"x_{N}"]) ** 2)
    return ctx, pb, A
