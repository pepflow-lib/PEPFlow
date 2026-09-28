# %% Explicit coefficients and their finite-product solution.
import sympy as sp
import numpy as np
import pepflow as pf

k_sp,N_sp=sp.symbols('k N',integer=True)
L_sp=sp.symbols('L',positive=True)
c_sp=sp.symbols('c',nonnegative=True)

def transfer_matrix(j,n):
    t=2*n-j
    return sp.Matrix([[2*j*(j+1)*t*(t-1)**2,j*(j+1)*(t-1)*(j+t+1)],
        [4*t**2*(t-1)*((2*j+1)*t-j),2*t**2*((j**2+3*j+1)*t+1)]])

def beta_closed(index,horizon):
    n=sp.Integer(horizon)
    if index==0:
        return sp.S.Zero
    product=sp.eye(2)
    for j in range(index,horizon-1):
        product=product*transfer_matrix(sp.Integer(j),n)
    seed=sp.Matrix([(n-1)/(2*(n+1)**2),1])
    result=product*seed
    return sp.cancel(result[0]/result[1])

def beta_recurrence(k,n,c):
    T=transfer_matrix(k,n)
    return sp.cancel((T[0,0]*c+T[0,1])/(T[1,0]*c+T[1,1]))

a_num,a_den=sp.symbols('a_num a_den',positive=True)
T_generic=transfer_matrix(k_sp,N_sp)
product_identity=sp.cancel((T_generic[0,0]*a_num+T_generic[0,1]*a_den)/(T_generic[1,0]*a_num+T_generic[1,1]*a_den)
    -beta_recurrence(k_sp,N_sp,a_num/a_den))
assert product_identity==0
assert beta_recurrence(0,N_sp,c_sp)==0
print('Finite-product first-factor identity:',product_identity,'; beta_0=0')
print('Exact discovered coefficients at N=4:',[beta_closed(j,4) for j in range(1,4)])

# %% Local square factors obtained by eliminating the next gradient and proximal subgradient.
def local_coefficients(k,n,c):
    t=2*n-k
    a=c+(k+2)/(2*(t-1))
    d=((2*k+1)*t-k)/(2*(t-1)**2)
    e=(k+1)/(2*(t-1))
    v=(k+1)/(2*t*(t-1))
    w=(k*t+1)/(2*(t-1)**2)
    delta=sp.factor(d-e**2/a)
    return a,delta,e/a,v/a,sp.factor((w-e*v/a)/delta)

t_sp=sp.symbols('t',positive=True)
a,delta,ez,vp,wp=local_coefficients(k_sp,(t_sp+k_sp)/2,c_sp)
positive_numerator=2*c_sp*(t_sp-1)*((2*k_sp+1)*t_sp-k_sp)+(k_sp**2+3*k_sp+1)*t_sp+1
delta_identity=sp.factor(delta-positive_numerator/(4*(t_sp-1)**3*a))
assert delta_identity==0
print('Schur complement positive-factor identity:',delta_identity)

# %% Native PEPFlow symbolic helper definitions, shared by the separate identity cells.
proof_parameters={}
weight_counter=0

def proof_weight(value):
    global weight_counter
    weight_counter+=1
    name=f'proof_weight_{weight_counter}'
    proof_parameters[name]=sp.factor(sp.cancel(sp.sympify(value)))
    return pf.Parameter(name)

def analytic_potential(x,anchor,xstar,fun,regularizer,k,n,beta,Lvalue):
    u=x-xstar
    grad=fun.grad(x)
    t=2*n-k
    return (-proof_weight(Lvalue/(4*n))*(anchor-xstar)**2
            +proof_weight(Lvalue*(n-k)/t**2)*u**2
            -proof_weight(1/t)*(u*grad)
            -proof_weight(beta/Lvalue)*(grad-fun.grad(xstar))**2
            +proof_weight((k+1)/t)*(fun(x)-fun(xstar))
            +(proof_weight(k/t)*(regularizer(x)-regularizer(xstar)) if k!=0 else pf.Scalar.zero()))

def local_square_sum(x,xnext,xstar,fun,regularizer,k,n,c,Lvalue):
    p=fun.grad(x)-fun.grad(xstar)
    q=regularizer.grad(xnext)+fun.grad(xstar)
    r=fun.grad(xnext)-fun.grad(xstar)
    z=q-proof_weight(Lvalue/(2*n-k))*(x-xstar)
    a,delta,ez,vp,wp=local_coefficients(k,n,c)
    first=r+proof_weight(ez)*z+proof_weight(vp)*p
    second=z+proof_weight(wp)*p
    return proof_weight(a/Lvalue)*first**2+proof_weight(delta/Lvalue)*second**2

