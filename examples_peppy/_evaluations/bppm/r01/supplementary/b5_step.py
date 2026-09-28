# This saved notebook fragment shares its caller's execution namespace.
# These names are supplied by the notebook cells or serialized proof source.
# ty: ignore[unresolved-reference]
# ruff: noqa: F821

pm_step = pf.ExpressionManager(ctx_step, resolve_parameters=resolved_parameters)
# The original abstract LHS and RHS are evaluated after exact substitution.
proof_checks["step"] = verify_exact("Step", step_LHS - step_RHS, pm_step)
