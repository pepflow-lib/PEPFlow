# Exact local PGM identities; this source is included visibly in the notebook.
from typing import Any

import numpy as np
import sympy as sp

import pepflow as pf

k_sym, N_sym = sp.symbols("k N", integer=True)
L_sym = sp.Symbol("L", positive=True)
KP, NP, LP = pf.Parameter("k_proof"), pf.Parameter("N_proof"), pf.Parameter("L_proof")
symbolic_parameters: dict[str, Any] = {
    "k_proof": k_sym,
    "N_proof": N_sym,
    "L_proof": L_sym,
}


def residual_f(fun, u, v):
    return (
        fun(v)
        - fun(u)
        + fun.grad(v) * (u - v)
        + (fun.grad(u) - fun.grad(v)) ** 2 / (2 * LP)
    )


def residual_g(fun, u, v):
    return fun(v) - fun(u) + fun.grad(v) * (u - v)


def supplied_piece(fun, convex, xprev, xnext, xstar, i):
    ap, ai, ast = fun.grad(xprev), fun.grad(xnext), fun.grad(xstar)
    si = convex.grad(xnext)
    c1 = NP / ((2 * NP + 1 - i) * (2 * NP - i) * LP)
    u1 = i / (2 * NP) * ai + (2 * NP - i) / (2 * NP) * ap - ast
    c2 = (
        (i - 1) / (2 * NP - i) * (2 * NP + 2) / (2 * NP + 1)
        + 2 * NP / ((2 * NP - i) ** 2 * (2 * NP + 1))
    ) / (2 * LP)
    u2 = ap + si - LP / (2 * NP + 1 - i) * (xprev - xstar)
    c3 = i / (2 * NP + 1 - i) * (2 * NP) / (2 * NP + 1) / (2 * LP)
    u3 = (
        (2 * NP + 1) / (2 * NP) * (ai + si)
        - (ap + si) / (2 * NP)
        - LP / (2 * NP - i) * (xnext - xstar)
    )
    return c1 * u1**2 + c2 * u2**2 + c3 * u3**2


def analytic_potential(fun, convex, x, xstar, r0, index):
    r = x - xstar
    a, ast = fun.grad(x), fun.grad(xstar)
    return (
        -LP / (4 * NP) * r0**2
        + LP * (NP - index) / (2 * NP - index) ** 2 * r**2
        + (a - ast) ** 2 / (2 * LP * (2 * NP - index))
        - r * a / (2 * NP - index)
        + (index + 1) / (2 * NP - index) * (fun(x) - fun(xstar))
        + index / (2 * NP - index) * (convex(x) - convex(xstar))
    )


def symbolic_components(expression, manager):
    evaluated = manager.eval_scalar(expression, sympy_mode=True)
    gram = sp.Matrix(evaluated.inner_prod_coords).applyfunc(sp.cancel)
    functions = sp.Matrix(list(evaluated.func_coords)).applyfunc(sp.cancel)
    offset = sp.cancel(evaluated.offset)
    return gram, functions, offset


def verify_identity(label, expression, context, parameters):
    manager = pf.ExpressionManager(context, resolve_parameters=parameters)
    gram, functions, offset = symbolic_components(expression, manager)
    passed = all(value == 0 for value in [*gram, *functions, offset])
    print(
        label,
        "exact zero:",
        passed,
        "function residual:",
        functions.T,
        "offset:",
        offset,
    )
    pf.pprint_labeled_matrix(
        np.asarray(gram, dtype=object),
        [str(v) for v in context.basis_vectors()],
        [str(v) for v in context.basis_vectors()],
    )
    assert passed, (label, gram, functions, offset)
    return True


