ctx_step=pf.PEPContext('bppm_symbolic_step').set_as_current()
f_step=pf.ConvexFunction(is_basis=True,tags=['f_{step}'])
h_step=pf.ConvexFunction(is_basis=True,tags=['h_{step}'])
xs_step=f_step.set_stationary_point('x_{star,step}')
x0_step=pf.Vector(is_basis=True,tags=['x_{0,step}'])
xk_step=pf.Vector(is_basis=True,tags=['x_{k}'])
xp_step=pf.Vector(is_basis=True,tags=['x_{k+1}'])
gp_step=f_step.grad(xp_step)
h_step.add_point_with_grad_restriction(xp_step,h_step.grad(xk_step)-alpha_parameter*gp_step)
D0_step=bregman(h_step,xs_step,x0_step)
Vk_step=k_parameter/N_parameter*(f_step(xk_step)-f_step(xs_step))+(bregman(h_step,xs_step,xk_step)-D0_step)/(alpha_parameter*N_parameter)
Vp_step=(k_parameter+1)/N_parameter*(f_step(xp_step)-f_step(xs_step))+(bregman(h_step,xs_step,xp_step)-D0_step)/(alpha_parameter*N_parameter)
Q_star=f_step.interp_ineq(xs_step,xp_step)
Q_forward=f_step.interp_ineq(xk_step,xp_step)
H_reverse=h_step.interp_ineq(xp_step,xk_step)
H_forward=h_step.interp_ineq(xk_step,xp_step)
mu_symbols=sp.symbols('mu_star mu_f mu_reverse mu_forward',real=True)
mu_parameters=[pf.Parameter(str(s)) for s in mu_symbols]
LHS_step=Vp_step-Vk_step
RHS_unknown=sum((m*q for m,q in zip(mu_parameters,(Q_star,Q_forward,H_reverse,H_forward))),pf.Scalar.zero())
unknown_parameters: dict[str, Any] = {**symbolic_parameters,**{str(s):s for s in mu_symbols}}
pm_unknown=pf.ExpressionManager(ctx_step,resolve_parameters=unknown_parameters)
gram_eq,function_eq,offset_eq=symbolic_components(LHS_step-RHS_unknown,pm_unknown)
equations=[term for term in [*gram_eq,*function_eq,offset_eq] if term!=0]
solutions=sp.solve(equations,mu_symbols,dict=True)
expected={mu_symbols[0]:1/N_symbol,mu_symbols[1]:k_symbol/N_symbol,mu_symbols[2]:(k_symbol+1)/(alpha_symbol*N_symbol),mu_symbols[3]:k_symbol/(alpha_symbol*N_symbol)}
assert len(solutions)==1
assert all(sp.simplify(solutions[0][key]-value)==0 for key,value in expected.items())
print('Exact local multiplier solution:',solutions[0])
RHS_step=Q_star/N_parameter+k_parameter/N_parameter*Q_forward+(k_parameter+1)/(alpha_parameter*N_parameter)*H_reverse+k_parameter/(alpha_parameter*N_parameter)*H_forward
pm_step=pf.ExpressionManager(ctx_step,resolve_parameters=symbolic_parameters)
step_check=exact_check('Step',LHS_step,RHS_step,pm_step,ctx_step)

