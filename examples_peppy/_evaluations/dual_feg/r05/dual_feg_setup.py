"""Dual FEG setup; terminal squared operator residual, initial radius R."""
import pepflow as pf
import sympy as sp

L = pf.Parameter("L")
A = pf.LipschitzMonotoneOperator(is_basis=True, tags=["A"], L=L)


def make_ctx_dual_feg(ctx_name: str, N, **kwargs) -> pf.PEPContext:
    ctx = pf.PEPContext(ctx_name).set_as_current()
    x = pf.Vector(is_basis=True, tags=["x_0"])
    A.set_zero_point("x_star")
    z = pf.Vector.zero().add_tag("z_0")
    for k in range(int(N)):
        a = A(x)
        a.add_tag(f"a_{k}")
        y = (x - z / L - a / L).add_tag(f"y_{k}")
        b = A(y)
        b.add_tag(f"b_{k}")
        q = sp.Rational(int(N) - k - 1, int(N) - k)
        x = (y - q * (b - a) / L).add_tag(f"x_{k + 1}")
        z = (q * z - b / (int(N) - k)).add_tag(f"z_{k + 1}")
    A(x).add_tag(f"a_{N}")
    return ctx


def get_pep_setup(N, params):
    R = pf.Parameter("R")
    ctx = make_ctx_dual_feg(f"ctx_{N}", N)
    pb = pf.PEPBuilder(ctx)
    pb.add_initial_constraint(
        ((ctx["x_0"] - ctx["x_star"]) ** 2).le(R**2, name="initial_condition")
    )
    pb.set_performance_metric(A(ctx[f"x_{N}"]) ** 2)
    return ctx, pb, A
