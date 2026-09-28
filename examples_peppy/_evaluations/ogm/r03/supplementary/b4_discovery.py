"""Discover and check interpretable bases from the saved B3 partial sums."""

import json
import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
for key in (
    "OMP_NUM_THREADS",
    "OPENBLAS_NUM_THREADS",
    "MKL_NUM_THREADS",
    "NUMEXPR_NUM_THREADS",
):
    os.environ[key] = "1"
sys.path[:0] = [
    str(ROOT / "supplementary" / "approved"),
    str(ROOT),
    str(ROOT / "supplementary" / "helpers"),
]
import numpy as np  # noqa: E402
import sympy as sp  # noqa: E402

# local helper resolved by the notebook runtime path
from partial_sums import (  # noqa: E402  # ty: ignore[unresolved-import]
    build_partial_sums,
    check_certificate,
)

import pepflow as pf  # noqa: E402
from pepflow.lyapunov_utils import find_basis_with_sparsest_coefficients  # noqa: E402
from pepflow.lyapunov_utils import (  # noqa: E402 - imports follow runtime or notebook setup
    find_symmetric_coefficient_matrix,
    vectors_in_column_space,
)

certificate = json.loads((ROOT / "state" / "ogm_b3.json").read_text())
observation, coordinates, coverage = build_partial_sums(certificate, ROOT)
assert observation["rank_profile"] == certificate["rank_profile"]
ctx, pb, obj, pm, weighted_terms, checks = check_certificate(certificate, ROOT)
params_sp: dict[str, pf.NUMERICAL_TYPE] = {"L": sp.Integer(1), "R": sp.Integer(1)}
N = certificate["N"]
lyap = [pf.Scalar.zero()]
for k in range(N):
    lyap.append(
        lyap[-1]
        + sum(
            (
                weighted_terms[name]
                for name, step in certificate["grouping_coverage"][
                    "constraint_assignment"
                ].items()
                if step == k
            ),
            pf.Scalar.zero(),
        )
    )
for k, V in enumerate(lyap):
    value = pm.eval_scalar(V)
    assert np.allclose(
        value.inner_prod_coords,
        certificate["lyap_inner_prod_coords"][k],
        atol=1e-4,
        rtol=1e-5,
    )
    assert np.allclose(
        value.func_coords, certificate["lyap_func_coords"][k], atol=1e-4, rtol=1e-5
    )
    assert abs(value.offset - certificate["lyap_offsets"][k]) < 1e-4

candidates = []


def add_candidate(label, vector):
    vector_coords = np.asarray(pm.eval_vector(vector).coords, dtype=float)
    if np.linalg.norm(vector_coords) < 1e-7:
        return
    if any(
        np.allclose(
            vector_coords,
            np.asarray(pm.eval_vector(v).coords, dtype=float),
            atol=1e-7,
            rtol=0,
        )
        for _, v in candidates
    ):
        return
    candidates.append((label, vector))


for k in range(N + 1):
    add_candidate(f"x_{k}-x_star", ctx[f"x_{k}"] - ctx["x_star"])
    add_candidate(f"z_{k}-x_star", ctx[f"z_{k}"] - ctx["x_star"])
    add_candidate(f"g_{k}", obj.grad(ctx[f"x_{k}"]))
    add_candidate(f"z_{k}-x_{k}", ctx[f"z_{k}"] - ctx[f"x_{k}"])
    if k:
        add_candidate(f"y_{k}-x_star", ctx[f"y_{k}"] - ctx["x_star"])
        add_candidate(f"x_{k}-x_{k - 1}", ctx[f"x_{k}"] - ctx[f"x_{k - 1}"])
for v in ctx.basis_vectors():
    add_candidate(str(v), v)


def V_k_basis(k):
    if k == 0:
        return []
    if k == 1:
        return [
            ctx["x_0"] - ctx["x_star"],
            ctx["z_1"] - ctx["x_star"],
            obj.grad(ctx["x_1"]),
        ]
    return [
        ctx["x_0"] - ctx["x_star"],
        ctx[f"z_{k}"] - ctx["x_star"],
        ctx[f"x_{k}"] - ctx["x_star"],
        obj.grad(ctx[f"x_{k}"]),
    ]


def V_k_basis_labels(k):
    if k == 0:
        return []
    if k == 1:
        return ["x_0-x_star", "z_1-x_star", "g_1"]
    return ["x_0-x_star", f"z_{k}-x_star", f"x_{k}-x_star", f"g_{k}"]


records = {}
coeff_by_k = {}
for k in range(N + 1):
    V = lyap[k]
    if k:
        in_col = vectors_in_column_space(
            V,
            [v for _, v in candidates],
            pep_context=ctx,
            resolve_parameters=params_sp,
            atol=1e-4,
            rtol=1e-4,
        )
        in_labels = [label for label, v in candidates if any(v is c for c in in_col)]
        print(f"V_{k} column-space candidates:", in_labels, flush=True)
        sparse_basis, C_sparse = find_basis_with_sparsest_coefficients(
            V,
            in_col,
            pep_context=ctx,
            resolve_parameters=params_sp,
            zero_tol=1e-6,
            indep_tol=1e-7,
            span_tol=1e-5,
        )
        sparse_labels = [
            next(label for label, v in candidates if v is vector)
            for vector in sparse_basis
        ]
        print(
            f"k={k} rank {certificate['rank_profile'][k]} sparse basis: {sparse_labels}; zero coefficients: {np.sum(np.abs(C_sparse) < 1e-6)}/{C_sparse.size}",
            flush=True,
        )
    else:
        in_labels = sparse_labels = []
    basis = V_k_basis(k)
    C = find_symmetric_coefficient_matrix(
        V,
        basis,
        pep_context=ctx,
        resolve_parameters=params_sp,
        indep_tol=1e-7,
        span_tol=1e-5,
    )
    coeff_by_k[k] = C
    B = (
        np.asarray(
            np.column_stack([pm.eval_vector(v).coords for v in basis]), dtype=float
        )
        if basis
        else np.zeros((len(ctx.basis_vectors()), 0))
    )
    assert (
        np.linalg.matrix_rank(B, tol=1e-7)
        == len(basis)
        == certificate["rank_profile"][k]
    )
    target = pm.eval_scalar(V)
    target_matrix = np.asarray(target.inner_prod_coords, dtype=float)
    error = float(np.linalg.norm(B @ C @ B.T - target_matrix, ord="fro"))
    assert error <= 1e-5 * max(1.0, np.linalg.norm(target_matrix, ord="fro"))
    records[str(k)] = {
        "column_candidates": in_labels,
        "sparse_basis": sparse_labels,
        "adopted_basis": V_k_basis_labels(k),
        "coefficient_matrix": C.tolist(),
        "quadratic_residual": error,
        "function_coords": np.asarray(target.func_coords, dtype=float).tolist(),
        "offset": float(target.offset),
    }
    print(
        "ADOPTED",
        k,
        V_k_basis_labels(k),
        C,
        "function",
        target.func_coords,
        "labels",
        certificate["basis_scalars"],
        flush=True,
    )
(ROOT / "supplementary" / "b4-discovery.json").write_text(json.dumps(records, indent=2))
