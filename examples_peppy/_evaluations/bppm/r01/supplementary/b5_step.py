pm_step=pf.ExpressionManager(ctx_step,resolve_parameters=resolved_parameters)
# The original abstract LHS and RHS are evaluated after exact substitution.
proof_checks['step']=verify_exact('Step',step_LHS-step_RHS,pm_step)
