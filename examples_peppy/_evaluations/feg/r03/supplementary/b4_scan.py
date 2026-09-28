# This saved notebook fragment shares its caller's execution namespace.
# These names are supplied by the notebook cells or serialized proof source.
# ty: ignore[unresolved-reference]
# ruff: noqa: F821

from itertools import combinations

from pepflow.lyapunov_utils import (
    vectors_in_column_space,
)

candidate_pairs = []
for k in range(N_int + 1):
    candidate_pairs.extend(
        [
            (f"g_{k}", obj(ctx[f"x_{k}"])),
            (f"x_{k}-x_0", ctx[f"x_{k}"] - ctx["x_0"]),
            (f"x_{k}-x_star", ctx[f"x_{k}"] - ctx["x_star"]),
            (f"x_{k}", ctx[f"x_{k}"]),
        ]
    )
for v in ctx.basis_vectors():
    candidate_pairs.append((str(v), v))
base_pairs = list(candidate_pairs)
for (la, va), (lb, vb) in combinations(base_pairs, 2):
    candidate_pairs.append((f"({la})-({lb})", va - vb))
unique_pairs = []
unique_coords = []
for label, vector in candidate_pairs:
    coords = np.asarray(pm.eval_vector(vector).coords, dtype=float)
    if np.linalg.norm(coords) <= 1e-6:
        continue
    if any(np.allclose(coords, prior, atol=1e-6, rtol=0) for prior in unique_coords):
        continue
    unique_pairs.append((label, vector))
    unique_coords.append(coords)
candidates = [vector for _, vector in unique_pairs]
label_by_id = {id(vector): label for label, vector in unique_pairs}
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
    for vector in in_col:
        print("   " + label_by_id[id(vector)])
