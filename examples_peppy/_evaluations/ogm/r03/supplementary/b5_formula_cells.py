def closed_form_coefficients(k, n, theta, smoothness):
    T = sp.sympify(theta[n])
    smoothness = sp.sympify(smoothness)
    tau = smoothness/(2*T**2)
    if k == 0:
        return sp.zeros(0,0)
    if k == 1:
        cross = 1/(2*theta[1]*T**2)
        return sp.Matrix([[-tau,0,cross],[0,tau,-cross],[cross,-cross,1/(smoothness*T**2)]])
    rho = theta[k] if k < n else T/2
    C = sp.zeros(4,4)
    C[0,0],C[1,1] = -tau,tau
    C[1,3]=C[3,1]=-rho/T**2
    C[2,3]=C[3,2]=rho/T**2
    C[3,3]=theta[k-1]**2/(smoothness*T**2)
    return C

def closed_form_potential(k, context, function, theta, smoothness):
    n = len(theta)-1
    T = theta[n]
    if k == 0:
        return pf.Scalar.zero()
    rho = theta[k] if k < n else T/2
    previous_squared = theta[k-1]**2
    xk,zk,star,x0 = context[f"x_{k}"],context[f"z_{k}"],context["x_star"],context["x_0"]
    gk = function.grad(xk)
    return smoothness/(2*T**2)*((zk-star)**2-(x0-star)**2)+2*previous_squared/T**2*(function(xk)-function(star))+previous_squared/(smoothness*T**2)*gk**2+2*rho/T**2*gk*(xk-zk)

formula_comparisons = []
for state_path in (notebook_dir / "state" / "ogm_b4.json",notebook_dir / "supplementary" / "b2-N6-certificate.json"):
    sample = json.loads(state_path.read_text())
    ctx_sample,pb_sample,obj_sample,pm_sample,terms_sample,checks_sample = check_certificate(sample,notebook_dir)
    theta_sample = theta_sequence(sample["N"])
    partial_sample = pf.Scalar.zero()
    for k in range(sample["N"]+1):
        if k:
            tag = "z_0" if k == 1 else f"x_{k-1}"
            partial_sample += terms_sample[f"f:x_star,{tag}"]+terms_sample[f"f:{tag},x_{k}"]
        analytic_sample = closed_form_potential(k,ctx_sample,obj_sample,theta_sample,1)
        difference = pm_sample.eval_scalar(analytic_sample-partial_sample)
        errors = [float(np.max(np.abs(np.asarray(c,dtype=float)),initial=0)) for c in (difference.inner_prod_coords,difference.func_coords,np.asarray(difference.offset))]
        assert max(errors) <= 1e-5
        formula_comparisons.append(dict(N=sample["N"],k=k,gram=errors[0],function=errors[1],offset=errors[2]))
        if sample["N"] == b4_final["N"]:
            C_formula = np.array(closed_form_coefficients(k,sample["N"],theta_sample,1),dtype=float)
            C_observed = np.asarray(b4_final["coeff_by_k"][str(k)],dtype=float).reshape(C_formula.shape)
            assert np.allclose(C_formula,C_observed,atol=1e-4,rtol=1e-5)
            print(f"k={k}: closed-form coefficient residual {np.max(np.abs(C_formula-C_observed),initial=0):.3e}")
            if k:
                labels_formula = ["x_0-x_star","z_1-x_star","g_1"] if k==1 else ["x_0-x_star",f"z_{k}-x_star",f"x_{k}-x_star",f"g_{k}"]
                pf.pprint_labeled_matrix(pf.MatrixWithNames(C_formula,labels_formula,labels_formula))
print("Full potential comparisons at N=4,6:",formula_comparisons)
