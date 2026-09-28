# This saved notebook fragment shares its caller's execution namespace.
# These names are supplied by the notebook cells or serialized proof source.
# ty: ignore[unresolved-reference]
# ruff: noqa: F821

import sympy as sp

import pepflow as pf


def symbolic_components(expression, manager):
    value = manager.eval_scalar(pf.Scalar.zero() + expression, sympy_mode=True)
    return (
        sp.Matrix(value.inner_prod_coords).applyfunc(sp.simplify),
        sp.Matrix(list(value.func_coords)).applyfunc(sp.simplify),
        sp.simplify(sp.sympify(value.offset)),
    )


def verify_exact(name, expression, manager, context):
    gram, functions, offset = symbolic_components(expression, manager)
    assert all(v == 0 for v in [*gram, *functions, offset]), name
    labels = [str(v) for v in context.basis_vectors()]
    pf.pprint_labeled_matrix(
        pf.MatrixWithNames(np.asarray(gram, dtype=object), labels, labels)
    )
    print(
        name, "Gram residual: zero; function coordinates:", functions, "offset:", offset
    )
    return True


k_symbol, N_symbol = sp.symbols("k N", integer=True, positive=True)
L_symbol = sp.symbols("L", positive=True)
R_symbol = sp.symbols("R", nonnegative=True)
Kp = pf.Parameter("k_symbolic")
Np = pf.Parameter("N_symbolic")
Lp = pf.Parameter("L_symbolic")
Rp = pf.Parameter("R_symbolic")
ctx_step = pf.PEPContext("feg_symbolic_step").set_as_current()
A_step = pf.LipschitzMonotoneOperator(is_basis=True, tags=["A_{step}"], L=Lp)
x_anchor = pf.Vector(is_basis=True, tags=["x_{0}"])
x_current = pf.Vector(is_basis=True, tags=["x_{k}"])
g_current = A_step(x_current)
x_half = (
    x_current + (x_anchor - x_current) / (Kp + 1) - Kp / ((Kp + 1) * Lp) * g_current
)
x_half.add_tag("x_{k+1/2}")
g_half = A_step(x_half)
x_next = x_current + (x_anchor - x_current) / (Kp + 1) - g_half / Lp
x_next.add_tag("x_{k+1}")
g_next = A_step(x_next)
unknown_names = ["a_k", "b_k", "c_k", "a_next", "b_next", "c_next", "mu", "nu"]
unknown_symbols = dict(
    zip(unknown_names, sp.symbols("a_k b_k c_k a_next b_next c_next mu nu", real=True))
)
unknown_parameters = {name: pf.Parameter(name) for name in unknown_names}


def ansatz(a, b, c, g, x):
    return a * g**2 + 2 * b * g * (x - x_anchor) + c * (x - x_anchor) ** 2


V_unknown = ansatz(
    unknown_parameters["a_k"],
    unknown_parameters["b_k"],
    unknown_parameters["c_k"],
    g_current,
    x_current,
)
V_next_unknown = ansatz(
    unknown_parameters["a_next"],
    unknown_parameters["b_next"],
    unknown_parameters["c_next"],
    g_next,
    x_next,
)
mon_step = -(g_next - g_current) * (x_next - x_current)
lip_step = (g_next - g_half) ** 2 - Lp**2 * (x_next - x_half) ** 2
unknown_LHS = V_next_unknown - V_unknown
unknown_RHS = unknown_parameters["mu"] * mon_step + unknown_parameters["nu"] * lip_step
unknown_diff = unknown_LHS - unknown_RHS
symbolic_mapping = {
    "k_symbolic": k_symbol,
    "N_symbolic": N_symbol,
    "L_symbolic": L_symbol,
    **unknown_symbols,
}
pm_unknown = pf.ExpressionManager(ctx_step, resolve_parameters=symbolic_mapping)
gram_unknown, func_unknown, offset_unknown = symbolic_components(
    unknown_diff, pm_unknown
)
equations = [v for v in [*gram_unknown, *func_unknown, offset_unknown] if v != 0]
solution = sp.solve(
    equations, [unknown_symbols[name] for name in unknown_names[:-1]], dict=True
)
print("Coefficient-equation solution:", solution)
assert len(solution) == 1
