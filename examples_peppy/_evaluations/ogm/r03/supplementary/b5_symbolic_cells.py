# This saved notebook fragment shares its caller's execution namespace.
# These names are supplied by the notebook cells or serialized proof source.
# ty: ignore[unresolved-reference]
# ruff: noqa: F821

# %% Symbolic setup
from typing import Any


def symbolic_components(expression, manager):
    value = manager.eval_scalar(pf.Scalar.zero() + expression, sympy_mode=True)
    gram = sp.Matrix(value.inner_prod_coords).applyfunc(sp.simplify)
    functions = sp.Matrix(list(value.func_coords)).applyfunc(sp.simplify)
    offset = sp.simplify(sp.sympify(value.offset))
    return gram, functions, offset


def assert_exact_identity(name, expression, manager, context):
    gram, functions, offset = symbolic_components(expression, manager)
    assert all(term == 0 for term in [*gram, *functions, offset]), (
        name,
        gram,
        functions,
        offset,
    )
    labels = [str(v) for v in context.basis_vectors()]
    pf.pprint_labeled_matrix(
        pf.MatrixWithNames(np.array(gram, dtype=object), labels, labels)
    )
    print(name, "function residual:", functions.T, "offset:", offset)
    return {"gram_zero": True, "function_zero": True, "offset_zero": True}


ell_sym, t_sym, u_sym, T_sym = sp.symbols("L t u T", positive=True)
a_sym, b_sym, c_sym, d_sym, m_sym, n_sym = sp.symbols("a b c d m n", real=True)
L_exact, t_exact, u_exact, T_exact = [
    pf.Parameter(name) for name in ("L_exact", "t_exact", "u_exact", "T_exact")
]
aa, bb, cc, dd, mm, nn = [
    pf.Parameter(name) for name in ("aa", "bb", "cc", "dd", "mm", "nn")
]
symbolic_values: dict[str, Any] = {
    "L_exact": ell_sym,
    "t_exact": t_sym,
    "u_exact": u_sym,
    "T_exact": T_sym,
    "aa": a_sym,
    "bb": b_sym,
    "cc": c_sym,
    "dd": d_sym,
    "mm": m_sym,
    "nn": n_sym,
}


def interpolation_residual(function, first, second, smoothness):
    return (
        function(second)
        - function(first)
        + function.grad(second) * (first - second)
        + (function.grad(first) - function.grad(second)) ** 2 / (2 * smoothness)
    )


# %% Derivation
step_ctx = pf.PEPContext("ogm_symbolic_step").set_as_current()
f_step = pf.SmoothConvexFunction(is_basis=True, tags=["f_{step}"], L=L_exact)
f_step.set_stationary_point("x_{star}")
star_step = step_ctx["x_{star}"]
x_step = pf.Vector(is_basis=True, tags=["x_{k}"])
z_step = pf.Vector(is_basis=True, tags=["z_{k}"])
anchor_step = pf.Vector(is_basis=True, tags=["x_{0}"])
g_step = f_step.grad(x_step)
z_next = z_step - 2 * t_exact / L_exact * g_step
x_next = (1 - 1 / u_exact) * (x_step - g_step / L_exact) + z_next / u_exact
x_next.add_tag("x_{k+1}")
g_next = f_step.grad(x_next)
I_star_step = interpolation_residual(f_step, star_step, x_step, L_exact)
I_forward_step = interpolation_residual(f_step, x_step, x_next, L_exact)

