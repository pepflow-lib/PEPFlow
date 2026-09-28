# This saved notebook fragment shares its caller's execution namespace.
# These names are supplied by the notebook cells or serialized proof source.
# ty: ignore[unresolved-reference]
# ruff: noqa: F821

# Identify meaningful function gaps without discarding the saved residual.
function_coeff_by_k = {0: [0.0, 0.0]}
for k in range(1, N_int + 1):
    Fk = f(ctx[f"x_{k}"]) - f(ctx["x_star"])
    Gk = g(ctx[f"x_{k}"]) - g(ctx["x_star"])
    columns = np.column_stack(
        [pm.eval_scalar(Fk).func_coords, pm.eval_scalar(Gk).func_coords]
    ).astype(float)
    target = np.asarray(pm.eval_scalar(lyap[k]).func_coords, dtype=float)
    weights = np.linalg.lstsq(columns, target, rcond=None)[0]
    assert np.max(np.abs(columns @ weights - target), initial=0.0) <= 1e-5
    function_coeff_by_k[k] = weights.tolist()


def V_k_structure(k):
    vectors = V_k_basis(k)
    C = coeff_by_k[k]
    value = sum(
        (float(C[i, j]) * vectors[i] * vectors[j] for i, j in np.ndindex(C.shape)),
        pf.Scalar.zero(),
    )
    if k > 0:
        alpha, beta = function_coeff_by_k[k]
        value += alpha * (f(ctx[f"x_{k}"]) - f(ctx["x_star"]))
        value += beta * (g(ctx[f"x_{k}"]) - g(ctx["x_star"]))
    return value


component_residuals = {}
for k in range(N_int + 1):
    diff = pm.eval_scalar(V_k_structure(k) - lyap[k])
    values = [diff.inner_prod_coords, diff.func_coords, diff.offset]
    residual = [
        float(np.max(np.abs(np.asarray(v, dtype=float)), initial=0.0)) for v in values
    ]
    assert max(residual) <= 1e-5
    component_residuals[str(k)] = dict(zip(["gram", "function", "offset"], residual))
    print(
        f"k={k}: full-expression residuals",
        component_residuals[str(k)],
        "function-gap coefficients",
        function_coeff_by_k[k],
    )
print("All required indices 0 through N reconstructed with no constant terms.")
