# Closed-form coefficient solution as an explicit finite matrix product.
b4 = json.loads((notebook_dir / 'state/pgm_b4.json').read_text())
assert b4['certificate_id'] == certificate['certificate_id']
assert b4['numerical_reconstruction']['certificate_id'] == certificate['certificate_id']

def beta_closed(index, horizon):
    if index in (0,horizon):
        return sp.S.Zero
    assert 1 <= index <= horizon-1
    terminal = sp.Matrix([sp.Rational(horizon-1,2*(horizon+1)**2),1])
    product = sp.eye(2)
    for j in range(index,horizon-1):
        t = 2*horizon-j
        product *= sp.Matrix([[2*j*(j+1)*t*(t-1)**2,j*(j+1)*(t-1)*(j+t+1)],
                              [4*t*t*(t-1)*((2*j+1)*t-j),2*t*t*((j*j+3*j+1)*t+1)]])
    value = product*terminal
    return sp.cancel(value[0]/value[1])

def analytic_C(index,horizon,smoothness=1):
    ell = sp.sympify(smoothness)
    if index == 0:
        return sp.zeros(0)
    if index == horizon:
        return sp.Matrix([[-sp.Rational(1,4*horizon)]])
    t = 2*horizon-index
    Cmat = sp.zeros(4)
    Cmat[0,0] = -sp.Rational(1,4*horizon)
    Cmat[1,1] = sp.Rational(horizon-index,t*t)
    Cmat[1,2] = Cmat[2,1] = -1/(2*ell*t)
    Cmat[1,3] = Cmat[3,1] = -1/(2*ell*t)
    Cmat[2,2] = -beta_closed(index,horizon)/ell**2
    return Cmat

for j in range(N_int+1):
    closed = np.asarray(analytic_C(j,N_int),float).reshape(coeff_by_k[j].shape)
    error = float(np.max(np.abs(closed-coeff_by_k[j]),initial=0))
    assert error <= 1e-4
    print(f'k={j}: analytic/sample matrix discrepancy {error:.3e}; beta={beta_closed(j,N_int)}')
    if closed.size:
        pf.pprint_labeled_matrix(np.asarray(analytic_C(j,N_int),dtype=object),V_k_basis_labels(j),precision=7)
    weights = [0,0] if j==0 else [1,1] if j==N_int else [(j+1)/(2*N_int-j),j/(2*N_int-j)]
    assert np.allclose(weights,function_sample_coefficients[j],atol=1e-4,rtol=1e-5)
# CELL
k_sym,N_sym = sp.symbols('k N',integer=True,nonnegative=True)
t_sym = sp.symbols('t',positive=True)
c_next = sp.symbols('c_next',nonnegative=True)
u_sym,v_sym = sp.symbols('u v',positive=True)

def beta_recursion(k,t,c):
    return sp.cancel(k*(k+1)*(t-1)*(2*c*t*(t-1)+k+t+1) /
                     (2*t*t*(2*c*(t-1)*((2*k+1)*t-k)+(k*k+3*k+1)*t+1)))

def local_blocks(k,t,c):
    H = sp.Matrix([[c+(k+2)/(2*(t-1)),(k+1)/(2*(t-1))],
                   [(k+1)/(2*(t-1)),((2*k+1)*t-k)/(2*(t-1)**2)]])
    K = sp.Matrix([[-(k+1)/(2*t*(t-1)),(k+1)/(2*t*(t-1))],
                   [-((2*k+1)*t-k)/(2*t*(t-1)**2),(k*t+1)/(2*(t-1)**2)]])
    return H,K

M_transfer = sp.Matrix([[2*k_sym*(k_sym+1)*t_sym*(t_sym-1)**2,k_sym*(k_sym+1)*(t_sym-1)*(k_sym+t_sym+1)],
                       [4*t_sym*t_sym*(t_sym-1)*((2*k_sym+1)*t_sym-k_sym),2*t_sym*t_sym*((k_sym*k_sym+3*k_sym+1)*t_sym+1)]])
