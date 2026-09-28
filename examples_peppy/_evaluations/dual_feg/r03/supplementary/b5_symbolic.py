"""Exact symbolic local, initial, terminal and normalized boundary proof."""
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "supplementary"))
import run_b1  # noqa: E402,F401
import numpy as np  # noqa: E402
import pepflow as pf  # noqa: E402
import sympy as sp  # noqa: E402

# PROOF_CODE_START
# SECTION: helpers
ell_sp = sp.Symbol("L", positive=True)
N_sp = sp.Symbol("N", integer=True, positive=True)
q_sp = sp.Symbol("q", integer=True, positive=True)
R_sp = sp.Symbol("R", nonnegative=True)
ell_p = pf.Parameter("L_cert")
N_p = pf.Parameter("N_cert")
m_p = pf.Parameter("m_cert")
R_p = pf.Parameter("R_cert")


def potential(p, z, g_final, anchor, remaining, horizon, lipschitz):
    return (-4 * lipschitz / horizon * (g_final * anchor)
            + 4 * lipschitz / remaining * (g_final * p)
            - 4 * (g_final * z)
            + 4 * lipschitz / remaining * (p * z) - 2 * z**2)


def symbolic_manager(context, parameter_values):
    return pf.ExpressionManager(context, resolve_parameters=parameter_values)


def verify_exact(name, difference, manager, context):
    evaluated = manager.eval_scalar(difference, sympy_mode=True)
    gram = sp.Matrix(evaluated.inner_prod_coords).applyfunc(sp.simplify)
    functions = [sp.simplify(x) for x in evaluated.func_coords]
    offset = sp.simplify(evaluated.offset)
    assert all(x == 0 for x in gram) and all(x == 0 for x in functions) and offset == 0
    print(name, "Gram/function/offset residuals are exactly zero")
    pf.pprint_labeled_matrix(np.asarray(gram.tolist(), dtype=object), [str(v) for v in context.basis_vectors()])
    print("Function residual:", functions, "offset:", offset)
    return {"gram_zero": True, "function_zero": True, "offset_zero": True,
            "dimension": gram.rows}


exact_checks = {}

# SECTION: step
ctx_step = pf.PEPContext("dual_feg_symbolic_step").set_as_current()
A_step = pf.LipschitzMonotoneOperator(is_basis=True, tags=["A_{step}"], L=ell_p)
x_step = pf.Vector(is_basis=True, tags=["x_{k}"])
z_step = pf.Vector(is_basis=True, tags=["z_{k}"])
xf_step = pf.Vector(is_basis=True, tags=["x_{N}"])
x0_step = pf.Vector(is_basis=True, tags=["x_{0}"])
g_step = A_step(x_step)
gf_step = A_step(xf_step)
y_step = (x_step - z_step / ell_p - g_step / ell_p).add_tag("x_{k+1/2}")
h_step = A_step(y_step)
xp_step = (y_step - (m_p - 1) / m_p * (h_step - g_step) / ell_p).add_tag("x_{k+1}")
zp_step = ((m_p - 1) / m_p * z_step - h_step / m_p).add_tag("z_{k+1}")
V_step = potential(x_step-xf_step, z_step, gf_step, x0_step-xf_step, m_p, N_p, ell_p)
Vp_step = potential(xp_step-xf_step, zp_step, gf_step, x0_step-xf_step, m_p-1, N_p, ell_p)
M_step = -(xf_step-y_step) * (gf_step-h_step)
Q_step = (g_step-h_step)**2 - ell_p**2 * (x_step-y_step)**2
LHS_step = Vp_step - V_step
RHS_step = 4*ell_p/(m_p*(m_p-1))*M_step + 2/m_p**2*Q_step
diff_step = LHS_step - RHS_step
# m=q+1 ranges over all integers >=2; m=N-k in the actual recurrence.
pm_step = symbolic_manager(ctx_step, {"L_cert": ell_sp, "N_cert": N_sp, "m_cert": q_sp+1})
exact_checks["step"] = verify_exact("Interior step", diff_step, pm_step, ctx_step)

# SECTION: base
ctx_base = pf.PEPContext("dual_feg_symbolic_base").set_as_current()
A_base = pf.LipschitzMonotoneOperator(is_basis=True, tags=["A_{base}"], L=ell_p)
x0_base = pf.Vector(is_basis=True, tags=["x_{0}"])
xf_base = pf.Vector(is_basis=True, tags=["x_{N}"])
g0_base, gf_base = A_base(x0_base), A_base(xf_base)
z0_base = pf.Vector.zero()
y0_base = (x0_base-g0_base/ell_p).add_tag("x_{1/2}")
h0_base = A_base(y0_base)
x1_base = y0_base-(N_p-1)/N_p*(h0_base-g0_base)/ell_p
z1_base = -h0_base/N_p
V0_base = potential(x0_base-xf_base, z0_base, gf_base, x0_base-xf_base, N_p, N_p, ell_p)
V1_base = potential(x1_base-xf_base, z1_base, gf_base, x0_base-xf_base, N_p-1, N_p, ell_p)
M0_base = -(xf_base-y0_base)*(gf_base-h0_base)
Q0_base = (g0_base-h0_base)**2-ell_p**2*(x0_base-y0_base)**2
LHS_base = V1_base - V0_base
RHS_base = 4*ell_p/(N_p*(N_p-1))*M0_base+2/N_p**2*Q0_base
diff_base = LHS_base-RHS_base
# Here N=q+1 ranges over every horizon >=2.
pm_base = symbolic_manager(ctx_base, {"L_cert": ell_sp, "N_cert": q_sp+1})
exact_checks["base_zero"] = verify_exact("Initial potential", V0_base, pm_base, ctx_base)
exact_checks["base"] = verify_exact("Initial step N>=2", diff_base, pm_base, ctx_base)

