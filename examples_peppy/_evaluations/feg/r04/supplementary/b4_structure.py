def V_k_structure(k):
    vectors=V_k_basis(k)
    C=coeff_by_k[k]
    # Every sample has no function-value or offset contribution.
    return sum((float(C[i,j])*vectors[i]*vectors[j] for i,j in np.ndindex(C.shape)),pf.Scalar.zero())
