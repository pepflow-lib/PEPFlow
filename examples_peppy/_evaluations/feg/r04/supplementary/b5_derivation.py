# This saved notebook fragment shares its caller's execution namespace.
# These names are supplied by the notebook cells or serialized proof source.
# ty: ignore[unresolved-reference]
# ruff: noqa: F821

from typing import Any, Callable, cast

k_symbol, N_symbol = sp.symbols("k N", integer=True, positive=True)
L_symbol = sp.Symbol("L", positive=True)
R_symbol = sp.Symbol("R", nonnegative=True)
k_param, N_param, L_param, R_param = [
    pf.Parameter(s) for s in ("k_symbolic", "N_symbolic", "L_symbolic", "R_symbolic")
]
params_symbolic: dict[str, Any] = {
    "k_symbolic": k_symbol,
    "N_symbolic": N_symbol,
    "L_symbolic": L_symbol,
    "R_symbolic": R_symbol,
}


def symbolic_components(expression, manager):
    value = manager.eval_scalar(pf.Scalar.zero() + expression, sympy_mode=True)
    return (
        sp.Matrix(value.inner_prod_coords).applyfunc(sp.simplify),
        sp.Matrix(list(value.func_coords)).applyfunc(sp.simplify),
        sp.simplify(sp.sympify(value.offset)),
    )


def verify_identity(label, expression, manager, context):
    gram, functions, offset = symbolic_components(expression, manager)
    pf.pprint_labeled_matrix(
        pf.MatrixWithNames(
            np.array(gram, dtype=object),
            [str(v) for v in context.basis_vectors()],
            [str(v) for v in context.basis_vectors()],
        )
    )
    print(label, "function coordinates:", functions, "offset:", offset)
    assert all(v == 0 for v in [*gram, *functions, offset]), label
    return {"gram_zero": True, "function_zero": True, "offset_zero": True}


ctx_step = pf.PEPContext("feg_symbolic_step").set_as_current()
A_step = pf.LipschitzMonotoneOperator(is_basis=True, tags=["A_{step}"], L=L_param)
x_anchor = pf.Vector(is_basis=True, tags=["x_{0}"])
x_current = pf.Vector(is_basis=True, tags=["x_{k}"])
g_current = A_step(x_current)
x_half = (
    x_current
    + (x_anchor - x_current) / (k_param + 1)
    - k_param / ((k_param + 1) * L_param) * g_current
)
x_half.add_tag("x_{k+1/2}")
g_half = A_step(x_half)
x_next = x_current + (x_anchor - x_current) / (k_param + 1) - g_half / L_param
x_next.add_tag("x_{k+1}")
g_next = A_step(x_next)
q_current = x_current - x_anchor
q_next = x_next - x_anchor
lip_step = (g_next - g_half) ** 2 - L_param**2 * (x_next - x_half) ** 2
mon_step = -(g_next - g_current) * (x_next - x_current)
unknown_names = ["a", "b", "c", "a_next", "b_next", "c_next", "mu_lip", "mu_mon"]
unknown_parameters = {name: pf.Parameter(name) for name in unknown_names}
unknown_symbols = {
    name: cast(Callable[..., Any], sp.Function(name))(k_symbol, N_symbol, L_symbol)
    for name in unknown_names
}
unknown_map = {**params_symbolic, **unknown_symbols}
V_unknown = (
    unknown_parameters["a"] * g_current**2
    + 2 * unknown_parameters["b"] * (g_current * q_current)
    + unknown_parameters["c"] * q_current**2
)
V_unknown_next = (
    unknown_parameters["a_next"] * g_next**2
    + 2 * unknown_parameters["b_next"] * (g_next * q_next)
    + unknown_parameters["c_next"] * q_next**2
)
unknown_diff = (
    V_unknown_next
    - V_unknown
    - unknown_parameters["mu_lip"] * lip_step
    - unknown_parameters["mu_mon"] * mon_step
)
manager_unknown = pf.ExpressionManager(ctx_step, resolve_parameters=unknown_map)
gram_equations, function_equations, offset_equation = symbolic_components(
    unknown_diff, manager_unknown
)
equations = [
    sp.factor(v)
    for v in [*gram_equations, *function_equations, offset_equation]
    if v != 0
]
solution = sp.solve(
    equations,
    [unknown_symbols[name] for name in unknown_names if name != "a"],
    dict=True,
)
assert len(solution) == 1
coefficient_recursion = {
    str(key): sp.factor(value) for key, value in solution[0].items()
}
print("Coefficient and multiplier recurrences:", coefficient_recursion)
# Solve the recurrence by induction: a(k+1)/(k+1)^2 = a(k)/k^2.
# The normalization a(N)=2 chooses a(k)=2*k^2/N^2.
chosen = {
    unknown_symbols["a"]: 2 * k_symbol**2 / N_symbol**2,
    unknown_symbols["b"]: 2 * L_symbol * k_symbol / N_symbol**2,
    unknown_symbols["c"]: sp.S.Zero,
    unknown_symbols["a_next"]: 2 * (k_symbol + 1) ** 2 / N_symbol**2,
    unknown_symbols["b_next"]: 2 * L_symbol * (k_symbol + 1) / N_symbol**2,
    unknown_symbols["c_next"]: sp.S.Zero,
    unknown_symbols["mu_lip"]: 2 * (k_symbol + 1) ** 2 / N_symbol**2,
    unknown_symbols["mu_mon"]: 4 * L_symbol * k_symbol * (k_symbol + 1) / N_symbol**2,
}
assert all(sp.simplify(eq.subs(chosen)) == 0 for eq in equations)
assert sp.simplify((2 * k_symbol**2 / N_symbol**2).subs(k_symbol, N_symbol) - 2) == 0
print("Normalized coefficients: a=2*k**2/N**2, b=2*L*k/N**2, c=0")
