# This saved notebook fragment shares its caller's execution namespace.
# These names are supplied by the notebook cells or serialized proof source.
# ty: ignore[unresolved-reference]
# ruff: noqa: F821

component_residuals = {}
for k in required_indices:
    diff = pm.eval_scalar(V_k_structure(k) - lyap[k])
    target = pm.eval_scalar(lyap[k])
    component_residuals[str(k)] = {}
    for name, residual, target_component in [
        ("gram", diff.inner_prod_coords, target.inner_prod_coords),
        ("function", diff.func_coords, target.func_coords),
        ("offset", diff.offset, target.offset),
    ]:
        residual = np.asarray(residual, dtype=float)
        target_component = np.asarray(target_component, dtype=float)
        error = float(np.max(np.abs(residual), initial=0))
        scale = float(np.max(np.abs(target_component), initial=0))
        assert np.all(np.isfinite(residual))
        assert error <= 1e-4 + 1e-5 * scale
        component_residuals[str(k)][name] = error
print("Full-component reconstruction passed at all indices:", required_indices)
