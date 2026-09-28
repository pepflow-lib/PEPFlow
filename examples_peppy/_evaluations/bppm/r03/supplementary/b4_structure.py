# This saved notebook fragment shares its caller's execution namespace.
# These names are supplied by the notebook cells or serialized proof source.
# ty: ignore[unresolved-reference]
# ruff: noqa: F821


def V_k_structure(k):
    if k == 0:
        return pf.Scalar.zero()
    vectors = V_k_basis(k)
    C = coeff_by_k[k]
    quadratic = sum(
        (float(C[i, j]) * vectors[i] * vectors[j] for i, j in np.ndindex(C.shape)),
        pf.Scalar.zero(),
    )
    return (
        quadratic
        + (k / N_int) * (f_obj(ctx[f"x_{k}"]) - f_obj(ctx["x_star"]))
        + (h_obj(ctx["x_0"]) - h_obj(ctx[f"x_{k}"])) / (params_sp["alpha"] * N_int)
    )


component_residuals = {}
for k in range(N_int + 1):
    difference = pm.eval_scalar(V_k_structure(k) - lyap[k])
    target = pm.eval_scalar(lyap[k])
    component_residuals[str(k)] = {}
    for name, residual, target_component in (
        ("gram", difference.inner_prod_coords, target.inner_prod_coords),
        ("function", difference.func_coords, target.func_coords),
        ("offset", difference.offset, target.offset),
    ):
        error = float(np.max(np.abs(np.asarray(residual, dtype=float)), initial=0))
        scale = float(
            np.max(np.abs(np.asarray(target_component, dtype=float)), initial=0)
        )
        assert error <= 1e-5 + 1e-5 * scale, (k, name, error)
        component_residuals[str(k)][name] = error
    print(f"k={k} full component residuals:", component_residuals[str(k)])
    print(
        "function terms:",
        []
        if k == 0
        else [
            f"{k}/{N_int}*(f(x_{k})-f(x_star))",
            f"1/(alpha*{N_int})*(h(x_0)-h(x_{k}))",
        ],
        "offset: 0",
    )
