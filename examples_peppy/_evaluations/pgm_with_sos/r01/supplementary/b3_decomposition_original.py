# Use the supplied, already reconstructed direct squares without mixing certificates.
S_piece_terms = {f"{j}:{family}": c*u**2 for j,family,c,u in pieces}
S_assignment = {name: int(name.split(':')[0])-1 for name in S_piece_terms}
piece_diff = pm.eval_scalar(sum(S_piece_terms.values(),pf.Scalar.zero()) - S_scalar)
assert all(maxabs(v) <= 1e-5 for v in (piece_diff.inner_prod_coords,piece_diff.func_coords,piece_diff.offset))
for piece in S_piece_terms.values():
    coords = pm.eval_scalar(piece)
    assert maxabs(coords.func_coords) <= 1e-5 and maxabs(coords.offset) <= 1e-5
    matrix = np.asarray(coords.inner_prod_coords,dtype=float)
    assert np.linalg.eigvalsh((matrix+matrix.T)/2).min() >= -1e-6
