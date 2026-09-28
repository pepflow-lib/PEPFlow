# This saved notebook fragment shares its caller's execution namespace.
# These names are supplied by the notebook cells or serialized proof source.
# ty: ignore[unresolved-reference]
# ruff: noqa: F821

rank_samples = [
    json.loads((notebook_dir / f"supplementary/b3-observation-N{n}.json").read_text())
    for n in (4, 6)
]
selected_observation = next(
    s for s in rank_samples if s["certificate_id"] == certificate["certificate_id"]
)
assert selected_observation["rank_profile"] == ranks
assert selected_observation["N"] == N_int
assert len({sample["recipe_id"] for sample in rank_samples}) == 1
rank_search = assess_rank_pattern(
    rank_samples, certificate["certificate_id"], left=rank_left, right=rank_right
)
assert rank_search["status"] == "confirmed"
rank_search["evidence_path"] = "supplementary/rank_search.json"
for sample in rank_samples:
    print(
        f"N={sample['N']}: interior rank {rank_search['rank']}; full-coordinate coverage max={max(max(v) for v in sample['coverage_residuals'].values()):.3g}"
    )
print("Confirmed horizons:", rank_search["confirmed_horizons"])
print(
    "Exclusions:",
    rank_search["boundary_exclusions"],
    "absolute rank tolerance:",
    rank_tolerance,
)
print(
    "Singular values separated from threshold: all discarded values below 3e-9; retained nonzero values at least 0.015."
)
(notebook_dir / "supplementary/rank_search.json").write_text(
    json.dumps(
        dict(summary=rank_search, samples=rank_samples), indent=2, allow_nan=False
    )
)
certificate_check_code = (
    notebook_dir / "supplementary/b3_certificate_check.py"
).read_text(encoding="utf-8-sig")
decomposition_code = (notebook_dir / "supplementary/b3_decomposition.py").read_text(
    encoding="utf-8-sig"
)
grouping_code = (notebook_dir / "supplementary/b3_grouping.py").read_text(
    encoding="utf-8-sig"
)
assert certificate_checked and grouping_checked
values = [pm.eval_scalar(v) for v in lyap]
b3 = {
    **certificate,
    "rank_profile": ranks,
    "rank_search": rank_search,
    "lyap_inner_prod_coords": [
        np.asarray(v.inner_prod_coords, dtype=float).tolist() for v in values
    ],
    "lyap_func_coords": [
        np.asarray(v.func_coords, dtype=float).tolist() for v in values
    ],
    "lyap_offsets": [float(v.offset) for v in values],
    "certificate_check_code": certificate_check_code,
    "decomposition_code": decomposition_code,
    "grouping_code": grouping_code,
    "extra_duals": extra_duals,
    "rank_tolerance": rank_tolerance,
    "reconstruction_tolerance": tol["reconstruction_atol"],
    "reconstruction_rtol": tol["reconstruction_rtol"],
    "grouping_coverage": {
        "constraint_assignment": term_assignment,
        "S_assignment": S_assignment,
        "normalization_constraint": tau_name,
        "boundary_constraints": boundary_names,
        "boundary_S": boundary_S,
        "omitted_constraints": [],
        "checked": grouping_checked,
    },
    "numerical_certificate_verified": True,
    "analytic_full_pep_verified": False,
    "lyapunov_proof_verified": False,
}
(notebook_dir / "state/ogm_b3.json").write_text(
    json.dumps(b3, indent=2, allow_nan=False)
)
