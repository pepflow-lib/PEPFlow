# This saved notebook fragment shares its caller's execution namespace.
# These names are supplied by the notebook cells or serialized proof source.
# ty: ignore[unresolved-reference]
# ruff: noqa: F821

# Exact formulas selected from the solved coefficient family with d=4L and e=-4L.
def V_closed(t, zz, xx, anchor, terminal, output, Lpar, Npar):
    return (
        -4 * Lpar / Npar * (anchor - terminal) * output
        - 2 * zz**2
        + 4 * Lpar / t * zz * (xx - terminal)
        - 4 * zz * output
        + 4 * Lpar / t * (xx - terminal) * output
    )


proof_checks = {}
ctx_der.set_as_current()
LHS = V_closed(Tp - 1, zp, xp, x0, xN, G, Lp, Np) - V_closed(
    Tp, z, x, x0, xN, G, Lp, Np
)
RHS = 2 / Tp**2 * lip + 4 * Lp / (Tp * (Tp - 1)) * mon
step_mapping: dict[str, Any] = {"t_exact": Ts, "N_exact": Ns, "L_exact": Ls}
pm_step = pf.ExpressionManager(ctx_der, resolve_parameters=step_mapping)
proof_checks["step"] = verify_exact("Interior step (t>=2)", LHS, RHS, pm_step)
