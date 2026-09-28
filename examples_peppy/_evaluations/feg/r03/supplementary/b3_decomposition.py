# Retain the whole coherent PSD remainder as one terminal PSD block.
# B2's candidate square was compared but is not substituted for saved S.
D = np.asarray(certificate["numerical_decomposition"]["D"],dtype=float)
E = np.asarray(certificate["numerical_decomposition"]["ell_coords"],dtype=float)
ell = [sum((float(c)*v for c,v in zip(row,basis)),pf.Vector.zero()) for row in E]
full_S = sum((float(D[i,j])*ell[i]*ell[j] for i,j in np.ndindex(D.shape)),pf.Scalar.zero())
assert np.allclose(E.T@D@E,S_array,atol=tol["reconstruction_atol"],rtol=tol["reconstruction_rtol"])
S_piece_terms = {"terminal_PSD_remainder": full_S}
