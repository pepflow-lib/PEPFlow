ctx_terminal=pf.PEPContext('feg_symbolic_terminal').set_as_current()
A_terminal=pf.LipschitzMonotoneOperator(is_basis=True,tags=['A_{boundary}'],L=L_param)
x_initial=pf.Vector(is_basis=True,tags=['x_{0}'])
x_terminal=pf.Vector(is_basis=True,tags=['x_{N}'])
x_solution=A_terminal.set_zero_point('x_{star}')
g_terminal=A_terminal(x_terminal)
V_terminal=2*g_terminal**2+4*L_param/N_param*(g_terminal*(x_terminal-x_initial))
mon_terminal=-(g_terminal*(x_terminal-x_solution))
initial_residual=(x_initial-x_solution)**2-R_param**2
S_terminal=(g_terminal-2*L_param/N_param*(x_initial-x_solution))**2
LHS_terminal=g_terminal**2-4*L_param**2*R_param**2/N_param**2
RHS_terminal=V_terminal+4*L_param/N_param*mon_terminal+4*L_param**2/N_param**2*initial_residual-S_terminal
diff_terminal=LHS_terminal-RHS_terminal
pm_terminal=pf.ExpressionManager(ctx_terminal,resolve_parameters=params_symbolic)
boundary_check=verify_identity('Boundary',diff_terminal,pm_terminal,ctx_terminal)
print('All base, step and terminal coordinates are exactly zero on the symbolic domain.')
