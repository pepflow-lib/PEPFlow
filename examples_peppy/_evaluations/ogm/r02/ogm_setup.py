"""OGM for smooth convex functions, with the special terminal theta update."""

from math import sqrt

import pepflow as pf

L = pf.Parameter("L")
R = pf.Parameter("R")
f = pf.SmoothConvexFunction(is_basis=True, tags=["f"], L=L)


def theta_sequence(N):
    """Numerical theta coefficients for a finite PEP sample, including theta_N."""
    if N < 1:
        raise ValueError("N must be positive")
    theta = []
    previous = 0.0
    for _ in range(N):
        previous = (1 + sqrt(1 + 4 * previous**2)) / 2
        theta.append(previous)
    theta.append((1 + sqrt(1 + 8 * previous**2)) / 2)
    return theta


def make_ctx_ogm(ctx_name: str, N, **kwargs) -> pf.PEPContext:
    ctx = pf.PEPContext(ctx_name).set_as_current()
    x = pf.Vector(is_basis=True, tags=["x_0", "z_0"])
    z = x
    f.set_stationary_point("x_star")
    theta = theta_sequence(N)
    for k in range(N):
        g = f.grad(x)
        g.add_tag(f"g_{k}")
        y = x - g / L
        y.add_tag(f"y_{k + 1}")
        z = z - (2 * theta[k] / L) * g
        z.add_tag(f"z_{k + 1}")
        x = (1 - 1 / theta[k + 1]) * y + z / theta[k + 1]
        x.add_tag(f"x_{k + 1}")
    f.grad(x).add_tag(f"g_{N}")
    return ctx


def get_pep_setup(N, params):
    ctx = make_ctx_ogm(f"ogm_{N}", N)
    pb = pf.PEPBuilder(ctx)
    pb.add_initial_constraint(
        ((ctx["x_0"] - ctx["x_star"]) ** 2).le(R**2, name="initial_condition")
    )
    pb.set_performance_metric(f(ctx[f"x_{N}"]) - f(ctx["x_star"]))
    return ctx, pb, f