transferred = M_transfer*sp.Matrix([u_sym,v_sym])
assert sp.cancel(transferred[0]/transferred[1]-beta_recursion(k_sym,t_sym,u_sym/v_sym)) == 0
H_symbolic,K_symbolic = local_blocks(k_sym,t_sym,c_next)
det_expected = (2*c_next*(t_sym-1)*((2*k_sym+1)*t_sym-k_sym)+(k_sym*k_sym+3*k_sym+1)*t_sym+1)/(4*(t_sym-1)**3)
assert sp.cancel(H_symbolic.det()-det_expected) == 0
print('Exact transfer-ratio identity: zero; positive determinant formula:',sp.factor(det_expected))
print('beta_0 recurrence:',sp.cancel(beta_recursion(0,t_sym,c_next)))
# CELL
# All following identities are actual PEPFlow Scalar expressions.
L_sym = sp.symbols('L',positive=True)

def local_context(label,with_current_g=True):
    context = pf.PEPContext(label).set_as_current()
    Lpar = pf.Parameter('L_exact')
    fs = pf.SmoothConvexFunction(is_basis=True,tags=['f_{'+label+'}'],L=Lpar)
    gs = pf.ConvexFunction(is_basis=True,tags=['g_{'+label+'}'])
    hs = fs+gs
    xs = hs.set_stationary_point('x_{star}')
    x = pf.Vector(is_basis=True,tags=['x_{k}'])
    anchor = pf.Vector(is_basis=True,tags=['e_{0}'])
    xp = gs.prox(x-fs.grad(x)/Lpar,1/Lpar,tag='x_{k+1}')
    fs(xp)
    if with_current_g:
        gs(x)
    mapping = {'L_exact':L_sym}
    return context,fs,gs,xs,x,xp,anchor,Lpar,mapping

def scalar_parameter(mapping,name,value):
    mapping[name] = sp.cancel(value)
    return pf.Parameter(name)

def local_potential(fs,gs,xs,x,anchor,Lpar,mapping,a,b,A,d,beta,N,name):
    e = x-xs
    p = (fs.grad(x)-fs.grad(xs))/Lpar
    return (scalar_parameter(mapping,name+'_a',a)*(fs(x)-fs(xs))/Lpar
            +scalar_parameter(mapping,name+'_b',b)*(gs(x)-gs(xs))/Lpar
            +scalar_parameter(mapping,name+'_A',A)*e**2
            -scalar_parameter(mapping,name+'_d',d)*e*(fs.grad(x)/Lpar)
            -scalar_parameter(mapping,name+'_beta',beta)*p**2
            -scalar_parameter(mapping,name+'_tau',1/(4*N))*anchor**2)

def block_square(H,K,e,p,r,q,mapping,name):
    # Q = [w+H^{-1}Kz]^T H [w+H^{-1}Kz], w=(r,q), z=(e,p).
    lower = (K.T*H.inv()*K).applyfunc(sp.cancel)
    block = H.row_join(K).col_join(K.T.row_join(lower))
    vectors = [r,q,e,p]
    return sum((scalar_parameter(mapping,f'{name}_{i}_{j}',block[i,j])*vectors[i]*vectors[j]
                for i,j in np.ndindex((4,4))),pf.Scalar.zero())

def verify_exact(label,expression,context,mapping):
    manager = pf.ExpressionManager(context,resolve_parameters=mapping)
    evaluated = manager.eval_scalar(expression,sympy_mode=True)
    gram = sp.Matrix(evaluated.inner_prod_coords).applyfunc(sp.cancel)
    funcs = sp.Matrix(list(evaluated.func_coords)).applyfunc(sp.cancel)
    offset = sp.cancel(evaluated.offset)
    assert all(value==0 for value in list(gram)+list(funcs)+[offset]),label
    print(label,': exact zero in Gram, function and offset coordinates')
    pf.pprint_labeled_matrix(np.asarray(gram,dtype=object),[str(v) for v in context.basis_vectors()])
    print('Function residual:',funcs.T,'offset:',offset)
    return True
