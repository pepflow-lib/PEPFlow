# LOAD
import json
from typing import Any
import sympy as sp
import pepflow as pf
import numpy as np
import runtime

b4_final = json.loads((runtime.ROOT/'state/feg_b4.json').read_text())
assert b4_final['numerical_reconstruction']['certificate_id'] == b4_final['certificate_id']
assert b4_final['numerical_reconstruction']['passed']
proof_checks = {}

# HELPERS
def exact_components(expression, manager):
    value = manager.eval_scalar(pf.Scalar.zero()+expression,sympy_mode=True)
    gram = sp.Matrix(value.inner_prod_coords).applyfunc(sp.factor)
    function = sp.Matrix(list(value.func_coords)).applyfunc(sp.factor)
    offset = sp.factor(sp.sympify(value.offset))
    return gram,function,offset


def exact_check(name,expression,manager):
    gram,function,offset = exact_components(expression,manager)
    labels = [str(v) for v in manager.context.basis_vectors()]
    pf.pprint_labeled_matrix(np.array(gram.tolist(),dtype=object),labels,labels,precision=0)
    print(name,'function residual:',function,'constant residual:',offset)
    assert all(value == 0 for value in [*gram,*function,offset]), name
    print(name,'all scalar components exactly zero.')
    return True

# DERIVATION
k_sym,N_sym = sp.symbols('k N',integer=True,positive=True)
L_sym = sp.Symbol('L',positive=True)
a_sym,b_sym,c_sym,ap_sym,bp_sym,cp_sym,u_sym,v_sym = sp.symbols('a b c a_next b_next c_next u v',real=True)
K = pf.Parameter('k_symbolic')
LL = pf.Parameter('L_symbolic')
NN = pf.Parameter('N_symbolic')
ctx_step = pf.PEPContext('feg_symbolic_step').set_as_current()
A_step = pf.LipschitzMonotoneOperator(is_basis=True,tags=['A_{step}'],L=LL)
x_anchor = pf.Vector(is_basis=True,tags=['x_{0}'])
x_current = pf.Vector(is_basis=True,tags=['x_{k}'])
g_current = A_step(x_current)
x_half = x_current+(x_anchor-x_current)/(K+1)-K/((K+1)*LL)*g_current
x_half.add_tag('x_{k+1/2}')
g_half = A_step(x_half)
x_next = x_current+(x_anchor-x_current)/(K+1)-g_half/LL
x_next.add_tag('x_{k+1}')
g_next = A_step(x_next)
q_current = x_current-x_anchor
q_next = x_next-x_anchor
pa,pb_unknown,pc_unknown,pap,pbp,pcp,pu,pv = [pf.Parameter(name) for name in ['a','b','c','a_next','b_next','c_next','u','v']]
P_current = pa*g_current**2+2*pb_unknown*(g_current*q_current)+pc_unknown*q_current**2
P_next = pap*g_next**2+2*pbp*(g_next*q_next)+pcp*q_next**2
I_lip = (g_next-g_half)**2-LL**2*(x_next-x_half)**2
I_mon = -(g_next-g_current)*(x_next-x_current)
unknown_map: dict[str,Any] = {'k_symbolic':k_sym,'L_symbolic':L_sym,'a':a_sym,'b':b_sym,'c':c_sym,'a_next':ap_sym,'b_next':bp_sym,'c_next':cp_sym,'u':u_sym,'v':v_sym}
manager_unknown = pf.ExpressionManager(ctx_step,resolve_parameters=unknown_map)
unknown_diff = P_next-P_current-pu*I_lip-pv*I_mon
G_unknown,F_unknown,o_unknown = exact_components(unknown_diff,manager_unknown)
equations = [entry for entry in [*G_unknown,*F_unknown,o_unknown] if entry!=0]
solutions = sp.solve(equations,[b_sym,c_sym,ap_sym,bp_sym,cp_sym,u_sym,v_sym],dict=True)
assert len(solutions)==1
solution = solutions[0]
print('Coefficient equations give:',solution)
expected = {b_sym:L_sym*a_sym/k_sym,c_sym:0,ap_sym:a_sym*(k_sym+1)**2/k_sym**2,bp_sym:L_sym*a_sym*(k_sym+1)/k_sym**2,cp_sym:0,u_sym:a_sym*(k_sym+1)**2/k_sym**2,v_sym:2*L_sym*a_sym*(k_sym+1)/k_sym}
assert all(sp.factor(solution[s]-expected[s])==0 for s in expected)
print('a_(k+1)/(k+1)^2 = a_k/k^2. Choose a_1=1: a_k=k^2, b_k=L*k, c_k=0.')
assert sp.simplify(((k_sym+1)**2)/(k_sym+1)**2-k_sym**2/k_sym**2)==0

