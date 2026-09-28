"""Audit executed notebook evidence and close the B5 state without changing it."""

import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path

# optional notebook-generation dependency
import nbformat  # ty: ignore[unresolved-import]

root = Path(__file__).resolve().parents[1]
notebook_path = root / "ogm_example_lyap.ipynb"
nb = nbformat.read(notebook_path, as_version=4)
streams = []
png_count = 0
for cell in nb.cells:
    if cell.cell_type == "markdown":
        assert "\\(" not in cell.source and "\\[" not in cell.source
        assert not any(ord(c) < 32 and c not in "\n\t" for c in cell.source)
    else:
        assert cell.execution_count is not None
        for output in cell.get("outputs", []):
            assert output.output_type != "error"
            if output.output_type == "stream":
                streams.append(output.text)
            if "image/png" in output.get("data", {}):
                png_count += 1
text = "\n".join(streams)
assert png_count >= 1
for name in ("step", "base", "boundary", "N1"):
    assert f"{name} Gram residual exactly zero: True" in text
    assert f"{name} function residual:" in text
assert (
    "Positive roots, recurrence polynomial identities, and all multiplier/square signs verified."
    in text
)
assert "Full-expression reconstruction:" in text
assert "sparse basis:" in text
assert "Confirmed horizons: 4, 6" in text
execution = json.loads(
    (root / "supplementary/b5-nbconvert-execution-003.json").read_text()
)
assert execution["returncode"] == 0
static = json.loads((root / "supplementary/b5-static-004.json").read_text())
assert static["status"] == "passed"
replay = json.loads((root / "supplementary/final-replay-evidence.json").read_text())
assert (
    replay["certificate_replay"]
    and replay["grouping_replay"]
    and replay["basis_and_structure_replay"]
)
b4 = json.loads((root / "state/ogm_b4.json").read_text())
proof_evidence = json.loads(
    (root / "supplementary/b5-symbolic-evidence.json").read_text()
)
assert all(
    all(row[key] for key in ("gram_zero", "function_zero", "offset_zero"))
    for row in proof_evidence.values()
)
final_structure = {
    "quadratic_convention": "sum_ij C_ij <v_i,v_j>, symmetric C; off-diagonals counted twice",
    "initial": {"index_domain": "k=0", "basis_labels": [], "quadratic": "0"},
    "interior": {
        "index_domain": "1 <= k < N",
        "basis_labels": ["x_0-x_star", "z_(k+1)-x_star", "g_k"],
        "C": "diag(-L/(2 theta_N^2), L/(2 theta_N^2), -theta_k^2/(L theta_N^2))",
    },
    "terminal": {
        "index_domain": "k=N, including N=1",
        "basis_labels": ["x_0-x_star"],
        "C": "[[-L/(2 theta_N^2)]]",
    },
    "function_terms": [
        {
            "index_domain": "1 <= k < N",
            "expression": "f(x_k)-f(x_star)",
            "coefficient": "2 theta_k^2/theta_N^2",
        },
        {"index_domain": "k=N", "expression": "f(x_N)-f(x_star)", "coefficient": "1"},
    ],
    "constant_terms": [],
}
arguments = {
    "step": "Exact Gram, function, and offset identity with t=theta_k, u=theta_(k+1), t^2=u^2-u; notebook cells 46-48. H_(k+1)-H_k=2u I_star,k+1+2t^2 I_k,k+1.",
    "base": "theta_0=1 and z_1=x_0-2g_0/L give H_0-L||x_0-x_star||^2/2=2 I_star,0 exactly; cells 49-51.",
    "boundary": "2t^2=u^2-u is the special terminal relation. u^2 gap_N-H_(N-1)=u I_star,N+2t^2 I_N-1,N-(L/2)||z_N-x_star-u*g_N/L||^2; cells 52-54. N=1 separately checked in cells 55-57.",
    "signs": "Smooth convex interpolation residuals are <=0. Positive-root recurrence gives every theta>=1, so all interpolation multipliers and L/(2 theta_N^2) are positive. Subtracted squares are nonpositive.",
    "domain": "Finite-dimensional real Euclidean spaces, convex L-smooth f, L>0, R>=0, integer N>=1. No division by R. Empty interior ranges handled by direct N=1 identity.",
    "normalization": "V_N<=V_0=0 gives gap_N<=L||x_0-x_star||^2/(2 theta_N^2)<=LR^2/(2 theta_N^2).",
    "global_certificate": "Sum base, k=0..N-2 ordinary identities and terminal identity. All H terms telescope, proving every global multiplier and the rank-one slack formula (notebook cell 60).",
    "sharpness": "For f(x)=L*x^2/2, x_star=0 and x_0=z_0=R, induction gives z_k=(-1)^k R and x_k=(-1)^k R/theta_k. Exact scalar update checked in cell 62.",
}
state = {
    **b4,
    "proof_checks": {
        name: True
        for name in ("step", "base", "boundary", "signs", "domain", "normalization")
    },
    "proof_arguments": arguments,
    "symbolic_component_checks": proof_evidence,
    "lyapunov_formula": "V_0=0; V_k=[2 theta_k^2 (f(x_k)-f_star)-theta_k^2 ||g_k||^2/L+(L/2)||z_(k+1)-x_star||^2-(L/2)||x_0-x_star||^2]/theta_N^2 for 1<=k<N; V_N=f(x_N)-f_star-L||x_0-x_star||^2/(2 theta_N^2)",
    "theorem": "For every N>=1, f(x_N)-f(x_star)<=L*R^2/(2*theta_N^2), with the supplied special terminal theta_N recurrence; sharp on the one-dimensional quadratic.",
    "discovery_expression_structure": b4["expression_structure"],
    "expression_structure": final_structure,
    "coefficient_formula_status": "verified",
    "formula_status": {"lambda": "verified", "S": "verified"},
    "closed_form_search_resolution": "The B2 candidates are proved by the exact B5 local identities and finite telescoping.",
    "local_multiplier_code": "def local_multipliers(t, u, T, L, terminal=False):\n    return dict(stationary=(u if terminal else 2*u)/T**2, consecutive=2*t**2/T**2, square=L/(2*T**2) if terminal else 0)\n",
    "remaining_unknowns": [],
    "unresolved_coefficients": [],
    "unresolved_work": [],
    "numerical_certificate_verified": True,
    "analytic_full_pep_verified": True,
    "lyapunov_proof_verified": True,
    "final_static_evidence": "supplementary/b5-static-004.json",
    "final_execution_evidence": "supplementary/b5-nbconvert-execution-003.json",
    "notebook_sha256": hashlib.sha256(notebook_path.read_bytes()).hexdigest(),
    "presentation_policy": "evaluation-ancillary-v1",
    "rendered_visual_review": "not performed under evaluation override",
    "run_status": "completed",
    "completed_blocks": ["B1", "B2", "B3", "B4", "B5"],
}
(root / "state/ogm_b5.json").write_text(
    json.dumps(state, indent=2, allow_nan=False), encoding="utf-8"
)
items = [
    (
        "title, problem description, and the algorithm update equations in LaTeX",
        "0",
        "All assumptions and all updates, including terminal recurrence, present; source math checks passed.",
    ),
    (
        "proof statement placeholder, to be filled with the final theorem and proof outline in Block 5",
        "1-3",
        "Separate theorem and self-contained proof outline; full potential, all increments, signs, N=1 and final normalization.",
    ),
    ("imports", "4-5", "Approved import origin asserted and printed in fresh kernel."),
    (
        "function/operator definitions",
        "6-7",
        "Smooth convex function and L/R parameters visible.",
    ),
    (
        "make_ctx_ogm and get_pep_setup",
        "8-9",
        "Actual tagged updates, squared radius and target metric visible and executed.",
    ),
    (
        "numerical evidence, including a plot comparing the PEP values against the discovered or conjectured rate",
        "10-12",
        "Seven printed values, residual 3.12e-9, and embedded comparison plot present; no visual inspection performed.",
    ),
    (
        "dense and relaxed proof solves",
        "13-15",
        "Coherent dense and relaxed state/provenance; complete summaries and preserved-objective check.",
    ),
    (
        "lambda and S verification (closed-form when available, otherwise numerical with explicit analytic status)",
        "16-22,60",
        "Initial search, candidate comparisons, labeled matrices, full numerical identity/LDL reconstruction; final global analytic identity by proved telescoping.",
    ),
    (
        "partial-sum Lyapunov construction and rank profile",
        "23-27",
        "Actual grouping loop, all-coordinate coverage and fixed-exclusion two-horizon rank check; independent saved-source replay also passed.",
    ),
    (
        "special-vector identification",
        "28-36",
        "Visible candidate scan and actual sparse basis search; all-index independence and reconstruction.",
    ),
    (
        "coefficient extraction and closed-form V_k",
        "37-45",
        "Labeled numerical and exact coefficient matrices, function terms, full expression reconstruction and resolved formula.",
    ),
    (
        "symbolic step, base, and boundary identities",
        "46-63",
        "Separate exact zero Gram/function/offset checks, N=1, positive-root/sign proofs, normalization and sharpness.",
    ),
]
lines = [
    "# Notebook evidence checklist",
    "",
    "Notebook: ogm_example_lyap.ipynb",
    "Last reviewed block: B5",
    "SHA-256: " + state["notebook_sha256"],
    "Presentation: evaluation-ancillary-v1. No browser, rendered preview or image inspection; source and executed-output checks only.",
    "",
    "| Item | Requirement | Status | Cell indices | Evidence |",
    "|---|---|---|---|---|",
]
for i, (requirement, cells, evidence) in enumerate(items, start=1):
    lines.append(f"| {i} | {requirement} | verified | {cells} | {evidence} |")
