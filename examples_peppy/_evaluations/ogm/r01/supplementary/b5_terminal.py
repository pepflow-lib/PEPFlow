# Special terminal transition: t=theta_{N-1}, s=theta_N, s^2-s=2t^2.
terminal_ctx=pf.PEPContext('ogm_symbolic_terminal').set_as_current()
terminal_f=pf.SmoothConvexFunction(is_basis=True,tags=['f_{terminal}'],L=L_proof)
terminal_x=pf.Vector(is_basis=True,tags=['x_{N-1}'])
terminal_z=pf.Vector(is_basis=True,tags=['z_{N-1}'])
terminal_f.set_stationary_point('x_{star}')
terminal_star=terminal_ctx['x_{star}']
terminal_g=terminal_f.grad(terminal_x)
terminal_p=terminal_z-2*t_proof/L_proof*terminal_g
terminal_next=(1-1/s_proof)*(terminal_x-terminal_g/L_proof)+terminal_p/s_proof
terminal_gnext=terminal_f.grad(terminal_next)
terminal_q=terminal_p-terminal_star-s_proof/L_proof*terminal_gnext
terminal_old=2*t_proof**2*(terminal_f(terminal_x)-terminal_f(terminal_star))-t_proof**2/L_proof*terminal_g**2+L_proof/2*(terminal_p-terminal_star)**2
terminal_Phi=s_proof**2*(terminal_f(terminal_next)-terminal_f(terminal_star))+L_proof/2*terminal_q**2
terminal_LHS=terminal_Phi-terminal_old
terminal_RHS=s_proof*interpolation_residual(terminal_f,terminal_star,terminal_next)+2*t_proof**2*interpolation_residual(terminal_f,terminal_x,terminal_next)
terminal_diff=terminal_LHS-terminal_RHS
terminal_pm=pf.ExpressionManager(terminal_ctx,resolve_parameters={'L_proof':ell_sym,'t_proof':t_sym,'s_proof':s_sym})
symbolic_results['terminal_step']=assert_exact('Terminal step',terminal_diff,terminal_pm,terminal_ctx,t_sym**2-(s_sym**2-s_sym)/2)
# The final potential controls the requested metric, without dropping a negative term.
boundary_LHS=terminal_Phi-s_proof**2*(terminal_f(terminal_next)-terminal_f(terminal_star))
boundary_RHS=L_proof/2*terminal_q**2
boundary_diff=boundary_LHS-boundary_RHS
symbolic_results['boundary']=assert_exact('Terminal metric identity',boundary_diff,terminal_pm,terminal_ctx)
