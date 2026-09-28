# Historical Block 2 notebook fragment; not a standalone module.
# Inputs and intermediate results are supplied by the notebook namespace.
# The notebook validates extracted function sources and the saved-state schema.
# ty: ignore[unresolved-reference, no-matching-overload, invalid-assignment, not-subscriptable, unresolved-attribute]
# ruff: noqa: F821

"""Save Block 2 after the visible notebook certificate and candidate checks."""

import ast
import copy

candidate_source = (HERE / "block2_candidates.py").read_text()
tree = ast.parse(candidate_source)
functions = {
    node.name: ast.get_source_segment(candidate_source, node)
    for node in tree.body
    if isinstance(node, ast.FunctionDef)
}
lamb_code = "\n\n".join(
    functions[name] for name in ("candidate_theta", "candidate_weights", "lamb")
)
S_code = functions["candidate_S"]
closed_form_search = dict(
    completed=True,
    references_reviewed=[
        "Current-run B1/B2 setup and fresh dense/sparse captures only; other examples and reference formulas excluded by clean-room instruction."
    ],
    attempts=[
        dict(
            method="Ratios and star-chain function balance",
            outcome="Chain weights equal cumulative star weights; sum(star)=1 within solver tolerance.",
        ),
        dict(
            method="a_i=4*tau*theta_i and a_y=2*tau",
            outcome="Rejected: Schur remainder has negative eigenvalue at N=4.",
            minimum_eigenvalue=search_record["candidates"][0]["schur_eigenvalues"][0],
        ),
        dict(
            method="Constant-gradient null equations followed by telescoping theta identities",
            outcome="Explicit general-N multiplier candidate; agrees with selected multipliers at atol=1e-4.",
            lambda_max_abs_error=lambda_candidate_error,
            formula=search_record["closed_form"],
        ),
        dict(
            method="Candidate S from full weighted interpolation identity",
            outcome="Matches selected S at atol=1e-4; function/offset components vanish numerically; generic all-N PSD remains unresolved.",
            checks=candidate_component_checks,
        ),
        dict(
            method="Exact elementary telescope and derivative identities",
            outcome="All exact residuals zero; weights nonnegative for q>=1 and 0<=s<=q.",
            residuals={k: str(v) for k, v in exact_residuals.items()},
        ),
    ],
    accepted_algebra_only_samples=candidate_sample_checks,
    unresolved_components=[
        "Analytic PSD proof of candidate Gram/Schur remainder for arbitrary N",
        "Complete all-N full-PEP proof",
    ],
)
state = {
    **b1,
    **copy.deepcopy(selected),
    "numerical_checks": numerical_checks,
    "numerical_decomposition": numerical_decomposition,
    "closed_form_search": closed_form_search,
    "formula_status": {"lambda": "candidate", "S": "candidate"},
    "formula_domain": "Integer N>=1, L>0, R>=0; candidates not yet globally verified",
    "lamb_code": lamb_code,
    "S_code": S_code,
    "S_decomp_type": "ldl",
    "numerical_certificate_verified": bool(passed),
    "analytic_full_pep_verified": False,
    "lyapunov_proof_verified": False,
    "require_analytic_full_pep": bool(b1.get("require_analytic_full_pep", False)),
    "proof_valid": bool(passed),
}
for filename in (
    "verify_block2.py",
    "b2_formula_search.py",
    "block2_candidates.py",
    "save_block2.py",
):
    path = HERE / filename
    state["certificate_provenance"]["source_hashes"][
        path.relative_to(ROOT).as_posix()
    ] = hashlib.sha256(path.read_bytes()).hexdigest()
for path, digest in state["certificate_provenance"]["source_hashes"].items():
    assert hashlib.sha256((ROOT / path).read_bytes()).hexdigest() == digest
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
assert state["numerical_certificate_verified"] and closed_form_search["completed"]
for filename in (f"{NAME}_relaxed.json", f"{NAME}_b2.json"):
    (STATE / filename).write_text(json.dumps(state, indent=2, allow_nan=False) + "\n")
print("Certificate ID:", state["certificate_id"])
print("Numerical certificate verified:", state["numerical_certificate_verified"])
print("Analytic full-PEP verified:", state["analytic_full_pep_verified"])
print("Lyapunov proof verified:", state["lyapunov_proof_verified"])
print("Candidate formula status:", state["formula_status"])
print("Saved:", STATE / f"{NAME}_b2.json")
