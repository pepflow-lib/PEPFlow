# This saved notebook fragment shares its caller's execution namespace.
# These names are supplied by the notebook cells or serialized proof source.
# ty: ignore[unresolved-reference]
# ruff: noqa: F821

basis_code = (notebook_dir / "supplementary/b4_basis.py").read_text()
structure_code = (notebook_dir / "supplementary/b4_structure.py").read_text()
coeff_code = (notebook_dir / "supplementary/b4_formula.py").read_text()
templates = {
    "interior": ["A(x_N)", "x_0-x_N", "x_k-x_N", "z_k"],
    "initial": [],
    "terminal": ["A(x_N)", "x_0-x_N"],
}
expression_structure = {
    "quadratic_convention": "V_quadratic = sum_ij C_ij <v_i,v_j>; C symmetric, off-diagonal counted twice",
    "interior": {
        "index_domain": "1<=k<=N-1 (left=right=1)",
        "basis_labels": templates["interior"],
        "coefficients": {
            "C01": "-2/N",
            "C02": "2/(N-k)",
            "C03": "-2",
            "C23": "2/(N-k)",
            "C33": "-2",
            "other_independent_entries": "0",
        },
        "status": "candidate at L=R=1, checked at N=6",
    },
    "initial": {
        "index_domain": "k=0",
        "basis_labels": [],
        "coefficients": {},
        "expression": "0",
    },
    "terminal": {
        "index_domain": "k=N",
        "basis_labels": templates["terminal"],
        "coefficients": {"C00": "2", "C01": "-2/N", "C11": "0"},
        "status": "candidate at L=R=1",
    },
    "function_terms": [],
    "constant_terms": [],
}
numerical_reconstruction = {
    "certificate_id": b3["certificate_id"],
    "required_indices": list(range(N_int + 1)),
    "quadratic_residuals": {
        str(k): value for k, value in coefficient_residuals.items()
    },
    "component_residuals": component_residuals,
    "tolerances": {
        **extraction_tolerances,
        "component_atol": 1e-4,
        "component_rtol": 1e-5,
    },
    "passed": True,
}
b4 = {
    **b3,
    "basis_templates": templates,
    "basis_code": basis_code,
    "structure_code": structure_code,
    "coeff_by_k": {str(k): C.tolist() for k, C in coeff_by_k.items()},
    "coeff_code": coeff_code,
    "coefficient_formula_status": "candidate",
    "expression_structure": expression_structure,
    "unresolved_coefficients": [],
    "numerical_reconstruction": numerical_reconstruction,
    "sparse_search": sparse_search,
    "formula_residuals": formula_residuals,
    "basis_independence_ranks": independence,
    "numerical_certificate_verified": True,
    "analytic_full_pep_verified": False,
    "lyapunov_proof_verified": False,
    "analytic_obligations": [
        "Extend coefficient formulas to all N and L>0",
        "Prove exact step/base/terminal identities and final residual bound",
    ],
}
(notebook_dir / "state/dual_feg_b4.json").write_text(
    json.dumps(b4, indent=2, allow_nan=False)
)
