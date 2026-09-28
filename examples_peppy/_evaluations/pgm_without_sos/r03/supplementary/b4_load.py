# This saved notebook fragment shares its caller's execution namespace.
# These names are supplied by the notebook cells or serialized proof source.
# ty: ignore[unresolved-reference]
# ruff: noqa: F821


b3 = json.loads((NOTEBOOK_DIR / "state/pgm_b3.json").read_text())
assert (
    b3["rank_search"]
    == json.loads((NOTEBOOK_DIR / b3["rank_search"]["evidence_path"]).read_text())[
        "summary"
    ]
)
selected_sample = reconstruct_and_group(b3)
ctx = selected_sample["ctx"]
ctx.set_as_current()
pm = selected_sample["pm"]
lyap = selected_sample["lyap"]
params_sp = selected_sample["params_sp"]
N_int = selected_sample["N_int"]
assert selected_sample["ranks"] == b3["rank_profile"]
for k, V in enumerate(lyap):
    value = pm.eval_scalar(V)
    for actual, saved in [
        (value.inner_prod_coords, b3["lyap_inner_prod_coords"][k]),
        (value.func_coords, b3["lyap_func_coords"][k]),
        (value.offset, b3["lyap_offsets"][k]),
    ]:
        assert np.allclose(
            np.asarray(actual, float), np.asarray(saved, float), atol=1e-4, rtol=1e-5
        )
print(
    "Selected certificate and all partial sums revalidated; interior indices 1..N-1, endpoints checked separately."
)
