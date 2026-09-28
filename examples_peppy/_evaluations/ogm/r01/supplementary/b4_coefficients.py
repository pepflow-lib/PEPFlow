# This saved notebook fragment shares its caller's execution namespace.
# These names are supplied by the notebook cells or serialized proof source.
# ty: ignore[unresolved-reference]
# ruff: noqa: F821

import sympy as sp

from pepflow.lyapunov_utils import find_symmetric_coefficient_matrix

params_sp = {"L": sp.Integer(1), "R": sp.Integer(1)}
required_indices = list(range(N_int + 1))
coeff_by_k = {}
coefficient_residuals = {}
function_sample_coefficients = {}
function = next(iter(ctx.func_to_triplets))
for k in required_indices:
    selected_basis = V_k_basis(k)
    evaluated = pm.eval_scalar(lyap[k])
    target = np.asarray(evaluated.inner_prod_coords, dtype=float)
    if selected_basis:
        matrix = np.column_stack(
            [pm.eval_vector(v).coords for v in selected_basis]
        ).astype(float)
        assert (
            np.linalg.matrix_rank(matrix, tol=1e-7) == len(selected_basis) == ranks[k]
        )
        C = find_symmetric_coefficient_matrix(
            lyap[k],
            selected_basis,
            pep_context=ctx,
            resolve_parameters={"L": sp.Integer(1), "R": sp.Integer(1)},
            indep_tol=1e-7,
            span_tol=1e-5,
        )
        assert np.array_equal(C, C.T)
        difference = matrix @ C @ matrix.T - target
    else:
        assert ranks[k] == 0
        C = np.zeros((0, 0))
        difference = -target
    coefficient_residuals[k] = float(np.linalg.norm(difference, ord="fro"))
    assert coefficient_residuals[k] <= 1e-5 * max(
        1.0, float(np.linalg.norm(target, ord="fro"))
    )
    coeff_by_k[k] = C
    gap = pm.eval_scalar(function(ctx[f"x_{k}"]) - function(ctx["x_star"]))
    gap_coords = np.asarray(gap.func_coords, dtype=float)
    target_function = np.asarray(evaluated.func_coords, dtype=float)
    alpha = float(np.dot(gap_coords, target_function) / np.dot(gap_coords, gap_coords))
    function_sample_coefficients[k] = alpha
    assert np.allclose(alpha * gap_coords, target_function, atol=1e-4, rtol=1e-5)
    assert abs(float(evaluated.offset)) < 1e-5
    print(f"k={k}: rank {ranks[k]} basis {V_k_basis_labels(k)}")
    print("Quadratic reconstruction residual:", coefficient_residuals[k])
    if C.size:
        pf.pprint_labeled_matrix(C, V_k_basis_labels(k), precision=8)
    print(
        "Function term coefficient:",
        alpha,
        "multiplying f(x_k)-f_star; offset:",
        float(evaluated.offset),
    )
