import hashlib
import json
from pathlib import Path

root = Path(__file__).resolve().parent.parent
path = root / "pgm_example_lyap.ipynb"
book = json.loads(path.read_text())
for i, cell in enumerate(book["cells"]):
    source = "".join(cell["source"])
    if cell["cell_type"] == "markdown":
        assert not any(t in source for t in ("\\(", "\\)", "\\[", "\\]", "\x0c", "\r"))
        assert source.count("$$") % 2 == 0
        assert source.replace("$$", "").count("$") % 2 == 0
    else:
        assert cell["execution_count"] is not None
        assert not any(o["output_type"] == "error" for o in cell["outputs"])
for index, label in [
    (38, "Interior step"),
    (41, "Base, N>=2"),
    (44, "Terminal, N>=2"),
    (47, "Exceptional horizon N=1"),
]:
    out = "".join("".join(o.get("text", [])) for o in book["cells"][index]["outputs"])
    assert label + " Gram residual zero" in out and "offset: 0" in out
    assert any(
        "text/latex" in o.get("data", {}) for o in book["cells"][index]["outputs"]
    )
for index in (10, 13, 16, 23, 27, 33, 35):
    assert book["cells"][index]["outputs"]
assert any("image/png" in o.get("data", {}) for o in book["cells"][8]["outputs"])
static = json.loads((root / "supplementary/b5-static-001.json").read_text())
assert static["status"] == "passed"
digest = hashlib.sha256(path.read_bytes()).hexdigest()
p = root / "supplementary/pgm_example_lyap_checklist.md"
old = p.read_text()
lines = old.splitlines()
items = {
    int(line.split("|")[1]): line.split("|")[2].strip()
    for line in lines
    if line.startswith("| ") and line.split("|")[1].strip().isdigit()
}
rows = {
    1: (
        "0",
        "Assumptions, metric and recurrence present; source delimiters and escapes checked.",
    ),
    2: (
        "1,2,3",
        "Separate heading, theorem including full potential and self-contained proof outline with every local multiplier and square.",
    ),
    3: (
        "4,13,20,27,32",
        "Pinned kernel imported approved framework and private helpers; numerical and symbolic imports executed.",
    ),
    4: ("5", "Smooth convex f, convex g, h=f+g and symbolic L,R defined."),
    5: (
        "6",
        "Proximal update, optimum stationarity, radius constraint and objective implemented and replayed.",
    ),
    6: (
        "7,8",
        "Seven saved PEP values and comparison plot retained; PNG output existence checked without image inspection.",
    ),
    7: (
        "9,10",
        "Dense and relaxed solve summaries, coherent certificate matrices and metadata replayed.",
    ),
    8: (
        "11-14",
        "Initial candidate search, numerical complete certificate, matrix labels, signs, SOS reconstruction, source hashes and exact fixed-N check retained. Global analytic formula explicitly unverified.",
    ),
    9: (
        "15,16",
        "Explicit partial_sum and lyap construction, verified PSD allocation, ranks 4 at N4/N6 with exclusions (1,1), coverage checked.",
    ),
    10: (
        "17-25",
        "Actual per-index sparse basis search, candidate filtering, selected coefficients and uniform basis verified.",
    ),
    11: (
        "26-35",
        "All-index numeric coefficient extraction and labeled matrices; exact formulas, function gaps, zero offset, all-component coefficient equations and unique solution. Analytic comparison maximum 9.579e-6.",
    ),
    12: (
        "36-49",
        "Separate native symbolic step/base/boundary contexts plus N=1. Every Gram/function/offset residual exactly zero; labeled residuals retained. Signs, domains and LR^2/(4N) normalization established.",
    ),
}
text = (
    "Notebook: pgm_example_lyap.ipynb\nLast reviewed block: B5\nSHA-256: "
    + digest
    + "\nPresentation policy: evaluation-ancillary-v1; source checks complete. Rendering and image inspection omitted as required; no rendered-verification claim.\n\n| # | Item | Status | Cells (zero based) | Evidence |\n|---|---|---|---|---|\n"
)
for i in range(1, 13):
    text += f"| {i} | {items[i]} | verified | {rows[i][0]} | {rows[i][1]} |\n"
