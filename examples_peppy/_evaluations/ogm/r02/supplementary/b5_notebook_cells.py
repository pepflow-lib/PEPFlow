"""Exact, visible PEPFlow symbolic proof of the OGM Lyapunov identities."""

LOAD = '''b4 = json.loads((notebook_dir / "state/ogm_b4.json").read_text())
assert b4["certificate_id"] == b2["certificate_id"] == b3["certificate_id"]
assert b4["numerical_reconstruction"]["certificate_id"] == b4["certificate_id"]
assert b4["numerical_reconstruction"]["required_indices"] == list(range(N+1))
print("Selected B4 basis and full-expression reconstruction are rechecked by the preceding executed cells.")
print("Known coefficients are candidates entering this block; no unknown coefficient is silently set to zero.")
'''

HELPERS = '''from typing import Any

proof_results: dict[str,dict[str,Any]] = {}
L_exact, T_exact, a_exact, b_exact = sp.symbols("L T a b", positive=True)
k_exact, N_exact = sp.symbols("k N", integer=True, nonnegative=True)

def exact_check(name, expression, manager, context):
    evaluated = manager.eval_scalar(expression, sympy_mode=True)
    gram = sp.Matrix(evaluated.inner_prod_coords).applyfunc(sp.simplify)
    functions = sp.Matrix(list(evaluated.func_coords)).applyfunc(sp.simplify)
    offset = sp.simplify(evaluated.offset)
    assert all(term == 0 for term in [*gram,*functions,offset]), (name,gram,functions,offset)
    labels = [str(v) for v in context.basis_vectors()]
    pf.pprint_labeled_matrix(np.asarray(gram.tolist(),dtype=object),labels)
    print(name,"function-value residual:",functions.T,"constant residual:",offset)
    proof_results[name] = dict(exact_zero=True,gram_shape=list(gram.shape),
        function_components=len(functions),constant=str(offset))
    return True

def interpolation(F, u, v, ell):
    return F(v)-F(u)+F.grad(v)*(u-v)+(sp.Rational(1,2)/ell)*(F.grad(u)-F.grad(v))**2
'''

STEP = '''ctx_step = pf.PEPContext("ogm_exact_step").set_as_current()
ell_step, b_step, a2_step = pf.Parameter("ell_step"),pf.Parameter("b_step"),pf.Parameter("a2_step")
F_step = pf.SmoothConvexFunction(is_basis=True,tags=["F_{step}"],L=ell_step)
s_step = F_step.set_stationary_point("x_{star,step}")
x_step = pf.Vector(is_basis=True,tags=["x_{k}"])
w_step = pf.Vector(is_basis=True,tags=["z_{k+1}"])
g_step = F_step.grad(x_step)
x_next_step = (1-1/b_step)*(x_step-g_step/ell_step)+w_step/b_step
x_next_step.add_tag("x_{k+1}")
h_step = F_step.grad(x_next_step)
w_next_step = w_step-(2*b_step/ell_step)*h_step
U_step = (ell_step/2)*(w_step-s_step)**2+2*a2_step*(F_step(x_step)-F_step(s_step))-(a2_step/ell_step)*g_step**2
U_next_step = (ell_step/2)*(w_next_step-s_step)**2+2*b_step**2*(F_step(x_next_step)-F_step(s_step))-(b_step**2/ell_step)*h_step**2
LHS_step = U_next_step-U_step
RHS_step = 2*b_step*interpolation(F_step,s_step,x_next_step,ell_step)+2*a2_step*interpolation(F_step,x_step,x_next_step,ell_step)
diff_step = LHS_step-RHS_step
# theta_{k+1}^2-theta_{k+1}=theta_k^2, valid for 0<=k<=N-2.
step_parameters: dict[str,Any] = {"ell_step":L_exact,"b_step":b_exact,"a2_step":b_exact**2-b_exact}
pm_step = pf.ExpressionManager(ctx_step,resolve_parameters=step_parameters)
step_verified = exact_check("interior_step",diff_step,pm_step,ctx_step)
'''

