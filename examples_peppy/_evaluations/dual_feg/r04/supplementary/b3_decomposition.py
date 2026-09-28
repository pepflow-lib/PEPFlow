# Preserve the entire selected S as one PSD block. The B2 rank-one formula is
# close at 2.0e-5 but is not substituted for the saved matrix (identity atol 1e-5).
assert S_sol.row_names == basis_labels and S_sol.col_names == basis_labels
S_piece_terms = {'terminal_S': S_scalar}
piece_check = pm.eval_scalar(sum(S_piece_terms.values(), pf.Scalar.zero()) - S_scalar)
assert np.allclose(piece_check.inner_prod_coords, 0, atol=1e-5, rtol=0)
assert np.allclose(piece_check.func_coords, 0, atol=1e-5, rtol=0)
assert abs(float(piece_check.offset)) <= 1e-5
for piece in S_piece_terms.values():
    evaluated_piece = pm.eval_scalar(piece)
    assert np.linalg.eigvalsh(np.asarray(evaluated_piece.inner_prod_coords, dtype=float)).min() >= -1e-6
    assert np.allclose(evaluated_piece.func_coords, 0, atol=1e-5, rtol=0)
    assert abs(float(evaluated_piece.offset)) <= 1e-5
