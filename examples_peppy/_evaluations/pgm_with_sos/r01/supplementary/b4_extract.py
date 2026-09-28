# This saved notebook fragment shares its caller's execution namespace.
# These names are supplied by the notebook cells or serialized proof source.
# ty: ignore[unresolved-reference]
# ruff: noqa: F821

from pepflow.lyapunov_utils import find_symmetric_coefficient_matrix

coeff_by_k = {}
function_coefficients = {}
coefficient_residuals = {}
required_indices = list(range(N + 1))
for k in required_indices:
    selected = V_k_basis(k)
    C = find_symmetric_coefficient_matrix(
        lyap[k],
        selected,
        pep_context=ctx_b2,
        resolve_parameters={"L": sp.S.One, "R": sp.S.One},
        indep_tol=1e-7,
        span_tol=1e-5,
    )
    coeff_by_k[k] = C
    M = np.asarray(pm.eval_scalar(lyap[k]).inner_prod_coords, dtype=float)
    if selected:
        B = np.column_stack([pm.eval_vector(v).coords for v in selected]).astype(float)
        assert np.linalg.matrix_rank(B, tol=1e-7) == len(selected) == ranks[k]
        error = float(np.linalg.norm(M - B @ C @ B.T, ord="fro"))
    else:
        assert ranks[k] == 0
        error = float(np.linalg.norm(M, ord="fro"))
    assert error <= 1e-5 * max(1, np.linalg.norm(M, ord="fro"))
    coefficient_residuals[k] = error
    print(f"k={k}: rank {ranks[k]} basis {V_k_basis_labels(k)}; residual {error:.3g}")
    if C.size:
        pf.pprint_labeled_matrix(
            C, V_k_basis_labels(k), V_k_basis_labels(k), precision=7
        )
    if k == 0:
        function_coefficients[k] = [0.0, 0.0]
    else:
        x = ctx_b2[f"x_{k}"]
        xs = ctx_b2["x_star"]
        F = np.column_stack(
            [pm.eval_scalar(term).func_coords for term in (f(x) - f(xs), g(x) - g(xs))]
        ).astype(float)
        target = np.asarray(pm.eval_scalar(lyap[k]).func_coords, dtype=float)
        coeff = np.linalg.lstsq(F, target, rcond=None)[0]
        assert np.max(np.abs(F @ coeff - target), initial=0) <= 1e-4
        function_coefficients[k] = coeff.tolist()
    assert abs(float(pm.eval_scalar(lyap[k]).offset)) <= 1e-5
    print(
        "Function gap coefficients [f,g]:",
        function_coefficients[k],
        "; scalar offset: 0",
    )


def V_k_structure(k):
    selected = V_k_basis(k)
    C = coeff_by_k[k]
    quadratic = sum(
        (float(C[i, j]) * selected[i] * selected[j] for i, j in np.ndindex(C.shape)),
        pf.Scalar.zero(),
    )
    if k == 0:
        return quadratic
    x, xs = ctx_b2[f"x_{k}"], ctx_b2["x_star"]
    A, B = function_coefficients[k]
    return quadratic + A * (f(x) - f(xs)) + B * (g(x) - g(xs))


component_residuals = {}
for k in required_indices:
    difference = pm.eval_scalar(V_k_structure(k) - lyap[k])
    target = pm.eval_scalar(lyap[k])
    component_residuals[str(k)] = {}
    for label, actual, scale in (
        ("gram", difference.inner_prod_coords, target.inner_prod_coords),
        ("function", difference.func_coords, target.func_coords),
        ("offset", difference.offset, target.offset),
    ):
        error = maxabs(actual)
        assert error <= 1e-4 + 1e-5 * maxabs(scale)
        component_residuals[str(k)][label] = error
print("All-index full-component reconstruction passed:", component_residuals)
