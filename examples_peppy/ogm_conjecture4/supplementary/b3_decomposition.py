# Notebook code fragment; required globals are supplied by its caller.
# Retained for notebook execution or serialized proof/state source.
# ty: ignore[unresolved-reference]
# ruff: noqa: F821

"""All PSD pieces of this certificate's saved reverse LDL, with no solve."""

assert certificate_checked
if certificate["numerical_decomposition"]["method"] != "reverse_ldl":
    raise ValueError("This recipe requires the verified reverse LDL decomposition")
expected_labels = (
    ["x_0", "x_star"]
    + [f"grad_f(x_{i})" for i in range(N_int)]
    + [f"grad_f(y_{N_int})"]
)
assert basis_labels == expected_labels
# These captures have exactly diagonal D; do not silently discard a block entry.
assert np.array_equal(D_saved, np.diag(np.diag(D_saved)))
assert np.all(np.diag(D_saved) >= 0)
ell = [
    sum((float(coef) * v for coef, v in zip(row, basis)), pf.Vector.zero())
    for row in E_saved
]
S_piece_terms = {}
S_piece_pivots = {}
for i, vector in enumerate(ell):
    nonzero = np.flatnonzero(E_saved[i] != 0)
    assert nonzero.size
    pivot = int(nonzero[-1])
    assert E_saved[i, pivot] == 1
    name = f"reverse_ldl_{i}"
    S_piece_terms[name] = float(D_saved[i, i]) * vector**2
    S_piece_pivots[name] = pivot
assert sorted(S_piece_pivots.values()) == list(range(len(basis)))
piece_value = pm.eval_scalar(sum(S_piece_terms.values(), pf.Scalar.zero()) - S_scalar)
piece_reconstruction_error = float(np.max(np.abs(piece_value.inner_prod_coords)))
assert piece_reconstruction_error <= tol["reconstruction_atol"]
print(
    "Saved-S reverse LDL pieces:",
    len(S_piece_terms),
    "reconstruction error:",
    piece_reconstruction_error,
)
