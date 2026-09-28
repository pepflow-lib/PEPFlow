ctx_terminal=pf.PEPContext('bppm_symbolic_terminal').set_as_current()
f_terminal=pf.ConvexFunction(is_basis=True,tags=['f_{terminal}'])
h_terminal=pf.ConvexFunction(is_basis=True,tags=['h_{terminal}'])
xs_terminal=f_terminal.set_stationary_point('x_{star,terminal}')
x0_terminal=pf.Vector(is_basis=True,tags=['x_{0,terminal}'])
xN_terminal=pf.Vector(is_basis=True,tags=['x_{N,terminal}'])
D0_terminal=bregman(h_terminal,xs_terminal,x0_terminal)
DN_terminal=bregman(h_terminal,xs_terminal,xN_terminal)
gap_terminal=f_terminal(xN_terminal)-f_terminal(xs_terminal)
VN_terminal=gap_terminal+(DN_terminal-D0_terminal)/(alpha_parameter*N_parameter)
initial_residual=D0_terminal-R_parameter
terminal_residual=h_terminal.interp_ineq(xs_terminal,xN_terminal)
LHS_boundary=gap_terminal-R_parameter/(alpha_parameter*N_parameter)
RHS_boundary=VN_terminal+(initial_residual+terminal_residual)/(alpha_parameter*N_parameter)
pm_terminal=pf.ExpressionManager(ctx_terminal,resolve_parameters=symbolic_parameters)
boundary_check=exact_check('Boundary',LHS_boundary,RHS_boundary,pm_terminal,ctx_terminal)
for multiplier in expected.values():
    assert sp.simplify(multiplier).is_nonnegative is True
assert (1/(alpha_symbol*N_symbol)).is_positive is True
print('Signs: all local multipliers nonnegative for integer k>=0, N>=1, alpha>0; initial and terminal multipliers positive.')
print('Domain: interior steps 1<=k<N, separate base k=0; N=1 uses base and terminal only. R>=0; no division by R.')
print('Normalization: V0=0, VN<=0, initial_residual<=0, terminal_residual=-D_h(x_star,x_N)<=0 imply gap<=R/(alpha*N).')
