"""
feg setup module for pep_runner.py.

Algorithm: Fast extragradient method for monotone L-Lipschitz operators.
Performance metric: ||A(x_N)||^2
Initial condition: ||x_0 - x_star||^2 <= R^2, where A(x_star)=0.
Conjectured rate: to be determined
"""

import sympy as sp

import pepflow as pf

# Module-level objects shared across get_pep_setup calls.
L = pf.Parameter("L")
R = pf.Parameter("R")
A = pf.LipschitzMonotoneOperator(is_basis=True, tags=["A"], L=L)


def make_ctx_feg(ctx_name: str, N, **kwargs) -> pf.PEPContext:
    """Build the PEPContext encoding N steps of FEG."""
    del kwargs
    ctx = pf.PEPContext(ctx_name).set_as_current()

    x0 = pf.Vector(is_basis=True, tags=["x_0"])
    x = x0
    A.set_zero_point("x_star")

    for k in range(int(N)):
        if k == 0:
            x_half = x
            x_half.add_tag("x_0.5")
        else:
            k_sp = sp.S(k)
            denom = k_sp + 1
            x_half = (
                x + sp.S(1) / denom * (x0 - x) - k_sp / denom * (sp.S(1) / L) * A(x)
            )
            x_half.add_tag(f"x_{k + 0.5}")

        x_next = x + sp.S(1) / (k + 1) * (x0 - x) - (sp.S(1) / L) * A(x_half)
        x_next.add_tag(f"x_{k + 1}")
        x = x_next

    return ctx


def get_pep_setup(N, params):
    """Standard interface for pep_runner.py."""
    del params
    ctx = make_ctx_feg(f"ctx_{N}", N)
    pb = pf.PEPBuilder(ctx)
    pb.add_initial_constraint(
        ((ctx["x_0"] - ctx["x_star"]) ** 2).le(R**2, name="initial_condition")
    )
    pb.set_performance_metric(A(ctx[f"x_{N}"]) ** 2)
    return ctx, pb, A
