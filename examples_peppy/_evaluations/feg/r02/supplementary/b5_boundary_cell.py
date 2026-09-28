ctx_terminal=pf.PEPContext('feg_symbolic_terminal').set_as_current()
A_terminal=pf.LipschitzMonotoneOperator(is_basis=True,tags=['A_{boundary}'],L=Lp)
x0_terminal=pf.Vector(is_basis=True,tags=['x_{0}'])
xN_terminal=pf.Vector(is_basis=True,tags=['x_{N}'])
xs_terminal=A_terminal.set_zero_point('x_{star}')
gN_terminal=A_terminal(xN_terminal)
V_terminal=2*gN_terminal**2+4*Lp/Np*gN_terminal*(xN_terminal-x0_terminal)
mon_terminal=-gN_terminal*(xN_terminal-xs_terminal)
S_terminal=(gN_terminal-2*Lp/Np*(x0_terminal-xs_terminal))**2
init_terminal=(x0_terminal-xs_terminal)**2-Rp**2
boundary_LHS=gN_terminal**2-4*Lp**2*Rp**2/Np**2
boundary_RHS=V_terminal+4*Lp/Np*mon_terminal-S_terminal+4*Lp**2/Np**2*init_terminal
boundary_diff=boundary_LHS-boundary_RHS
pm_terminal=pf.ExpressionManager(ctx_terminal,resolve_parameters={'N_symbolic':N_symbol,'L_symbolic':L_symbol,'R_symbolic':R_symbol})
boundary_verified=verify_exact('Symbolic boundary',boundary_diff,pm_terminal,ctx_terminal)
assert expected['mu'].is_positive and expected['nu'].is_positive
assert (4*L_symbol/N_symbol).is_positive and (4*L_symbol**2/N_symbol**2).is_positive
print('Signs: k>=1, N>=1, L>0; all residual multipliers positive, terminal square subtracted. R>=0.')
print('Base V1<=0, steps V(k+1)<=V(k), terminal identity implies ||A(xN)||^2<=4 L^2 R^2/N^2, including N=1.')
