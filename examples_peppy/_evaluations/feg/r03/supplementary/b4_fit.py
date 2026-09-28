def coeff_pattern(k,N,L=1):
    if k==0:
        return np.zeros((0,0))
    return np.array([[2*k*k/N**2,2*k*L/N**2],[2*k*L/N**2,0.0]])

formula_residuals={}
for k in range(N_int+1):
    guess=coeff_pattern(k,N_int,float(params_sp['L']))
    error=float(np.max(np.abs(guess-coeff_by_k[k]),initial=0))
    formula_residuals[k]=error
    assert np.allclose(guess,coeff_by_k[k],atol=1e-4,rtol=1e-5)
    print(f'Candidate coefficient discrepancy k={k}: {error:.3e}')
