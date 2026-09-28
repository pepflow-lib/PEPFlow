# This saved notebook fragment shares its caller's execution namespace.
# These names are supplied by the notebook cells or serialized proof source.
# ty: ignore[unresolved-reference]
# ruff: noqa: F821

# Nonincreasing convention: increments are nonnegative multipliers times
# monotonicity/Lipschitz residuals <= 0. The one PSD piece is a boundary term.
grouping_checked = False
rank_tolerance = 1e-4
rank_left, rank_right = 1, 1
group_terms = {name: term for name, term in weighted_terms.items() if name != tau_name}
term_assignment = {}
for name in group_terms:
    if name == f"A monotone:x_{N_int},x_star":
        term_assignment[name] = "boundary"
    elif name == f"A Lipschitz:x_{N_int - 1},x_{N_int}":
        term_assignment[name] = N_int - 1
    else:
        matched = False
        for k in range(N_int - 1):
            if name in (f"A monotone:x_{N_int},y_{k}", f"A Lipschitz:x_{k},y_{k}"):
                term_assignment[name] = k
                matched = True
                break
        assert matched, name
lyap = [pf.Scalar.zero()]
partial_sum = pf.Scalar.zero()
for k in range(N_int):
    partial_sum += sum(
        (group_terms[name] for name, step in term_assignment.items() if step == k),
        pf.Scalar.zero(),
    )
    lyap.append(partial_sum)
ranks = []
singular_values = []
for k, Vk in enumerate(lyap):
    matrix = np.asarray(pm.eval_scalar(Vk).inner_prod_coords, dtype=float)
    singular_values.append(np.linalg.svd(matrix, compute_uv=False).tolist())
    rank = int(np.linalg.matrix_rank(matrix, tol=rank_tolerance))
    ranks.append(rank)
    print(f"rank V_{k}: {rank}")
    if k == 0:
        print()
retained_ranks = ranks[rank_left : N_int + 1 - rank_right]
print(
    "Interior rank is constant at this N:",
    len(retained_ranks) >= 3 and len(set(retained_ranks)) == 1,
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
coverage_residuals = []
for expr in [coverage_diff, sum(S_piece_terms.values(), pf.Scalar.zero()) - S_scalar]:
    ev = pm.eval_scalar(expr)
    for coords in (ev.inner_prod_coords, ev.func_coords, np.asarray(ev.offset)):
        arr = np.asarray(coords, dtype=float)
        coverage_residuals.append(float(np.max(np.abs(arr), initial=0)))
        assert np.allclose(arr, 0, atol=tol["identity_atol"], rtol=0)
for k in range(N_int):
    increment = sum(
        (group_terms[name] for name, step in term_assignment.items() if step == k),
        pf.Scalar.zero(),
    )
    ev = pm.eval_scalar(lyap[k + 1] - lyap[k] - increment)
    for coords in (ev.inner_prod_coords, ev.func_coords, np.asarray(ev.offset)):
        assert np.allclose(
            np.asarray(coords, dtype=float), 0, atol=tol["identity_atol"], rtol=0
        )
for piece in S_piece_terms.values():
    ev = pm.eval_scalar(piece)
    assert np.allclose(ev.func_coords, 0, atol=tol["identity_atol"], rtol=0)
    assert np.allclose(ev.offset, 0, atol=tol["identity_atol"], rtol=0)
    assert (
        np.linalg.eigvalsh(np.asarray(ev.inner_prod_coords, dtype=float)).min()
        >= -tol["psd_tol"]
    )
grouping_checked = True
print("Full-coordinate coverage residual:", max(coverage_residuals))
