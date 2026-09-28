# This saved notebook fragment shares its caller's execution namespace.
# These names are supplied by the notebook cells or serialized proof source.
# ty: ignore[unresolved-reference]
# ruff: noqa: F821

# All residuals are <=0 and all assigned multipliers are nonnegative.
# V_{k+1}-V_k therefore has the nonincreasing sign.
rank_tolerance = 1e-4
rank_left, rank_right = 1, 1
group_terms = {**interpolation_terms, **extra_terms}
term_assignment = {}
for name in group_terms:
    family, pair = name.split(":")
    p, q = pair.split(",")
    pair_set = {p, q}
    if "x_star" in pair_set:
        assert pair_set == {f"x_{N_int}", "x_star"}
        term_assignment[name] = "boundary"
    elif family == "A monotone":
        indices = sorted(int(s.split("_")[1]) for s in (p, q))
        assert indices[1] == indices[0] + 1
        term_assignment[name] = indices[1] - 1
    elif family == "A Lipschitz":
        full = p if "/" not in p else q
        j = int(full.split("_")[1])
        assert pair_set == {f"x_{j}", f"x_{2 * j - 1}/2"}
        term_assignment[name] = j - 1
    else:
        raise ValueError(name)
S_assignment = {"whole_S": "boundary"}
lyap = [pf.Scalar.zero()]
partial_sum = pf.Scalar.zero()
for k in range(N_int):
    partial_sum += sum(
        (group_terms[name] for name, step in term_assignment.items() if step == k),
        pf.Scalar.zero(),
    )
    partial_sum -= sum(
        (S_piece_terms[name] for name, step in S_assignment.items() if step == k),
        pf.Scalar.zero(),
    )
    lyap.append(partial_sum)
ranks, singular_values = [], []
for k, Vk in enumerate(lyap):
    M = np.asarray(pm.eval_scalar(Vk).inner_prod_coords, dtype=float)
    sv = np.linalg.svd(M, compute_uv=False)
    singular_values.append(sv.tolist())
    rank = int(np.sum(sv > rank_tolerance))
    ranks.append(rank)
    print(f"rank V_{k}: {rank}")
    if k == 0:
        print()
retained = ranks[rank_left : N_int + 1 - rank_right]
print(
    "Interior rank is constant at this N:",
    len(retained) >= 3 and len(set(retained)) == 1,
    "boundary exclusions:",
    (rank_left, rank_right),
)
boundary_names = [name for name, step in term_assignment.items() if step == "boundary"]
boundary_S = [name for name, step in S_assignment.items() if step == "boundary"]
assert len(boundary_names) <= 1 and len(boundary_S) <= 1
leftover = sum((group_terms[name] for name in boundary_names), pf.Scalar.zero()) - sum(
    (S_piece_terms[name] for name in boundary_S), pf.Scalar.zero()
)
coverage_diff = (
    lyap[N_int] + leftover - (sum(group_terms.values(), pf.Scalar.zero()) - S_scalar)
)
piece_diff = sum(S_piece_terms.values(), pf.Scalar.zero()) - S_scalar
coverage_residuals = {}
for label, expr in [("coverage", coverage_diff), ("S_pieces", piece_diff)]:
    ev = pm.eval_scalar(expr)
    vals = [
        float(np.max(np.abs(np.asarray(a, dtype=float)), initial=0))
        for a in (ev.inner_prod_coords, ev.func_coords, ev.offset)
    ]
    coverage_residuals[label] = vals
    assert max(vals) <= 1e-5
for k in range(N_int):
    increment = sum(
        (group_terms[name] for name, step in term_assignment.items() if step == k),
        pf.Scalar.zero(),
    )
    ev = pm.eval_scalar(lyap[k + 1] - lyap[k] - increment)
    assert all(
        np.allclose(a, 0, atol=1e-5, rtol=0)
        for a in (ev.inner_prod_coords, ev.func_coords, ev.offset)
    )
for piece in S_piece_terms.values():
    ev = pm.eval_scalar(piece)
    assert np.allclose(ev.func_coords, 0, atol=1e-5, rtol=0) and abs(ev.offset) <= 1e-5
    assert (
        np.linalg.eigvalsh(np.asarray(ev.inner_prod_coords, dtype=float)).min() >= -1e-6
    )
grouping_checked = True
rank_credible = all(
    not any(rank_tolerance / 10 <= s <= 10 * rank_tolerance for s in sv)
    for sv in singular_values
)
print("Coverage residuals:", coverage_residuals, "Rank credible:", rank_credible)
