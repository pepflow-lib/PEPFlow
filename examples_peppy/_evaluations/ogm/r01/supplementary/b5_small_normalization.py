# N=1 is covered directly: theta_0=1, theta_1=2, x_1=x_0-3g_0/(2L).
small_ctx=pf.PEPContext('ogm_symbolic_N1').set_as_current()
small_f=pf.SmoothConvexFunction(is_basis=True,tags=['f_{N=1}'],L=L_proof)
small_x=pf.Vector(is_basis=True,tags=['x_{0}'])
small_f.set_stationary_point('x_{star}')
small_star=small_ctx['x_{star}']
small_g=small_f.grad(small_x)
small_z1=small_x-2/L_proof*small_g
small_x1=small_x-sp.Rational(3,2)/L_proof*small_g
small_g1=small_f.grad(small_x1)
small_final=4*(small_f(small_x1)-small_f(small_star))+L_proof/2*(small_z1-small_star-2/L_proof*small_g1)**2
small_LHS=small_final-L_proof/2*(small_x-small_star)**2
small_RHS=2*interpolation_residual(small_f,small_star,small_x)+2*interpolation_residual(small_f,small_star,small_x1)+2*interpolation_residual(small_f,small_x,small_x1)
small_diff=small_LHS-small_RHS
small_pm=pf.ExpressionManager(small_ctx,resolve_parameters={'L_proof':ell_sym})
symbolic_results['N1']=assert_exact('N=1 direct certificate',small_diff,small_pm,small_ctx)
# Radius normalization is an identity, and the initial residual is nonpositive.
R_proof=pf.Parameter('R_proof')
normalization_LHS=L_proof/(2*s_proof**2)*(small_x-small_star)**2-L_proof*R_proof**2/(2*s_proof**2)
normalization_RHS=L_proof/(2*s_proof**2)*((small_x-small_star)**2-R_proof**2)
normalization_diff=normalization_LHS-normalization_RHS
normalization_pm=pf.ExpressionManager(small_ctx,resolve_parameters={'L_proof':ell_sym,'s_proof':T_sym,'R_proof':R_sym})
symbolic_results['normalization']=assert_exact('Radius normalization',normalization_diff,normalization_pm,small_ctx)
print('Signs: L>0, theta_j>=1, theta_N>=2, so every local multiplier and square coefficient is nonnegative.')
print('Each interpolation residual is nonpositive by convex L-smooth interpolation. Hence the potentials decrease.')