BASE = '''ctx_base = pf.PEPContext("ogm_exact_base").set_as_current()
ell_base = pf.Parameter("ell_base")
F_base = pf.SmoothConvexFunction(is_basis=True,tags=["F_{base}"],L=ell_base)
s_base = F_base.set_stationary_point("x_{star,base}")
x_base = pf.Vector(is_basis=True,tags=["x_{0}"])
g_base = F_base.grad(x_base)
# theta_0=1 and z_0=x_0 give z_1=x_0-2*g_0/L.
z1_base = x_base-(2/ell_base)*g_base
U0_base = (ell_base/2)*(z1_base-s_base)**2+2*(F_base(x_base)-F_base(s_base))-(1/ell_base)*g_base**2
LHS_base = U0_base-(ell_base/2)*(x_base-s_base)**2
RHS_base = 2*interpolation(F_base,s_base,x_base,ell_base)
diff_base = LHS_base-RHS_base
base_parameters: dict[str,Any] = {"ell_base":L_exact}
pm_base = pf.ExpressionManager(ctx_base,resolve_parameters=base_parameters)
base_verified = exact_check("base",diff_base,pm_base,ctx_base)
'''

TERMINAL = '''ctx_terminal = pf.PEPContext("ogm_exact_terminal").set_as_current()
ell_terminal,T_terminal,a2_terminal = pf.Parameter("ell_terminal"),pf.Parameter("T_terminal"),pf.Parameter("a2_terminal")
F_terminal = pf.SmoothConvexFunction(is_basis=True,tags=["F_{terminal}"],L=ell_terminal)
s_terminal = F_terminal.set_stationary_point("x_{star,terminal}")
x_terminal = pf.Vector(is_basis=True,tags=["x_{N-1}"])
w_terminal = pf.Vector(is_basis=True,tags=["z_{N}"])
g_terminal = F_terminal.grad(x_terminal)
x_final = (1-1/T_terminal)*(x_terminal-g_terminal/ell_terminal)+w_terminal/T_terminal
x_final.add_tag("x_{N}")
h_terminal = F_terminal.grad(x_final)
q_terminal = w_terminal-s_terminal-(T_terminal/ell_terminal)*h_terminal
U_before_terminal = (ell_terminal/2)*(w_terminal-s_terminal)**2+2*a2_terminal*(F_terminal(x_terminal)-F_terminal(s_terminal))-(a2_terminal/ell_terminal)*g_terminal**2
U_terminal = T_terminal**2*(F_terminal(x_final)-F_terminal(s_terminal))+(ell_terminal/2)*q_terminal**2
LHS_terminal = U_terminal-U_before_terminal
RHS_terminal = T_terminal*interpolation(F_terminal,s_terminal,x_final,ell_terminal)+2*a2_terminal*interpolation(F_terminal,x_terminal,x_final,ell_terminal)
diff_terminal = LHS_terminal-RHS_terminal
# The special terminal recurrence gives T^2-T=2*theta_{N-1}^2.
terminal_parameters: dict[str,Any] = {"ell_terminal":L_exact,"T_terminal":T_exact,"a2_terminal":(T_exact**2-T_exact)/2}
pm_terminal = pf.ExpressionManager(ctx_terminal,resolve_parameters=terminal_parameters)
terminal_verified = exact_check("terminal_transition",diff_terminal,pm_terminal,ctx_terminal)
'''

