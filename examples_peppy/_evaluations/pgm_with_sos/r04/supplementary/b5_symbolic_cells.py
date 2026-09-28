# Symbolic local definitions. All coefficients remain exact.
k_sym, n_sym = sp.symbols('k N', integer=True, positive=True)
ell_sym = sp.Symbol('L', positive=True)
kp, np_, lp = pf.Parameter('k_symbolic'), pf.Parameter('N_symbolic'), pf.Parameter('L_symbolic')
symbolic_mapping = {'k_symbolic':k_sym,'N_symbolic':n_sym,'L_symbolic':ell_sym}

def interior_potential(x, anchor, star, ff, gg, k, n, ell):
    a, astar = ff.grad(x), ff.grad(star)
    return (-ell/(4*n)*anchor**2 + ell*(n-k)/(2*n-k)**2*(x-star)**2
            + (a-astar)**2/(2*ell*(2*n-k)) - (x-star)*a/(2*n-k)
            + (k+1)/(2*n-k)*(ff(x)-ff(star)) + k/(2*n-k)*(gg(x)-gg(star)))

def If(ff,u,v,ell):
    return ff(v)-ff(u)+ff.grad(v)*(u-v)+(ff.grad(u)-ff.grad(v))**2/(2*ell)

def Ig(gg,u,v):
    return gg(v)-gg(u)+gg.grad(v)*(u-v)

def alpha(i,n):
    return i/(2*n+1-i)

def beta(i,n):
    return i/(2*n-i)

def local_square_piece(x,y,star,ff,gg,i,n,ell):
    ap,a,astar,s = ff.grad(x),ff.grad(y),ff.grad(star),gg.grad(y)
    c1 = n/((2*n+1-i)*(2*n-i)*ell)
    c2 = ((i-1)/(2*n-i)*(2*n+2)/(2*n+1)+2*n/((2*n-i)**2*(2*n+1)))/(2*ell)
    c3 = i/(2*n+1-i)*(2*n)/(2*n+1)/(2*ell)
    u1 = i/(2*n)*a+(2*n-i)/(2*n)*ap-astar
    u2 = ap+s-ell/(2*n+1-i)*(x-star)
    u3 = (2*n+1)/(2*n)*(a+s)-(ap+s)/(2*n)-ell/(2*n-i)*(y-star)
    return c1*u1**2+c2*u2**2+c3*u3**2

def exact_components(expression,manager):
    value = manager.eval_scalar(expression,sympy_mode=True)
    gram = sp.Matrix(value.inner_prod_coords).applyfunc(lambda z:sp.factor(sp.cancel(z)))
    funcs = sp.Matrix(list(value.func_coords)).applyfunc(lambda z:sp.factor(sp.cancel(z)))
    offset = sp.factor(sp.cancel(sp.sympify(value.offset)))
    return gram,funcs,offset

def check_exact(name,expression,manager,context):
    gram,funcs,offset = exact_components(expression,manager)
    assert all(z == 0 for z in [*gram,*funcs,offset]), (name,gram,funcs,offset)
    print(name, 'all Gram/function/offset residuals exactly zero')
    pf.pprint_labeled_matrix(np.array(gram.tolist(),dtype=object),[str(v) for v in context.basis_vectors()])
    pf.pprint_labeled_matrix(np.array(funcs.tolist(),dtype=object),[str(v) for v in context.basis_scalars()],['residual'])
    print('constant residual:',offset)
    return {'gram_shape':list(gram.shape),'function_shape':list(funcs.shape),'offset':str(offset),'exact_zero':True}

# SECTION symbolic_step
ctx_step = pf.PEPContext('symbolic_step').set_as_current()
f_step = pf.SmoothConvexFunction(is_basis=True,tags=['f_{step}'],L=lp)
g_step = pf.ConvexFunction(is_basis=True,tags=['g_{step}'])
star_step = (f_step+g_step).set_stationary_point('x_{star,step}')
x_step = pf.Vector(is_basis=True,tags=['x_{k}'])
anchor_step = pf.Vector(is_basis=True,tags=['d_{0}'])
y_step = g_step.prox(x_step-f_step.grad(x_step)/lp,1/lp,tag='x_{k+1}')
f_step(y_step)
i_step = kp+1
LHS_step = interior_potential(y_step,anchor_step,star_step,f_step,g_step,kp+1,np_,lp)-interior_potential(x_step,anchor_step,star_step,f_step,g_step,kp,np_,lp)
RHS_step = ((alpha(i_step+1,np_)-alpha(i_step,np_))*If(f_step,star_step,y_step,lp)
            + alpha(i_step,np_)*If(f_step,x_step,y_step,lp)
            + (beta(i_step,np_)-beta(i_step-1,np_))*Ig(g_step,star_step,y_step)
            + beta(i_step-1,np_)*Ig(g_step,x_step,y_step)
            - local_square_piece(x_step,y_step,star_step,f_step,g_step,i_step,np_,lp))