(root / "supplementary/ogm_example_lyap_checklist.md").write_text(
    "\n".join(lines) + "\n", encoding="utf-8"
)
event = {
    "current_block": "B5",
    "completion_status": "complete",
    "next_block": None,
    "entry_exit_reason": "Exact proof, full artifact replay, static checks, and final clean-kernel nbconvert execution passed.",
    "operational_status": "closed",
    "run_status": "completed",
    "unresolved_work": [],
    "timestamp_utc": datetime.now(timezone.utc).isoformat(),
    "deadline_utc": "2026-09-23T23:46:53.255961+00:00",
    "access_control": "instruction_only",
    "prohibited_sources_observed": False,
    "access_limitations": "Instruction-scoped reads; no exhaustive OS read audit or claim about training knowledge.",
    "approved_reads": [
        "plugins/pepflow-workflows/skills/lyap-closed-form/references/workflow.md",
        "pepflow/utils.py",
    ],
    "commands": [
        "python -I -B supplementary/run_b5.py",
        "python -I -B supplementary/update_b5_notebook.py",
        "Reviewed static adapter checks b5-static-001/002/003/004.json",
        "Pinned python -I -B -m nbconvert --execute; exact argv in execution evidence",
        "python -I -B supplementary/finalize_replay.py",
        "python -I -B supplementary/finalize_b5.py",
    ],
    "incidents": [
        "Symbolic coefficient display initially used numeric rounding; fixed own call to precision=0.",
        "One inline Python repair failed shell quoting before execution; corrected quoting.",
        "Final replay audit packaged stored source scopes and indentation; independent full replay passed without changing mathematical certificate components.",
        "Annotated the exec namespace as a heterogeneous dictionary to resolve a replay-audit type diagnostic.",
    ],
    "source_records": [
        "preflight-access-record.json",
        "b1-access-events.json",
        "b2-access-events.json",
        "b3-return-b2.json",
        "b2-N6-events.json",
        "b3-access-events.json",
        "b4-access-events.json",
    ],
    "notebook": "ogm_example_lyap.ipynb",
    "state": "state/ogm_b5.json",
    "provider_token_usage": None,
    "external_resources": [],
    "exports": False,
}
(root / "supplementary/b5-access-events.json").write_text(
    json.dumps(event, indent=2), encoding="utf-8"
)
print(
    json.dumps(
        {
            "run_status": "completed",
            "all_blocks_complete": True,
            "unresolved_work": [],
            "notebook_sha256": state["notebook_sha256"],
            "proof_checks": state["proof_checks"],
        }
    )
)