BOUNDARY = '''ctx_boundary = pf.PEPContext("ogm_exact_boundary").set_as_current()
ell_boundary,T_boundary,R_boundary = pf.Parameter("ell_boundary"),pf.Parameter("T_boundary"),pf.Parameter("R_boundary")
F_boundary = pf.SmoothConvexFunction(is_basis=True,tags=["F_{boundary}"],L=ell_boundary)
s_boundary = F_boundary.set_stationary_point("x_{star,boundary}")
x0_boundary = pf.Vector(is_basis=True,tags=["x_{0,boundary}"])
xN_boundary = pf.Vector(is_basis=True,tags=["x_{N,boundary}"])
zN_boundary = pf.Vector(is_basis=True,tags=["z_{N,boundary}"])
gN_boundary = F_boundary.grad(xN_boundary)
qN_boundary = zN_boundary-s_boundary-(T_boundary/ell_boundary)*gN_boundary
gap_boundary = F_boundary(xN_boundary)-F_boundary(s_boundary)
tau_boundary = ell_boundary/(2*T_boundary**2)
VN_boundary = gap_boundary+tau_boundary*(qN_boundary**2-(x0_boundary-s_boundary)**2)
LHS_boundary = gap_boundary-tau_boundary*R_boundary**2
RHS_boundary = VN_boundary-tau_boundary*qN_boundary**2+tau_boundary*((x0_boundary-s_boundary)**2-R_boundary**2)
diff_boundary = LHS_boundary-RHS_boundary
R_exact = sp.symbols("R",nonnegative=True)
boundary_parameters: dict[str,Any] = {"ell_boundary":L_exact,"T_boundary":T_exact,"R_boundary":R_exact}
pm_boundary = pf.ExpressionManager(ctx_boundary,resolve_parameters=boundary_parameters)
boundary_verified = exact_check("boundary_normalization",diff_boundary,pm_boundary,ctx_boundary)
'''

SMALL = '''ctx_small = pf.PEPContext("ogm_exact_N1").set_as_current()
ell_small = pf.Parameter("ell_small")
F_small = pf.SmoothConvexFunction(is_basis=True,tags=["F_{N=1}"],L=ell_small)
s_small = F_small.set_stationary_point("x_{star,N=1}")
x0_small = pf.Vector(is_basis=True,tags=["x_{0,N=1}"])
g0_small = F_small.grad(x0_small)
z1_small = x0_small-(2/ell_small)*g0_small
x1_small = sp.Rational(1,2)*(x0_small-g0_small/ell_small)+sp.Rational(1,2)*z1_small
h_small = F_small.grad(x1_small)
q_small = z1_small-s_small-(2/ell_small)*h_small
V1_small = F_small(x1_small)-F_small(s_small)+(ell_small/8)*(q_small**2-(x0_small-s_small)**2)
LHS_small = V1_small
RHS_small = sp.Rational(1,2)*(interpolation(F_small,s_small,x0_small,ell_small)+interpolation(F_small,s_small,x1_small,ell_small)+interpolation(F_small,x0_small,x1_small,ell_small))
diff_small = LHS_small-RHS_small
small_parameters: dict[str,Any] = {"ell_small":L_exact}
pm_small = pf.ExpressionManager(ctx_small,resolve_parameters=small_parameters)
small_verified = exact_check("N_equals_1",diff_small,pm_small,ctx_small)
'''

SIGNS = '''ordinary_root = (1+sp.sqrt(1+4*a_exact**2))/2
terminal_root = (1+sp.sqrt(1+8*a_exact**2))/2
assert sp.simplify(ordinary_root**2-ordinary_root-a_exact**2) == 0
assert sp.simplify(terminal_root**2-terminal_root-2*a_exact**2) == 0
assert sp.simplify((1+sp.sqrt(1+4*sp.Integer(0)**2))/2) == 1
assert sp.simplify(terminal_root.subs(a_exact,1)) == 2
assert (2*a_exact**2).is_positive and (2*b_exact).is_positive and T_exact.is_positive
assert (L_exact/(2*T_exact**2)).is_positive
assert (1/T_exact**2).is_positive
proof_results["recurrences_and_signs"] = dict(exact_zero=True,positive_multipliers=True)
print("Exact recurrences checked; local multipliers and normalization coefficient are positive for the stated domain.")
print("By the recurrence theta_0=1 and all later theta values exceed 1. Thus all denominators are nonzero.")
print("Interpolation residuals are nonpositive, so U_N <= ... <= U_0 <= L||x_0-x_star||^2/2.")
print("Boundary: gap - L*R^2/(2*T^2) = V_N - tau*||q_N||^2 + tau*(||d_0||^2-R^2) <= 0.")
assert all(record["exact_zero"] for record in proof_results.values())
'''
