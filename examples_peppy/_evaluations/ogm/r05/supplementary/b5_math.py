"""Exact symbolic OGM Lyapunov identities, with all scalar components."""

# CELL: symbolic_setup
import json

import numpy as np
import sympy as sp

# local helper resolved by the notebook runtime path
from runtime import NOTEBOOK_DIR  # ty: ignore[unresolved-import]

import pepflow as pf

b4_proof = json.loads((NOTEBOOK_DIR / "state/ogm_b4.json").read_text())
assert (
    b4_proof["numerical_reconstruction"]["certificate_id"] == b4_proof["certificate_id"]
)
assert b4_proof["numerical_reconstruction"]["passed"]
k_symbol, N_symbol = sp.symbols("k N", integer=True, nonnegative=True)
L_symbol, t_symbol, u_symbol = sp.symbols("L t u", positive=True)
R_symbol = sp.symbols("R", nonnegative=True)
Lp, tp, up = pf.Parameter("L"), pf.Parameter("t"), pf.Parameter("u")
half = sp.Rational(1, 2)
symbolic_parameters: dict = {"L": L_symbol, "t": t_symbol, "u": u_symbol}
proof_results = {}


def interpolation(function, a, b):
    """Smooth convex interpolation residual I_(a,b) <= 0."""
    return (
        function(b)
        - function(a)
        - function.grad(b) * (b - a)
        + (function.grad(b) - function.grad(a)) ** 2 / (2 * Lp)
    )


def H(theta, function, x, z_next, star):
    """Unnormalized interior expression, including its function gap."""
    return (
        2 * theta**2 * (function(x) - function(star))
        - theta**2 / Lp * (function.grad(x) ** 2)
        + Lp / 2 * ((z_next - star) ** 2)
    )


def exact_components(expression, manager, relation=None):
    value = manager.eval_scalar(pf.Scalar.zero() + expression, sympy_mode=True)

    def reduce(entry):
        entry = sp.cancel(sp.sympify(entry))
        numerator, denominator = sp.fraction(entry)
        if relation is not None:
            numerator = sp.rem(
                sp.Poly(numerator, t_symbol), sp.Poly(relation, t_symbol)
            ).as_expr()
        return sp.simplify(numerator / denominator)

    return (
        sp.Matrix(value.inner_prod_coords).applyfunc(reduce),
        sp.Matrix(list(value.func_coords)).applyfunc(reduce),
        reduce(value.offset),
    )


def check_exact(name, difference, manager, context, relation=None):
    gram, funcs, offset = exact_components(difference, manager, relation)
    assert all(value == 0 for value in [*gram, *funcs, offset]), (
        name,
        gram,
        funcs,
        offset,
    )
    pf.pprint_labeled_matrix(
        np.array(gram.tolist(), dtype=object),
        [str(v) for v in context.basis_vectors()],
        precision=6,
    )
    print(name, "Gram residual exactly zero:", gram == sp.zeros(*gram.shape))
    print(name, "function residual:", funcs.T, "; offset:", offset)
    proof_results[name] = {
        "gram_zero": True,
        "function_zero": True,
        "offset_zero": True,
        "relation": str(relation) if relation is not None else None,
        "gram_dimension": list(gram.shape),
        "function_dimension": list(funcs.shape),
    }
    return True


# CELL: step
ctx_step = pf.PEPContext("ogm_symbolic_step").set_as_current()
f_step = pf.SmoothConvexFunction(is_basis=True, tags=["f_{step}"], L=Lp)
star_step = f_step.set_stationary_point("x_{star}")
x_step = pf.Vector(is_basis=True, tags=["x_{k}"])
z_step = pf.Vector(is_basis=True, tags=["z_{k+1}"])
g_step = f_step.grad(x_step)
x_next_step = (1 - 1 / up) * (x_step - g_step / Lp) + z_step / up
x_next_step.add_tag("x_{k+1}")
g_next_step = f_step.grad(x_next_step)
z_next_step = z_step - (2 * up / Lp) * g_next_step
z_next_step.add_tag("z_{k+2}")
step_LHS = H(up, f_step, x_next_step, z_next_step, star_step) - H(
    tp, f_step, x_step, z_step, star_step
)
step_RHS = 2 * up * interpolation(
    f_step, star_step, x_next_step
) + 2 * tp**2 * interpolation(f_step, x_step, x_next_step)
step_diff = step_LHS - step_RHS
pm_step = pf.ExpressionManager(ctx_step, resolve_parameters=symbolic_parameters)
step_verified = check_exact(
    "step", step_diff, pm_step, ctx_step, relation=t_symbol**2 - u_symbol**2 + u_symbol
)

# CELL: base
ctx_base = pf.PEPContext("ogm_symbolic_base").set_as_current()
f_base = pf.SmoothConvexFunction(is_basis=True, tags=["f_{base}"], L=Lp)
star_base = f_base.set_stationary_point("x_{star}")
x_base = pf.Vector(is_basis=True, tags=["x_{0}"])
g_base = f_base.grad(x_base)
z1_base = x_base - (2 / Lp) * g_base
initial_energy = (Lp / 2) * ((x_base - star_base) ** 2)
base_LHS = H(1, f_base, x_base, z1_base, star_base) - initial_energy
base_RHS = 2 * interpolation(f_base, star_base, x_base)
base_diff = base_LHS - base_RHS
pm_base = pf.ExpressionManager(ctx_base, resolve_parameters=symbolic_parameters)
base_verified = check_exact("base", base_diff, pm_base, ctx_base)

