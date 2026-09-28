"""Derive and exactly verify a local FEG Lyapunov certificate."""

import json
from pathlib import Path
from typing import Any

import numpy as np
import sympy as sp

import pepflow as pf


# BEGIN SYMBOLIC HELPERS
def symbolic_components(expression, manager):
    value = manager.eval_scalar(pf.Scalar.zero() + expression, sympy_mode=True)
    gram = sp.Matrix(value.inner_prod_coords).applyfunc(sp.simplify)
    functions = sp.Matrix(list(value.func_coords)).applyfunc(sp.simplify)
    offset = sp.simplify(sp.sympify(value.offset))
    return gram, functions, offset


def verify_symbolic_identity(name, expression, manager):
    gram, functions, offset = symbolic_components(expression, manager)
    labels = [str(v) for v in manager.context.basis_vectors()]
    print(name, "Gram residual shape:", gram.shape)
    pf.pprint_labeled_matrix(np.asarray(gram.tolist(), dtype=object), labels, labels)
    print(name, "function residual:", functions, "offset:", offset)
    assert all(term == 0 for term in [*gram, *functions, offset]), name
    return True


# END SYMBOLIC HELPERS

# BEGIN DERIVATION
k_sym, N_sym = sp.symbols("k N", integer=True, positive=True)
L_sym = sp.Symbol("L", positive=True)
k_par, N_par, L_par = pf.Parameter("k"), pf.Parameter("N"), pf.Parameter("L_local")
ctx_step = pf.PEPContext("symbolic_feg_step").set_as_current()
A_step = pf.LipschitzMonotoneOperator(is_basis=True, tags=["A_{step}"], L=L_par)
x_anchor = pf.Vector(is_basis=True, tags=["x_{0}"])
x_current = pf.Vector(is_basis=True, tags=["x_{k}"])
g_current = A_step(x_current)
anchor_step = x_current + (x_anchor - x_current) / (k_par + 1)
x_half = anchor_step - k_par / ((k_par + 1) * L_par) * g_current
x_half.add_tag("x_{k+1/2}")
g_half = A_step(x_half)
x_next = anchor_step - g_half / L_par
x_next.add_tag("x_{k+1}")
g_next = A_step(x_next)
mon_step = -(x_current - x_next) * (g_current - g_next)
lip_step = (g_next - g_half) ** 2 - L_par**2 * (x_next - x_half) ** 2
unknown_names = (
    "a",
    "b",
    "c",
    "a_plus",
    "b_plus",
    "c_plus",
    "lambda_local",
    "mu_local",
)
unknown_symbols = sp.symbols(" ".join(unknown_names), real=True)
unknown_parameters = {name: pf.Parameter(name) for name in unknown_names}
a, b, c, ap, bp, cp, lam, mu = [unknown_parameters[name] for name in unknown_names]
V_ansatz = (
    a * g_current**2
    + 2 * b * g_current * (x_current - x_anchor)
    + c * (x_current - x_anchor) ** 2
)
V_next_ansatz = (
    ap * g_next**2
    + 2 * bp * g_next * (x_next - x_anchor)
    + cp * (x_next - x_anchor) ** 2
)
step_ansatz_diff = V_next_ansatz - V_ansatz - lam * mon_step - mu * lip_step
symbolic_parameters: dict[str, Any] = {
    "k": k_sym,
    "N": N_sym,
    "L_local": L_sym,
    **dict(zip(unknown_names, unknown_symbols)),
}
pm_derivation = pf.ExpressionManager(ctx_step, resolve_parameters=symbolic_parameters)
gram_unknown, func_unknown, offset_unknown = symbolic_components(
    step_ansatz_diff, pm_derivation
)
equations = [
    term for term in [*gram_unknown, *func_unknown, offset_unknown] if term != 0
]
solution_list = sp.solve(equations, list(unknown_symbols[1:]), dict=True)
assert len(solution_list) == 1
coefficient_solution = {
    symbol: sp.factor(value) for symbol, value in solution_list[0].items()
}
print("Exact local coefficient solution:", coefficient_solution)
a_sym, b_sym, c_sym, ap_sym, bp_sym, cp_sym, lam_sym, mu_sym = unknown_symbols
assert (
    sp.simplify(coefficient_solution[ap_sym] / a_sym - (k_sym + 1) ** 2 / k_sym**2) == 0
)
assert sp.simplify(coefficient_solution[b_sym] - a_sym * L_sym / k_sym) == 0
assert coefficient_solution[c_sym] == 0 and coefficient_solution[cp_sym] == 0
normalization_constant = sp.S(2) / N_sym**2
derived_substitution = {a_sym: normalization_constant * k_sym**2}
derived_values = {
    a_sym: derived_substitution[a_sym],
    **{
        symbol: sp.factor(value.subs(derived_substitution))
        for symbol, value in coefficient_solution.items()
    },
}
print("Normalized coefficients:", derived_values)
print(
    "V_k LaTeX:",
    sp.latex(2 * k_sym**2 / N_sym**2),
    "||A(x_k)||^2 +",
    sp.latex(4 * k_sym * L_sym / N_sym**2),
    "<A(x_k),x_k-x_0>",
)
# END DERIVATION

