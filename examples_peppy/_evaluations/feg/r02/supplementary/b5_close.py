import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path

root = Path(__file__).resolve().parents[1]
notebook = root / "feg_example_lyap.ipynb"
nb = json.loads(notebook.read_text(encoding="utf-8"))
state = json.loads((root / "state/feg_b5.json").read_text())
sha = hashlib.sha256(notebook.read_bytes()).hexdigest()
assert sha == state["final_notebook_sha256"]
rows = [
    (
        "title, problem description, and the algorithm update equations in LaTeX",
        "0",
        "Assumptions, exact two-step updates and shared initial half-step inspected in source.",
    ),
    (
        "proof statement placeholder, to be filled with the final theorem and proof outline in Block 5",
        "1–3",
        "Replaced by separate proof heading, theorem with exact V_k, and self-contained base/step/boundary proof.",
    ),
    (
        "imports",
        "4,5",
        "Final kernel prints approved framework import origin; private pinned kernel used.",
    ),
    (
        "function/operator definitions",
        "6,7",
        "LipschitzMonotoneOperator with L and radius parameter; final execution passed.",
    ),
    (
        "make_ctx_feg and get_pep_setup",
        "8–10",
        "Actual recurrence, R squared initial constraint, final residual metric, shared initial point assertion.",
    ),
    (
        "numerical evidence, including a plot comparing the PEP values against the discovered or conjectured rate",
        "11–13",
        "Seven printed optimal values and image/png plot output; initial discrepancy explicitly explained.",
    ),
    (
        "dense and relaxed proof solves",
        "14,15,17,21,22",
        "Dense and sparse sampled solves with complete saved coherent certificates; N6 selected and N8 confirmation.",
    ),
    (
        "lambda and S verification (closed-form when available, otherwise numerical with explicit analytic status)",
        "16–20,25",
        "Full numerical identities, labeled matrices, LDL reconstruction, mandatory initial formula search and unresolved global analytic status.",
    ),
    (
        "partial-sum Lyapunov construction and rank profile",
        "23–29",
        "Visible full certificate replay and grouping loop; coverage, nonincreasing signs and rank two at N6/N8 verified.",
    ),
    (
        "special-vector identification",
        "30–38",
        "Candidate generation/filter and actual sparse basis search with per-index outputs; common residual/anchor basis independence verified.",
    ),
    (
        "coefficient extraction and closed-form V_k",
        "39–47,50,51",
        "All-index numerical matrices and full reconstruction; exact coefficient equations solved; labeled analytic matrix and honest numerical discrepancy comparisons.",
    ),
    (
        "symbolic step, base, and boundary identities",
        "48–58",
        "Separate visible PEPFlow symbolic LHS/RHS/diff constructions, zero Gram/function/offset outputs; domain, sign and full radius normalization proof.",
    ),
]
lines = [
    "Notebook: feg_example_lyap.ipynb",
    "Last reviewed block: B5",
    "SHA-256: " + sha,
    "Presentation policy: evaluation-ancillary-v1. Source math delimiters and control characters checked; executed plot/matrix outputs retained. No rendering, image inspection, or visual verification was performed or claimed.",
    "",
    "| Item | Requirement | Status | Cell indices | Evidence |",
    "|---|---|---|---|---|",
]
for i, (name, cells, evidence) in enumerate(rows, 1):
    lines.append(f"| {i} | {name} | verified | {cells} | {evidence} |")
(root / "supplementary/feg_example_lyap_checklist.md").write_text(
    "\n".join(lines), encoding="utf-8"
)
approved = root / "supplementary/approved"
allowlist = json.loads((approved / "allowlist.json").read_text())
consulted = [
    str(Path(p).relative_to(root)).replace("\\", "/")
    for p in allowlist["exact_read_files"]
    if Path(p).parent == approved / "pepflow"
]
consulted += [
    "supplementary/approved/" + p
    for p in (
        "preflight-only.md",
        "allowlist.json",
        "settings.json",
        "clean-room.md",
        "dispatch.md",
        "input.md",
        "worker-protocol.md",
        "plugins/pepflow-workflows/references/output-layout.md",
        "plugins/pepflow-workflows/optional/with-clean-room/references/tool-recovery.md",
        "plugins/pepflow-workflows/optional/with-clean-room/scripts/check_static.py",
    )
]
for skill in (
    "pep-implement",
    "pep-full-proof",
    "lyap-define",
    "lyap-vectors",
    "lyap-closed-form",
):
    consulted += [
        "supplementary/approved/plugins/pepflow-workflows/skills/" + skill + "/" + p
        for p in ("SKILL.md", "references/workflow.md")
    ]
records = [
    "preflight-access-record.json",
    "b1-access-handoff.json",
    "b2-access-handoff.json",
    "b3-return-b2.json",
    "b2-N8-handoff.json",
    "b3-access-handoff.json",
    "b4-access-handoff.json",
]
closure = dict(
    attempt_id="feg_r02",
    current_block="B5",
    completion_status="complete",
    next_block=None,
    entry_exit_reason="Exact local Lyapunov proof completed; final static checks and clean-kernel nbconvert execution passed; all twelve notebook requirements audited under presentation override.",
    operational_status="finished",
    run_status="completed",
    completed_blocks=["B1", "B2", "B3", "B4", "B5"],
    unresolved_work=[],
    numerical_certificate_verified=True,
    analytic_full_pep_verified=False,
    lyapunov_proof_verified=True,
    separate_unverified_optional_work="Global analytic lambda/S tables remain unverified; not required by the selected local Lyapunov proof path.",
    notebook_sha256=sha,
    closed_at_utc=datetime.now(timezone.utc).isoformat(),
    original_deadline_utc="2026-09-23T19:12:11.207049+00:00",
    access_control="instruction_only",
    prohibited_sources_used_or_encountered="None observed in this worker session.",
    access_limitations="Instruction-only restrictions; no exhaustive OS-level read trace or claim of isolation enforcement. Approved dependency and interpreter origins are recorded in preflight; transitive installed-library accesses are not exhaustively traced.",
    approved_consulted_sources=sorted(set(consulted)),
    prior_access_and_command_records=records,
    b5_commands=[
        "Read exact approved B5 workflow and ipython_utils.py",
        "Python -I -B supplementary/b5_symbolic.py",
        "Python -I -B supplementary/b5_notebook.py",
        "Python -I -B supplementary/b5_finish_source.py",
        "Python -I -B supplementary/b5_display_repair.py",
        "Approved static adapter b5-static-001/002/003.json",
        "Python -I -B supplementary/final_nbconvert.py (two invocations; original failed display, second passed)",
        "Python -I -B supplementary/b5_finalize.py",
        "Python -I -B supplementary/b5_close.py",
        "Exact own saved notebook source/output inspection",
    ],
    incidents=[
        dict(
            classification="Failed process launch",
            detail="One initial B5 read used a mistyped working directory; process did not start and no content was read. Corrected to the assigned attempt root.",
        ),
        dict(
            classification="Operational display conversion",
            evidence="b5-final-nbconvert-console.txt",
            detail="MatrixWithNames display cast symbolic coefficients to float; changed own notebook call to supported raw symbolic array with precision=0.",
            resolution="b5-static-003.json and b5-final-nbconvert-002-console.txt passed",
        ),
    ],
    integrity_exceptions=[],
    external_resources=[],
    token_usage="unavailable",
    presentation_policy="evaluation-ancillary-v1",
    rendered_review=False,
)
(root / "supplementary/attempt-closure.json").write_text(
    json.dumps(closure, indent=2), encoding="utf-8"
)
print("Attempt closed: all required blocks complete; final notebook hash", sha)
