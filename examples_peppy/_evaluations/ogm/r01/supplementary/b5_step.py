# Nonterminal transition: t=theta_j, s=theta_{j+1}, 0 <= j <= N-2.
step_ctx=pf.PEPContext('ogm_symbolic_step').set_as_current()
step_f=pf.SmoothConvexFunction(is_basis=True,tags=['f_{step}'],L=L_proof)
step_x=pf.Vector(is_basis=True,tags=['x_{j}'])
step_z=pf.Vector(is_basis=True,tags=['z_{j}'])
step_f.set_stationary_point('x_{star}')
step_star=step_ctx['x_{star}']
step_g=step_f.grad(step_x)
step_p=step_z-2*t_proof/L_proof*step_g
step_next=(1-1/s_proof)*(step_x-step_g/L_proof)+step_p/s_proof
step_gnext=step_f.grad(step_next)
step_q=step_p-2*s_proof/L_proof*step_gnext
Phi_old=2*t_proof**2*(step_f(step_x)-step_f(step_star))-t_proof**2/L_proof*step_g**2+L_proof/2*(step_p-step_star)**2
Phi_new=2*s_proof**2*(step_f(step_next)-step_f(step_star))-s_proof**2/L_proof*step_gnext**2+L_proof/2*(step_q-step_star)**2
step_LHS=Phi_new-Phi_old
step_RHS=2*s_proof*interpolation_residual(step_f,step_star,step_next)+2*t_proof**2*interpolation_residual(step_f,step_x,step_next)
step_diff=step_LHS-step_RHS
step_pm=pf.ExpressionManager(step_ctx,resolve_parameters={'L_proof':ell_sym,'t_proof':t_sym,'s_proof':s_sym})
symbolic_results['step']=assert_exact('Nonterminal step',step_diff,step_pm,step_ctx,t_sym**2-(s_sym**2-s_sym))
