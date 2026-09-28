# This saved notebook fragment shares its caller's execution namespace.
# These names are supplied by the notebook cells or serialized proof source.
# ty: ignore[unresolved-reference]
# ruff: noqa: F821

ctx_last = pf.PEPContext("dual_feg_exact_last").set_as_current()
xl = pf.Vector(is_basis=True, tags=["x_{N-1}"])
zl = pf.Vector(is_basis=True, tags=["z_{N-1}"])
anchor_l = pf.Vector(is_basis=True, tags=["x_{0}"])
A_last = pf.LipschitzMonotoneOperator(is_basis=True, tags=["A_{last}"], L=Lp)
ul = A_last(xl)
nl = (xl - (zl + ul) / Lp).add_tag("x_{N}")
Gl = A_last(nl)
V_before = V_closed(1, zl, xl, anchor_l, nl, Gl, Lp, Np)
V_terminal = 2 * Gl**2 - 4 * Lp / Np * (anchor_l - nl) * Gl
LHS = V_terminal - V_before
RHS = 2 * ((ul - Gl) ** 2 - Lp**2 * (xl - nl) ** 2)
pm_last = pf.ExpressionManager(ctx_last, resolve_parameters=base_mapping)
last_step_check = verify_exact("Last step", LHS, RHS, pm_last)
# N=1 is verified in its actual initial/terminal context rather than substituting t=0.
ctx_one = pf.PEPContext("dual_feg_exact_N1").set_as_current()
xo = pf.Vector(is_basis=True, tags=["x_{0}"])
A_one = pf.LipschitzMonotoneOperator(is_basis=True, tags=["A_{one}"], L=Lp)
uo = A_one(xo)
no = (xo - uo / Lp).add_tag("x_{1}")
Go = A_one(no)
LHS = 2 * Go**2 - 4 * Lp * (xo - no) * Go
RHS = 2 * ((uo - Go) ** 2 - Lp**2 * (xo - no) ** 2)
one_mapping: dict[str, Any] = {"L_exact": Ls}
pm_one = pf.ExpressionManager(ctx_one, resolve_parameters=one_mapping)
small_horizon_check = verify_exact("N=1 direct endpoint", LHS, RHS, pm_one)
proof_checks["last_step"] = last_step_check
proof_checks["small_horizon"] = small_horizon_check
