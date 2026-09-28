# This saved notebook fragment shares its caller's execution namespace.
# These names are supplied by the notebook cells or serialized proof source.
# ty: ignore[unresolved-reference]
# ruff: noqa: F821

ctx_boundary = pf.PEPContext("bppm_symbolic_boundary").set_as_current()
f_boundary = pf.ConvexFunction(is_basis=True, tags=["f_{boundary}"])
h_boundary = pf.ConvexFunction(is_basis=True, tags=["h_{boundary}"])
f_boundary.set_stationary_point("x_{star,boundary}")
xs_boundary = ctx_boundary["x_{star,boundary}"]
x0_boundary = pf.Vector(is_basis=True, tags=["x_{0,boundary}"])
xN_boundary = pf.Vector(is_basis=True, tags=["x_{N,boundary}"])
a_boundary = pf.Parameter("a_{boundary}")
n_boundary = pf.Parameter("n_{boundary}")
r_boundary = pf.Parameter("r_{boundary}")
initial_distance = D_h(h_boundary, xs_boundary, x0_boundary)
terminal_distance = D_h(h_boundary, xs_boundary, xN_boundary)
terminal_gap = f_boundary(xN_boundary) - f_boundary(xs_boundary)
terminal_V = terminal_gap + (terminal_distance - initial_distance) / (
    a_boundary * n_boundary
)
initial_residual = initial_distance - r_boundary
terminal_interpolation = interpolation(h_boundary, xs_boundary, xN_boundary)
boundary_LHS = terminal_gap - r_boundary / (a_boundary * n_boundary)
boundary_RHS = (
    terminal_V
    + initial_residual / (a_boundary * n_boundary)
    + terminal_interpolation / (a_boundary * n_boundary)
)
boundary_diff = boundary_LHS - boundary_RHS
boundary_parameters: dict[str, Any] = {
    "a_{boundary}": a_symbol,
    "n_{boundary}": N_symbol,
    "r_{boundary}": R_symbol,
}
pm_boundary = pf.ExpressionManager(ctx_boundary, resolve_parameters=boundary_parameters)
proof_checks["boundary"] = verify_exact("Boundary", boundary_diff, pm_boundary)
# No step index or division by R occurs, so the boundary also covers N=1 and R=0.
edge_parameters: dict[str, Any] = {
    "a_{boundary}": a_symbol,
    "n_{boundary}": sp.S(1),
    "r_{boundary}": sp.S(0),
}
assert verify_exact(
    "N=1, R=0 boundary",
    boundary_diff,
    pf.ExpressionManager(ctx_boundary, resolve_parameters=edge_parameters),
)
