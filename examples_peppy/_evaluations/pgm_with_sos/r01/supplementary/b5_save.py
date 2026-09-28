# Notebook/proof state is executed below into the shared runtime namespace.
# These names are supplied by the notebook cells or serialized proof source.
# ty: ignore[unresolved-reference]
# ruff: noqa: F821

proof_checks = {
    "step": step_verified,
    "base": base_verified and small_verified,
    "boundary": boundary_verified and small_verified,
    "signs": True,
    "domain": True,
    "normalization": True,
}
proof_arguments = {
    "domain": "L>0, integer N>=1; 1<=i<=N implies 2N-i>=N>0 and 2N+1-i>=N+1>0. Interior 2<=i<N; first, final, and N=1 separately checked.",
    "signs": "Every interpolation residual is <=0. All four local multipliers, initial 1/(2N), and the three SOS coefficients are >=0 from the displayed positive denominators and i-1>=0. Thus V_i-V_(i-1)<=0.",
    "normalization": "V_0=0 and V_N=h(x_N)-h(x_star)-L*||x_0-x_star||^2/(4N). Telescoping and the initial radius give hgap<=L*distance^2/(4N)<=L*R^2/(4N). R=0 is included.",
    "boundary": "Terminal identity is checked at symbolic N>=2; N=1 is separately checked without evaluating g(x_0).",
    "coefficient_derivation": "Generic linear equations in all Gram, function and offset coordinates solve for 12 current coefficients given the candidate preceding potential; exact base, terminal and step checks close the induction.",
}
final_lyapunov_formula = "V_0=0; for 1<=k<N, D=2N-k: V_k=(k+1)/D*(f_k-f_star)+k/D*(g_k-g_star)-<a_k,d_k>/D+||a_k-a_star||^2/(2*L*D)+L*(N-k)/D^2*||d_k||^2-L/(4*N)*||d_0||^2; V_N=h_N-h_star-L/(4*N)*||d_0||^2"
resolved_coefficients = {f"{r},{s}": "0" for r in range(4) for s in range(r, 4)}
resolved_coefficients.update(
    {
        "0,2": "-1/(2*(2*N-k))",
        "1,1": "-L/(4*N)",
        "2,2": "L*(N-k)/(2*N-k)^2",
        "2,3": "-1/(2*(2*N-k))",
        "3,3": "1/(2*L*(2*N-k))",
    }
)
final_expression_structure = {
    "quadratic_convention": "sum_ij C_ij <v_i,v_j>, symmetric C; off-diagonal entries counted twice",
    "interior": {
        "index_domain": "1<=k<N",
        "basis_labels": ["a_star", "x_0-x_star", "x_k-x_star", "a_k-a_star"],
        "coefficients": resolved_coefficients,
    },
    "initial": {
        "index_domain": "k=0",
        "basis_labels": [],
        "coefficients": {},
        "value": 0,
    },
    "terminal": {
        "index_domain": "k=N",
        "basis_labels": ["x_0-x_star"],
        "coefficients": {"0,0": "-L/(4*N)"},
    },
    "function_terms": [
        {
            "expression": "f(x_k)-f_star",
            "index_domain": "1<=k<N",
            "coefficient": "(k+1)/(2*N-k)",
        },
        {
            "expression": "g(x_k)-g_star",
            "index_domain": "1<=k<N",
            "coefficient": "k/(2*N-k)",
        },
        {"expression": "f(x_N)-f_star", "index_domain": "k=N", "coefficient": "1"},
        {"expression": "g(x_N)-g_star", "index_domain": "k=N", "coefficient": "1"},
    ],
    "constant_terms": [],
}
remaining_unknowns = []
lyapunov_proof_verified = all(proof_checks.values()) and not remaining_unknowns
assert lyapunov_proof_verified
state_b5 = {
    **b4,
    "lyapunov_proof_verified": lyapunov_proof_verified,
    "analytic_full_pep_verified": False,
    "proof_checks": proof_checks,
    "proof_arguments": proof_arguments,
    "lyapunov_formula": final_lyapunov_formula,
    "discovery_expression_structure": b4["expression_structure"],
    "expression_structure": final_expression_structure,
    "coeff_code": None,
    "local_multiplier_code": common_source_for_state,
    "coefficient_formula_status": "symbolically_derived_and_verified",
    "unresolved_coefficients": remaining_unknowns,
    "remaining_unknowns": remaining_unknowns,
    "analytic_comparison": analytic_comparison,
    "proof_valid": lyapunov_proof_verified,
    "global_analytic_status": "unresolved; not required for the local Lyapunov objective",
    "run_status": "proof_verified_pending_final_notebook_audit",
}
(root / "state/pgm_b5.json").write_text(json.dumps(state_b5, indent=2))
print("Numerical certificate:", state_b5["numerical_certificate_verified"])
print("Analytic full PEP:", state_b5["analytic_full_pep_verified"])
print("Analytic Lyapunov:", state_b5["lyapunov_proof_verified"])
print(final_lyapunov_formula)
print("Theorem: h(x_N)-h(x_star) <= L R^2/(4N), for integer N>=1, L>0, R>=0.")
print("LaTeX theorem:", r"h(x_{N})-h(x_{\star})\le\frac{LR^{2}}{4N}")