# BEGIN STEP
V_step = (
    2 * k_par** 2 / N_par** 2 * g_current** 2
    + 4 * k_par * L_par / N_par** 2 * g_current * (x_current - x_anchor)
)
V_step_next = 2 * (k_par + 1) ** 2 / N_par**2 * g_next**2 + 4 * (
    k_par + 1
) * L_par / N_par**2 * g_next * (x_next - x_anchor)
step_LHS = V_step_next - V_step
step_RHS = (
    4 * L_par * k_par * (k_par + 1) / N_par**2 * mon_step
    + 2 * (k_par + 1) ** 2 / N_par**2 * lip_step
)
step_diff = step_LHS - step_RHS
step_parameters: dict[str, Any] = {"k": k_sym, "N": N_sym, "L_local": L_sym}
pm_step = pf.ExpressionManager(ctx_step, resolve_parameters=step_parameters)
step_verified = verify_symbolic_identity("Step", step_diff, pm_step)
# END STEP

# BEGIN BASE
ctx_base = pf.PEPContext("symbolic_feg_base").set_as_current()
A_base = pf.LipschitzMonotoneOperator(is_basis=True, tags=["A_{base}"], L=L_par)
x_base0 = pf.Vector(is_basis=True, tags=["x_{0}", "x_{1/2}"])
g_base0 = A_base(x_base0)
x_base1 = x_base0 - g_base0 / L_par
x_base1.add_tag("x_{1}")
g_base1 = A_base(x_base1)
base_lip = (g_base1 - g_base0) ** 2 - L_par**2 * (x_base1 - x_base0) ** 2
base_LHS = 2 / N_par**2 * g_base1**2 + 4 * L_par / N_par**2 * g_base1 * (
    x_base1 - x_base0
)
base_RHS = 2 / N_par**2 * base_lip
base_diff = base_LHS - base_RHS
base_parameters: dict[str, Any] = {"N": N_sym, "L_local": L_sym}
pm_base = pf.ExpressionManager(ctx_base, resolve_parameters=base_parameters)
base_verified = verify_symbolic_identity("Base", base_diff, pm_base)
# END BASE

# BEGIN BOUNDARY
ctx_boundary = pf.PEPContext("symbolic_feg_boundary").set_as_current()
A_boundary = pf.LipschitzMonotoneOperator(is_basis=True, tags=["A_{boundary}"], L=L_par)
x_bound0 = pf.Vector(is_basis=True, tags=["x_{0}"])
x_boundN = pf.Vector(is_basis=True, tags=["x_{N}"])
x_boundstar = A_boundary.set_zero_point("x_{star}")
g_boundN = A_boundary(x_boundN)
R_par = pf.Parameter("R_local")
R_sym = sp.Symbol("R", nonnegative=True)
V_terminal = 2 * g_boundN**2 + 4 * L_par / N_par * g_boundN * (x_boundN - x_bound0)
initial_residual = (x_bound0 - x_boundstar) ** 2 - R_par**2
terminal_mon = -(x_boundN - x_boundstar) * g_boundN
terminal_square = (g_boundN - 2 * L_par / N_par * (x_bound0 - x_boundstar)) ** 2
boundary_LHS = g_boundN**2 - 4 * L_par**2 * R_par**2 / N_par**2
boundary_RHS = (
    V_terminal
    + 4 * L_par**2 / N_par**2 * initial_residual
    + 4 * L_par / N_par * terminal_mon
    - terminal_square
)
boundary_diff = boundary_LHS - boundary_RHS
boundary_parameters: dict[str, Any] = {"N": N_sym, "L_local": L_sym, "R_local": R_sym}
pm_boundary = pf.ExpressionManager(ctx_boundary, resolve_parameters=boundary_parameters)
boundary_verified = verify_symbolic_identity("Boundary", boundary_diff, pm_boundary)
# END BOUNDARY

# BEGIN SIGNS
sign_coefficients = {
    "monotonicity": 4 * L_sym * k_sym * (k_sym + 1) / N_sym**2,
    "Lipschitz": 2 * (k_sym + 1) ** 2 / N_sym**2,
    "base": 2 / N_sym**2,
    "initial": 4 * L_sym**2 / N_sym**2,
    "terminal": 4 * L_sym / N_sym,
}
assert all(value.is_positive is True for value in sign_coefficients.values())
assert (L_sym * N_sym * k_sym * (k_sym + 1)).is_nonzero is True
print("All active multipliers positive for L>0, N>=1, k>=1; R>=0.")
print("Step applies for 1<=k<N; N=1 uses only the base and terminal identities.")
print(
    "Every residual is nonpositive, the square is nonnegative, V_N<=V_0=0, hence ||A(x_N)||²<=4L²R²/N²."
)
# END SIGNS

result = {
    "step": step_verified,
    "base": base_verified,
    "boundary": boundary_verified,
    "signs": True,
    "domain": True,
    "normalization": True,
    "coefficient_solution": {
        str(key): str(value) for key, value in coefficient_solution.items()
    },
    "derived_coefficients": {
        str(key): str(value) for key, value in derived_values.items()
    },
    "sign_coefficients": {key: str(value) for key, value in sign_coefficients.items()},
}
Path("supplementary/b5-symbolic-results.json").write_text(json.dumps(result, indent=2))
print(json.dumps(result))
