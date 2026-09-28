def V_k_structure(k):
    vectors=V_k_basis(k)
    C=coeff_by_k[k]
    # The operator problem has no function-value coordinates or scalar offsets.
    return sum((float(C[i,j])*vectors[i]*vectors[j] for i,j in np.ndindex(C.shape)),pf.Scalar.zero())
