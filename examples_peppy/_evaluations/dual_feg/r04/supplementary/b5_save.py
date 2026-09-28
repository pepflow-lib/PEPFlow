# This saved notebook fragment shares its caller's execution namespace.
# These names are supplied by the notebook cells or serialized proof source.
# ty: ignore[unresolved-reference]
# ruff: noqa: F821

final_formula = "For 0<=k<N: V_k=-(4L/N)<g,a>+(4L/(N-k))<g,b_k>-4<g,z_k>+(4L/(N-k))<b_k,z_k>-2||z_k||^2, where g=A(x_N), a=x_0-x_N, b_k=x_k-x_N. V_0=0. V_N=2||g||^2-(4L/N)<g,a>."
final_structure = {
    "quadratic_convention": "V=sum_ij C_ij <v_i,v_j>, symmetric C; off-diagonal entries counted twice",
    "interior": {
        "index_domain": "1<=k<N",
        "basis_labels": ["A(x_N)", "x_0-x_N", "x_k-x_N", "z_k"],
        "coefficients": {
            "C01": "-2L/N",
            "C02": "2L/(N-k)",
            "C03": "-2",
            "C23": "2L/(N-k)",
            "C33": "-2",
            "other_independent_entries": "0",
        },
    },
    "initial": {
        "index_domain": "k=0, N>=1",
        "basis_labels": [],
        "coefficients": {},
        "expression": "0",
    },
    "terminal": {
        "index_domain": "k=N, N>=1",
        "basis_labels": ["A(x_N)", "x_0-x_N"],
        "coefficients": {"C00": "2", "C01": "-2L/N", "C11": "0"},
    },
    "function_terms": [],
    "constant_terms": [],
}
proof_arguments = {
    "step": "Exact native symbolic Gram/function/offset identities. For t=N-k>=2, difference equals (2/t^2)Lip+(4L/[t(t-1)])Mon. Local multipliers solved from all coefficient equations.",
    "base": "Separate symbolic initial context uses z_0=0; V_0=0 for every N>=1. Actual first step is checked for N>=2.",
    "last_step": "At t=1, x_N=x_(N-1)-[z_(N-1)+A(x_(N-1))]/L; difference is 2 Lip(x_(N-1),x_N). Separate N=1 check uses z_0=0.",
    "boundary": "||g||^2-4L^2R^2/N^2 = V_N+(4L/N)Mon(x_N,x_star)-||g-(2L/N)(x_0-x_star)||^2+(4L^2/N^2)(||x_0-x_star||^2-R^2).",
    "signs": "Lip<=0 by L-Lipschitz continuity; Mon<=0 by monotonicity; A(x_star)=0. Coefficients positive for L>0,N>=1,t>=2. Square nonnegative. Initial residual<=0.",
    "domain": "Real finite-dimensional Euclidean space, monotone L-Lipschitz A, L>0,R>=0, integer N>=1. Denominators t and t-1 used only for t>=2; last step and N=1 checked separately.",
    "normalization": "No division by R or g is used. The boundary gives ||A(x_N)||^2<=4L^2R^2/N^2 from V_N<=V_0=0, including R=0.",
}
assert all(proof_checks.values()) and len(exact_identity_results) == 6
b5_state = {
    **b4,
    "proof_checks": proof_checks,
    "proof_arguments": proof_arguments,
    "lyapunov_formula": final_formula,
    "discovery_expression_structure": b4["expression_structure"],
    "expression_structure": final_structure,
    "coefficient_formula_status": "verified",
    "remaining_unknowns": [],
    "coeff_code": (
        notebook_dir / "supplementary/b5_analytic_coefficients.py"
    ).read_text(),
    "local_multiplier_code": (
        notebook_dir / "supplementary/b5_analytic_coefficients.py"
    ).read_text(),
    "exact_identity_results": exact_identity_results,
    "numerical_certificate_verified": True,
    "analytic_full_pep_verified": False,
    "lyapunov_proof_verified": True,
    "analytic_full_pep_status": "Global B2 lambda/S remain numerical candidates; the arbitrary-horizon theorem is established by the local Lyapunov proof.",
    "theorem": "For all integer N>=1, ||A(x_N)||^2 <= 4 L^2 R^2/N^2.",
    "theorem_latex": r"\|A(x_N)\|^2\leq\frac{4L^2R^2}{N^2}",
    "run_status": "completed",
    "unresolved_work": [],
    "presentation_policy": "evaluation-ancillary-v1",
    "rendered_visual_inspection": "Not performed under evaluation presentation override",
}
(notebook_dir / "state/dual_feg_b5.json").write_text(
    json.dumps(b5_state, indent=2, allow_nan=False)
)
