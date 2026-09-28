# This saved notebook fragment shares its caller's execution namespace.
# These names are supplied by the notebook cells or serialized proof source.
# ty: ignore[unresolved-reference]
# ruff: noqa: F821

from fractions import Fraction

from pepflow.lyapunov_utils import find_symmetric_coefficient_matrix

required_indices = list(range(N_int + 1))
coeff_by_k = {}
coefficient_residuals = {}
extraction_tolerances = {"indep_tol": 1e-7, "span_tol": 1e-5}
for k in required_indices:
    vectors = V_k_basis(k)
    target = np.asarray(pm.eval_scalar(lyap[k]).inner_prod_coords, dtype=float)
    if vectors:
        B = np.column_stack([pm.eval_vector(v).coords for v in vectors]).astype(float)
        actual_rank = int(np.linalg.matrix_rank(B, tol=1e-7))
        assert actual_rank == len(vectors) == ranks[k]
        C = find_symmetric_coefficient_matrix(
            lyap[k],
            vectors,
            pep_context=ctx,
            resolve_parameters=params_sp,
            **extraction_tolerances,
        )
        assert np.array_equal(C, C.T)
        error = float(np.linalg.norm(B @ C @ B.T - target, ord="fro"))
    else:
        actual_rank = 0
        C = np.zeros((0, 0))
        error = float(np.linalg.norm(target, ord="fro"))
        assert ranks[k] == 0
    assert error <= 1e-5 * max(1.0, np.linalg.norm(target, ord="fro"))
    coeff_by_k[k] = C
    coefficient_residuals[k] = error
    print(
        f"k={k}: rank {actual_rank} basis {V_k_basis_labels(k)}; reconstruction residual {error:.3e}"
    )
    if C.size:
        pf.pprint_labeled_matrix(
            pf.MatrixWithNames(C, V_k_basis_labels(k), V_k_basis_labels(k))
        )
        print(
            "Independent nonzero entries:",
            {
                f"{i},{j}": str(Fraction(float(C[i, j])).limit_denominator(1000))
                for i in range(len(C))
                for j in range(i, len(C))
                if abs(C[i, j]) > 1e-6
            },
        )
    value = pm.eval_scalar(lyap[k])
    assert np.allclose(value.func_coords, 0, atol=1e-5, rtol=0) and np.allclose(
        value.offset, 0, atol=1e-5, rtol=0
    )
    print("Function terms: absent; offset:", float(value.offset))
