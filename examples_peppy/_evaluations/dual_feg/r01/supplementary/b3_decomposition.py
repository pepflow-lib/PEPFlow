# Keep the whole positive Gram remainder as one terminal boundary piece.
# It is reconstructed from the selected saved factors, with all tiny terms retained.
D=np.asarray(certificate['numerical_decomposition']['D'],dtype=float)
E=np.asarray(certificate['numerical_decomposition']['ell_coords'],dtype=float)
ell=[sum((float(coef)*vector for coef,vector in zip(row,basis)),pf.Vector.zero()) for row in E]
S_piece_terms={'terminal_gram':sum((float(D[i,j])*ell[i]*ell[j] for i,j in np.ndindex(D.shape)),pf.Scalar.zero())}
S_assignment={'terminal_gram':'boundary'}