# The sparse ansatz is motivated by B4, but its constants are still unknown.
W_current_ansatz = (
    aa * L_exact * ((z_step - star_step) ** 2 - (anchor_step - star_step) ** 2)
    + bb * (t_exact**2 - t_exact) * (f_step(x_step) - f_step(star_step))
    + cc * (t_exact**2 - t_exact) / L_exact * g_step**2
    + dd * t_exact * g_step * (x_step - z_step)
)
W_next_ansatz = (
    aa * L_exact * ((z_next - star_step) ** 2 - (anchor_step - star_step) ** 2)
    + bb * t_exact**2 * (f_step(x_next) - f_step(star_step))
    + cc * t_exact**2 / L_exact * g_next**2
    + dd * t_exact**2 / (u_exact - 1) * g_next * (x_next - z_next)
)
ansatz_residual = (
    W_next_ansatz
    - W_current_ansatz
    - mm * t_exact * I_star_step
    - nn * t_exact**2 * I_forward_step
)
pm_ansatz = pf.ExpressionManager(step_ctx, resolve_parameters=symbolic_values)
gram_eq, function_eq, offset_eq = symbolic_components(ansatz_residual, pm_ansatz)
equations = [term for term in [*gram_eq, *function_eq, offset_eq] if term != 0] + [
    a_sym - sp.Rational(1, 2)
]
derived_constants = sp.solve(
    equations, [a_sym, b_sym, c_sym, d_sym, m_sym, n_sym], dict=True
)
assert derived_constants == [
    {a_sym: sp.Rational(1, 2), b_sym: 2, c_sym: 1, d_sym: 2, m_sym: 2, n_sym: 2}
]
print("Derived normalized constants:", derived_constants[0])

# %% Step
resolved_values: dict[str, Any] = {
    **symbolic_values,
    "aa": sp.Rational(1, 2),
    "bb": sp.Integer(2),
    "cc": sp.Integer(1),
    "dd": sp.Integer(2),
    "mm": sp.Integer(2),
    "nn": sp.Integer(2),
}
pm_step = pf.ExpressionManager(step_ctx, resolve_parameters=resolved_values)
step_LHS = (W_next_ansatz - W_current_ansatz) / T_exact**2
step_RHS = (
    2 * t_exact / T_exact**2 * I_star_step
    + 2 * t_exact**2 / T_exact**2 * I_forward_step
)
step_diff = step_LHS - step_RHS
exact_step = assert_exact_identity("Generic step", step_diff, pm_step, step_ctx)

# %% Base
base_ctx = pf.PEPContext("ogm_symbolic_base").set_as_current()
f_base = pf.SmoothConvexFunction(is_basis=True, tags=["f_{base}"], L=L_exact)
f_base.set_stationary_point("x_{star}")
star_base = base_ctx["x_{star}"]
x_base = pf.Vector(is_basis=True, tags=["x_{0}"])
g_base = f_base.grad(x_base)
z_base_next = x_base - 2 / L_exact * g_base
x_base_next = (1 - 1 / u_exact) * (x_base - g_base / L_exact) + z_base_next / u_exact
x_base_next.add_tag("x_{1}")
g_base_next = f_base.grad(x_base_next)
V_zero = pf.Scalar.zero()
V_one = (
    L_exact / 2 * ((z_base_next - star_base) ** 2 - (x_base - star_base) ** 2)
    + 2 * (f_base(x_base_next) - f_base(star_base))
    + g_base_next**2 / L_exact
    + 2 / (u_exact - 1) * g_base_next * (x_base_next - z_base_next)
) / T_exact**2
base_LHS = V_one - V_zero
base_RHS = (
    2 * interpolation_residual(f_base, star_base, x_base, L_exact)
    + 2 * interpolation_residual(f_base, x_base, x_base_next, L_exact)
) / T_exact**2
base_diff = base_LHS - base_RHS
pm_base = pf.ExpressionManager(base_ctx, resolve_parameters=resolved_values)
exact_base = assert_exact_identity("Base step", base_diff, pm_base, base_ctx)

# %% First coefficient reduction
first_anchor = x_base - star_base
first_aux = z_base_next - star_base
V_one_reduced = (
    L_exact / (2 * T_exact**2) * (first_aux**2 - first_anchor**2)
    + 2 / T_exact**2 * (f_base(x_base_next) - f_base(star_base))
    + g_base_next**2 / (L_exact * T_exact**2)
    + (g_base_next * (first_anchor - first_aux)) / (u_exact * T_exact**2)
)
first_coeff_diff = V_one_reduced - V_one
exact_first_coefficients = assert_exact_identity(
    "Three-vector initial basis", first_coeff_diff, pm_base, base_ctx
)