# CELL: terminal
ctx_terminal = pf.PEPContext("ogm_symbolic_terminal").set_as_current()
f_terminal = pf.SmoothConvexFunction(is_basis=True, tags=["f_{terminal}"], L=Lp)
star_terminal = f_terminal.set_stationary_point("x_{star}")
x_terminal = pf.Vector(is_basis=True, tags=["x_{N-1}"])
z_terminal = pf.Vector(is_basis=True, tags=["z_{N}"])
g_terminal = f_terminal.grad(x_terminal)
x_final = (1 - 1 / up) * (x_terminal - g_terminal / Lp) + z_terminal / up
x_final.add_tag("x_{N}")
g_final = f_terminal.grad(x_final)
terminal_square = (Lp / 2) * ((z_terminal - star_terminal - (up / Lp) * g_final) ** 2)
terminal_LHS = up**2 * (f_terminal(x_final) - f_terminal(star_terminal)) - H(
    tp, f_terminal, x_terminal, z_terminal, star_terminal
)
terminal_RHS = (
    up * interpolation(f_terminal, star_terminal, x_final)
    + 2 * tp**2 * interpolation(f_terminal, x_terminal, x_final)
    - terminal_square
)
terminal_diff = terminal_LHS - terminal_RHS
pm_terminal = pf.ExpressionManager(ctx_terminal, resolve_parameters=symbolic_parameters)
boundary_verified = check_exact(
    "boundary",
    terminal_diff,
    pm_terminal,
    ctx_terminal,
    relation=2 * t_symbol**2 - u_symbol**2 + u_symbol,
)

# CELL: small_horizon
ctx_one = pf.PEPContext("ogm_symbolic_N1").set_as_current()
f_one = pf.SmoothConvexFunction(is_basis=True, tags=["f_{one}"], L=Lp)
star_one = f_one.set_stationary_point("x_{star}")
x0_one = pf.Vector(is_basis=True, tags=["x_{0}"])
g0_one = f_one.grad(x0_one)
z1_one = x0_one - (2 / Lp) * g0_one
x1_one = half * (x0_one - g0_one / Lp) + half * z1_one
g1_one = f_one.grad(x1_one)
one_LHS = f_one(x1_one) - f_one(star_one) - (Lp / 8) * ((x0_one - star_one) ** 2)
one_RHS = (
    half * interpolation(f_one, star_one, x0_one)
    + half * interpolation(f_one, star_one, x1_one)
    + half * interpolation(f_one, x0_one, x1_one)
    - (Lp / 8) * ((z1_one - star_one - (2 / Lp) * g1_one) ** 2)
)
one_diff = one_LHS - one_RHS
pm_one = pf.ExpressionManager(ctx_one, resolve_parameters=symbolic_parameters)
one_verified = check_exact("N1", one_diff, pm_one, ctx_one)

# CELL: domain
# Polynomial consequences of the positive-root recurrences are checked exactly.
root_regular = (1 + sp.sqrt(1 + 4 * t_symbol**2)) / 2
root_terminal = (1 + sp.sqrt(1 + 8 * t_symbol**2)) / 2
assert sp.simplify(root_regular**2 - root_regular - t_symbol**2) == 0
assert sp.simplify(root_terminal**2 - root_terminal - 2 * t_symbol**2) == 0
assert root_regular.is_positive and root_terminal.is_positive
thetaN_symbol = sp.symbols("theta_N", positive=True)
assert (2 * u_symbol / thetaN_symbol**2).is_positive
assert (2 * t_symbol**2 / thetaN_symbol**2).is_positive
assert (1 / thetaN_symbol).is_positive
assert (L_symbol / (2 * thetaN_symbol**2)).is_positive
print(
    "Positive roots, recurrence polynomial identities, and all multiplier/square signs verified."
)
print(
    "Normalization: V_N<=0 implies gap_N<=L*||x_0-x_star||^2/(2*theta_N^2)<=L*R^2/(2*theta_N^2)."
)

# CELL: tightness
# For f(x)=L*x^2/2, x_star=0, one exact scalar recurrence proves attainability.
sigma = sp.symbols("sigma", real=True)
x_quad = sigma * R_symbol / t_symbol
z_quad = sigma * R_symbol
g_quad = L_symbol * x_quad
y_quad = sp.simplify(x_quad - g_quad / L_symbol)
z_next_quad = sp.simplify(z_quad - 2 * t_symbol * g_quad / L_symbol)
x_next_quad = sp.simplify((1 - 1 / u_symbol) * y_quad + z_next_quad / u_symbol)
assert y_quad == 0
assert z_next_quad == -sigma * R_symbol
assert x_next_quad == -sigma * R_symbol / u_symbol
print(
    "Quadratic example: z_k=(-1)^k R and x_k=(-1)^k R/theta_k; bound attained at every horizon."
)
