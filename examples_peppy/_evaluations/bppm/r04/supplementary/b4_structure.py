# This saved notebook fragment shares its caller's execution namespace.
# These names are supplied by the notebook cells or serialized proof source.
# ty: ignore[unresolved-reference]
# ruff: noqa: F821


def V_k_structure(k):
    basis_k = V_k_basis(k)
    C = coeff_by_k[k]
    quadratic = sum(
        (float(C[i, j]) * basis_k[i] * basis_k[j] for i, j in np.ndindex(C.shape)),
        pf.Scalar.zero(),
    )
    f_local = next(q for q in ctx.func_to_triplets if str(q) == "f")
    h_local = next(q for q in ctx.func_to_triplets if str(q) == "h")
    sample = function_samples[k]
    return (
        quadratic
        + sample["h"] * (h_local(ctx["x_0"]) - h_local(ctx[f"x_{k}"]))
        + sample["f"] * (f_local(ctx[f"x_{k}"]) - f_local(ctx["x_star"]))
        + sample["offset"]
    )


for k in required_indices:
    diff = pm.eval_scalar(V_k_structure(k) - lyap[k])
    ev = pm.eval_scalar(lyap[k])
    component_residuals[str(k)] = {}
    for label, residual, target in (
        ("gram", diff.inner_prod_coords, ev.inner_prod_coords),
        ("function", diff.func_coords, ev.func_coords),
        ("offset", diff.offset, ev.offset),
    ):
        error = max_abs(residual)
        assert error <= 1e-4 + 1e-5 * max_abs(target)
        component_residuals[str(k)][label] = error
    print("Full expression reconstruction k=", k, component_residuals[str(k)])
