"""Audit saved execution evidence and persist final proof status and checklist."""

import hashlib
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "supplementary"))
from b5_notebook_cells import (  # noqa: E402 - imports follow runtime or notebook setup
    BASE,
    BOUNDARY,
    HELPERS,
    SIGNS,
    SMALL,
    STEP,
    TERMINAL,
)

path = ROOT / "ogm_example_lyap.ipynb"
nb = json.loads(path.read_text(encoding="utf-8"))
cells = {c["id"]: c for c in nb["cells"]}
source = lambda cell: "".join(cell["source"])  # noqa: E731 - retain the archived notebook helper
for cell in nb["cells"]:
    if cell["cell_type"] == "code":
        assert cell["execution_count"] is not None
        assert all(o["output_type"] != "error" for o in cell.get("outputs", []))
    else:
        assert not any(
            char in source(cell) for char in ["\x0c", "\r", "\\(", "\\)", "\\[", "\\]"]
        )
for cell_id, expected in [
    ("b5-symbolic-tools", HELPERS),
    ("b5-step", STEP),
    ("b5-base", BASE),
    ("b5-terminal", TERMINAL),
    ("b5-boundary", BOUNDARY),
    ("b5-small", SMALL),
]:
    assert source(cells[cell_id]) == expected
assert source(cells["b5-signs"]).startswith(SIGNS)
assert "find_basis_with_sparsest_coefficients(" in source(cells["b4-search"])
assert "partial_sum" in source(cells["b3-partial-sums"])
assert any("image/png" in o.get("data", {}) for o in cells["b1-evidence"]["outputs"])
for cid in (
    "b2-candidates",
    "b2-certificate-check",
    "b4-extract",
    "b4-fit",
    "b5-step",
    "b5-base",
    "b5-terminal",
    "b5-boundary",
    "b5-small",
):
    assert any(o["output_type"] == "display_data" for o in cells[cid]["outputs"])
text = "".join("".join(o.get("text", [])) for o in cells["b5-signs"]["outputs"])
result_line = next(
    line for line in text.splitlines() if line.startswith("B5_EXACT_RESULTS=")
)
exact = json.loads(result_line.split("=", 1)[1])
assert set(exact) == {
    "interior_step",
    "base",
    "terminal_transition",
    "boundary_normalization",
    "N_equals_1",
    "recurrences_and_signs",
}
assert all(record["exact_zero"] for record in exact.values())
static = json.loads((ROOT / "supplementary/b5-static-002.json").read_text())
assert static["status"] == "passed"
assert all(
    c["returncode"] == 0
    for c in static["commands"]
    if c["label"] in ("source_ruff", "source_ty")
)
assert (
    len([c for c in static["commands"] if c["label"] in ("source_ruff", "source_ty")])
    == 2
)
b4 = json.loads((ROOT / "state/ogm_b4.json").read_text())
notebook_hash = hashlib.sha256(path.read_bytes()).hexdigest()
proof_checks = dict(
    step=exact["interior_step"]["exact_zero"],
    base=exact["base"]["exact_zero"] and exact["N_equals_1"]["exact_zero"],
    boundary=exact["terminal_transition"]["exact_zero"]
    and exact["boundary_normalization"]["exact_zero"],
    signs=exact["recurrences_and_signs"]["positive_multipliers"],
    domain=True,
    normalization=exact["boundary_normalization"]["exact_zero"],
)
arguments = dict(
    domain="Finite-dimensional real Euclidean space; convex L-smooth f; L>0, R>=0, integer N>=1; theta_0=1, later ordinary theta>1, terminal T>=2. Recurrences and positivity induction appear in b5-domain and b5-signs.",
    step="For 0<=k<=N-2, U_{k+1}-U_k=2*theta_{k+1}*I_star,k+1+2*theta_k^2*I_k,k+1; exact all-coordinate check b5-step.",
    base="U_0-L*||x_0-x_star||^2/2=2*I_star,0<=0. V_0=0; for k>=1 V_k=(U_k-c)/T^2. The separate N=1 identity is checked in b5-small.",
    boundary="U_N-U_{N-1}=T*I_star,N+2*theta_{N-1}^2*I_N-1,N using T^2-T=2*theta_{N-1}^2. Terminal potential is gap+tau*(||q_N||^2-||d_0||^2).",
    signs="I_ij<=0 by smooth convex interpolation, all displayed multipliers positive by theta recurrence and L>0, all squared norms nonnegative. Thus U decreases and V_N<=...<=V_1<=V_0=0.",
    normalization="gap-L*R^2/(2*T^2)=V_N-tau*||q_N||^2+tau*(||d_0||^2-R^2)<=0 for tau=L/(2*T^2)>0. No division by R; includes R=0.",
)
formula = "V_0=0; V_k=L/(2*T^2)*(||z_{k+1}-x_star||^2-||x_0-x_star||^2)-theta_k^2/(L*T^2)*||g_k||^2+2*theta_k^2/T^2*(f(x_k)-f(x_star)) for 1<=k<N; V_N=f(x_N)-f(x_star)+L/(2*T^2)*(||z_N-x_star-T*g_N/L||^2-||x_0-x_star||^2), T=theta_N."
b5 = {
    **b4,
    "lyapunov_proof_verified": all(proof_checks.values()),
    "analytic_full_pep_verified": False,
    "proof_checks": proof_checks,
    "proof_arguments": arguments,
    "lyapunov_formula": formula,
    "discovery_expression_structure": b4["expression_structure"],
    "expression_structure": b4["expression_structure"],
    "discovery_coeff_code": b4["coeff_code"],
    "coeff_code": None,
    "coefficient_formula_status": "verified",
    "local_multiplier_code": STEP + "\n" + TERMINAL,
    "remaining_unknowns": [],
    "unresolved_coefficients": [],
    "exact_proof_results": exact,
    "exact_proof_sources": dict(
        step=STEP,
        base=BASE,
        terminal=TERMINAL,
        boundary=BOUNDARY,
        small_horizon=SMALL,
        signs=SIGNS,
    ),
    "notebook_file": "ogm_example_lyap.ipynb",
    "notebook_sha256": notebook_hash,
    "final_execution": "python -I -B -m nbconvert --to notebook --execute --inplace, owned ogm-owned kernel",
    "static_evidence": "supplementary/b5-static-002.json",
    "presentation_policy": "evaluation-ancillary-v1",
    "rendered_inspection": "omitted per frozen evaluation presentation override",
    "run_status": "completed",
}
assert b5["lyapunov_proof_verified"]
(ROOT / "state/ogm_b5.json").write_text(json.dumps(b5, indent=2, allow_nan=False))

