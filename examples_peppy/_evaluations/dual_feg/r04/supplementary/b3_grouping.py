# This saved notebook fragment shares its caller's execution namespace.
# These names are supplied by the notebook cells or serialized proof source.
# ty: ignore[unresolved-reference]
# ruff: noqa: F821

# Each increment sums within-step Lipschitz and half-step-to-terminal monotonicity.
# Both residuals are <=0 with nonnegative saved multipliers, hence V[k+1]<=V[k].
grouping_checked = False
rank_tolerance = 1e-4
rank_left, rank_right = 1, 1
group_terms = {
    name: value for name, value in weighted_terms.items() if name != tau_name
}
term_assignment = {f"A monotone:x_{N_int},x_star": "boundary"}
for k in range(N_int - 1):
    term_assignment[f"A monotone:x_{k}_half,x_{N_int}"] = k
    term_assignment[f"A Lipschitz:x_{k},x_{k}_half"] = k
term_assignment[f"A Lipschitz:x_{N_int - 1},x_{N_int}"] = N_int - 1
S_assignment = {"terminal_S": "boundary"}
assert set(term_assignment) == set(group_terms)
assert set(S_assignment) == set(S_piece_terms)
lyap = [pf.Scalar.zero()]
partial_sum = pf.Scalar.zero()
for k in range(N_int):
    partial_sum += sum(
        (term for name, term in group_terms.items() if term_assignment[name] == k),
        pf.Scalar.zero(),
    )
    partial_sum -= sum(
        (term for name, term in S_piece_terms.items() if S_assignment[name] == k),
        pf.Scalar.zero(),
    )
    lyap.append(partial_sum)
ranks, singular_values = [], []
for k, Vk in enumerate(lyap):
    matrix = np.asarray(pm.eval_scalar(Vk).inner_prod_coords, dtype=float)
    sv = np.linalg.svd(matrix, compute_uv=False)
    singular_values.append(sv.tolist())
    rank = int(np.count_nonzero(sv > rank_tolerance))
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
assert len(boundary_names) == 1 and len(boundary_S) == 1
leftover = sum((group_terms[name] for name in boundary_names), pf.Scalar.zero())
leftover -= sum((S_piece_terms[name] for name in boundary_S), pf.Scalar.zero())
coverage_diff = (
    lyap[N_int] + leftover - (sum(group_terms.values(), pf.Scalar.zero()) - S_scalar)
)
coverage_residuals = []


def component_error(expr):
    ev = pm.eval_scalar(expr)
    return max(
        float(np.max(np.abs(np.asarray(ev.inner_prod_coords, dtype=float)), initial=0)),
        float(np.max(np.abs(np.asarray(ev.func_coords, dtype=float)), initial=0)),
        abs(float(ev.offset)),
    )


coverage_residuals.append(component_error(coverage_diff))
for k in range(N_int):
    increment = sum(
        (term for name, term in group_terms.items() if term_assignment[name] == k),
        pf.Scalar.zero(),
    )
    coverage_residuals.append(component_error(lyap[k + 1] - lyap[k] - increment))
assert max(coverage_residuals) <= 1e-5
grouping_checked = True
print("Coverage and step identity maximum residual:", max(coverage_residuals))
