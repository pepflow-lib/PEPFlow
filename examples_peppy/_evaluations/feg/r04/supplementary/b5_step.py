# Original step expressions with the derived coefficients substituted.
V_step=2*k_param**2/N_param**2*g_current**2+4*L_param*k_param/N_param**2*(g_current*q_current)
V_step_next=2*(k_param+1)**2/N_param**2*g_next**2+4*L_param*(k_param+1)/N_param**2*(g_next*q_next)
LHS_step=V_step_next-V_step
RHS_step=2*(k_param+1)**2/N_param**2*lip_step+4*L_param*k_param*(k_param+1)/N_param**2*mon_step
diff_step=LHS_step-RHS_step
pm_step=pf.ExpressionManager(ctx_step,resolve_parameters=params_symbolic)
step_check=verify_identity('Step',diff_step,pm_step,ctx_step)
