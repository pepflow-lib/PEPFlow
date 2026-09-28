# This saved notebook fragment shares its caller's execution namespace.
# These names are supplied by the notebook cells or serialized proof source.
# ty: ignore[unresolved-reference]
# ruff: noqa: F821

ctx_base = pf.PEPContext("feg_symbolic_base").set_as_current()
A_base = pf.LipschitzMonotoneOperator(is_basis=True, tags=["A_{base}"], L=L_param)
x_base = pf.Vector(is_basis=True, tags=["x_{0}", "x_{1/2}"])
g_base = A_base(x_base)
x_first = x_base - g_base / L_param
x_first.add_tag("x_{1}")
g_first = A_base(x_first)
V_zero = pf.Scalar.zero()
V_first = 2 / N_param**2 * g_first**2 + 4 * L_param / N_param**2 * (
    g_first * (x_first - x_base)
)
lip_base = (g_first - g_base) ** 2 - L_param**2 * (x_first - x_base) ** 2
LHS_base = V_first - V_zero
RHS_base = 2 / N_param**2 * lip_base
diff_base = LHS_base - RHS_base
pm_base = pf.ExpressionManager(ctx_base, resolve_parameters=params_symbolic)
base_check = verify_identity("Base", diff_base, pm_base, ctx_base)
