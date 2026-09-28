# This saved notebook fragment shares its caller's execution namespace.
# These names are supplied by the notebook cells or serialized proof source.
# ty: ignore[unresolved-reference]
# ruff: noqa: F821

b4 = json.loads((notebook_dir / "state/feg_b4.json").read_text())
assert b4["certificate_id"] == certificate["certificate_id"]
assert b4["numerical_reconstruction"]["certificate_id"] == certificate["certificate_id"]
assert certificate_checked and grouping_checked
assert set(component_residuals) == {str(k) for k in range(N_int + 1)}
for key, value in b4["coeff_by_k"].items():
    expected_matrix = np.asarray(value, dtype=float).reshape(coeff_by_k[int(key)].shape)
    assert np.allclose(coeff_by_k[int(key)], expected_matrix, atol=1e-4, rtol=1e-5)
print(
    "B4 input unchanged; complete certificate and numerical structure were rechecked in the preceding cells."
)
print(
    "Exact coefficient functions to derive:",
    [u["name"] for u in b4["unresolved_coefficients"]],
)
