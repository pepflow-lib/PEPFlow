ctx_boundary=pf.PEPContext('symbolic_boundary').set_as_current()
L_boundary=pf.Parameter('L_symbolic')
N_boundary=pf.Parameter('N_symbolic')
f_boundary=pf.SmoothConvexFunction(is_basis=True,tags=['f_{boundary}'],L=L_boundary)
g_boundary=pf.ConvexFunction(is_basis=True,tags=['g_{boundary}'])
xs_boundary=(f_boundary+g_boundary).set_stationary_point('x_{star}')
x0_boundary=pf.Vector(is_basis=True,tags=['x_{0}'])
xp_boundary=pf.Vector(is_basis=True,tags=['x_{N-1}'])
xn_boundary=g_boundary.prox(xp_boundary-f_boundary.grad(xp_boundary)/L_boundary,1/L_boundary,tag='x_{N}')
V_terminal=f_boundary(xn_boundary)-f_boundary(xs_boundary)+g_boundary(xn_boundary)-g_boundary(xs_boundary)-L_boundary/(4*N_boundary)*(x0_boundary-xs_boundary)**2
V_penultimate=analytic_potential(xp_boundary,f_boundary,g_boundary,xs_boundary,x0_boundary,N_boundary-1,N_boundary,L_boundary)
LHS_boundary=V_terminal-V_penultimate
RHS_boundary=local_contribution(f_boundary,g_boundary,xp_boundary,xn_boundary,xs_boundary,N_boundary,N_boundary,L_boundary,terminal=True)
diff_boundary=LHS_boundary-RHS_boundary
pm_boundary=pf.ExpressionManager(ctx_boundary,resolve_parameters={'L_symbolic':ell_symbol,'N_symbolic':n_symbol})
boundary_verified=verify_identity('Terminal, N>=2',diff_boundary,pm_boundary)