# STEP
ctx_step = pf.PEPContext("pgm_symbolic_step").set_as_current()
f_step = pf.SmoothConvexFunction(is_basis=True, tags=["f_{step}"], L=LP)
g_step = pf.ConvexFunction(is_basis=True, tags=["g_{step}"])
xstar_step = (f_step + g_step).set_stationary_point("x_{star,step}")
r0_step = pf.Vector(is_basis=True, tags=["r_{0,step}"])
x_step = pf.Vector(is_basis=True, tags=["x_{k}"])
f_step.grad(x_step)
g_step(x_step)
xn_step = g_step.prox(x_step - f_step.grad(x_step) / LP, 1 / LP, tag="x_{k+1}")
f_step.grad(xn_step)
step_LHS = analytic_potential(
    f_step, g_step, xn_step, xstar_step, r0_step, KP + 1
) - analytic_potential(f_step, g_step, x_step, xstar_step, r0_step, KP)
step_RHS = (
    (2 * NP + 1)
    / ((2 * NP - KP - 1) * (2 * NP - KP))
    * residual_f(f_step, xstar_step, xn_step)
    + (KP + 1) / (2 * NP - KP) * residual_f(f_step, x_step, xn_step)
    + 2
    * NP
    / ((2 * NP - KP - 1) * (2 * NP - KP))
    * residual_g(g_step, xstar_step, xn_step)
    + KP / (2 * NP - KP) * residual_g(g_step, x_step, xn_step)
    - supplied_piece(f_step, g_step, x_step, xn_step, xstar_step, KP + 1)
)
step_diff = step_LHS - step_RHS
step_verified = verify_identity(
    "Interior step, 1<=k<=N-2", step_diff, ctx_step, symbolic_parameters
)
# BASE
ctx_base = pf.PEPContext("pgm_symbolic_base").set_as_current()
f_base = pf.SmoothConvexFunction(is_basis=True, tags=["f_{base}"], L=LP)
g_base = pf.ConvexFunction(is_basis=True, tags=["g_{base}"])
xstar_base = (f_base + g_base).set_stationary_point("x_{star,base}")
x0_base = pf.Vector(is_basis=True, tags=["x_{0,base}"])
f_base.grad(x0_base)
x1_base = g_base.prox(x0_base - f_base.grad(x0_base) / LP, 1 / LP, tag="x_{1,base}")
f_base.grad(x1_base)
base_LHS = analytic_potential(
    f_base, g_base, x1_base, xstar_base, x0_base - xstar_base, sp.S(1)
)
base_RHS = (
    residual_f(f_base, xstar_base, x0_base) / (2 * NP)
    + (2 * NP + 1) / ((2 * NP - 1) * 2 * NP) * residual_f(f_base, xstar_base, x1_base)
    + residual_f(f_base, x0_base, x1_base) / (2 * NP)
    + residual_g(g_base, xstar_base, x1_base) / (2 * NP - 1)
    - supplied_piece(f_base, g_base, x0_base, x1_base, xstar_base, sp.S(1))
)
base_diff = base_LHS - base_RHS
base_verified = verify_identity("Base, N>=2", base_diff, ctx_base, symbolic_parameters)
# BOUNDARY
ctx_terminal = pf.PEPContext("pgm_symbolic_terminal").set_as_current()
f_terminal = pf.SmoothConvexFunction(is_basis=True, tags=["f_{terminal}"], L=LP)
g_terminal = pf.ConvexFunction(is_basis=True, tags=["g_{terminal}"])
xstar_terminal = (f_terminal + g_terminal).set_stationary_point("x_{star,terminal}")
r0_terminal = pf.Vector(is_basis=True, tags=["r_{0,terminal}"])
xp_terminal = pf.Vector(is_basis=True, tags=["x_{N-1}"])
f_terminal.grad(xp_terminal)
g_terminal(xp_terminal)
xn_terminal = g_terminal.prox(
    xp_terminal - f_terminal.grad(xp_terminal) / LP, 1 / LP, tag="x_{N}"
)
f_terminal.grad(xn_terminal)
V_terminal = (
    f_terminal(xn_terminal)
    - f_terminal(xstar_terminal)
    + g_terminal(xn_terminal)
    - g_terminal(xstar_terminal)
    - LP / (4 * NP) * r0_terminal**2
)
terminal_LHS = V_terminal - analytic_potential(
    f_terminal, g_terminal, xp_terminal, xstar_terminal, r0_terminal, NP - 1
)
terminal_RHS = (
    residual_f(f_terminal, xstar_terminal, xn_terminal) / (NP + 1)
    + NP / (NP + 1) * residual_f(f_terminal, xp_terminal, xn_terminal)
    + 2 / (NP + 1) * residual_g(g_terminal, xstar_terminal, xn_terminal)
    + (NP - 1) / (NP + 1) * residual_g(g_terminal, xp_terminal, xn_terminal)
    - supplied_piece(
        f_terminal, g_terminal, xp_terminal, xn_terminal, xstar_terminal, NP
    )
)
terminal_diff = terminal_LHS - terminal_RHS
boundary_verified = verify_identity(
    "Terminal, N>=2", terminal_diff, ctx_terminal, symbolic_parameters
)
# N1
ctx_single = pf.PEPContext("pgm_symbolic_single").set_as_current()
f_single = pf.SmoothConvexFunction(is_basis=True, tags=["f_{single}"], L=LP)
g_single = pf.ConvexFunction(is_basis=True, tags=["g_{single}"])
xstar_single = (f_single + g_single).set_stationary_point("x_{star,single}")
x0_single = pf.Vector(is_basis=True, tags=["x_{0,single}"])
f_single.grad(x0_single)
x1_single = g_single.prox(
    x0_single - f_single.grad(x0_single) / LP, 1 / LP, tag="x_{1,single}"
)
f_single.grad(x1_single)
single_LHS = (
    f_single(x1_single)
    - f_single(xstar_single)
    + g_single(x1_single)
    - g_single(xstar_single)
    - LP / sp.S(4) * (x0_single - xstar_single) ** 2
)
single_RHS = (
    sp.Rational(1, 2) * residual_f(f_single, xstar_single, x0_single)
    + sp.Rational(1, 2) * residual_f(f_single, xstar_single, x1_single)
    + sp.Rational(1, 2) * residual_f(f_single, x0_single, x1_single)
    + residual_g(g_single, xstar_single, x1_single)
    - supplied_piece(f_single, g_single, x0_single, x1_single, xstar_single, sp.S(1))
)
single_diff = single_LHS - single_RHS
single_verified = verify_identity(
    "Single iteration, N=1",
    single_diff,
    ctx_single,
    {**symbolic_parameters, "N_proof": sp.S(1)},
)
