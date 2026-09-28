ctx_step=pf.PEPContext('exact_step').set_as_current()
f_step=pf.ConvexFunction(is_basis=True,tags=['f_{step}'])
h_step=pf.ConvexFunction(is_basis=True,tags=['h_{step}'])
x_anchor=pf.Vector(is_basis=True,tags=['x_{0}'])
x_current=pf.Vector(is_basis=True,tags=['x_{k}'])
f_step.set_stationary_point('x_{star}')
x_star_step=ctx_step['x_{star}']
f_step(x_current)
x_next=f_step.bregman_prox(x_current,cast(Number,a_par),h_step,tag='x_{k+1}')
V_current=(divergence(h_step,x_star_step,x_current)-divergence(h_step,x_star_step,x_anchor))/(a_par*n_par)+k_par/n_par*(f_step(x_current)-f_step(x_star_step))
V_next=(divergence(h_step,x_star_step,x_next)-divergence(h_step,x_star_step,x_anchor))/(a_par*n_par)+(k_par+1)/n_par*(f_step(x_next)-f_step(x_star_step))
step_LHS=V_next-V_current
step_RHS=(convex_residual(f_step,x_star_step,x_next)/n_par
          +k_par/n_par*convex_residual(f_step,x_current,x_next)
          +(k_par+1)/(a_par*n_par)*convex_residual(h_step,x_next,x_current)
          +k_par/(a_par*n_par)*convex_residual(h_step,x_current,x_next))
diff_step=step_LHS-step_RHS
proof_checks['step']=verify_exact('Step',diff_step,ctx_step)
# Verify that the B4 coefficient structure is exactly this potential.
q0=x_anchor-x_star_step
qk=x_current-x_star_step
representation=(-q0*h_step.grad(x_anchor)+qk*h_step.grad(x_current)+h_step(x_anchor)-h_step(x_current))/(a_par*n_par)+k_par/n_par*(f_step(x_current)-f_step(x_star_step))
verify_exact('Coefficient structure',V_current-representation,ctx_step)
