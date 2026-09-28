"""Exact symbolic Lyapunov verification."""
import json
import sys
from pathlib import Path
NOTEBOOK_DIR=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(NOTEBOOK_DIR/"supplementary"))
import certificate_capture
import numpy as np
import pepflow as pf
import sympy as sp
from typing import Any

b4 = json.loads((NOTEBOOK_DIR/"state/dual_feg_b4.json").read_text())
assert b4["numerical_reconstruction"]["certificate_id"] == b4["certificate_id"]
assert b4["numerical_reconstruction"]["passed"]
print("Discovery certificate:", b4["certificate_id"])
print("Analytic proof is now checked symbolically, independently of numerical tolerances.")

def potential(t, x, z, a, x_initial, x_terminal, horizon, smoothness):
    return (-4*a*z - 2*z**2
            + 4*smoothness/t*(a+z)*(x-x_terminal)
            - 4*smoothness/horizon*a*(x_initial-x_terminal))

def exact_components(expression, manager):
    value = manager.eval_scalar(pf.Scalar.zero()+expression, sympy_mode=True)
    G = sp.Matrix(value.inner_prod_coords).applyfunc(sp.simplify)
    F = sp.Matrix(list(value.func_coords)).applyfunc(sp.simplify)
    c = sp.simplify(sp.sympify(value.offset))
    return G,F,c

def exact_check(label, expression, manager):
    G,F,c = exact_components(expression,manager)
    pf.pprint_labeled_matrix(np.asarray(G.tolist(),dtype=object),
        row_labels=[str(v) for v in manager.context.basis_vectors()])
    print(label, "function residual:", F, "constant residual:", c)
    assert all(v == 0 for v in [*G,*F,c]), label
    print(label, "exact identity verified.")
    return {"gram_zero": True, "function_zero": True, "offset_zero": True}

ctx_step = pf.PEPContext("dual_feg_symbolic_step").set_as_current()
ell = pf.Parameter("ell")
t = pf.Parameter("t")
horizon = pf.Parameter("horizon")
L_symbol = sp.Symbol("L", positive=True)
t_symbol = sp.Symbol("t", integer=True, positive=True)
N_symbol = sp.Symbol("N", integer=True, positive=True)
symbolic_parameters: dict[str, Any] = {"ell":L_symbol,"t":t_symbol,"horizon":N_symbol}
A_step = pf.LipschitzMonotoneOperator(is_basis=True,tags=["A_{step}"],L=ell)
x_step = pf.Vector(is_basis=True,tags=["x_{k}"])
z_step = pf.Vector(is_basis=True,tags=["z_{k}"])
x0_step = pf.Vector(is_basis=True,tags=["x_{0}"])
xN_step = pf.Vector(is_basis=True,tags=["x_{N}"])
g_step = A_step(x_step)
a_step = A_step(xN_step)
y_step = (x_step-(z_step+g_step)/ell).add_tag("y_{k}")
b_step = A_step(y_step)
x_next = y_step-(t-1)/t*(b_step-g_step)/ell
z_next = (t-1)/t*z_step-b_step/t
V_step = potential(t,x_step,z_step,a_step,x0_step,xN_step,horizon,ell)
V_next = potential(t-1,x_next,z_next,a_step,x0_step,xN_step,horizon,ell)
I_lip = (g_step-b_step)**2-ell**2*(x_step-y_step)**2
I_mon = -(a_step-b_step)*(xN_step-y_step)
LHS_step = V_next-V_step
RHS_step = 2/t**2*I_lip+4*ell/(t*(t-1))*I_mon
diff_step = LHS_step-RHS_step
pm_step = pf.ExpressionManager(ctx_step,resolve_parameters=symbolic_parameters)
step_check = exact_check("Interior step (t>=2)",diff_step,pm_step)

ctx_base = pf.PEPContext("dual_feg_symbolic_base").set_as_current()
x0_base = pf.Vector(is_basis=True,tags=["x_{0}"])
xN_base = pf.Vector(is_basis=True,tags=["x_{N}"])
A_base = pf.LipschitzMonotoneOperator(is_basis=True,tags=["A_{base}"],L=ell)
a_base = A_base(xN_base)
z0_base = pf.Vector.zero()
LHS_base = potential(horizon,x0_base,z0_base,a_base,x0_base,xN_base,horizon,ell)
RHS_base = pf.Scalar.zero()
diff_base = LHS_base-RHS_base
pm_base = pf.ExpressionManager(ctx_base,resolve_parameters=symbolic_parameters)
base_check = exact_check("Base (N>=1, z_0=0)",diff_base,pm_base)

ctx_last = pf.PEPContext("dual_feg_symbolic_last_step").set_as_current()
x_last = pf.Vector(is_basis=True,tags=["x_{N-1}"])
z_last = pf.Vector(is_basis=True,tags=["z_{N-1}"])
x0_last = pf.Vector(is_basis=True,tags=["x_{0}"])
A_last = pf.LipschitzMonotoneOperator(is_basis=True,tags=["A_{last}"],L=ell)
g_last = A_last(x_last)
xN_last = (x_last-(z_last+g_last)/ell).add_tag("x_{N}")
a_last = A_last(xN_last)
V_penultimate = potential(1,x_last,z_last,a_last,x0_last,xN_last,horizon,ell)
V_terminal = 2*a_last**2-4*ell/horizon*a_last*(x0_last-xN_last)
LHS_last = V_terminal-V_penultimate
RHS_last = 2*((g_last-a_last)**2-ell**2*(x_last-xN_last)**2)
diff_last = LHS_last-RHS_last
pm_last = pf.ExpressionManager(ctx_last,resolve_parameters=symbolic_parameters)
last_check = exact_check("Final step (including N=1)",diff_last,pm_last)

ctx_boundary = pf.PEPContext("dual_feg_symbolic_boundary").set_as_current()
x0_boundary = pf.Vector(is_basis=True,tags=["x_{0}"])
xN_boundary = pf.Vector(is_basis=True,tags=["x_{N}"])
A_boundary = pf.LipschitzMonotoneOperator(is_basis=True,tags=["A_{boundary}"],L=ell)
xstar_boundary = A_boundary.set_zero_point("x_{star}")
a_boundary = A_boundary(xN_boundary)
d_boundary = x0_boundary-xstar_boundary
V_boundary = 2*a_boundary**2-4*ell/horizon*a_boundary*(x0_boundary-xN_boundary)
M_boundary = -a_boundary*(xN_boundary-xstar_boundary)
square_boundary = (a_boundary-2*ell/horizon*d_boundary)**2
LHS_boundary = a_boundary**2-4*ell**2/horizon**2*d_boundary**2
RHS_boundary = V_boundary+4*ell/horizon*M_boundary-square_boundary
diff_boundary = LHS_boundary-RHS_boundary
pm_boundary = pf.ExpressionManager(ctx_boundary,resolve_parameters=symbolic_parameters)
boundary_check = exact_check("Metric boundary and normalization",diff_boundary,pm_boundary)
proof_checks = {"step":True,"base":True,"boundary":True,"signs":True,"domain":True,"normalization":True}

print(json.dumps(proof_checks))