# CELL
ctx_step,f_step,g_step,xs_step,x_step,xp_step,e0_step,Lp_step,map_step = local_context('step')
t_step = 2*N_sym-k_sym
beta_k = beta_recursion(k_sym,t_step,c_next)
H_step,K_step = local_blocks(k_sym,t_step,c_next)
V_step = local_potential(f_step,g_step,xs_step,x_step,e0_step,Lp_step,map_step,
    (k_sym+1)/t_step,k_sym/t_step,(N_sym-k_sym)/t_step**2,1/t_step,beta_k,N_sym,'old')
V_next = local_potential(f_step,g_step,xs_step,xp_step,e0_step,Lp_step,map_step,
    (k_sym+2)/(t_step-1),(k_sym+1)/(t_step-1),(N_sym-k_sym-1)/(t_step-1)**2,1/(t_step-1),c_next,N_sym,'new')
a_step = (k_sym+1)/t_step
b_step = k_sym/t_step
mu_f = (k_sym+2)/(t_step-1)-a_step
mu_g = (k_sym+1)/(t_step-1)-b_step
I_step = (scalar_parameter(map_step,'mu_f',mu_f)*f_step.interp_ineq(xs_step,xp_step)
          +scalar_parameter(map_step,'a',a_step)*f_step.interp_ineq(x_step,xp_step)
          +scalar_parameter(map_step,'mu_g',mu_g)*g_step.interp_ineq(xs_step,xp_step)
          +scalar_parameter(map_step,'b',b_step)*g_step.interp_ineq(x_step,xp_step))/Lp_step
p_step = (f_step.grad(x_step)-f_step.grad(xs_step))/Lp_step
r_step = (f_step.grad(xp_step)-f_step.grad(xs_step))/Lp_step
q_step = (g_step.grad(xp_step)+f_step.grad(xs_step))/Lp_step
Q_step = block_square(H_step,K_step,x_step-xs_step,p_step,r_step,q_step,map_step,'Q')
LHS_step = V_next-V_step
RHS_step = I_step-Q_step
step_verified = verify_exact('Interior step',LHS_step-RHS_step,ctx_step,map_step)
# CELL
ctx_base,f_base,g_base,xs_base,x_base,xp_base,e0_unused,Lp_base,map_base = local_context('base',with_current_g=False)
t_base = 2*N_sym
H_base,K_base = local_blocks(sp.S.Zero,t_base,c_next)
V_base = local_potential(f_base,g_base,xs_base,xp_base,x_base-xs_base,Lp_base,map_base,
    2/(2*N_sym-1),1/(2*N_sym-1),(N_sym-1)/(2*N_sym-1)**2,1/(2*N_sym-1),c_next,N_sym,'base')
a0 = 1/(2*N_sym)
base_terms = (scalar_parameter(map_base,'a0',a0)*f_base.interp_ineq(xs_base,x_base)
    +scalar_parameter(map_base,'af1',2/(2*N_sym-1)-a0)*f_base.interp_ineq(xs_base,xp_base)
    +scalar_parameter(map_base,'a01',a0)*f_base.interp_ineq(x_base,xp_base)
    +scalar_parameter(map_base,'bg1',1/(2*N_sym-1))*g_base.interp_ineq(xs_base,xp_base))/Lp_base
p_base = (f_base.grad(x_base)-f_base.grad(xs_base))/Lp_base
r_base = (f_base.grad(xp_base)-f_base.grad(xs_base))/Lp_base
q_base = (g_base.grad(xp_base)+f_base.grad(xs_base))/Lp_base
Q_base = block_square(H_base,K_base,x_base-xs_base,p_base,r_base,q_base,map_base,'Qb')
LHS_base = V_base
RHS_base = base_terms-Q_base-scalar_parameter(map_base,'initial_square',1/(4*N_sym))*p_base**2
base_verified = verify_exact('Base N>=2',LHS_base-RHS_base,ctx_base,map_base)
# CELL
ctx_end,f_end,g_end,xs_end,x_end,xp_end,e0_end,Lp_end,map_end = local_context('boundary')
a_end = N_sym/(N_sym+1)
b_end = (N_sym-1)/(N_sym+1)
V_before = local_potential(f_end,g_end,xs_end,x_end,e0_end,Lp_end,map_end,
    a_end,b_end,1/(N_sym+1)**2,1/(N_sym+1),(N_sym-1)/(2*(N_sym+1)**2),N_sym,'last')
