ctx_terminal=pf.PEPContext('feg_symbolic_terminal').set_as_current()
A_boundary=pf.LipschitzMonotoneOperator(is_basis=True,tags=['A_{boundary}'],L=LL)
x0_terminal=pf.Vector(is_basis=True,tags=['x_{0}'])
xN_terminal=pf.Vector(is_basis=True,tags=['x_{N}'])
xstar_terminal=A_boundary.set_zero_point('x_{star}')
gN_terminal=A_boundary(xN_terminal)
VN_terminal=2*gN_terminal**2+4*LL/NN*gN_terminal*(xN_terminal-x0_terminal)
Mon_terminal=-gN_terminal*(xN_terminal-xstar_terminal)
initial_residual=(x0_terminal-xstar_terminal)**2-RR**2
S_terminal=(2*LL/NN*(x0_terminal-xstar_terminal)-gN_terminal)**2
LHS_boundary=gN_terminal**2-4*LL**2*RR**2/NN**2
RHS_boundary=VN_terminal+4*LL/NN*Mon_terminal-S_terminal+4*LL**2/NN**2*initial_residual
diff_boundary=LHS_boundary-RHS_boundary
pm_terminal=pf.ExpressionManager(ctx_terminal,resolve_parameters=params_symbolic)
boundary_verified=verify_exact('Boundary',diff_boundary,pm_terminal,ctx_terminal)

# All denominators are nonzero for N>=1, k>=1, L>0.
# The initial residual is <=0, monotonicity residuals are <=0,
# Lipschitz residuals are <=0, and S_terminal is a squared norm >=0.
mu_lip=2*(k_sp+1)**2/N_sp**2
mu_mon=4*L_sp*k_sp*(k_sp+1)/N_sp**2
mu_base=2/N_sp**2
mu_terminal=4*L_sp/N_sp
mu_initial=4*L_sp**2/N_sp**2
assert all(coefficient.is_positive is True for coefficient in [mu_lip,mu_mon,mu_base,mu_terminal,mu_initial])
assert (k_sp+1).is_positive and N_sp.is_positive and L_sp.is_positive
signs_verified=True
domain_verified=True
normalization_verified=boundary_verified
print('Positive multipliers and nonzero denominators certified for k>=1,N>=1,L>0; R>=0.')
print('Base V1<=V0=0, steps V(k+1)<=Vk, boundary metric-target<=VN, hence metric<=4 L^2 R^2/N^2.')
print('For N=1 the interior step range is empty; the same base and terminal identities apply.')
