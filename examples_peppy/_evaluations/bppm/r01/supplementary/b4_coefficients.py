# This saved notebook fragment shares its caller's execution namespace.
# These names are supplied by the notebook cells or serialized proof source.
# ty: ignore[unresolved-reference]
# ruff: noqa: F821

from pepflow.lyapunov_utils import find_symmetric_coefficient_matrix

required_indices = list(range(N_int + 1))
extraction_tolerances = dict(indep_tol=1e-7, span_tol=1e-5)
coeff_by_k = {}
coefficient_residuals = {}
function_coeff_by_k = {}
offset_by_k = {}
for k in required_indices:
    target = pm.eval_scalar(lyap[k])
    gram = np.asarray(target.inner_prod_coords, dtype=float)
    basis_k = V_k_basis(k)
    if not basis_k:
        C = np.zeros((0, 0))
        quadratic_residual = float(np.linalg.norm(gram))
        assert quadratic_residual <= 1e-5
        function_coeff_by_k[k] = [0.0, 0.0]
    else:
        matrix = np.column_stack([pm.eval_vector(v).coords for v in basis_k]).astype(
            float
        )
        cached_basis = search_basis_by_k[k]
        cached_matrix = np.column_stack(
            [pm.eval_vector(v).coords for v in cached_basis]
        ).astype(float)
        cached_C = search_coeff_by_k[k]
        if np.array_equal(matrix, cached_matrix) and np.linalg.norm(
            matrix @ cached_C @ matrix.T - gram
        ) <= 1e-5 * max(1.0, np.linalg.norm(gram)):
            C = cached_C
        else:
            C = find_symmetric_coefficient_matrix(
                lyap[k],
                basis_k,
                pep_context=ctx,
                resolve_parameters=params_sp,
                **extraction_tolerances,
            )
        assert np.array_equal(C, C.T)
        quadratic_residual = float(np.linalg.norm(matrix @ C @ matrix.T - gram))
        assert quadratic_residual <= 1e-5 * max(1.0, np.linalg.norm(gram))
        function_terms = [
            objective(ctx[f"x_{k}"]) - objective(ctx["x_star"]),
            kernel(ctx["x_0"]) - kernel(ctx[f"x_{k}"]),
        ]
        design = np.column_stack(
            [pm.eval_scalar(term).func_coords for term in function_terms]
        ).astype(float)
        sample_coeffs = np.linalg.lstsq(
            design, np.asarray(target.func_coords, dtype=float), rcond=None
        )[0]
        assert (
            np.max(
                np.abs(
                    design @ sample_coeffs - np.asarray(target.func_coords, dtype=float)
                ),
                initial=0.0,
            )
            <= 1e-5
        )
        function_coeff_by_k[k] = sample_coeffs.tolist()
    coeff_by_k[k] = C
    coefficient_residuals[k] = quadratic_residual
    offset_by_k[k] = float(target.offset)
    print(f"k={k}: quadratic reconstruction residual={quadratic_residual:.3e}")
    if basis_k:
        pf.pprint_labeled_matrix(
            pf.MatrixWithNames(C, V_k_basis_labels(k), V_k_basis_labels(k))
        )
    print(
        "  function coefficients [f(x_k)-f_star, h(x_0)-h(x_k)]:",
        function_coeff_by_k[k],
    )
    print("  offset:", offset_by_k[k])