def local_matrix_sum(x,xnext,xstar,fun,regularizer,k,n,c,Lvalue):
    t=2*n-k
    p=fun.grad(x)-fun.grad(xstar)
    q=regularizer.grad(xnext)+fun.grad(xstar)
    r=fun.grad(xnext)-fun.grad(xstar)
    z=q-proof_weight(Lvalue/t)*(x-xstar)
    a=c+(k+2)/(2*(t-1))
    d=((2*k+1)*t-k)/(2*(t-1)**2)
    e=(k+1)/(2*(t-1))
    v=(k+1)/(2*t*(t-1))
    w=(k*t+1)/(2*(t-1)**2)
    m=(k*t*t-k*t+k+1)/(2*t*(t-1)**2)
    return (proof_weight(m/Lvalue)*p**2-proof_weight(beta_recurrence(k,n,c)/Lvalue)*p**2
        +proof_weight(d/Lvalue)*z**2+proof_weight(a/Lvalue)*r**2
        +proof_weight(2*w/Lvalue)*(p*z)+proof_weight(2*v/Lvalue)*(p*r)+proof_weight(2*e/Lvalue)*(z*r))

def check_exact(name,expression,manager):
    value=manager.eval_scalar(expression,sympy_mode=True)
    print(name,'coordinates extracted; simplifying',flush=True)
    def reduction(z):
        return sp.factor(sp.cancel(z.subs(N_sp,(t_sp+k_sp)/2))) if name=='Step' else sp.factor(sp.cancel(z))
    gram=sp.Matrix(value.inner_prod_coords).applyfunc(reduction)
    funcs=sp.Matrix(list(value.func_coords)).applyfunc(reduction)
    offset=sp.factor(sp.cancel(sp.sympify(value.offset)))
    labels=[str(v) for v in manager.context.basis_vectors()]
    print(name,'Gram residual:')
    pf.pprint_labeled_matrix(np.array(gram,dtype=object),labels,precision=0)
    print(name,'function residual:',list(funcs),'constant residual:',offset)
    assert all(v==0 for v in [*gram,*funcs,offset]),name
    return True

# %% Symbolic step identity for 1 <= k <= N-2.
ctx_step=pf.PEPContext('pgm_symbolic_step').set_as_current()
L_proof=pf.Parameter('L_proof')
f_step=pf.SmoothConvexFunction(is_basis=True,tags=['f_{step}'],L=L_proof)
g_step=pf.ConvexFunction(is_basis=True,tags=['g_{step}'])
h_step=f_step+g_step
xstar_step=h_step.set_stationary_point('x_{star}')
x_step=pf.Vector(is_basis=True,tags=['x_{k}'])
anchor_step=pf.Vector(is_basis=True,tags=['x_{0}'])
xnext_step=g_step.prox(x_step-f_step.grad(x_step)/L_proof,1/L_proof,tag='x_{k+1}')
f_step(xnext_step)
g_step(x_step)
proof_parameters={'L_proof':L_sp}
weight_counter=0
beta_k=beta_recurrence(k_sp,N_sp,c_sp)
V_step=analytic_potential(x_step,anchor_step,xstar_step,f_step,g_step,k_sp,N_sp,beta_k,L_sp)
V_next=analytic_potential(xnext_step,anchor_step,xstar_step,f_step,g_step,k_sp+1,N_sp,c_sp,L_sp)
t=2*N_sp-k_sp
step_residuals=(proof_weight((2*N_sp+1)/(t*(t-1)))*f_step.interp_ineq(xstar_step,xnext_step)
    +proof_weight((k_sp+1)/t)*f_step.interp_ineq(x_step,xnext_step)
    +proof_weight(2*N_sp/(t*(t-1)))*g_step.interp_ineq(xstar_step,xnext_step)
    +proof_weight(k_sp/t)*g_step.interp_ineq(x_step,xnext_step))
Q_step=local_matrix_sum(x_step,xnext_step,xstar_step,f_step,g_step,k_sp,N_sp,c_sp,L_sp)
step_LHS=V_next-V_step
step_RHS=step_residuals-Q_step
diff_step=step_LHS-step_RHS
pm_step=pf.ExpressionManager(ctx_step,resolve_parameters=proof_parameters)
step_verified=check_exact('Step',diff_step,pm_step)


