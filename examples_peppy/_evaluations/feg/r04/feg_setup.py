"""FEG setup: monotone L-Lipschitz operator and squared final residual."""
import pepflow as pf
import sympy as sp

L = pf.Parameter("L")
R = pf.Parameter("R")
A = pf.LipschitzMonotoneOperator(is_basis=True, tags=["A"], L=L)


def make_ctx_feg(ctx_name: str, N, **kwargs) -> pf.PEPContext:
    """Encode the supplied recurrence, sharing x_0 and x_{1/2}."""
    ctx = pf.PEPContext(ctx_name).set_as_current()
    x0 = pf.Vector(is_basis=True, tags=["x_0"])
    A.set_zero_point("x_star")
    x = x0
    for k in range(int(N)):
        t = sp.Integer(k + 1)
        if k == 0:
            half = x0
            half.add_tag("x_1/2")
        else:
            half = x + (x0 - x) / t - sp.Integer(k) / (t * L) * A(x)
            half.add_tag(f"x_{2 * k + 1}/2")
        x = x + (x0 - x) / t - A(half) / L
        x.add_tag(f"x_{k + 1}")
    A(x)
    return ctx


def get_pep_setup(N, params):
    """Return context, builder, and operator for the numerical PEP."""
    ctx = make_ctx_feg(f"ctx_{N}", N)
    pb = pf.PEPBuilder(ctx)
    pb.add_initial_constraint(
        ((ctx["x_0"] - ctx["x_star"]) ** 2).le(R**2, name="initial_condition")
    )
    pb.set_performance_metric(A(ctx[f"x_{N}"]) ** 2)
    return ctx, pb, A

