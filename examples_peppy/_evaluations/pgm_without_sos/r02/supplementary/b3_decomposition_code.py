# Reuse all factors of this same certificate. No candidate formula replaces numerical data.
assert np.allclose(D_saved,np.diag(np.diag(D_saved)),atol=0,rtol=0)
ell_saved=[sum((float(c)*v for c,v in zip(row,basis)),pf.Vector.zero()) for row in E_saved]
S_piece_terms={i:float(D_saved[i,i])*ell_saved[i]**2 for i in range(len(D_saved))}
piece_residual=pm.eval_scalar(sum(S_piece_terms.values(),pf.Scalar.zero())-S_scalar)
assert max(max_abs(piece_residual.inner_prod_coords),max_abs(piece_residual.func_coords),max_abs(piece_residual.offset))<1e-5
for piece in S_piece_terms.values():
    value=pm.eval_scalar(piece)
    assert max_abs(value.func_coords)==0 and max_abs(value.offset)==0
    assert np.linalg.eigvalsh(np.asarray(value.inner_prod_coords,dtype=float)).min()>=-1e-6
