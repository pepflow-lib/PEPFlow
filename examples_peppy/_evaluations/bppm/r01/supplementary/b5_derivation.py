import sympy as sp
import numpy as np
import pepflow as pf
from typing import Any

b4=json.loads((notebook_dir/'state/bppm_b4.json').read_text())
assert b4['certificate_id']==certificate['certificate_id']
assert b4['numerical_reconstruction']['required_indices']==list(range(N_int+1))
assert certificate_checked and grouping_checked
for k_index in range(N_int+1):
    residual=pm.eval_scalar(V_k_structure(k_index)-lyap[k_index])
    assert all(np.max(np.abs(np.asarray(v,dtype=float)),initial=0.0)<=1e-4 for v in (residual.inner_prod_coords,residual.func_coords,np.asarray(residual.offset)))
proof_checks={name:False for name in ('step','base','boundary','signs','domain','normalization')}
exact_identity_evidence={}


def symbolic_components(expression,manager):
    value=manager.eval_scalar(pf.Scalar.zero()+expression,sympy_mode=True)
    gram=sp.Matrix(value.inner_prod_coords).applyfunc(sp.simplify)
    funcs=sp.Matrix(list(value.func_coords)).applyfunc(sp.simplify)
    offset=sp.simplify(sp.sympify(value.offset))
    return gram,funcs,offset


def verify_exact(name,expression,manager):
    gram,funcs,offset=symbolic_components(expression,manager)
    assert all(term==0 for term in [*gram,*funcs,offset]),name
    vector_labels=[str(v) for v in manager.context.basis_vectors()]
    function_labels=[str(v) for v in manager.context.basis_scalars()]
    print(name,'Gram residual:')
    pf.pprint_labeled_matrix(pf.MatrixWithNames(np.array(gram,dtype=object),vector_labels,vector_labels))
    print(name,'function residual:')
    pf.pprint_labeled_matrix(pf.MatrixWithNames(np.array(funcs,dtype=object),function_labels,['coefficient']))
    print(name,'offset residual:',offset)
    exact_identity_evidence[name]=dict(gram_zero=True,function_zero=True,offset_zero=True)
    return True


def D_h(kernel,u,v):
    return kernel(u)-kernel(v)-kernel.grad(v)*(u-v)


def interpolation(function,u,v):
    return function(v)-function(u)+function.grad(v)*(u-v)


k_symbol=sp.Symbol('k',integer=True,nonnegative=True)
N_symbol=sp.Symbol('N',integer=True,positive=True)
a_symbol=sp.Symbol('alpha',positive=True)
R_symbol=sp.Symbol('R',nonnegative=True)
A_current,A_next,B=sp.symbols('A_current A_next B',real=True)
mu_star,mu_f,mu_back,mu_forward=sp.symbols('mu_star mu_f mu_back mu_forward',real=True)
ctx_step=pf.PEPContext('bppm_symbolic_step').set_as_current()
f_step=pf.ConvexFunction(is_basis=True,tags=['f_{step}'])
h_step=pf.ConvexFunction(is_basis=True,tags=['h_{step}'])
f_step.set_stationary_point('x_{star}')
xs_step=ctx_step['x_{star}']
x0_step=pf.Vector(is_basis=True,tags=['x_{0}'])
xk_step=pf.Vector(is_basis=True,tags=['x_{k}'])
a_step: Any=pf.Parameter('a_{step}')
xkp_step=f_step.bregman_prox(xk_step,a_step,h_step,tag='x_{k+1}')
Ac=pf.Parameter('A_current')
An=pf.Parameter('A_next')
Bp=pf.Parameter('B')
m_star=pf.Parameter('mu_star')
m_f=pf.Parameter('mu_f')
m_back=pf.Parameter('mu_back')
m_forward=pf.Parameter('mu_forward')
V_current=Ac*(f_step(xk_step)-f_step(xs_step))+Bp*(D_h(h_step,xs_step,xk_step)-D_h(h_step,xs_step,x0_step))
V_next=An*(f_step(xkp_step)-f_step(xs_step))+Bp*(D_h(h_step,xs_step,xkp_step)-D_h(h_step,xs_step,x0_step))
I_star=interpolation(f_step,xs_step,xkp_step)
I_f=interpolation(f_step,xk_step,xkp_step)
I_back=interpolation(h_step,xkp_step,xk_step)
I_forward=interpolation(h_step,xk_step,xkp_step)
step_LHS=V_next-V_current
step_RHS=m_star*I_star+m_f*I_f+m_back*I_back+m_forward*I_forward
step_diff=step_LHS-step_RHS
unknown_parameters: dict[str,Any]={'a_{step}':a_symbol,'A_current':A_current,'A_next':A_next,'B':B,'mu_star':mu_star,'mu_f':mu_f,'mu_back':mu_back,'mu_forward':mu_forward}
manager_unknown=pf.ExpressionManager(ctx_step,resolve_parameters=unknown_parameters)
gram_eq,func_eq,offset_eq=symbolic_components(step_diff,manager_unknown)
equations=[term for term in [*gram_eq,*func_eq,offset_eq] if term!=0]
solutions=sp.solve(equations,[A_next,mu_star,mu_f,mu_back,mu_forward],dict=True)
assert len(solutions)==1
solution=solutions[0]
print('Exact local coefficient equations give:',solution)
A_sequence: Any=sp.Function('A')
recurrence=sp.Eq(A_sequence(k_symbol+1)-A_sequence(k_symbol),a_symbol*B)
A_formula=sp.rsolve(recurrence,A_sequence(k_symbol),{A_sequence(0):0})
assert sp.simplify(A_formula-a_symbol*B*k_symbol)==0
B_formula=sp.solve(sp.Eq(A_formula.subs(k_symbol,N_symbol),1),B)[0]
assert sp.simplify(B_formula-1/(a_symbol*N_symbol))==0
A_formula=sp.simplify(A_formula.subs(B,B_formula))
print('With A(0)=0 and A(N)=1:', 'A(k)=',A_formula,'B=',B_formula)
resolved_parameters: dict[str,Any]={'a_{step}':a_symbol,'A_current':k_symbol/N_symbol,'A_next':(k_symbol+1)/N_symbol,'B':1/(a_symbol*N_symbol),'mu_star':1/N_symbol,'mu_f':k_symbol/N_symbol,'mu_back':(k_symbol+1)/(a_symbol*N_symbol),'mu_forward':k_symbol/(a_symbol*N_symbol)}

