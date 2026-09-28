# This saved notebook fragment shares its caller's execution namespace.
# These names are supplied by the notebook cells or serialized proof source.
# ty: ignore[unresolved-reference]
# ruff: noqa: F821

from itertools import combinations

b3 = json.loads((notebook_dir / "state/bppm_b3.json").read_text())
assert certificate["certificate_id"] == b3["certificate_id"]
assert ranks == b3["rank_profile"]
rank_evidence = json.loads(
    (notebook_dir / b3["rank_search"]["evidence_path"]).read_text()
)
assert rank_evidence["summary"] == b3["rank_search"]
for k, Vk in enumerate(lyap):
    ev = pm.eval_scalar(Vk)
    for actual, saved in (
        (ev.inner_prod_coords, b3["lyap_inner_prod_coords"][k]),
        (ev.func_coords, b3["lyap_func_coords"][k]),
        (ev.offset, b3["lyap_offsets"][k]),
    ):
        assert np.allclose(np.asarray(actual, dtype=float), saved, atol=1e-4, rtol=1e-5)
f_obj = next(q for q in ctx.func_to_triplets if str(q) == "f")
h_obj = next(q for q in ctx.func_to_triplets if str(q) == "h")
xs = ctx["x_star"]
raw_candidates = []
for k in range(N_int + 1):
    xk = ctx[f"x_{k}"]
    raw_candidates += [
        (f"x_{k}-x_star", xk - xs),
        (f"grad_h(x_{k})", h_obj.grad(xk)),
        (f"grad_f(x_{k})", f_obj.grad(xk)),
        (f"x_{k}", xk),
    ]
raw_candidates += [("x_star", xs)]
raw_candidates += [(str(v), v) for v in ctx.basis_vectors()]
for i, j in combinations(range(N_int + 1), 2):
    raw_candidates += [(f"x_{i}-x_{j}", ctx[f"x_{i}"] - ctx[f"x_{j}"])]
candidate_pairs, seen = [], []
for label, vector in raw_candidates:
    coords = np.asarray(pm.eval_vector(vector).coords, dtype=float)
    if np.linalg.norm(coords) < 1e-6 or any(
        np.allclose(coords, prev, atol=1e-6, rtol=0) for prev in seen
    ):
        continue
    candidate_pairs.append((label, vector))
    seen.append(coords)
candidates = [v for _, v in candidate_pairs]
labels_by_id = {id(v): label for label, v in candidate_pairs}
print("Candidate count:", len(candidates))
