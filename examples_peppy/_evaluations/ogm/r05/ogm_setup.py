"""OGM setup: smooth convex f, terminal function gap, radius R."""
import math

import pepflow as pf

L = pf.Parameter("L")
R = pf.Parameter("R")
f = pf.SmoothConvexFunction(is_basis=True, tags=["f"], L=L)


def theta_sequence(N):
    """Numerical coefficients; preserve the special terminal recurrence."""
    N = int(N)
    if N < 1:
        raise ValueError("N must be positive")
    previous = 0.0
    theta = []
    for _ in range(N):
        previous = (1.0 + math.sqrt(1.0 + 4.0 * previous**2)) / 2.0
        theta.append(previous)
    theta.append((1.0 + math.sqrt(1.0 + 8.0 * previous**2)) / 2.0)
    return theta


def make_ctx_ogm(ctx_name, N):
    """Encode all iterates, with z_0=x_0 and grad f(x_star)=0."""
    N = int(N)
    theta = theta_sequence(N)
    ctx = pf.PEPContext(ctx_name).set_as_current()
    x = pf.Vector(is_basis=True, tags=["x_0"])
    z = x
    z.add_tag("z_0")
    f.set_stationary_point("x_star")
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
    """Build the normalized PEP; params resolve L and R at solve time."""
    N = int(N)
    ctx = make_ctx_ogm(f"ctx_{N}", N)
    pb = pf.PEPBuilder(ctx)
    pb.add_initial_constraint(
        ((ctx["x_0"] - ctx["x_star"]) ** 2).le(R**2, name="initial_condition")
    )
    pb.set_performance_metric(f(ctx[f"x_{N}"]) - f(ctx["x_star"]))
    return ctx, pb, f
