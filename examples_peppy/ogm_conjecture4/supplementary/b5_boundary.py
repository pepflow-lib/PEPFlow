"""Exact terminal Lyapunov identity and initial-radius implication."""

import b5_local_common as common

ctx = common.pf.PEPContext("b5_exact_boundary").set_as_current()
L, q, t, R, parameters = common.b5_parameters()
f = common.pf.SmoothConvexFunction(is_basis=True, tags=["f"], L=L)
x = common.pf.Vector(is_basis=True, tags=["x_last"])
Q = common.pf.Vector(is_basis=True, tags=["q_N"])
r = common.pf.Vector(is_basis=True, tags=["r"])
f.set_stationary_point("x_star")
xs = ctx["x_star"]
g = f.grad(x)
y = x - g / L
y.add_tag("y_N")
H = y - xs
gy = f.grad(y)
tau = L / (2 * (2 * q + 1))
Vlast = common.b5_potential(q, x, g, Q, H, r, f, xs, L, q)
VN = f(y) - f(xs) - tau * (r**2)
Istar = common.b5_star(y, gy, f, xs, L)
Ichain = common.b5_chain(x, g, y, gy, f, L)
D = L / 2 * ((gy / L - H / (q + 1)) ** 2) + L / (4 * (q + 1)) * ((Q - H / (q + 1)) ** 2)
rhs = Istar / (q + 1) + common.b5_weight(q, q) * Ichain - D
checks = [
    common.b5_exact_scalar(
        "V_N-V_(N-1)=a_y I_star+b_last I_chain-D_terminal",
        VN - Vlast - rhs,
        ctx,
        parameters,
    )
]
checks.append(
    common.b5_exact_scalar(
        "native terminal star interpolation",
        Istar - common.b5_native_residual(f, ctx, "f:x_star,y_N"),
        ctx,
        parameters,
    )
)
checks.append(
    common.b5_exact_scalar(
        "native terminal chain interpolation",
        Ichain - common.b5_native_residual(f, ctx, "f:x_last,y_N"),
        ctx,
        parameters,
    )
)
checks.append(
    common.b5_exact_scalar(
        "performance-bound=V_N+tau*(radius residual)",
        f(y) - f(xs) - tau * R**2 - VN - tau * ((r**2) - R**2),
        ctx,
        parameters,
    )
)
common.b5_write_result(common.Path(__file__).with_suffix(".json"), checks)
