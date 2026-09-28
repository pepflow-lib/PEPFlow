ctx_step=pf.PEPContext('symbolic_step').set_as_current()
L_step=pf.Parameter('L_symbolic')
N_step=pf.Parameter('N_symbolic')
i_step=pf.Parameter('i_symbolic')
f_step=pf.SmoothConvexFunction(is_basis=True,tags=['f_{step}'],L=L_step)
g_step=pf.ConvexFunction(is_basis=True,tags=['g_{step}'])
h_step=f_step+g_step
xs_step=h_step.set_stationary_point('x_{star}')
x0_step=pf.Vector(is_basis=True,tags=['x_{0}'])
xp_step=pf.Vector(is_basis=True,tags=['x_{i-1}'])
xn_step=g_step.prox(xp_step-f_step.grad(xp_step)/L_step,1/L_step,tag='x_{i}')
V_previous=analytic_potential(xp_step,f_step,g_step,xs_step,x0_step,i_step-1,N_step,L_step)
V_current=analytic_potential(xn_step,f_step,g_step,xs_step,x0_step,i_step,N_step,L_step)
RHS_step=local_contribution(f_step,g_step,xp_step,xn_step,xs_step,i_step,N_step,L_step)
LHS_step=V_current-V_previous
diff_step=LHS_step-RHS_step
pm_step=pf.ExpressionManager(ctx_step,resolve_parameters={'L_symbolic':ell_symbol,'N_symbolic':n_symbol,'i_symbolic':i_symbol})
step_verified=verify_identity('Interior step',diff_step,pm_step)
# Derive the current coefficient functions by solving every scalar-component equation.
unknown_names=[f'c{r}{s}' for r in range(4) for s in range(r,4)]+['Af','Bg']
unknown_symbols=sp.symbols(' '.join(unknown_names),real=True)
unknown_parameters={name:pf.Parameter(name) for name in unknown_names}
resolve_unknown={'L_symbolic':ell_symbol,'N_symbolic':n_symbol,'i_symbolic':i_symbol,**dict(zip(unknown_names,unknown_symbols))}
vectors=[f_step.grad(xs_step),x0_step-xs_step,xn_step-xs_step,f_step.grad(xn_step)-f_step.grad(xs_step)]
V_unknown=pf.Scalar.zero()
for r in range(4):
    for s in range(r,4):
        V_unknown+=(1 if r==s else 2)*unknown_parameters[f'c{r}{s}']*vectors[r]*vectors[s]
V_unknown+=unknown_parameters['Af']*(f_step(xn_step)-f_step(xs_step))
V_unknown+=unknown_parameters['Bg']*(g_step(xn_step)-g_step(xs_step))
unknown_manager=pf.ExpressionManager(ctx_step,resolve_parameters=resolve_unknown)
unknown_gram,unknown_func,unknown_offset=symbolic_components(V_unknown-V_previous-RHS_step,unknown_manager)
coefficient_equations=[sp.Eq(value,0) for value in [*unknown_gram,*unknown_func,unknown_offset] if value!=0]
print('All nonzero coefficient equations:',coefficient_equations)
coefficient_solution=sp.solve(coefficient_equations,unknown_symbols,dict=True)
assert len(coefficient_solution)==1
print('Derived current coefficient functions:')
for variable,value in coefficient_solution[0].items():
    print(variable,sp.factor(value))