# %% Base identity: the first transition, for N >= 2.
ctx_base=pf.PEPContext('pgm_symbolic_base').set_as_current()
f_base=pf.SmoothConvexFunction(is_basis=True,tags=['f_{base}'],L=L_proof)
g_base=pf.ConvexFunction(is_basis=True,tags=['g_{base}'])
h_base=f_base+g_base
xstar_base=h_base.set_stationary_point('x_{star}')
x0_base=pf.Vector(is_basis=True,tags=['x_{0}'])
x1_base=g_base.prox(x0_base-f_base.grad(x0_base)/L_proof,1/L_proof,tag='x_{1}')
f_base(x1_base)
proof_parameters={'L_proof':L_sp}
weight_counter=0
base_LHS=analytic_potential(x1_base,x0_base,xstar_base,f_base,g_base,sp.S.One,N_sp,c_sp,L_sp)
t0=2*N_sp
base_RHS=(proof_weight(1/(2*N_sp))*f_base.interp_ineq(xstar_base,x0_base)
    +proof_weight((2*N_sp+1)/(t0*(t0-1)))*f_base.interp_ineq(xstar_base,x1_base)
    +proof_weight(1/t0)*f_base.interp_ineq(x0_base,x1_base)
    +proof_weight(2*N_sp/(t0*(t0-1)))*g_base.interp_ineq(xstar_base,x1_base)
    -local_matrix_sum(x0_base,x1_base,xstar_base,f_base,g_base,sp.S.Zero,N_sp,c_sp,L_sp)
    -proof_weight(1/(4*N_sp*L_sp))*(f_base.grad(x0_base)-f_base.grad(xstar_base))**2)
diff_base=base_LHS-base_RHS
pm_base=pf.ExpressionManager(ctx_base,resolve_parameters=proof_parameters)
base_verified=check_exact('Base',diff_base,pm_base)

# %% Boundary identity: last transition, for N >= 2, and distance normalization.
ctx_boundary=pf.PEPContext('pgm_symbolic_boundary').set_as_current()
f_boundary=pf.SmoothConvexFunction(is_basis=True,tags=['f_{boundary}'],L=L_proof)
g_boundary=pf.ConvexFunction(is_basis=True,tags=['g_{boundary}'])
h_boundary=f_boundary+g_boundary
xstar_boundary=h_boundary.set_stationary_point('x_{star}')
xprev=pf.Vector(is_basis=True,tags=['x_{N-1}'])
anchor_boundary=pf.Vector(is_basis=True,tags=['x_{0}'])
xlast=g_boundary.prox(xprev-f_boundary.grad(xprev)/L_proof,1/L_proof,tag='x_{N}')
f_boundary(xlast)
g_boundary(xprev)
proof_parameters={'L_proof':L_sp}
weight_counter=0
beta_last=(N_sp-1)/(2*(N_sp+1)**2)
V_previous=analytic_potential(xprev,anchor_boundary,xstar_boundary,f_boundary,g_boundary,N_sp-1,N_sp,beta_last,L_sp)
last_gap=h_boundary(xlast)-h_boundary(xstar_boundary)
V_terminal=last_gap-proof_weight(L_sp/(4*N_sp))*(anchor_boundary-xstar_boundary)**2
p_end=f_boundary.grad(xprev)-f_boundary.grad(xstar_boundary)
q_end=g_boundary.grad(xlast)+f_boundary.grad(xstar_boundary)
r_end=f_boundary.grad(xlast)-f_boundary.grad(xstar_boundary)
u_end=xprev-xstar_boundary
terminal_square_1=r_end+q_end+proof_weight(1/(N_sp+1))*p_end-proof_weight(L_sp/(N_sp+1))*u_end
terminal_square_2=q_end+proof_weight(N_sp/(N_sp+1))*p_end-proof_weight(L_sp/(N_sp+1))*u_end
Q_terminal=proof_weight(1/(2*L_sp))*(terminal_square_1**2+terminal_square_2**2)
boundary_LHS=V_terminal-V_previous
boundary_RHS=(proof_weight(1/(N_sp+1))*f_boundary.interp_ineq(xstar_boundary,xlast)
    +proof_weight(N_sp/(N_sp+1))*f_boundary.interp_ineq(xprev,xlast)
    +proof_weight(2/(N_sp+1))*g_boundary.interp_ineq(xstar_boundary,xlast)
    +proof_weight((N_sp-1)/(N_sp+1))*g_boundary.interp_ineq(xprev,xlast)-Q_terminal)
