# This saved notebook fragment shares its caller's execution namespace.
# These names are supplied by the notebook cells or serialized proof source.
# ty: ignore[unresolved-reference]
# ruff: noqa: F821

ctx_boundary = pf.PEPContext("exact_boundary").set_as_current()
f_boundary = pf.ConvexFunction(is_basis=True, tags=["f_{boundary}"])
h_boundary = pf.ConvexFunction(is_basis=True, tags=["h_{boundary}"])
x_start = pf.Vector(is_basis=True, tags=["x_{0}"])
x_terminal = pf.Vector(is_basis=True, tags=["x_{N}"])
f_boundary.set_stationary_point("x_{star}")
x_star_boundary = ctx_boundary["x_{star}"]
D_start = divergence(h_boundary, x_star_boundary, x_start)
D_terminal = divergence(h_boundary, x_star_boundary, x_terminal)
metric = f_boundary(x_terminal) - f_boundary(x_star_boundary)
V_terminal = (D_terminal - D_start) / (a_par * n_par) + metric
boundary_LHS = metric - r_par / (a_par * n_par)
boundary_RHS = (
    V_terminal
    + (D_start - r_par) / (a_par * n_par)
    + convex_residual(h_boundary, x_star_boundary, x_terminal) / (a_par * n_par)
)
diff_boundary = boundary_LHS - boundary_RHS
proof_checks["boundary"] = verify_exact("Boundary", diff_boundary, ctx_boundary)
proof_checks["normalization"] = verify_exact(
    "Metric domination",
    metric - (V_terminal + D_start / (a_par * n_par) - D_terminal / (a_par * n_par)),
    ctx_boundary,
)
