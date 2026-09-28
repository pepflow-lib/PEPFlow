"""Exact initial Lyapunov identity for arbitrary L>0 and horizon q>=1."""

import b5_local_common as common

ctx = common.pf.PEPContext("b5_exact_base").set_as_current()
L, q, t, R, parameters = common.b5_parameters()
f = common.pf.SmoothConvexFunction(is_basis=True, tags=["f"], L=L)
x = common.pf.Vector(is_basis=True, tags=["x_0"])
f.set_stationary_point("x_star")
xs = ctx["x_star"]
g = f.grad(x)
r = x - xs
Q = r - 2 * g / L
H = r - g / L
V0 = common.b5_potential(common.sp.S(1), x, g, Q, H, r, f, xs, L, q)
I0 = common.b5_star(x, g, f, xs, L)
D0 = L / (32 * q**4 * (2 * q + 1)) * ((r - (2 * q + 1) * g / L) ** 2)
checks = [
    common.b5_exact_scalar(
        "V_0=b_0 I_star-D_0",
        V0 - common.b5_weight(common.sp.S(1), q) * I0 + D0,
        ctx,
        parameters,
    )
]
checks.append(
    common.b5_exact_scalar(
        "native initial interpolation",
        I0 - common.b5_native_residual(f, ctx, "f:x_star,x_0"),
        ctx,
        parameters,
    )
)
common.b5_write_result(common.Path(__file__).with_suffix(".json"), checks)
