# This saved notebook fragment shares its caller's execution namespace.
# These names are supplied by the notebook cells or serialized proof source.
# ty: ignore[unresolved-reference]
# ruff: noqa: F821

component_residuals = {}
for k in required_indices:
    ev = pm.eval_scalar(V_k_structure(k) - lyap[k])
    target = pm.eval_scalar(lyap[k])
    component_residuals[str(k)] = {}
    for name, delta, base in [
        ("gram", ev.inner_prod_coords, target.inner_prod_coords),
        ("function", ev.func_coords, target.func_coords),
        ("offset", ev.offset, target.offset),
    ]:
        error = float(np.max(np.abs(np.asarray(delta, dtype=float)), initial=0))
        scale = float(np.max(np.abs(np.asarray(base, dtype=float)), initial=0))
        assert error <= 1e-4 + 1e-5 * scale
        component_residuals[str(k)][name] = error
print("Full-component reconstruction at every index:", component_residuals)
