# This saved notebook fragment shares its caller's execution namespace.
# These names are supplied by the notebook cells or serialized proof source.
# ty: ignore[unresolved-reference]
# ruff: noqa: F821


def V_k_structure(k):
    vectors = V_k_basis(k)
    C = coeff_by_k[k]
    quadratic = sum(
        (float(C[i, j]) * vectors[i] * vectors[j] for i, j in np.ndindex(C.shape)),
        pf.Scalar.zero(),
    )
    function = next(iter(ctx.func_to_triplets))
    return quadratic + function_sample_coefficients[k] * (
        function(ctx[f"x_{k}"]) - function(ctx["x_star"])
    )


component_residuals = {}
for k in range(N_int + 1):
    diff = pm.eval_scalar(V_k_structure(k) - lyap[k])
    target = pm.eval_scalar(lyap[k])
    component_residuals[str(k)] = {}
    for name, residual, target_component in (
        ("gram", diff.inner_prod_coords, target.inner_prod_coords),
        ("function", diff.func_coords, target.func_coords),
        ("offset", diff.offset, target.offset),
    ):
        residual = np.asarray(residual, dtype=float)
        scale = float(
            np.max(np.abs(np.asarray(target_component, dtype=float)), initial=0)
        )
        error = float(np.max(np.abs(residual), initial=0))
        assert error <= 1e-4 + 1e-5 * scale
        component_residuals[str(k)][name] = error
print("All-index full-component reconstruction:", component_residuals)
