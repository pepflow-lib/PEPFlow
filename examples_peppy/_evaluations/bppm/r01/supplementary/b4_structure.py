# This saved notebook fragment shares its caller's execution namespace.
# These names are supplied by the notebook cells or serialized proof source.
# ty: ignore[unresolved-reference]
# ruff: noqa: F821


def V_k_structure(k):
    if k == 0:
        return pf.Scalar.zero()
    basis_k = V_k_basis(k)
    quadratic = sum(
        (
            float(coeff_by_k[k][i, j]) * basis_k[i] * basis_k[j]
            for i, j in np.ndindex(coeff_by_k[k].shape)
        ),
        pf.Scalar.zero(),
    )
    objective = next(owner for owner in ctx.func_to_triplets if str(owner) == "f")
    kernel = next(owner for owner in ctx.func_to_triplets if str(owner) == "h")
    cf, ch = function_coeff_by_k[k]
    return (
        quadratic
        + cf * (objective(ctx[f"x_{k}"]) - objective(ctx["x_star"]))
        + ch * (kernel(ctx["x_0"]) - kernel(ctx[f"x_{k}"]))
        + offset_by_k[k]
    )


component_residuals = {}
for k in range(N_int + 1):
    difference = pm.eval_scalar(V_k_structure(k) - lyap[k])
    target = pm.eval_scalar(lyap[k])
    component_residuals[str(k)] = {}
    for name, value, target_value in (
        ("gram", difference.inner_prod_coords, target.inner_prod_coords),
        ("function", difference.func_coords, target.func_coords),
        ("offset", np.asarray(difference.offset), np.asarray(target.offset)),
    ):
        error = float(np.max(np.abs(np.asarray(value, dtype=float)), initial=0.0))
        scale = float(
            np.max(np.abs(np.asarray(target_value, dtype=float)), initial=0.0)
        )
        assert error <= 1e-4 + 1e-5 * scale
        component_residuals[str(k)][name] = error
    print(f"k={k}: full-expression reconstruction", component_residuals[str(k)])
