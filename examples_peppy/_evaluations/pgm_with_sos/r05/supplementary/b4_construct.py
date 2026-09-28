# Notebook/proof state is executed below into the shared runtime namespace.
# These names are supplied by the notebook cells or serialized proof source.
# ty: ignore[unresolved-reference]
# ruff: noqa: F821

# B4 reconstruction and basis search; caller supplies setup and notebook_dir.
import json
from itertools import combinations

import numpy as np

import pepflow as pf
from pepflow.lyapunov_utils import (
    find_basis_with_sparsest_coefficients,
    find_symmetric_coefficient_matrix,
    vectors_in_column_space,
)

b3 = json.loads((notebook_dir / "state" / "pgm_b3.json").read_text())
certificate = b3
for field in ("certificate_check_code", "decomposition_code", "grouping_code"):
    exec(compile(b3[field], f"B3-{field}", "exec"), globals())
assert certificate_checked and grouping_checked
assert ranks == b3["rank_profile"]
rank_evidence = json.loads(
    (notebook_dir / b3["rank_search"]["evidence_path"]).read_text()
)
assert rank_evidence["summary"] == b3["rank_search"]
assert b3["rank_search"]["boundary_exclusions"] == {"left": 1, "right": 1}
assert b3["rank_search"]["status"] == "confirmed"
assert b3["rank_search"]["selected_certificate_id"] == b3["certificate_id"]
assert len(set(b3["rank_search"]["confirmed_horizons"])) >= 2
for k, V in enumerate(lyap):
    evaluated = pm.eval_scalar(V)
    for actual, saved in [
        (evaluated.inner_prod_coords, b3["lyap_inner_prod_coords"][k]),
        (evaluated.func_coords, b3["lyap_func_coords"][k]),
        (evaluated.offset, b3["lyap_offsets"][k]),
    ]:
        assert np.allclose(np.asarray(actual, dtype=float), saved, atol=1e-5, rtol=1e-5)
# SCAN
candidate_pairs = []
astar = f.grad(ctx["x_star"])
for i in range(N_int + 1):
    candidate_pairs.append((f"r_{i}", ctx[f"x_{i}"] - ctx["x_star"]))
    candidate_pairs.append((f"a_{i}-a_star", f.grad(ctx[f"x_{i}"]) - astar))
    if i >= 1:
        candidate_pairs.append(
            (f"a_{i}+s_{i}", f.grad(ctx[f"x_{i}"]) + g.grad(ctx[f"x_{i}"]))
        )
candidate_pairs.extend((str(v), v) for v in ctx.basis_vectors())
candidate_pairs.extend((f"x_{i}", ctx[f"x_{i}"]) for i in range(N_int + 1))
base = list(candidate_pairs)
candidate_pairs.extend(
    (f"({a})-({b})", va - vb) for (a, va), (b, vb) in combinations(base, 2)
)
unique_pairs, seen = [], []
for label, vector in candidate_pairs:
    coords = np.asarray(pm.eval_vector(vector).coords, dtype=float)
    if np.linalg.norm(coords) <= 1e-6 or any(
        np.allclose(coords, old, atol=1e-10, rtol=0) for old in seen
    ):
        continue
    seen.append(coords)
    unique_pairs.append((label, vector))
candidate_labels = {id(v): label for label, v in unique_pairs}
spanning_by_k = {}
for k in range(1, N_int + 1):
    spanning_by_k[k] = vectors_in_column_space(
        lyap[k],
        [v for _, v in unique_pairs],
        pep_context=ctx,
        resolve_parameters=params_sp,
        rtol=1e-4,
        atol=1e-4,
    )
    print(f"V_{k} column-space candidates:")
    for v in spanning_by_k[k]:
        print("   ", candidate_labels[id(v)])
# SEARCH
sparse_basis_by_k, sparse_coeff_by_k = {}, {}
for k in range(1, N_int + 1):
    sparse_basis, sparse_C = find_basis_with_sparsest_coefficients(
        lyap[k],
        spanning_by_k[k],
        pep_context=ctx,
        resolve_parameters=params_sp,
        zero_tol=1e-6,
        indep_tol=1e-7,
        span_tol=1e-5,
    )
    assert len(sparse_basis) == ranks[k]
    sparse_basis_by_k[k], sparse_coeff_by_k[k] = sparse_basis, sparse_C
    print(
        f"k={k}, rank={ranks[k]} sparse basis:",
        [candidate_labels[id(v)] for v in sparse_basis],
    )
    print(
        "zero coefficients:", int(np.sum(np.abs(sparse_C) < 1e-6)), "/", sparse_C.size
    )


# BASIS
def V_k_basis(k):
    if k == 0:
        return []
    r0 = ctx["x_0"] - ctx["x_star"]
    if k == N_int:
        return [r0]
    xk = ctx[f"x_{k}"]
    return [r0, xk - ctx["x_star"], f.grad(xk) - f.grad(ctx["x_star"]), f.grad(xk)]


def V_k_basis_labels(k):
    if k == 0:
        return []
    if k == N_int:
        return ["r_0"]
    return ["r_0", f"r_{k}", f"a_{k}-a_star", f"a_{k}"]


# COEFFICIENTS
coeff_by_k, coefficient_residuals, independence = {}, {}, {}
for k in range(N_int + 1):
    vectors = V_k_basis(k)
    B = (
        np.column_stack([pm.eval_vector(v).coords for v in vectors]).astype(float)
        if vectors
        else np.zeros((len(basis), 0))
    )
    rank = int(np.linalg.matrix_rank(B, tol=1e-7)) if vectors else 0
    assert rank == len(vectors) == ranks[k]
    independence[k] = rank
    C = find_symmetric_coefficient_matrix(
        lyap[k],
        vectors,
        pep_context=ctx,
        resolve_parameters=params_sp,
        indep_tol=1e-7,
        span_tol=1e-5,
    )
    target = np.asarray(pm.eval_scalar(lyap[k]).inner_prod_coords, dtype=float)
    residual = float(np.linalg.norm(B @ C @ B.T - target, ord="fro"))
    assert residual <= 1e-5 * max(1.0, np.linalg.norm(target, ord="fro"))
    coeff_by_k[k], coefficient_residuals[k] = C, residual
    print(
        f"k={k}: rank {rank} basis",
        V_k_basis_labels(k),
        "reconstruction residual:",
        residual,
    )
    if vectors:
        pf.pprint_labeled_matrix(C, V_k_basis_labels(k), V_k_basis_labels(k))
    ev = pm.eval_scalar(lyap[k])
    print(
        "Function coordinates:",
        [
            (str(v), float(c))
            for v, c in zip(ctx.basis_scalars(), ev.func_coords)
            if abs(c) > 1e-7
        ],
        "offset:",
        ev.offset,
    )
