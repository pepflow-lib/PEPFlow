# This saved notebook fragment shares its caller's execution namespace.
# These names are supplied by the notebook cells or serialized proof source.
# ty: ignore[unresolved-reference]
# ruff: noqa: F821

"""Extract coefficients and fit the two meaningful function-value terms."""

coeff_by_k = {}
coefficient_residuals = {}
function_sample_coefficients = {}
for k in range(N_int + 1):
    vectors = V_k_basis(k)
    C = find_symmetric_coefficient_matrix(
        lyap[k],
        vectors,
        pep_context=ctx,
        resolve_parameters=params_sp,
        indep_tol=1e-7,
        span_tol=1e-5,
    )
    coeff_by_k[k] = C
    evaluated = pm.eval_scalar(lyap[k])
    target = np.asarray(evaluated.inner_prod_coords, dtype=float)
    matrix = (
        np.column_stack([pm.eval_vector(v).coords for v in vectors]).astype(float)
        if vectors
        else np.zeros((len(ctx.basis_vectors()), 0))
    )
    residual = float(np.linalg.norm(matrix @ C @ matrix.T - target, ord="fro"))
    assert residual <= 1e-5 * max(1.0, np.linalg.norm(target, ord="fro"))
    assert np.array_equal(C, C.T)
    coefficient_residuals[k] = residual
    if k:
        terms = [f(ctx[f"x_{k}"]) - f(ctx["x_star"]), h(ctx["x_0"]) - h(ctx[f"x_{k}"])]
        columns = np.column_stack(
            [pm.eval_scalar(v).func_coords for v in terms]
        ).astype(float)
        fitted, *_ = np.linalg.lstsq(
            columns, np.asarray(evaluated.func_coords, dtype=float), rcond=None
        )
        function_sample_coefficients[str(k)] = {
            "gap": float(fitted[0]),
            "h_difference": float(fitted[1]),
        }
    else:
        function_sample_coefficients[str(k)] = {"gap": 0.0, "h_difference": 0.0}
    print(f"k={k}: quadratic reconstruction residual {residual:.3g}")
    if vectors:
        pf.pprint_labeled_matrix(
            pf.MatrixWithNames(C, V_k_basis_labels(k), V_k_basis_labels(k))
        )
    else:
        print("Empty 0-by-0 quadratic matrix.")
    print(
        "Function coefficients:",
        function_sample_coefficients[str(k)],
        "offset:",
        evaluated.offset,
    )
    pf.pprint_labeled_matrix(
        pf.MatrixWithNames(
            np.asarray(evaluated.func_coords, dtype=float).reshape(1, -1),
            ["function coordinates"],
            [str(v) for v in ctx.basis_scalars()],
        )
    )


def V_k_structure(k):
    if k == 0:
        return pf.Scalar.zero()
    vectors = V_k_basis(k)
    C = coeff_by_k[k]
    quadratic = sum(
        (float(C[i, j]) * vectors[i] * vectors[j] for i, j in np.ndindex(C.shape)),
        pf.Scalar.zero(),
    )
    fitted = function_sample_coefficients[str(k)]
    return (
        quadratic
        + fitted["gap"] * (f(ctx[f"x_{k}"]) - f(ctx["x_star"]))
        + fitted["h_difference"] * (h(ctx["x_0"]) - h(ctx[f"x_{k}"]))
    )


component_residuals = {}
for k in range(N_int + 1):
    value = pm.eval_scalar(V_k_structure(k) - lyap[k])
    component_residuals[str(k)] = {}
    for label, coords in (
        ("gram", value.inner_prod_coords),
        ("function", value.func_coords),
        ("offset", value.offset),
    ):
        error = float(np.max(np.abs(np.asarray(coords, dtype=float)), initial=0))
        assert error <= 1e-4
        component_residuals[str(k)][label] = error
    print("Full reconstruction", k, component_residuals[str(k)])


def coeff_pattern(k, N, alpha):
    if k == 0:
        return sp.zeros(0, 0)
    C = sp.zeros(4, 4)
    C[0, 2] = C[2, 0] = 1 / (2 * alpha * N)
    C[1, 3] = C[3, 1] = -1 / (2 * alpha * N)
    return C


formula_residuals = {}
for k in range(N_int + 1):
    predicted = np.asarray(
        coeff_pattern(k, sp.Integer(N_int), params_sp["alpha"]), dtype=float
    )
    error = float(np.max(np.abs(predicted - coeff_by_k[k]), initial=0))
    if k:
        error = max(
            error,
            abs(function_sample_coefficients[str(k)]["gap"] - k / N_int),
            abs(
                function_sample_coefficients[str(k)]["h_difference"]
                - 1 / (float(params_sp["alpha"]) * N_int)
            ),
        )
    assert error < 1e-4
    formula_residuals[str(k)] = error
print("Candidate coefficient formula residuals:", formula_residuals)