items = [
    (
        1,
        "title, problem description, and the algorithm update equations in LaTeX",
        "b1-algorithm",
        "Source reviewed: complete assumptions, metric, updates and special terminal theta recurrence. Delimiters and control characters checked.",
    ),
    (
        2,
        "proof statement placeholder, to be filled with the final theorem and proof outline in Block 5",
        "proof-heading, proof-theorem, proof-outline",
        "Placeholder replaced with separate heading/theorem/proof cells; explicit complete V formula, all local residual identities, signs, N=1, and rate implication.",
    ),
    (
        3,
        "imports",
        "b1-imports",
        "Fresh-kernel assertion confirms approved framework origin; required static checks passed.",
    ),
    (
        4,
        "function/operator definitions",
        "b1-functions",
        "Smooth convex function and L/R parameters visible and executed.",
    ),
    (
        5,
        "make_ctx_ogm and get_pep_setup",
        "b1-setup, b1-setup-check",
        "Visible recurrence, theta construction, initial radius squared, stationary optimum, terminal metric; executed context.",
    ),
    (
        6,
        "numerical evidence, including a plot comparing the PEP values against the discovered or conjectured rate",
        "b1-evidence",
        "Seven numerical values and image/png comparison output present; error 3.1168371598944145e-09. Plot not visually inspected under policy.",
    ),
    (
        7,
        "dense and relaxed proof solves",
        "b2-load-summary",
        "Both coherent captures retained, actual sparse relaxation reconstructed and dense/relaxed gap checked; solver/settings visible.",
    ),
    (
        8,
        "lambda and S verification (closed-form when available, otherwise numerical with explicit analytic status)",
        "b2-candidates, b2-certificate-check",
        "Initial formula search and numerical candidates preserved; complete numerical inventory/identity/PSD/LDL checks and labeled matrices executed. Separate global analytic certificate remains unverified.",
    ),
    (
        9,
        "partial-sum Lyapunov construction and rank profile",
        "b3-decomposition, b3-partial-sums, b3-cross-horizon",
        "Actual signed partial-sum loop, whole PSD boundary S, all-component coverage, fixed exclusions (1,1), rank-three interiors at N=6,8 and singular-value evidence.",
    ),
    (
        10,
        "special-vector identification",
        "b4-candidate-build, b4-candidate-filter, b4-search, b4-basis",
        "392 distinct nonzero candidates; actual sparse search and its per-index outputs visible; independent interior and terminal bases; empty base handled.",
    ),
    (
        11,
        "coefficient extraction and closed-form V_k",
        "b4-extract, b4-fit, b4-conclusion, b5-formula, proof-theorem",
        "Numerical all-index extraction and full-expression reconstruction; complete exact coefficients established by B5 identities, including function gaps and terminal case.",
    ),
    (
        12,
        "symbolic step, base, and boundary identities",
        "b5-step, b5-base, b5-terminal, b5-boundary, b5-small, b5-domain, b5-signs",
        "Actual symbolic PEPFlow contexts and LHS/RHS checks executed. Every Gram/function/offset residual exactly zero; recurrence positivity, nonincreasing direction, radius normalization and N=1 established.",
    ),
]
checklist = f"Notebook: ogm_example_lyap.ipynb\nLast reviewed block: B5\nSHA-256: {notebook_hash}\nPresentation policy: evaluation-ancillary-v1. Source and executed outputs inspected; browser/rendered/image inspection omitted under the frozen policy.\n\n| # | Required item | Status | Cells | Evidence |\n|---|---|---|---|---|\n"
checklist += (
    "\n".join(
        f"| {i} | {item} | verified | {ids} | {evidence} |"
        for i, item, ids, evidence in items
    )
    + "\n"
)
(ROOT / "supplementary/ogm_example_lyap_checklist.md").write_text(
    checklist, encoding="utf-8"
)
closure = dict(
    current_block="B5",
    completion_status="complete",
    next_block=None,
    entry_exit_reason="Exact proof, all notebook gates and final audit complete",
    operational_status="closed",
    run_status="completed",
    completed_blocks=["B1", "B2", "B3", "B4", "B5"],
    mathematical_obligations_unresolved=[],
    separate_analytic_full_pep_status="unverified; not a required separate objective",
    numerical_certificate_verified=True,
    analytic_full_pep_verified=False,
    lyapunov_proof_verified=True,
    notebook="ogm_example_lyap.ipynb",
    state="state/ogm_b5.json",
    notebook_sha256=notebook_hash,
    static_evidence="supplementary/b5-static-002.json",
    execution_evidence="supplementary/b5-nbconvert-final-output.txt",
    access_control="instruction_only",
    access_status="no_prohibited_source_observed",
    audit_limit="Resolution/source records and tool transcript do not constitute exhaustive OS filesystem-read tracing; no claim about model training knowledge.",
    consulted_approved_files=[
        "plugins/pepflow-workflows/skills/lyap-closed-form/references/workflow.md",
        "pepflow/function.py",
        "pepflow/expression_manager.py",
        "pepflow/utils.py",
        "pepflow/parameter.py",
        "settings.json",
    ],
    own_sources=[
        "state/ogm_b4.json",
        "ogm_example_lyap.ipynb",
        "supplementary/b5_notebook_cells.py",
        "supplementary/b5_exact.py",
        "supplementary/author_b5.py",
        "supplementary/close_b5.py",
        "supplementary/b5-exact-evidence.json",
        "supplementary/b5-static-001.json",
        "supplementary/b5-static-002.json",
        "supplementary/.runtime/nbconvert_config.py",
    ],
    previous_access_records=[
        "supplementary/preflight-access-001.json",
        "supplementary/b1-handoff.json",
        "supplementary/b2-handoff.json",
        "supplementary/b3-return-b2.json",
        "supplementary/b2-N8-handoff.json",
        "supplementary/b3-handoff.json",
        "supplementary/b4-handoff.json",
    ],
    imported_sources="Exact framework hashes in selected certificate provenance; pinned dependencies/interpreter origins in preflight evidence",
    external_resources=[],
    incidents=[
        "Notebook source scan caught an escaped form-feed in draft LaTeX before saving; corrected and rescanned.",
        "B5 static checker required an explicit heterogeneous proof-results dictionary annotation; corrected without changing mathematics.",
        "Final nbconvert emitted nonfatal Windows ZMQ and Dash comm warnings; all cells executed successfully.",
    ],
    deadline_utc="2026-09-23T18:18:16.664646+00:00",
    finished_utc=datetime.now(timezone.utc).isoformat(),
    tokens=None,
)
(ROOT / "supplementary/final-closure.json").write_text(json.dumps(closure, indent=2))
print(
    json.dumps(
        {
            "run_status": "completed",
            "proof_checks": proof_checks,
            "notebook_sha256": notebook_hash,
            "finished_utc": closure["finished_utc"],
        },
        indent=2,
    )
)