diff_boundary=boundary_LHS-boundary_RHS
pm_boundary=pf.ExpressionManager(ctx_boundary,resolve_parameters=proof_parameters)
boundary_verified=check_exact('Boundary',diff_boundary,pm_boundary)
R_sp=sp.symbols('R',nonnegative=True)
R_proof=pf.Parameter('R_proof')
proof_parameters['R_proof']=R_sp
normalization_LHS=last_gap-proof_weight(L_sp/(4*N_sp))*R_proof**2
normalization_RHS=V_terminal+proof_weight(L_sp/(4*N_sp))*((anchor_boundary-xstar_boundary)**2-R_proof**2)
diff_normalization=normalization_LHS-normalization_RHS
pm_normalization=pf.ExpressionManager(ctx_boundary,resolve_parameters=proof_parameters)
normalization_verified=check_exact('Normalization',diff_normalization,pm_normalization)

# %% The exceptional horizon N=1, without evaluating g at x_0.
ctx_one=pf.PEPContext('pgm_symbolic_one').set_as_current()
f_one=pf.SmoothConvexFunction(is_basis=True,tags=['f_{one}'],L=L_proof)
g_one=pf.ConvexFunction(is_basis=True,tags=['g_{one}'])
h_one=f_one+g_one
xs_one=h_one.set_stationary_point('x_{star}')
x0_one=pf.Vector(is_basis=True,tags=['x_{0}'])
x1_one=g_one.prox(x0_one-f_one.grad(x0_one)/L_proof,1/L_proof,tag='x_{1}')
f_one(x1_one)
proof_parameters={'L_proof':L_sp}
weight_counter=0
p_one=f_one.grad(x0_one)-f_one.grad(xs_one)
q_one=g_one.grad(x1_one)+f_one.grad(xs_one)
r_one=f_one.grad(x1_one)-f_one.grad(xs_one)
u_one=x0_one-xs_one
square_one_1=r_one+q_one+sp.Rational(1,2)*p_one-proof_weight(L_sp/2)*u_one
square_one_2=q_one+sp.Rational(1,2)*p_one-proof_weight(L_sp/2)*u_one
one_LHS=h_one(x1_one)-h_one(xs_one)-proof_weight(L_sp/4)*u_one**2
one_RHS=(sp.Rational(1,2)*f_one.interp_ineq(xs_one,x0_one)
    +sp.Rational(1,2)*f_one.interp_ineq(xs_one,x1_one)+sp.Rational(1,2)*f_one.interp_ineq(x0_one,x1_one)
    +g_one.interp_ineq(xs_one,x1_one)-proof_weight(1/(2*L_sp))*(square_one_1**2+square_one_2**2)
    -proof_weight(1/(4*L_sp))*p_one**2)
diff_one=one_LHS-one_RHS
pm_one=pf.ExpressionManager(ctx_one,resolve_parameters=proof_parameters)
one_verified=check_exact('N=1',diff_one,pm_one)


# %% Exact quadratic square completion, valid for arbitrary vector Gram entries.
import sympy as sp
k,t,c,b=sp.symbols('k t c b')
a=c+(k+2)/(2*(t-1))
d=((2*k+1)*t-k)/(2*(t-1)**2)
e=(k+1)/(2*(t-1))
v=(k+1)/(2*t*(t-1))
w=(k*t+1)/(2*(t-1)**2)
m=(k*t*t-k*t+k+1)/(2*t*(t-1)**2)
delta=sp.factor(d-e*e/a)
rec=k*(k+1)*(t-1)*(2*c*t*(t-1)+k+t+1)/(2*t*t*(2*c*(t-1)*((2*k+1)*t-k)+(k*k+3*k+1)*t+1))
derived_beta=sp.factor(m-v*v/a-(w-e*v/a)**2/delta)
assert sp.cancel(rec-beta_recurrence(k,(t+k)/2,c))==0
print('Solved final-pivot equation for beta_k:',derived_beta,flush=True)
print('checking coefficient',flush=True)
coefficient_identity=sp.factor(m-rec-v*v/a-(w-e*v/a)**2/delta)
assert coefficient_identity==0
print(coefficient_identity,flush=True)
A,D,E,V,W=sp.symbols('A D E V W',nonzero=True)
p,z,r=sp.symbols('p z r')
rho=V*V/A+(W-E*V/A)**2/(D-E*E/A)
Q=rho*p*p+D*z*z+A*r*r+2*W*p*z+2*V*p*r+2*E*z*r
squares=A*(r+E/A*z+V/A*p)**2+(D-E*E/A)*(z+(W-E*V/A)/(D-E*E/A)*p)**2
square_identity=sp.hessian(Q-squares,(p,z,r)).applyfunc(sp.factor)
assert square_identity==sp.zeros(3)
print('generic Gram square identity',square_identity,flush=True)
squares_verified=True