# SECTION: terminal
ctx_terminal = pf.PEPContext("dual_feg_symbolic_terminal").set_as_current()
A_terminal = pf.LipschitzMonotoneOperator(is_basis=True, tags=["A_{terminal}"], L=ell_p)
x_terminal = pf.Vector(is_basis=True, tags=["x_{N-1}"])
z_terminal = pf.Vector(is_basis=True, tags=["z_{N-1}"])
x0_terminal = pf.Vector(is_basis=True, tags=["x_{0}"])
g_terminal = A_terminal(x_terminal)
xf_terminal = (x_terminal-z_terminal/ell_p-g_terminal/ell_p).add_tag("x_{N}")
gf_terminal = A_terminal(xf_terminal)
Vpre_terminal = potential(x_terminal-xf_terminal, z_terminal, gf_terminal, x0_terminal-xf_terminal, sp.S.One, N_p, ell_p)
VN_terminal = 2*gf_terminal**2-4*ell_p/N_p*(gf_terminal*(x0_terminal-xf_terminal))
Q_terminal = (g_terminal-gf_terminal)**2-ell_p**2*(x_terminal-xf_terminal)**2
LHS_terminal = VN_terminal-Vpre_terminal
RHS_terminal = 2*Q_terminal
diff_terminal = LHS_terminal-RHS_terminal
pm_terminal = symbolic_manager(ctx_terminal, {"L_cert": ell_sp, "N_cert": N_sp})
exact_checks["terminal_step"] = verify_exact("Terminal step", diff_terminal, pm_terminal, ctx_terminal)

# SECTION: single
ctx_single = pf.PEPContext("dual_feg_symbolic_N1").set_as_current()
A_single = pf.LipschitzMonotoneOperator(is_basis=True, tags=["A_{single}"], L=ell_p)
x0_single = pf.Vector(is_basis=True, tags=["x_{0}"])
g0_single = A_single(x0_single)
x1_single = (x0_single-g0_single/ell_p).add_tag("x_{1}")
g1_single = A_single(x1_single)
V1_single = 2*g1_single**2-4*ell_p*(g1_single*(x0_single-x1_single))
Q_single = (g0_single-g1_single)**2-ell_p**2*(x0_single-x1_single)**2
LHS_single = V1_single
RHS_single = 2*Q_single
diff_single = LHS_single-RHS_single
pm_single = symbolic_manager(ctx_single, {"L_cert": ell_sp})
exact_checks["N1"] = verify_exact("N=1 exceptional horizon", diff_single, pm_single, ctx_single)

# SECTION: boundary
ctx_boundary = pf.PEPContext("dual_feg_symbolic_boundary").set_as_current()
A_boundary = pf.LipschitzMonotoneOperator(is_basis=True, tags=["A_{boundary}"], L=ell_p)
x0_boundary = pf.Vector(is_basis=True, tags=["x_{0}"])
xf_boundary = pf.Vector(is_basis=True, tags=["x_{N}"])
xs_boundary = A_boundary.set_zero_point("x_{star}")
gf_boundary = A_boundary(xf_boundary)
VN_boundary = 2*gf_boundary**2-4*ell_p/N_p*(gf_boundary*(x0_boundary-xf_boundary))
Mstar_boundary = -(xf_boundary-xs_boundary)*gf_boundary
S_boundary = (2*ell_p/N_p*(x0_boundary-xs_boundary)-gf_boundary)**2
initial_boundary = (x0_boundary-xs_boundary)**2-R_p**2
LHS_boundary = gf_boundary**2-4*ell_p**2*R_p**2/N_p**2
RHS_boundary = VN_boundary+4*ell_p/N_p*Mstar_boundary-S_boundary+4*ell_p**2/N_p**2*initial_boundary
diff_boundary = LHS_boundary-RHS_boundary
pm_boundary = symbolic_manager(ctx_boundary, {"L_cert": ell_sp, "N_cert": N_sp, "R_cert": R_sp})
exact_checks["boundary"] = verify_exact("Metric and radius normalization", diff_boundary, pm_boundary, ctx_boundary)
# PROOF_CODE_END

(ROOT / "supplementary/b5-exact-checks.json").write_text(json.dumps(exact_checks, indent=2))
print("ALL EXACT COMPONENT IDENTITIES PASSED")
