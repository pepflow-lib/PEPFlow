def coeff_pattern(k,N):
    theta=theta_sequence(N)
    tau=1/(2*theta[-1]**2)
    if k==0:
        return np.zeros((0,0)),0.0
    if k==N:
        return np.diag([-tau,tau]),1.0
    return np.diag([-tau,-theta[k]**2/theta[-1]**2,tau]),2*theta[k]**2/theta[-1]**2


formula_residuals={}
for k in range(N_int+1):
    C_guess,alpha_guess=coeff_pattern(k,N_int)
    error=float(np.max(np.abs(C_guess-coeff_by_k[k]),initial=0))
    alpha_error=abs(alpha_guess-function_sample_coefficients[k])
    assert error<=1e-4 and alpha_error<=1e-4
    formula_residuals[str(k)]=dict(quadratic=error,function=alpha_error)
    print('Candidate formula residual',k,formula_residuals[str(k)])
