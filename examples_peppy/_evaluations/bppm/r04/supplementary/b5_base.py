# This saved notebook fragment shares its caller's execution namespace.
# These names are supplied by the notebook cells or serialized proof source.
# ty: ignore[unresolved-reference]
# ruff: noqa: F821

ctx_base = pf.PEPContext("exact_base").set_as_current()
f_base = pf.ConvexFunction(is_basis=True, tags=["f_{base}"])
h_base = pf.ConvexFunction(is_basis=True, tags=["h_{base}"])
x_initial = pf.Vector(is_basis=True, tags=["x_{0}"])
f_base.set_stationary_point("x_{star}")
x_star_base = ctx_base["x_{star}"]
x_first = f_base.bregman_prox(x_initial, cast(Number, a_par), h_base, tag="x_{1}")
D_initial = divergence(h_base, x_star_base, x_initial)
V_initial = (D_initial - D_initial) / (a_par * n_par)
verify_exact("Initial zero", V_initial, ctx_base)
V_first = (divergence(h_base, x_star_base, x_first) - D_initial) / (a_par * n_par) + (
    f_base(x_first) - f_base(x_star_base)
) / n_par
base_LHS = V_first - V_initial
base_RHS = convex_residual(f_base, x_star_base, x_first) / n_par + convex_residual(
    h_base, x_first, x_initial
) / (a_par * n_par)
diff_base = base_LHS - base_RHS
proof_checks["base"] = verify_exact("Base first step", diff_base, ctx_base)
initial_residual = D_initial - r_par
W_initial = D_initial / (a_par * n_par)
verify_exact(
    "Initial normalization",
    W_initial - r_par / (a_par * n_par) - initial_residual / (a_par * n_par),
    ctx_base,
)
