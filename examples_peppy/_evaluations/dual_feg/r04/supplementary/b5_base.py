# This saved notebook fragment shares its caller's execution namespace.
# These names are supplied by the notebook cells or serialized proof source.
# ty: ignore[unresolved-reference]
# ruff: noqa: F821

base_ctx = pf.PEPContext("dual_feg_exact_base").set_as_current()
A_base = pf.LipschitzMonotoneOperator(is_basis=True, tags=["A_{base}"], L=Lp)
x0_base = pf.Vector(is_basis=True, tags=["x_{0}"])
xN_base = pf.Vector(is_basis=True, tags=["x_{N}"])
g_base = A_base(xN_base)
z0_base = pf.Vector.zero()
V0_base = potential_exact(Np, x0_base, z0_base, g_base, x0_base, xN_base, Lp, Np)
base_LHS, base_RHS = V0_base, pf.Scalar.zero()
base_diff = base_LHS - base_RHS
base_manager = pf.ExpressionManager(base_ctx, resolve_parameters=symbolic_values)
proof_checks["base"] = verify_exact(
    "Base V_0=0 for every N>=1", base_diff, base_manager, base_ctx
)

# Actual initial recursion for N>=2, checked separately from an interior substitution.
a_base = A_base(x0_base)
y_base = (x0_base - a_base / Lp).add_tag("x_{1/2}")
b_base = A_base(y_base)
x1_base = (y_base - (Np - 1) / Np / Lp * (b_base - a_base)).add_tag("x_{1}")
z1_base = -b_base / Np
base_step_LHS = potential_exact(
    Np - 1, x1_base, z1_base, g_base, x0_base, xN_base, Lp, Np
)
base_step_RHS = 2 / Np**2 * (
    (b_base - a_base) ** 2 - Lp**2 * ((y_base - x0_base) ** 2)
) - 4 * Lp / (Np * (Np - 1)) * ((b_base - g_base) * (y_base - xN_base))
base_step_diff = base_step_LHS - base_step_RHS
base_step_manager = pf.ExpressionManager(base_ctx, resolve_parameters=symbolic_values)
verify_exact(
    "Actual first-step identity (N>=2)", base_step_diff, base_step_manager, base_ctx
)
