# The numerical certificate S is one whole PSD boundary piece. The rank-one
# candidate matches to 1e-4 but is not substituted for the selected matrix.
S_piece_terms = {'whole_S': S_scalar}
S_assignment = {'whole_S': 'boundary'}
piece_value = pm.eval_scalar(sum(S_piece_terms.values(), pf.Scalar.zero()) - S_scalar)
for coordinates in (piece_value.inner_prod_coords, piece_value.func_coords, np.asarray(piece_value.offset)):
    assert np.allclose(np.asarray(coordinates,dtype=float),0,atol=tol['identity_atol'],rtol=0)
assert np.linalg.eigvalsh(S_array).min() >= -tol['psd_tol']
