# This saved notebook fragment shares its caller's execution namespace.
# These names are supplied by the notebook cells or serialized proof source.
# ty: ignore[unresolved-reference]
# ruff: noqa: F821

REPO_ROOT = repo_root
main_certificate = json.loads((notebook_dir / "state/dual_feg_b2.json").read_text())
extra_certificate = json.loads(
    (notebook_dir / "supplementary/n8/dual_feg_b2.json").read_text()
)
rank_samples = []
print("Selected N=6 sample:")
main_observation, main_partial_sums = evaluate_rank_sample(main_certificate)
rank_samples.append(main_observation)
print("Confirming N=8 sample:")
extra_observation, extra_partial_sums = evaluate_rank_sample(extra_certificate)
rank_samples.append(extra_observation)
assert len({sample["N"] for sample in rank_samples}) == 2
assert all(
    sample["certificate_checked"]
    and sample["grouping_checked"]
    and sample["rank_credible"]
    for sample in rank_samples
)
assert all(
    sample["rank_convention"] == rank_samples[0]["rank_convention"]
    for sample in rank_samples
)
assert all(
    sample["recipe_id"] == rank_samples[0]["recipe_id"] for sample in rank_samples
)
retained = [sample["rank_profile"][1 : sample["N"]] for sample in rank_samples]
assert all(len(profile) >= 3 and set(profile) == {4} for profile in retained)
rank_search = {
    "status": "confirmed",
    "boundary_exclusions": {"left": 1, "right": 1},
    "rank": 4,
    "confirmed_horizons": [6, 8],
    "selected_certificate_id": main_certificate["certificate_id"],
    "recipe_id": main_observation["recipe_id"],
    "rank_convention": main_observation["rank_convention"],
    "unresolved_samples": [],
    "evidence_path": "supplementary/rank_search.json",
}
print(
    "Confirmed interior rank:",
    4,
    "at horizons:",
    [6, 8],
    "fixed exclusions:",
    (1, 1),
    "absolute tolerance:",
    1e-4,
)
print(
    "Every N=6 and N=8 retained singular value is outside the ambiguity band [0.5e-4,2e-4]."
)
source_names = ["b3_certificate_check.py", "b3_decomposition.py", "b3_grouping.py"]
source_text = [
    (notebook_dir / "supplementary" / name).read_text() for name in source_names
]
b3_state = {
    **main_certificate,
    **main_partial_sums,
    "rank_profile": main_observation["rank_profile"],
    "rank_search": rank_search,
    "certificate_check_code": source_text[0],
    "decomposition_code": source_text[1],
    "grouping_code": source_text[2],
    "rank_tolerance": 1e-4,
    "reconstruction_tolerance": 1e-4,
    "reconstruction_rtol": 1e-5,
    "numerical_certificate_verified": True,
    "analytic_full_pep_verified": False,
    "lyapunov_proof_verified": False,
}
(notebook_dir / "supplementary/rank_search.json").write_text(
    json.dumps(
        {"summary": rank_search, "samples": rank_samples}, indent=2, allow_nan=False
    )
)
(notebook_dir / "state/dual_feg_b3.json").write_text(
    json.dumps(b3_state, indent=2, allow_nan=False)
)