diff_step = LHS_step-RHS_step
pm_step = pf.ExpressionManager(ctx_step,resolve_parameters=symbolic_mapping)
step_evidence = check_exact('Interior step: 1 <= k <= N-2',diff_step,pm_step,ctx_step)

# SECTION symbolic_base
ctx_base = pf.PEPContext('symbolic_base').set_as_current()
f_base = pf.SmoothConvexFunction(is_basis=True,tags=['f_{base}'],L=lp)
g_base = pf.ConvexFunction(is_basis=True,tags=['g_{base}'])
star_base = (f_base+g_base).set_stationary_point('x_{star,base}')
x_base = pf.Vector(is_basis=True,tags=['x_{0,base}'])
y_base = g_base.prox(x_base-f_base.grad(x_base)/lp,1/lp,tag='x_{1,base}')
f_base(y_base)
LHS_base = interior_potential(y_base,x_base-star_base,star_base,f_base,g_base,sp.Integer(1),np_,lp)
RHS_base = (alpha(sp.Integer(1),np_)*If(f_base,star_base,x_base,lp)
            + (alpha(sp.Integer(2),np_)-alpha(sp.Integer(1),np_))*If(f_base,star_base,y_base,lp)
            + alpha(sp.Integer(1),np_)*If(f_base,x_base,y_base,lp)
            + beta(sp.Integer(1),np_)*Ig(g_base,star_base,y_base)
            - local_square_piece(x_base,y_base,star_base,f_base,g_base,sp.Integer(1),np_,lp))
diff_base = LHS_base-RHS_base
pm_base = pf.ExpressionManager(ctx_base,resolve_parameters=symbolic_mapping)
base_evidence = check_exact('Base: N >= 2',diff_base,pm_base,ctx_base)

# SECTION symbolic_boundary
ctx_terminal = pf.PEPContext('symbolic_terminal').set_as_current()
f_terminal = pf.SmoothConvexFunction(is_basis=True,tags=['f_{terminal}'],L=lp)
g_terminal = pf.ConvexFunction(is_basis=True,tags=['g_{terminal}'])
star_terminal = (f_terminal+g_terminal).set_stationary_point('x_{star,terminal}')
x_terminal = pf.Vector(is_basis=True,tags=['x_{N-1}'])
anchor_terminal = pf.Vector(is_basis=True,tags=['d_{0,terminal}'])
y_terminal = g_terminal.prox(x_terminal-f_terminal.grad(x_terminal)/lp,1/lp,tag='x_{N}')
f_terminal(y_terminal)
V_terminal = f_terminal(y_terminal)-f_terminal(star_terminal)+g_terminal(y_terminal)-g_terminal(star_terminal)-lp/(4*np_)*anchor_terminal**2
LHS_terminal = V_terminal-interior_potential(x_terminal,anchor_terminal,star_terminal,f_terminal,g_terminal,np_-1,np_,lp)
RHS_terminal = ((1-alpha(np_,np_))*If(f_terminal,star_terminal,y_terminal,lp)
                + alpha(np_,np_)*If(f_terminal,x_terminal,y_terminal,lp)
                + (1-beta(np_-1,np_))*Ig(g_terminal,star_terminal,y_terminal)
                + beta(np_-1,np_)*Ig(g_terminal,x_terminal,y_terminal)
                - local_square_piece(x_terminal,y_terminal,star_terminal,f_terminal,g_terminal,np_,np_,lp))
diff_terminal = LHS_terminal-RHS_terminal
pm_terminal = pf.ExpressionManager(ctx_terminal,resolve_parameters=symbolic_mapping)
boundary_evidence = check_exact('Terminal: N >= 2',diff_terminal,pm_terminal,ctx_terminal)

# SECTION symbolic_n1
ctx_one = pf.PEPContext('symbolic_one').set_as_current()
f_one = pf.SmoothConvexFunction(is_basis=True,tags=['f_{one}'],L=lp)
g_one = pf.ConvexFunction(is_basis=True,tags=['g_{one}'])
star_one = (f_one+g_one).set_stationary_point('x_{star,one}')
x_one = pf.Vector(is_basis=True,tags=['x_{0,one}'])
y_one = g_one.prox(x_one-f_one.grad(x_one)/lp,1/lp,tag='x_{1,one}')
f_one(y_one)
one = sp.Integer(1)
LHS_one = f_one(y_one)-f_one(star_one)+g_one(y_one)-g_one(star_one)-lp/4*(x_one-star_one)**2
RHS_one = (sp.Rational(1,2)*If(f_one,star_one,x_one,lp)
           + sp.Rational(1,2)*If(f_one,star_one,y_one,lp)
           + sp.Rational(1,2)*If(f_one,x_one,y_one,lp)
           + Ig(g_one,star_one,y_one)
           - local_square_piece(x_one,y_one,star_one,f_one,g_one,one,one,lp))
diff_one = LHS_one-RHS_one
pm_one = pf.ExpressionManager(ctx_one,resolve_parameters=symbolic_mapping)
one_evidence = check_exact('Exceptional horizon N=1',diff_one,pm_one,ctx_one)
