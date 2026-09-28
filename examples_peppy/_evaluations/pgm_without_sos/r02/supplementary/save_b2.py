# This saved notebook fragment shares its caller's execution namespace.
# These names are supplied by the notebook cells or serialized proof source.
# ty: ignore[unresolved-reference]
# ruff: noqa: F821

# %% Save only after all current numerical checks have passed.
search = dict(
    completed=True,
    references_reviewed=[
        "Own input and approved generic API/workflow only; target references excluded by clean-room rules."
    ],
    attempts=[
        {
            "method": "Fraction recognition and telescoping scalar conservation",
            "outcome": "Candidate f flow a_i=(i+1)/(2N-i), g flow b_i=i/(2N-i); star weights are successive differences with terminal weight 1-flow(N-1).",
            "lambda_max_abs_error": lambda_error,
        },
        {
            "method": "Candidate residual S assembled exactly; numerical spectrum and reverse-LDL factors inspected",
            "outcome": "Candidate matches S at this sample; no arbitrary-horizon PSD decomposition established.",
            "S_gram_max_abs_error": S_candidate_error,
        },
    ],
    unresolved_components=[
        "arbitrary-horizon candidate identity and PSD proof",
        "interpretable all-horizon square families",
    ],
)
source_text = (notebook_dir / "supplementary/b2_notebook_cells.py").read_text(
    encoding="utf-8-sig"
)
lamb_code = source_text[
    source_text.index("def candidate_multiplier") : source_text.index("lambda_error =")
]
S_code = "S_candidate = weighted_candidate - pb.performance_metric + sp.Rational(1,4*N)"
state = {
    **b1,
    **selected,
    "normalization": dict(
        tau_name="initial_condition",
        initial_condition=b1["initial_condition"],
        performance_metric=b1["performance_metric"],
        bound_value=selected["opt_value"],
        bound_formula=b1["conjectured_rate"],
    ),
    "numerical_checks": dict(
        tolerances=tolerances, residuals=residuals, passed=bool(passed)
    ),
    "numerical_decomposition": dict(
        method="reverse_ldl",
        D=D.tolist(),
        ell_coords=E.tolist(),
        basis_labels=selected["basis_vectors"],
    ),
    "closed_form_search": search,
    "formula_status": {"lambda": "candidate", "S": "candidate"},
    "lamb_code": lamb_code,
    "S_code": S_code,
    "S_decomp_type": "ldl",
    "numerical_certificate_verified": True,
    "analytic_full_pep_verified": False,
    "lyapunov_proof_verified": False,
    "require_analytic_full_pep": False,
    "proof_valid": True,
    "verification_source": "supplementary/b2_notebook_cells.py",
    "verification_source_sha256": hashlib.sha256(source_text.encode()).hexdigest(),
}
certificate_keys = (
    "N_verify",
    "params_json",
    "relaxed_constraints",
    "S_matrix",
    "S_row_names",
    "S_col_names",
    "basis_vectors",
    "basis_scalars",
    "opt_value",
    "tau_sol",
    "tau_name",
    "named_dual_values",
    "constraint_metadata",
    "normalization",
    "certificate_provenance",
    "numerical_checks",
    "numerical_decomposition",
)
state["certificate_id"] = hashlib.sha256(
    json.dumps(
        {key: state[key] for key in certificate_keys},
        sort_keys=True,
        separators=(",", ":"),
        allow_nan=False,
    ).encode()
).hexdigest()
for filename in ("pgm_relaxed.json", "pgm_b2.json"):
    (notebook_dir / "state" / filename).write_text(
        json.dumps(state, indent=2, allow_nan=False)
    )
print("Saved verified coherent certificate:", state["certificate_id"])