text += "\nStatic evidence: supplementary/b5-static-001.json. Final clean-kernel nbconvert execution: supplementary/b5-nbconvert-001-output.txt (exit 0). Harmless Windows event-loop/comm warnings retained; duplicate auxiliary-context labels emitted warnings without failed checks.\n"
p.write_text(text)
state_path = root / "state/pgm_b5.json"
state = json.loads(state_path.read_text())
assert all(state["proof_checks"].values()) and state["lyapunov_proof_verified"]
state.update(
    {
        "run_status": "completed",
        "completion_status": "complete",
        "remaining_required_work": [],
        "final_notebook_sha256": digest,
        "final_notebook_execution": "supplementary/b5-nbconvert-001-output.txt",
        "final_static_evidence": "supplementary/b5-static-001.json",
        "notebook_checklist": "supplementary/pgm_example_lyap_checklist.md",
    }
)
state_path.write_text(json.dumps(state, indent=2))
audit = {
    "current_block": "B5",
    "completion_status": "complete",
    "next_block": None,
    "entry_exit_reason": "Closed-form coefficient derivation and exact step/base/terminal/N=1 identities completed; required static checks, clean-kernel nbconvert and final checklist passed.",
    "operational_status": "final_attempt_closure",
    "run_status": "completed",
    "notebook": "pgm_example_lyap.ipynb",
    "state": "state/pgm_b5.json",
    "notebook_sha256": digest,
    "completed_blocks": ["B1", "B2", "B3", "B4", "B5"],
    "unresolved_required_work": [],
    "unresolved_optional_work": [
        "Separate global analytic full-PEP formula remains unverified and was not required."
    ],
    "numerical_certificate_verified": True,
    "analytic_full_pep_verified": False,
    "lyapunov_proof_verified": True,
    "proof_checks": state["proof_checks"],
    "checks": [
        "supplementary/b5-static-001.json",
        "supplementary/b5-nbconvert-001-output.txt",
        "supplementary/pgm_example_lyap_checklist.md",
    ],
    "sources": [
        "Own approved dispatch.md, worker-protocol.md, settings.json, input.md previously read",
        "Approved lyap-closed-form/SKILL.md and references/workflow.md",
        "Approved pepflow/expression_manager.py symbolic coefficient API",
        "Own generated B1-B4 state, scripts, and notebook",
        "Own B5 generated proof scripts and markdown",
    ],
    "commands": [
        "Pinned Python -I -B supplementary/run_b5_step.py",
        "Pinned Python -I -B supplementary/run_b5_all.py",
        "Pinned Python -I -B supplementary/build_b5_notebook.py",
        "Pinned Python -I -B supplementary/run_static.py b5-static-001.json",
        "Pinned Python -I -B supplementary/execute_b5_nbconvert.py",
        "Pinned Python -I -B supplementary/final_audit_b5.py",
    ],
    "incidents": [
        "Initial direct SymPy symbolic coefficients were unsupported by PEPFlow; repaired to native pf.Parameter with resolve_parameters mappings.",
        "Initial sp.One typo repaired to sp.S.One.",
        "Nonfatal event-loop/comm and duplicate auxiliary-context label warnings retained in execution evidence.",
    ],
    "access_control": "instruction_only",
    "prohibited_sources_observed": False,
    "audit_limit": "No exhaustive filesystem audit",
    "presentation_policy": "evaluation-ancillary-v1",
    "rendered_inspection_performed": False,
    "deadline_utc": "2026-09-23T16:12:00.406449+00:00",
    "token_usage": None,
}
(root / "supplementary/b5-handoff-001.json").write_text(json.dumps(audit, indent=2))
print(
    json.dumps(
        {
            "run_status": "completed",
            "notebook_sha256": digest,
            "proof_checks": state["proof_checks"],
            "unresolved_required_work": [],
        },
        indent=2,
    )
)