# NORMALIZED_COEFFICIENTS
sigma_sample = b4_final['coeff_by_k']['1'][0][0]
assert sigma_sample > 0
for kk in range(1,b4_final['N_verify']+1):
    numerical_C = np.asarray(b4_final['coeff_by_k'][str(kk)])/sigma_sample
    exact_C = np.array([[kk**2,kk],[kk,0]],dtype=float)
    error = float(np.max(np.abs(numerical_C-exact_C)))
    print('k=',kk,'coefficient comparison after positive scalar normalization:',error)
    assert np.allclose(numerical_C,exact_C,atol=1e-4,rtol=1e-5)
    pf.pprint_labeled_matrix(exact_C,[f'g_{kk}',f'q_{kk}'],[f'g_{kk}',f'q_{kk}'],precision=0)
print('The final potential U is normalized by a_1=1; the numerical partial sums have a positive solver-dependent scale.')

# STEP
ctx_step.set_as_current()
step_LHS = (K+1)**2*g_next**2+2*(K+1)*LL*(g_next*q_next)-(K**2*g_current**2+2*K*LL*(g_current*q_current))
step_RHS = (K+1)**2*I_lip+2*K*(K+1)*LL*I_mon
step_diff = step_LHS-step_RHS
step_map: dict[str,Any] = {'k_symbolic':k_sym,'L_symbolic':L_sym}
manager_step = pf.ExpressionManager(ctx_step,resolve_parameters=step_map)
proof_checks['step'] = exact_check('Step',step_diff,manager_step)

# BASE
ctx_base = pf.PEPContext('feg_symbolic_base').set_as_current()
A_base = pf.LipschitzMonotoneOperator(is_basis=True,tags=['A_{base}'],L=LL)
x_initial = pf.Vector(is_basis=True,tags=['x_{0}'])
x_initial.add_tag('x_{1/2}')
g_initial = A_base(x_initial)
x_first = x_initial-g_initial/LL
x_first.add_tag('x_{1}')
g_first = A_base(x_first)
base_LHS = g_first**2+2*LL*(g_first*(x_first-x_initial))
base_RHS = (g_first-g_initial)**2-LL**2*(x_first-x_initial)**2
base_diff = base_LHS-base_RHS
base_map: dict[str,Any] = {'L_symbolic':L_sym}
manager_base = pf.ExpressionManager(ctx_base,resolve_parameters=base_map)
proof_checks['base'] = exact_check('Base U_1-U_0=Lip(x_0,x_1)',base_diff,manager_base)

# BOUNDARY
ctx_boundary = pf.PEPContext('feg_symbolic_boundary').set_as_current()
A_boundary = pf.LipschitzMonotoneOperator(is_basis=True,tags=['A_{boundary}'],L=LL)
x_start = pf.Vector(is_basis=True,tags=['x_{0}'])
x_terminal = pf.Vector(is_basis=True,tags=['x_{N}'])
x_zero = A_boundary.set_zero_point('x_{star}')
g_terminal = A_boundary(x_terminal)
d_initial = x_start-x_zero
U_terminal = NN**2*g_terminal**2+2*NN*LL*(g_terminal*(x_terminal-x_start))
I_terminal = -(g_terminal*(x_terminal-x_zero))
terminal_square = (NN*g_terminal-2*LL*d_initial)**2
boundary_LHS = NN**2*g_terminal**2-4*LL**2*d_initial**2
boundary_RHS = 2*U_terminal+4*NN*LL*I_terminal-terminal_square
boundary_diff = boundary_LHS-boundary_RHS
boundary_map: dict[str,Any] = {'N_symbolic':N_sym,'L_symbolic':L_sym}
manager_boundary = pf.ExpressionManager(ctx_boundary,resolve_parameters=boundary_map)
proof_checks['boundary'] = exact_check('Boundary',boundary_diff,manager_boundary)

# SIGNS
assert ((k_sym+1)**2).is_positive
assert (2*k_sym*(k_sym+1)*L_sym).is_positive
assert (4*N_sym*L_sym).is_positive
assert (N_sym**2).is_positive
proof_checks['signs'] = True
proof_checks['domain'] = True
proof_checks['normalization'] = True
print('For integer k>=1, N>=1 and L>0, all residual multipliers are nonnegative and denominators are nonzero.')
print('U_1<=0, U_(k+1)<=U_k, and terminal RHS<=0; hence N^2 ||A(x_N)||^2 <= 4 L^2 ||x_0-x_star||^2 <= 4 L^2 R^2.')
print('N=1 uses only base and boundary; R=0 is covered without dividing by R.')
assert all(proof_checks.values())
