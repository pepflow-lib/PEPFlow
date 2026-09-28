# This saved notebook fragment shares its caller's execution namespace.
# These names are supplied by the notebook cells or serialized proof source.
# ty: ignore[unresolved-reference]
# ruff: noqa: F821

ctx_base = pf.PEPContext("bppm_symbolic_base").set_as_current()
f_base = pf.ConvexFunction(is_basis=True, tags=["f_{base}"])
h_base = pf.ConvexFunction(is_basis=True, tags=["h_{base}"])
xs_base = f_base.set_stationary_point("x_{star,base}")
x0_base = pf.Vector(is_basis=True, tags=["x_{0,base}"])
x1_base = pf.Vector(is_basis=True, tags=["x_{1,base}"])
g1_base = f_base.grad(x1_base)
h_base.add_point_with_grad_restriction(
    x1_base, h_base.grad(x0_base) - alpha_parameter * g1_base
)
V0_base = pf.Scalar.zero()
V1_base = (f_base(x1_base) - f_base(xs_base)) / N_parameter + (
    bregman(h_base, xs_base, x1_base) - bregman(h_base, xs_base, x0_base)
) / (alpha_parameter * N_parameter)
LHS_base = V1_base - V0_base
RHS_base = f_base.interp_ineq(xs_base, x1_base) / N_parameter + h_base.interp_ineq(
    x1_base, x0_base
) / (alpha_parameter * N_parameter)
pm_base = pf.ExpressionManager(ctx_base, resolve_parameters=symbolic_parameters)
base_check = exact_check("Base", LHS_base, RHS_base, pm_base, ctx_base)
zero_gram, zero_functions, zero_offset = symbolic_components(V0_base, pm_base)
assert all(term == 0 for term in [*zero_gram, *zero_functions, zero_offset])
