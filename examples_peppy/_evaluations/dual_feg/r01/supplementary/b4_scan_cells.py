# This saved notebook fragment shares its caller's execution namespace.
# These names are supplied by the notebook cells or serialized proof source.
# ty: ignore[unresolved-reference]
# ruff: noqa: F821

from itertools import combinations

from pepflow.lyapunov_utils import (
    find_basis_with_sparsest_coefficients,
    vectors_in_column_space,
)

candidate_pairs = []
for j in range(N_int + 1):
    candidate_pairs.extend(
        [
            (f"z_{j}", ctx[f"z_{j}"]),
            (f"g_{j}", ctx[f"g_{j}"]),
            (f"x_{j}-x_N", ctx[f"x_{j}"] - ctx[f"x_{N_int}"]),
        ]
    )
for j in range(N_int):
    candidate_pairs.extend(
        [(f"h_{j}", ctx[f"h_{j}"]), (f"y_{j}-x_N", ctx[f"y_{j}"] - ctx[f"x_{N_int}"])]
    )
points = (
    [(f"x_{j}", ctx[f"x_{j}"]) for j in range(N_int + 1)]
    + [(f"y_{j}", ctx[f"y_{j}"]) for j in range(N_int)]
    + [("x_star", ctx["x_star"])]
)
for (a, av), (b, bv) in combinations(points, 2):
    candidate_pairs.append((f"{a}-{b}", av - bv))
for v in ctx.basis_vectors():
    candidate_pairs.append((str(v), v))
unique_pairs = []
unique_coords = []
for label, vector in candidate_pairs:
    coords = np.asarray(pm.eval_vector(vector).coords, dtype=float)
    if np.linalg.norm(coords) < 1e-12 or any(
        np.allclose(coords, a, atol=1e-12, rtol=0) for a in unique_coords
    ):
        continue
    unique_pairs.append((label, vector))
    unique_coords.append(coords)
candidate_pairs = unique_pairs
candidates = [v for _, v in candidate_pairs]
candidate_labels = {id(v): label for label, v in candidate_pairs}
print("Distinct nonzero candidates:", len(candidates))
spanning_by_k = {}
for k in range(1, N_int + 1):
    in_col = vectors_in_column_space(
        lyap[k],
        candidates,
        pep_context=ctx,
        resolve_parameters=params_sp,
        rtol=1e-4,
        atol=1e-4,
    )
    spanning_by_k[k] = in_col
    print(f"V_{k} column-space candidates:")
    for v in in_col:
        print("  ", candidate_labels[id(v)])
searched_basis = {}
searched_coeff = {}
for k in range(1, N_int + 1):
    found, C = find_basis_with_sparsest_coefficients(
        lyap[k],
        spanning_by_k[k],
        pep_context=ctx,
        resolve_parameters=params_sp,
        zero_tol=1e-6,
        indep_tol=1e-7,
        span_tol=1e-5,
    )
    searched_basis[k] = found
    searched_coeff[k] = C
    print(
        "k=",
        k,
        "rank=",
        ranks[k],
        "sparse basis:",
        [candidate_labels[id(v)] for v in found],
        "zero coefficients:",
        int(np.sum(np.abs(C) < 1e-6)),
        "/",
        C.size,
    )
    assert len(found) == ranks[k]
