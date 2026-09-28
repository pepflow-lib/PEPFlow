# Separate actual initial step, including the radius normalization.
ctx_base=pf.PEPContext('bppm_symbolic_base').set_as_current()
f_base=pf.ConvexFunction(is_basis=True,tags=['f_{base}'])
h_base=pf.ConvexFunction(is_basis=True,tags=['h_{base}'])
x0_base=pf.Vector(is_basis=True,tags=['x_{0}'])
xs_base=f_base.set_stationary_point('x_{star}')
x1_base=prox_step(f_base,x0_base,alpha_par,h_base,'x_{1}')
D0_base=D_of(h_base,xs_base,x0_base)
V0_base=(D0_base-D0_base)/(alpha_par*N_par)
V1_base=(f_base(x1_base)-f_base(xs_base))/N_par+(D_of(h_base,xs_base,x1_base)-D0_base)/(alpha_par*N_par)
rf_base=f_base(x1_base)-f_base(xs_base)+f_base.grad(x1_base)*(xs_base-x1_base)
rh_base=h_base(x0_base)-h_base(x1_base)+h_base.grad(x0_base)*(x1_base-x0_base)
base_LHS=V1_base-V0_base
base_RHS=rf_base/N_par+rh_base/(alpha_par*N_par)
diff_base=base_LHS-base_RHS
pm_base=symbolic_manager(ctx_base,symbolic_params)
base_verified=exact_check('Initial step',diff_base,pm_base,ctx_base)
zero_base_verified=exact_check('Initial value V_0',V0_base,pm_base,ctx_base)
initial_energy=D0_base
initial_residual=D0_base-R_par
initial_bound_verified=exact_check('Initial radius normalization',(initial_energy-R_par)-initial_residual,pm_base,ctx_base)
