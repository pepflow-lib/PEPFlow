# This saved notebook fragment shares its caller's execution namespace.
# These names are supplied by the notebook cells or serialized proof source.
# ty: ignore[unresolved-reference]
# ruff: noqa: F821

last_ctx = pf.PEPContext("dual_feg_exact_last_step").set_as_current()
A_last = pf.LipschitzMonotoneOperator(is_basis=True, tags=["A_{last}"], L=Lp)
x_last = pf.Vector(is_basis=True, tags=["x_{N-1}"])
z_last = pf.Vector(is_basis=True, tags=["z_{N-1}"])
x0_last = pf.Vector(is_basis=True, tags=["x_{0}"])
a_last = A_last(x_last)
xN_last = (x_last - z_last / Lp - a_last / Lp).add_tag("x_{N}")
g_last = A_last(xN_last)
last_LHS = terminal_exact(g_last, x0_last, xN_last, Lp, Np) - potential_exact(
    1, x_last, z_last, g_last, x0_last, xN_last, Lp, Np
)
last_RHS = 2 * ((g_last - a_last) ** 2 - Lp**2 * ((xN_last - x_last) ** 2))
last_diff = last_LHS - last_RHS
last_manager = pf.ExpressionManager(last_ctx, resolve_parameters=symbolic_values)
verify_exact("Last step t=1", last_diff, last_manager, last_ctx)

small_ctx = pf.PEPContext("dual_feg_exact_N1").set_as_current()
A_small = pf.LipschitzMonotoneOperator(is_basis=True, tags=["A_{N=1}"], L=Lp)
x0_small = pf.Vector(is_basis=True, tags=["x_{0}"])
a_small = A_small(x0_small)
x1_small = (x0_small - a_small / Lp).add_tag("x_{1}")
g_small = A_small(x1_small)
small_LHS = terminal_exact(g_small, x0_small, x1_small, Lp, 1)
small_RHS = 2 * ((g_small - a_small) ** 2 - Lp**2 * ((x1_small - x0_small) ** 2))
small_diff = small_LHS - small_RHS
small_manager = pf.ExpressionManager(small_ctx, resolve_parameters=symbolic_values)
verify_exact("Exceptional horizon N=1", small_diff, small_manager, small_ctx)
