# This saved notebook fragment shares its caller's execution namespace.
# These names are supplied by the notebook cells or serialized proof source.
# ty: ignore[unresolved-reference]
# ruff: noqa: F821

b3 = json.loads((notebook_dir / "state/bppm_b3.json").read_text())
assert certificate["certificate_id"] == b3["certificate_id"]
assert certificate_checked and grouping_checked
assert ranks == b3["rank_profile"]
rank_evidence = json.loads(
    (notebook_dir / b3["rank_search"]["evidence_path"]).read_text()
)
assert rank_evidence["summary"] == b3["rank_search"]
interior_indices = list(range(1, N_int))
exceptional_indices = [0, N_int]
for k, Vk in enumerate(lyap):
    evaluated = pm.eval_scalar(Vk)
    for actual, saved in (
        (evaluated.inner_prod_coords, b3["lyap_inner_prod_coords"][k]),
        (evaluated.func_coords, b3["lyap_func_coords"][k]),
        (evaluated.offset, b3["lyap_offsets"][k]),
    ):
        assert np.allclose(np.asarray(actual, dtype=float), saved, atol=1e-4, rtol=1e-5)
print(
    "Selected certificate and all saved partial-sum coordinates revalidated; interior indices:",
    interior_indices,
    "exceptions:",
    exceptional_indices,
)