V_terminal = (f_end(xp_end)+g_end(xp_end)-f_end(xs_end)-g_end(xs_end))/Lp_end-scalar_parameter(map_end,'tau_end',1/(4*N_sym))*e0_end**2
H_end = sp.Matrix([[sp.Rational(1,2),sp.Rational(1,2)],[sp.Rational(1,2),1]])
K_end = sp.Matrix([[-1/(2*(N_sym+1)),1/(2*(N_sym+1))],[-1/(N_sym+1),sp.Rational(1,2)]])
p_end = (f_end.grad(x_end)-f_end.grad(xs_end))/Lp_end
r_end = (f_end.grad(xp_end)-f_end.grad(xs_end))/Lp_end
q_end = (g_end.grad(xp_end)+f_end.grad(xs_end))/Lp_end
Q_end = block_square(H_end,K_end,x_end-xs_end,p_end,r_end,q_end,map_end,'Qe')
end_terms = (scalar_parameter(map_end,'afstar',1-a_end)*f_end.interp_ineq(xs_end,xp_end)
    +scalar_parameter(map_end,'afcon',a_end)*f_end.interp_ineq(x_end,xp_end)
    +scalar_parameter(map_end,'bgstar',1-b_end)*g_end.interp_ineq(xs_end,xp_end)
    +scalar_parameter(map_end,'bgcon',b_end)*g_end.interp_ineq(x_end,xp_end))/Lp_end
LHS_boundary = V_terminal-V_before
RHS_boundary = end_terms-Q_end
boundary_verified = verify_exact('Terminal step N>=2',LHS_boundary-RHS_boundary,ctx_end,map_end)
normalization_diff = (f_end(xp_end)+g_end(xp_end)-f_end(xs_end)-g_end(xs_end))-Lp_end*(V_terminal+scalar_parameter(map_end,'tau_normalization',1/(4*N_sym))*e0_end**2)
normalization_verified = verify_exact('Terminal normalization',normalization_diff,ctx_end,map_end)
# CELL
ctx_one,f_one,g_one,xs_one,x_one,xp_one,anchor_one,Lp_one,map_one = local_context('one',with_current_g=False)
H_one = H_end
K_one = K_end.subs(N_sym,1)
p_one = (f_one.grad(x_one)-f_one.grad(xs_one))/Lp_one
r_one = (f_one.grad(xp_one)-f_one.grad(xs_one))/Lp_one
q_one = (g_one.grad(xp_one)+f_one.grad(xs_one))/Lp_one
Q_one = block_square(H_one,K_one,x_one-xs_one,p_one,r_one,q_one,map_one,'Q1')
V_one = (f_one(xp_one)+g_one(xp_one)-f_one(xs_one)-g_one(xs_one))/Lp_one-sp.Rational(1,4)*(x_one-xs_one)**2
I_one = (sp.Rational(1,2)*f_one.interp_ineq(xs_one,x_one)+sp.Rational(1,2)*f_one.interp_ineq(xs_one,xp_one)
         +sp.Rational(1,2)*f_one.interp_ineq(x_one,xp_one)+g_one.interp_ineq(xs_one,xp_one))/Lp_one
LHS_one = V_one
RHS_one = I_one-Q_one-sp.Rational(1,4)*p_one**2
one_verified = verify_exact('Exceptional N=1',LHS_one-RHS_one,ctx_one,map_one)
print('All exact local identities passed; signs and telescoping follow the accompanying domain argument.')
