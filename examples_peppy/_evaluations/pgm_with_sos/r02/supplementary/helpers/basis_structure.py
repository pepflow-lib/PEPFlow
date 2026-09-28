"""Numerical basis templates and candidate coefficient formulas for the selected B3 recipe."""

import numpy as np
import pgm_setup as setup
import sympy as sp

import pepflow as pf
from pepflow.lyapunov_utils import find_symmetric_coefficient_matrix


def V_k_basis(k, ctx, N):
    if k == 0:
        return []
    x0gap = ctx["x_0"] - ctx["x_star"]
    if k == N:
        return [x0gap]
    x = ctx[f"x_{k}"]
    a = setup.f.grad(x)
    return [x0gap, x - ctx["x_star"], a, a - setup.f.grad(ctx["x_star"])]


def V_k_basis_labels(k, N):
    if k == 0:
        return []
    if k == N:
        return ["x_0-x_star"]
    return ["x_0-x_star", f"x_{k}-x_star", f"a_{k}", f"a_{k}-a_star"]


def coeff_pattern(k, N, L=sp.S.One):
    k, N, L = map(sp.sympify, (k, N, L))
    if k == 0:
        return sp.zeros(0)
    if k == N:
        return sp.Matrix([[-L / (4 * N)]])
    return sp.Matrix(
        [
            [-L / (4 * N), 0, 0, 0],
            [0, L * (N - k) / (2 * N - k) ** 2, -1 / (2 * (2 * N - k)), 0],
            [0, -1 / (2 * (2 * N - k)), 0, 0],
            [0, 0, 0, 1 / (2 * L * (2 * N - k))],
        ]
    )


def function_coeff_pattern(k, N):
    k, N = map(sp.sympify, (k, N))
    assert isinstance(k, sp.Expr) and isinstance(N, sp.Expr)
    if k == 0:
        return sp.S.Zero, sp.S.Zero
    if k == N:
        return sp.S.One, sp.S.One
    return (k + 1) / (2 * N - k), k / (2 * N - k)


def V_k_structure(k, ctx, N, coeff_by_k, function_coefficients, offset_coefficients):
    basis = V_k_basis(k, ctx, N)
    C = coeff_by_k[k]
    value = sum(
        (float(C[i, j]) * basis[i] * basis[j] for i, j in np.ndindex(C.shape)),
        pf.Scalar.zero(),
    )
    if k > 0:
        fcoef, gcoef = function_coefficients[k]
        value += float(fcoef) * (setup.f(ctx[f"x_{k}"]) - setup.f(ctx["x_star"]))
        value += float(gcoef) * (setup.g(ctx[f"x_{k}"]) - setup.g(ctx["x_star"]))
    return value + float(offset_coefficients[k])


def extract_structure(trial, N):
    ctx, pm, lyap = trial["ctx"], trial["pm"], trial["lyap"]
    coeffs, funcs, offsets, errors = {}, {}, {}, {}
    for k in range(N + 1):
        basis = V_k_basis(k, ctx, N)
        target = pm.eval_scalar(lyap[k])
        M = np.asarray(target.inner_prod_coords, dtype=float)
        if not basis:
            C = np.zeros((0, 0))
            B = np.zeros((len(M), 0))
        else:
            B = np.column_stack([pm.eval_vector(v).coords for v in basis]).astype(float)
            assert (
                np.linalg.matrix_rank(B, tol=1e-7)
                == len(basis)
                == trial["observation"]["rank_profile"][k]
            )
            C = find_symmetric_coefficient_matrix(
                lyap[k],
                basis,
                pep_context=ctx,
                resolve_parameters={"L": sp.S.One, "R": sp.S.One},
                indep_tol=1e-7,
                span_tol=1e-5,
            )
        residual = float(np.linalg.norm(B @ C @ B.T - M, "fro"))
        assert residual <= 1e-5 * max(1.0, np.linalg.norm(M, "fro"))
        coeffs[k] = C
        if k == 0:
            funcs[k] = [0.0, 0.0]
        else:
            columns = np.column_stack(
                [
                    pm.eval_scalar(fun(ctx[f"x_{k}"]) - fun(ctx["x_star"])).func_coords
                    for fun in (setup.f, setup.g)
                ]
            ).astype(float)
            funcs[k] = np.linalg.lstsq(
                columns, np.asarray(target.func_coords, dtype=float), rcond=None
            )[0].tolist()
        offsets[k] = float(target.offset)
        diff = pm.eval_scalar(
            V_k_structure(k, ctx, N, coeffs, funcs, offsets) - lyap[k]
        )
        components = {
            name: float(np.max(abs(np.asarray(arr, dtype=float)), initial=0))
            for name, arr in [
                ("gram", diff.inner_prod_coords),
                ("function", diff.func_coords),
                ("offset", np.asarray(diff.offset)),
            ]
        }
        assert all(value <= 1e-5 for value in components.values())
        Cguess = np.asarray(coeff_pattern(k, N), dtype=float).reshape(C.shape)
        fit = float(np.max(abs(Cguess - C), initial=0))
        assert fit <= 1e-4
        assert (
            np.max(
                abs(
                    np.asarray(function_coeff_pattern(k, N), dtype=float)
                    - np.asarray(funcs[k])
                ),
                initial=0,
            )
            <= 1e-5
        )
        errors[k] = dict(
            quadratic_frobenius=residual,
            components=components,
            candidate_coefficient_max_abs=fit,
        )
    return coeffs, funcs, offsets, errors


