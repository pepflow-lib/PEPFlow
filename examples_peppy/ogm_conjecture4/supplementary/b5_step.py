"""Exact generic interior identity using theta_j=t, theta_(j-1)^2=t^2-t."""

import b5_local_common as common

ctx = common.pf.PEPContext("b5_exact_step").set_as_current()
L, q, t, R, parameters = common.b5_parameters()
f = common.pf.SmoothConvexFunction(is_basis=True, tags=["f"], L=L)
xold = common.pf.Vector(is_basis=True, tags=["x_old"])
Q = common.pf.Vector(is_basis=True, tags=["q_j"])
r = common.pf.Vector(is_basis=True, tags=["r"])
f.set_stationary_point("x_star")
xs = ctx["x_star"]
gold = f.grad(xold)
H = xold - xs - gold / L
x = xs + (Q + (t - 1) * H) / t
x.add_tag("x_new")
g = f.grad(x)
v = g / L
Qnew = Q - 2 * t * v
Hnew = x - xs - v
s, p = t**2, t**2 - t
Vold = common.b5_potential(p, xold, gold, Q, H, r, f, xs, L, q)
Vnew = common.b5_potential(s, x, g, Qnew, Hnew, r, f, xs, L, q)
P = 8 * q * t - 6 * q - 4 * t**3 + 4 * t**2 + 4 * t - 3
h, hp = 2 * q + 1 - s, 2 * q + 1 - p
d = t**2 * P / (4 * q * h**3)
gamma = 3 * t * (t - 1) / (4 * q * hp * P)
ell1 = -(6 * q * t - 6 * q - 3 * t**3 + 4 * t**2 + 3 * t - 3) / (t * P)
ell2 = (
    (t - 1)
    * (
        12 * q**2
        - 18 * q * t**2
        + 6 * q * t
        + 12 * q
        + 6 * t**4
        - 4 * t**3
        - 9 * t**2
        + 3 * t
        + 3
    )
    / (t * hp * P)
)
D = L * d * ((v + ell1 * Q + ell2 * H) ** 2) + L * gamma * (
    (Q - (2 * q + 1 - 2 * p) / hp * H) ** 2
)
Istar = common.b5_star(x, g, f, xs, L)
Ichain = common.b5_chain(xold, gold, x, g, f, L)
rhs = (
    (common.b5_weight(s, q) - common.b5_weight(p, q)) * Istar
    + common.b5_weight(p, q) * Ichain
    - D
)
checks = [
    common.b5_exact_scalar(
        "V_j-V_(j-1)=a_j I_star+b_(j-1) I_chain-D_j", Vnew - Vold - rhs, ctx, parameters
    )
]
checks.append(
    common.b5_exact_scalar(
        "native step star interpolation",
        Istar - common.b5_native_residual(f, ctx, "f:x_star,x_new"),
        ctx,
        parameters,
    )
)
checks.append(
    common.b5_exact_scalar(
        "native step chain interpolation",
        Ichain - common.b5_native_residual(f, ctx, "f:x_old,x_new"),
        ctx,
        parameters,
    )
)
common.b5_write_result(common.Path(__file__).with_suffix(".json"), checks)
