"""Interpretable basis and candidate coefficients discovered in Block 4."""

import json

import numpy as np
import sympy as sp

import pepflow as pf
from pepflow.lyapunov_utils import find_symmetric_coefficient_matrix


def basis_for(ctx, k, n):
    if k == 0:
        return []
    basis = [ctx[f"g_{n}"], ctx["x_0"] - ctx[f"x_{n}"]]
    if k < n:
        basis.extend([ctx[f"x_{k}"] - ctx[f"x_{n}"], ctx[f"z_{k}"]])
    return basis


def basis_labels_for(k, n):
    if k == 0:
        return []
    labels = ["A(x_N)", "x_0-x_N"]
    if k < n:
        labels.extend([f"x_{k}-x_N", f"z_{k}"])
    return labels


def coeff_pattern(k, n, lipschitz=sp.S.One):
    n = sp.sympify(n)
    if k == 0:
        return sp.zeros(0, 0)
    if k == n:
        return sp.Matrix([[2, -2 * lipschitz / n], [-2 * lipschitz / n, 0]])
    m = n - k
    return sp.Matrix(
        [
            [0, -2 * lipschitz / n, 2 * lipschitz / m, -2],
            [-2 * lipschitz / n, 0, 0, 0],
            [2 * lipschitz / m, 0, 0, 2 * lipschitz / m],
            [-2, 0, 2 * lipschitz / m, -2],
        ]
    )


def numerical_structure(ctx, k, n, coefficients):
    basis = basis_for(ctx, k, n)
    C = coefficients[k]
    # Function-value and constant terms are absent, checked separately below.
    return sum(
        (float(C[i, j]) * basis[i] * basis[j] for i, j in np.ndindex(C.shape)),
        pf.Scalar.zero(),
    )


def reconstruct_all(certificate, ctx, pm, lyap, cached=None):
    n = certificate["N_verify"]
    params = json.loads(certificate["params_json"])
    coefficients, quadratic_residuals, component_residuals, fit_errors = {}, {}, {}, {}
    for k in range(n + 1):
        basis = basis_for(ctx, k, n)
        target = pm.eval_scalar(lyap[k])
        gram = np.asarray(target.inner_prod_coords, dtype=float)
        B = (
            np.column_stack([pm.eval_vector(v).coords for v in basis]).astype(float)
            if basis
            else np.empty((len(ctx.basis_vectors()), 0))
        )
        rank = int(np.linalg.matrix_rank(B, tol=1e-7)) if basis else 0
        assert rank == len(basis) == int(np.linalg.matrix_rank(gram, tol=1e-4))
        cache_C = None if cached is None else cached.get(k)
        if cache_C is not None and np.linalg.norm(
            B @ cache_C @ B.T - gram, ord="fro"
        ) <= 1e-5 * max(1.0, np.linalg.norm(gram, ord="fro")):
            C = cache_C
        else:
            C = find_symmetric_coefficient_matrix(
                lyap[k],
                basis,
                pep_context=ctx,
                resolve_parameters=params,
                indep_tol=1e-7,
                span_tol=1e-5,
            )
        assert C.shape == (len(basis), len(basis)) and np.array_equal(C, C.T)
        assert np.all(np.isfinite(C))
        residual = float(np.linalg.norm(B @ C @ B.T - gram, ord="fro"))
        assert residual <= 1e-5 * max(1.0, np.linalg.norm(gram, ord="fro"))
        coefficients[k] = C
        quadratic_residuals[str(k)] = residual
        assert np.allclose(target.func_coords, 0, atol=1e-4, rtol=1e-5)
        assert abs(float(target.offset)) <= 1e-4
        diff = pm.eval_scalar(numerical_structure(ctx, k, n, coefficients) - lyap[k])
        errors = {}
        for label, actual, target_component in [
            ("gram", diff.inner_prod_coords, target.inner_prod_coords),
            ("function", diff.func_coords, target.func_coords),
            ("offset", diff.offset, target.offset),
        ]:
            error = float(np.max(np.abs(np.asarray(actual, dtype=float)), initial=0))
            scale = float(
                np.max(np.abs(np.asarray(target_component, dtype=float)), initial=0)
            )
            assert error <= 1e-4 + 1e-5 * scale
            errors[label] = error
        component_residuals[str(k)] = errors
        candidate = np.asarray(coeff_pattern(k, n), dtype=float).reshape(C.shape)
        fit_error = float(np.max(np.abs(candidate - C), initial=0))
        fit_errors[str(k)] = fit_error
        assert fit_error <= 1e-4
        print(
            f"k={k}: rank {rank} basis {basis_labels_for(k, n)}; reconstruction {residual:.3e}; candidate error {fit_error:.3e}"
        )
    return (
        coefficients,
        dict(
            certificate_id=certificate["certificate_id"],
            required_indices=list(range(n + 1)),
            quadratic_residuals=quadratic_residuals,
            component_residuals=component_residuals,
            tolerances=dict(
                indep_tol=1e-7, span_tol=1e-5, component_atol=1e-4, component_rtol=1e-5
            ),
            passed=True,
        ),
        fit_errors,
    )
