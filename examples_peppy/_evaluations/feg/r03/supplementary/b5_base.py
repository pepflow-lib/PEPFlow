# This saved notebook fragment shares its caller's execution namespace.
# These names are supplied by the notebook cells or serialized proof source.
# ty: ignore[unresolved-reference]
# ruff: noqa: F821

ctx_base = pf.PEPContext("feg_symbolic_base").set_as_current()
A_base = pf.LipschitzMonotoneOperator(is_basis=True, tags=["A_{base}"], L=LL)
x0_base = pf.Vector(is_basis=True, tags=["x_{0}", "x_{1/2}"])
g0_base = A_base(x0_base)
x1_base = x0_base - g0_base / LL
x1_base.add_tag("x_{1}")
g1_base = A_base(x1_base)
V0_base = pf.Scalar.zero()
V1_base = 2 / NN**2 * g1_base**2 + 4 * LL / NN**2 * g1_base * (x1_base - x0_base)
Lip_base = (g1_base - g0_base) ** 2 - LL**2 * (x1_base - x0_base) ** 2
LHS_base = V1_base - V0_base
RHS_base = 2 / NN**2 * Lip_base
diff_base = LHS_base - RHS_base
pm_base = pf.ExpressionManager(ctx_base, resolve_parameters=params_symbolic)
base_verified = verify_exact("Base", diff_base, pm_base, ctx_base)
assert x0_base is ctx_base["x_{0}"] and x0_base is ctx_base["x_{1/2}"]
