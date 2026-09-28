# Solve the exact coefficient equations in the sparsity pattern suggested by B4.
ctx_derive = pf.PEPContext('pgm_coefficient_derivation').set_as_current()
f_derive = pf.SmoothConvexFunction(is_basis=True,tags=['f_{derive}'],L=LP)
g_derive = pf.ConvexFunction(is_basis=True,tags=['g_{derive}'])
xs_derive = (f_derive+g_derive).set_stationary_point('x_{star,derive}')
x_derive = pf.Vector(is_basis=True,tags=['x_{k,derive}'])
f_derive.grad(x_derive)
g_derive(x_derive)
xn_derive = g_derive.prox(x_derive-f_derive.grad(x_derive)/LP,1/LP,tag='x_{k+1,derive}')
f_derive.grad(xn_derive)
unknown_names = ['A_k','B_k','C_k','alpha_k','beta_k','A_next','B_next','C_next','alpha_next','beta_next']
unknown_symbols = sp.symbols(' '.join(unknown_names),real=True)
unknown_parameters = [pf.Parameter(name) for name in unknown_names]


def coefficient_ansatz(fun,convex,x,xstar,coefficients):
    aa,bb,cc,ff,gg = coefficients
    r = x-xstar
    a,ast = fun.grad(x),fun.grad(xstar)
    return aa*r**2+bb*(a-ast)**2+cc*r*a+ff*(fun(x)-fun(xstar))+gg*(convex(x)-convex(xstar))


derive_LHS = coefficient_ansatz(f_derive,g_derive,xn_derive,xs_derive,unknown_parameters[5:])-coefficient_ansatz(f_derive,g_derive,x_derive,xs_derive,unknown_parameters[:5])
derive_RHS = ((2*NP+1)/((2*NP-KP-1)*(2*NP-KP))*residual_f(f_derive,xs_derive,xn_derive)
    +(KP+1)/(2*NP-KP)*residual_f(f_derive,x_derive,xn_derive)
    +2*NP/((2*NP-KP-1)*(2*NP-KP))*residual_g(g_derive,xs_derive,xn_derive)
    +KP/(2*NP-KP)*residual_g(g_derive,x_derive,xn_derive)
    -supplied_piece(f_derive,g_derive,x_derive,xn_derive,xs_derive,KP+1))
derive_parameters: dict[str,Any] = {**symbolic_parameters,**dict(zip(unknown_names,unknown_symbols))}
derive_manager = pf.ExpressionManager(ctx_derive,resolve_parameters=derive_parameters)
derive_gram,derive_functions,derive_offset = symbolic_components(derive_LHS-derive_RHS,derive_manager)
coefficient_equations = list(dict.fromkeys(value for value in [*derive_gram,*derive_functions,derive_offset] if value != 0))
coefficient_solutions = sp.solve(coefficient_equations,unknown_symbols,dict=True,simplify=False)
assert len(coefficient_solutions) == 1
coefficient_solution = {str(symbol):sp.factor(value) for symbol,value in coefficient_solutions[0].items()}
print('Derived coefficients from full-coordinate step equations:')
for name,value in coefficient_solution.items():
    print(name,'=',value)
expected_current = [L_sym*(N_sym-k_sym)/(2*N_sym-k_sym)**2,
                    1/(2*L_sym*(2*N_sym-k_sym)),-1/(2*N_sym-k_sym),
                    (k_sym+1)/(2*N_sym-k_sym),k_sym/(2*N_sym-k_sym)]
expected_next = [sp.cancel(value.subs(k_sym,k_sym+1)) for value in expected_current]
assert all(sp.cancel(coefficient_solutions[0][symbol]-expected)==0 for symbol,expected in zip(unknown_symbols,expected_current+expected_next))
assert all(sp.cancel(eq.subs(coefficient_solutions[0])) == 0 for eq in coefficient_equations)
# The recurrence leaves an additive constant multiple of ||r_0||^2.
# Determine it from the initial identity, then verify the terminal normalization.
ctx_anchor = pf.PEPContext('pgm_anchor_derivation').set_as_current()
f_anchor = pf.SmoothConvexFunction(is_basis=True,tags=['f_{anchor}'],L=LP)
g_anchor = pf.ConvexFunction(is_basis=True,tags=['g_{anchor}'])
xs_anchor = (f_anchor+g_anchor).set_stationary_point('x_{star,anchor}')
x0_anchor = pf.Vector(is_basis=True,tags=['x_{0,anchor}'])
f_anchor.grad(x0_anchor)
x1_anchor = g_anchor.prox(x0_anchor-f_anchor.grad(x0_anchor)/LP,1/LP,tag='x_{1,anchor}')
f_anchor.grad(x1_anchor)
t_anchor = pf.Parameter('t_anchor')
t_symbol = sp.Symbol('t_anchor',real=True)
anchor_coefficients = [LP*(NP-1)/(2*NP-1)**2,1/(2*LP*(2*NP-1)),-1/(2*NP-1),2/(2*NP-1),1/(2*NP-1)]
anchor_LHS = coefficient_ansatz(f_anchor,g_anchor,x1_anchor,xs_anchor,anchor_coefficients)+t_anchor*(x0_anchor-xs_anchor)**2
anchor_RHS = (residual_f(f_anchor,xs_anchor,x0_anchor)/(2*NP)
    +(2*NP+1)/((2*NP-1)*2*NP)*residual_f(f_anchor,xs_anchor,x1_anchor)
    +residual_f(f_anchor,x0_anchor,x1_anchor)/(2*NP)
    +residual_g(g_anchor,xs_anchor,x1_anchor)/(2*NP-1)
    -supplied_piece(f_anchor,g_anchor,x0_anchor,x1_anchor,xs_anchor,sp.S(1)))
anchor_parameters: dict[str,Any] = {**symbolic_parameters,'t_anchor':t_symbol}
anchor_manager = pf.ExpressionManager(ctx_anchor,resolve_parameters=anchor_parameters)
anchor_gram,anchor_functions,anchor_offset = symbolic_components(anchor_LHS-anchor_RHS,anchor_manager)
anchor_equations = [value for value in [*anchor_gram,*anchor_functions,anchor_offset] if value != 0]
anchor_solution = sp.solve(anchor_equations,t_symbol,dict=True)
assert anchor_solution == [{t_symbol:-L_sym/(4*N_sym)}]
print('Initial-distance coefficient:',anchor_solution)
