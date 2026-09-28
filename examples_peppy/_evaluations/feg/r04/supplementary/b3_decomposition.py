# The candidate rank-one square failed the B2 comparison tolerance. Retain the
# entire saved S as one PSD boundary block, reconstructed from all LDL factors.
D = np.asarray(certificate['numerical_decomposition']['D'])
E = np.asarray(certificate['numerical_decomposition']['ell_coords'])
assert certificate['numerical_decomposition']['basis_labels'] == basis_labels
assert np.allclose(E.T @ D @ E, S_array, atol=1e-4, rtol=1e-5)
ell = [sum((float(a)*v for a,v in zip(row,basis)),pf.Vector.zero()) for row in E]
S_piece_terms = {'whole_S':sum((float(D[i,j])*ell[i]*ell[j] for i,j in np.ndindex(D.shape)),pf.Scalar.zero())}
assert np.linalg.eigvalsh((S_array+S_array.T)/2).min() >= -1e-6
