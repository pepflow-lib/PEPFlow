# This saved notebook fragment shares its caller's execution namespace.
# These names are supplied by the notebook cells or serialized proof source.
# ty: ignore[unresolved-reference]
# ruff: noqa: F821

ctx_terminal = pf.PEPContext("symbolic_terminal").set_as_current()
A_terminal = pf.LipschitzMonotoneOperator(is_basis=True, tags=["A_{terminal}"], L=l_p)
x0_terminal = pf.Vector(is_basis=True, tags=["x_{0,terminal}"])
x_terminal = pf.Vector(is_basis=True, tags=["x_{N-1,terminal}"])
z_terminal = pf.Vector(is_basis=True, tags=["z_{N-1,terminal}"])
g_terminal = A_terminal(x_terminal)
X_terminal = (x_terminal - z_terminal / l_p - g_terminal / l_p).add_tag(
    "x_{N,terminal}"
)
G_terminal = A_terminal(X_terminal)
terminal_LHS = terminal_potential(
    X_terminal, x0_terminal, G_terminal, l_p, n_p
) - potential(1, x_terminal, z_terminal, X_terminal, x0_terminal, G_terminal, l_p, n_p)
terminal_RHS = 2 * (
    (g_terminal - G_terminal) ** 2 - l_p**2 * (x_terminal - X_terminal) ** 2
)
pm_terminal = pf.ExpressionManager(
    ctx_terminal,
    resolve_parameters=cast(
        dict[str, pf.NUMERICAL_TYPE], {"N_symbolic": n_s, "L_symbolic": l_s}
    ),
)
terminal_diff = terminal_LHS - terminal_RHS
last_step_passed = verify_exact("Last-step identity (N>=2)", terminal_diff, pm_terminal)
