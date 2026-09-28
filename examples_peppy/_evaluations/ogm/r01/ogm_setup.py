"""OGM setup: smooth convex objective gap with initial squared radius R**2."""
import math

import pepflow as pf

L = pf.Parameter("L")
R = pf.Parameter("R")
f = pf.SmoothConvexFunction(is_basis=True, tags=["f"], L=L)


def theta_sequence(N):
    """Numerical coefficients; the terminal recurrence has factor eight."""
    theta = []
    previous = 0.0
    for k in range(int(N) + 1):
        factor = 8 if k == N else 4
        previous = (1 + math.sqrt(1 + factor * previous**2)) / 2
        theta.append(previous)
    return theta


def make_ctx_ogm(ctx_name, N, **kwargs):
    ctx = pf.PEPContext(ctx_name).set_as_current()
    x = pf.Vector(is_basis=True, tags=["x_0", "z_0"])
    z = x
    f.set_stationary_point("x_star")
    theta = theta_sequence(N)
    for k in range(int(N)):
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
    ctx = make_ctx_ogm(f"ctx_{N}", N)
    pb = pf.PEPBuilder(ctx)
    pb.add_initial_constraint(
        ((ctx["x_0"] - ctx["x_star"]) ** 2).le(R**2, name="initial_condition")
    )
    pb.set_performance_metric(f(ctx[f"x_{N}"]) - f(ctx["x_star"]))
    return ctx, pb, f
