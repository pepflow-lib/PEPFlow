# This saved notebook fragment shares its caller's execution namespace.
# These names are supplied by the notebook cells or serialized proof source.
# ty: ignore[unresolved-reference]
# ruff: noqa: F821

ctx_base = pf.PEPContext("dual_feg_exact_base").set_as_current()
xb = pf.Vector(is_basis=True, tags=["x_{0}"])
nb = pf.Vector(is_basis=True, tags=["x_{N}"])
A_base = pf.LipschitzMonotoneOperator(is_basis=True, tags=["A_{base}"], L=Lp)
ub = A_base(xb)
Gb = A_base(nb)
yb = (xb - ub / Lp).add_tag("y_{0}")
hb = A_base(yb)
x1b = yb - (Np - 1) / Np / Lp * (hb - ub)
z1b = -hb / Np
base_mapping: dict[str, Any] = {"N_exact": Ns, "L_exact": Ls}
pm_base = pf.ExpressionManager(ctx_base, resolve_parameters=base_mapping)
initial = V_closed(Np, pf.Vector.zero(), xb, xb, nb, Gb, Lp, Np)
initial_check = verify_exact("Initial value (N>=1)", initial, pf.Scalar.zero(), pm_base)
LHS = V_closed(Np - 1, z1b, x1b, xb, nb, Gb, Lp, Np)
RHS = 2 / Np**2 * ((ub - hb) ** 2 - Lp**2 * (xb - yb) ** 2) + 4 * Lp / (
    Np * (Np - 1)
) * (-(Gb - hb) * (nb - yb))
first_step_check = verify_exact("First step (N>=2)", LHS, RHS, pm_base)
proof_checks["base"] = initial_check and first_step_check