# %% Boundary
boundary_ctx = pf.PEPContext("ogm_symbolic_boundary").set_as_current()
f_boundary = pf.SmoothConvexFunction(is_basis=True, tags=["f_{boundary}"], L=L_exact)
f_boundary.set_stationary_point("x_{star}")
star_boundary = boundary_ctx["x_{star}"]
x_boundary = pf.Vector(is_basis=True, tags=["x_{N}"])
z_boundary = pf.Vector(is_basis=True, tags=["z_{N}"])
anchor_boundary = pf.Vector(is_basis=True, tags=["x_{0}"])
g_boundary = f_boundary.grad(x_boundary)
gap_boundary = f_boundary(x_boundary) - f_boundary(star_boundary)
V_terminal = (
    L_exact
    / 2
    * ((z_boundary - star_boundary) ** 2 - (anchor_boundary - star_boundary) ** 2)
    + (T_exact**2 - T_exact) * gap_boundary
    + (T_exact**2 - T_exact) / (2 * L_exact) * g_boundary**2
    + T_exact * g_boundary * (x_boundary - z_boundary)
) / T_exact**2
I_terminal = interpolation_residual(f_boundary, star_boundary, x_boundary, L_exact)
terminal_square = (
    L_exact
    / (2 * T_exact**2)
    * (z_boundary - star_boundary - T_exact / L_exact * g_boundary) ** 2
)
boundary_LHS = (
    gap_boundary - L_exact / (2 * T_exact**2) * (anchor_boundary - star_boundary) ** 2
)
boundary_RHS = V_terminal + I_terminal / T_exact - terminal_square
boundary_diff = boundary_LHS - boundary_RHS
pm_boundary = pf.ExpressionManager(boundary_ctx, resolve_parameters=resolved_values)
exact_boundary = assert_exact_identity(
    "Terminal identity", boundary_diff, pm_boundary, boundary_ctx
)

# %% Normalization
R_exact = pf.Parameter("R_exact")
R_sym = sp.symbols("R", nonnegative=True)
pm_normalization = pf.ExpressionManager(
    boundary_ctx, resolve_parameters={**resolved_values, "R_exact": R_sym}
)
normalization_LHS = gap_boundary - L_exact * R_exact**2 / (2 * T_exact**2)
normalization_RHS = (
    V_terminal
    + I_terminal / T_exact
    - terminal_square
    + L_exact / (2 * T_exact**2) * ((anchor_boundary - star_boundary) ** 2 - R_exact**2)
)
normalization_diff = normalization_LHS - normalization_RHS
exact_normalization = assert_exact_identity(
    "Radius normalization", normalization_diff, pm_normalization, boundary_ctx
)

# %% Terminal and small horizon recurrence checks
p_sym = sp.symbols("p", nonnegative=True)
theta_regular = (1 + sp.sqrt(1 + 4 * p_sym**2)) / 2
theta_terminal = (1 + sp.sqrt(1 + 8 * p_sym**2)) / 2
assert sp.simplify(theta_regular**2 - theta_regular - p_sym**2) == 0
assert sp.simplify(theta_terminal**2 - theta_terminal - 2 * p_sym**2) == 0
assert sp.simplify((theta_regular - 1) * theta_regular - p_sym**2) == 0
assert sp.simplify((theta_terminal - 1) * theta_terminal / 2 - p_sym**2) == 0
# N=1 has theta_0=1 and theta_1=2; the separately checked base applies.
base_ctx.set_as_current()
pm_one = pf.ExpressionManager(
    base_ctx,
    resolve_parameters={
        **resolved_values,
        "u_exact": sp.Integer(2),
        "T_exact": sp.Integer(2),
    },
)
one_LHS = (
    f_base(x_base_next) - f_base(star_base) - L_exact / 8 * (x_base - star_base) ** 2
)
one_square = L_exact / 8 * (z_base_next - star_base - 2 / L_exact * g_base_next) ** 2
one_RHS = (
    V_one
    + interpolation_residual(f_base, star_base, x_base_next, L_exact) / 2
    - one_square
)
exact_one = assert_exact_identity(
    "N=1 terminal identity", one_LHS - one_RHS, pm_one, base_ctx
)
symbolic_results = {
    "step": exact_step,
    "base": exact_base,
    "first_basis": exact_first_coefficients,
    "boundary": exact_boundary,
    "normalization": exact_normalization,
    "N1": exact_one,
}
print("All exact identities passed.")
