def coeff_pattern(k,N):
    if k==0:
        return np.zeros((0,0))
    if k==N:
        return np.array([[2,2/N],[2/N,0]],dtype=float)
    t=N-k
    return np.array([[0,-2,2/t,-2*k/(N*t)],[-2,-2,2/t,-2/t],[2/t,2/t,0,0],[-2*k/(N*t),-2/t,0,0]],dtype=float)

coefficient_formula_errors={}
for k,C in coeff_by_k.items():
    guess=coeff_pattern(k,N_int)
    error=float(np.max(np.abs(C-guess),initial=0.0))
    coefficient_formula_errors[str(k)]=error
    assert np.allclose(C,guess,atol=1e-4,rtol=1e-5)
    print(f'k={k}: normalized coefficient candidate error {error:.3e}')
