D = np.asarray(certificate['numerical_decomposition']['D'], dtype=float)
E = np.asarray(certificate['numerical_decomposition']['ell_coords'], dtype=float)
assert np.max(np.abs(D-np.diag(np.diag(D)))) < 1e-12
ell = [sum((float(coef)*vector for coef,vector in zip(row,basis)),pf.Vector.zero()) for row in E]
S_piece_terms = {str(i):float(D[i,i])*ell[i]**2 for i in range(len(D))}
assert np.allclose(E.T@D@E,S_array,atol=1e-4,rtol=1e-5)
for i in range(len(D)):
    pivot = len(D)-1-i
    assert abs(E[i,pivot]-1) < 1e-10
    assert np.max(np.abs(E[i,pivot+1:]),initial=0) < 1e-10
    assert D[i,i] >= -1e-6