def scan_candidate_bases(trial, N):
    from itertools import combinations

    from pepflow.lyapunov_utils import (
        find_basis_with_sparsest_coefficients,
        vectors_in_column_space,
    )

    ctx, pm, lyap = trial["ctx"], trial["pm"], trial["lyap"]
    results = {}
    for k in range(1, N + 1):
        pairs = list(zip(V_k_basis_labels(k, N), V_k_basis(k, ctx, N)))
        base = [(str(v), v) for v in ctx.basis_vectors()]
        base += [(f"x_{i}", ctx[f"x_{i}"]) for i in range(N + 1)] + [
            ("x_star", ctx["x_star"])
        ]
        base += [(f"a_{i}", setup.f.grad(ctx[f"x_{i}"])) for i in range(N + 1)]
        base += [(f"s_{i}", setup.g.grad(ctx[f"x_{i}"])) for i in range(1, N + 1)]
        base += [("a_star", setup.f.grad(ctx["x_star"]))]
        pairs += base
        pairs += [
            (f"({name1})-({name2})", v1 - v2)
            for (name1, v1), (name2, v2) in combinations(base, 2)
        ]
        unique = []
        coords = []
        for label, vector in pairs:
            row = np.asarray(pm.eval_vector(vector).coords, dtype=float)
            if np.linalg.norm(row) <= 1e-12 or any(
                np.allclose(row, old, atol=1e-12, rtol=0) for old in coords
            ):
                continue
            unique.append((label, vector))
            coords.append(row)
        in_col = vectors_in_column_space(
            lyap[k],
            [v for _, v in unique],
            pep_context=ctx,
            resolve_parameters={"L": sp.S.One, "R": sp.S.One},
            rtol=1e-4,
            atol=1e-4,
        )
        print(f"V_{k} column-space candidates:")
        names = {id(v): name for name, v in unique}
        for v in in_col:
            print("   " + names[id(v)])
        sparse, C = find_basis_with_sparsest_coefficients(
            lyap[k],
            in_col,
            pep_context=ctx,
            resolve_parameters={"L": sp.S.One, "R": sp.S.One},
            zero_tol=1e-6,
            indep_tol=1e-7,
            span_tol=1e-5,
        )
        assert len(sparse) == trial["observation"]["rank_profile"][k]
        print(
            f"k={k}: rank {len(sparse)}; sparse basis: {[names[id(v)] for v in sparse]}"
        )
        print(f"zero coefficients: {int(np.sum(abs(C) < 1e-6))}/{C.size}")
        results[k] = dict(
            candidate_count=len(unique),
            column_space_labels=[names[id(v)] for v in in_col],
            sparse_basis=[names[id(v)] for v in sparse],
            zero_coefficients=int(np.sum(abs(C) < 1e-6)),
            total_coefficients=int(C.size),
        )
    return results
