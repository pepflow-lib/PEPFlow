# This saved notebook fragment shares its caller's execution namespace.
# These names are supplied by the notebook cells or serialized proof source.
# ty: ignore[unresolved-reference]
# ruff: noqa: F821

from itertools import combinations

from pepflow.lyapunov_utils import vectors_in_column_space

kernel = next(owner for owner in ctx.func_to_triplets if str(owner) == "h")
objective = next(owner for owner in ctx.func_to_triplets if str(owner) == "f")
candidate_pairs = []
for k in range(N_int + 1):
    candidate_pairs.extend(
        [
            (f"p_{k}=x_{k}-x_star", ctx[f"x_{k}"] - ctx["x_star"]),
            (f"grad_h(x_{k})", kernel.grad(ctx[f"x_{k}"])),
        ]
    )
candidate_pairs.extend((str(v), v) for v in ctx.basis_vectors())
base = list(candidate_pairs)
for (left, u), (right, v) in combinations(base, 2):
    candidate_pairs.append((f"({left})-({right})", u - v))
deduplicated = []
candidate_coords = []
for label, vector in candidate_pairs:
    coords = np.asarray(pm.eval_vector(vector).coords, dtype=float)
    if np.linalg.norm(coords) <= 1e-6:
        continue
    if any(np.allclose(coords, old, atol=1e-7, rtol=0) for old in candidate_coords):
        continue
    deduplicated.append((label, vector))
    candidate_coords.append(coords)
candidate_pairs = deduplicated
candidate_labels = {id(v): label for label, v in candidate_pairs}
print("Distinct nonzero candidates:", len(candidate_pairs))
spanning_by_k = {}
for k in range(1, N_int + 1):
    spanning_by_k[k] = vectors_in_column_space(
        lyap[k],
        [v for _, v in candidate_pairs],
        pep_context=ctx,
        resolve_parameters=params_sp,
        atol=1e-4,
        rtol=1e-4,
    )
    print(f"V_{k} column-space candidates:")
    for v in spanning_by_k[k]:
        print("  ", candidate_labels[id(v)])
