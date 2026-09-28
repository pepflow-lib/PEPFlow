import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent / "helpers"))
import hashlib
import json
from datetime import datetime, timezone

import runtime

root = runtime.ATTEMPT
nb = root / "pgm_example_lyap.ipynb"
audit = json.loads((root / "supplementary/final-notebook-audit.json").read_text())
assert hashlib.sha256(nb.read_bytes()).hexdigest() == audit["sha256"]
rows = [
    (
        1,
        "title, problem description, and the algorithm update equations in LaTeX",
        "0",
        "Assumptions, recurrence, proximal optimality and composite metric present; source delimiters checked.",
    ),
    (
        2,
        "proof statement placeholder, to be filled with the final theorem and proof outline in Block 5",
        "1–3",
        "Replaced by separate proof-statement heading, full Lyapunov theorem with finite-product coefficients, and self-contained detailed proof.",
    ),
    (
        3,
        "imports",
        "4–5",
        "Approved framework origin asserted; pinned clean kernel executed.",
    ),
    (
        4,
        "function/operator definitions",
        "6–7",
        "Smooth convex f, closed proper convex g, sum stationarity and parameters visible.",
    ),
    (
        5,
        "make_ctx_pgm and get_pep_setup",
        "8–9",
        "Actual proximal recursion, squared-radius constraint and composite objective visible and executable.",
    ),
    (
        6,
        "numerical evidence, including a plot comparing the PEP values against the discovered or conjectured rate",
        "10–12",
        "N=1..7 results and statuses printed; maximum candidate discrepancy 4.3191076e-9; comparison plot embedded.",
    ),
    (
        7,
        "dense and relaxed proof solves",
        "13–14",
        "Complete captured dense and sparse solves, both function groups, coordinate basis and preserved optimum displayed; provenance/state retained.",
    ),
    (
        8,
        "lambda and S verification (closed-form when available, otherwise numerical with explicit analytic status)",
        "15–19",
        "Candidate multipliers, labeled true S and LDL matrices, reconstruction and Gram/function/constant identities present. Initial formula search retained; global analytic full-PEP status remains unverified.",
    ),
    (
        9,
        "partial-sum Lyapunov construction and rank profile",
        "20–26",
        "Full replay, visible partial-sum loop, all-coordinate coverage, signs and rank4 confirmation at N=4,6; fixed exclusions (1,1), absolute tolerance1e-4, singular-value evidence retained.",
    ),
    (
        10,
        "special-vector identification",
        "27–35",
        "Actual candidate generation/filtering, executable sparsity search and per-index output, adopted basis and endpoint independence checks.",
    ),
    (
        11,
        "coefficient extraction and closed-form V_k",
        "36–45",
        "Numerical labeled matrices and complete expression reconstruction at all indices; exact transfer-product solution and recurrence derivation; all sample coefficient comparisons pass.",
    ),
    (
        12,
        "symbolic step, base, and boundary identities",
        "46–61",
        "Separate symbolic PEPFlow step/base/terminal/normalization/N=1 contexts and all-coordinate exact-zero outputs; domain/sign proof and final telescoping present.",
    ),
]
text = (
    "Notebook: pgm_example_lyap.ipynb\nLast reviewed block: B5\nSHA-256: "
    + audit["sha256"]
    + "\nPresentation policy: evaluation-ancillary-v1. Rendering/image inspection intentionally not performed; no rendered-review claim. Source delimiters/control characters and all required executed outputs inspected.\n\n| # | Item | Status | Cells (zero-based) | Evidence |\n|---|---|---|---|---|\n"
)
for number, item, cells, evidence in rows:
    text += f"| {number} | {item} | verified | {cells} | {evidence} |\n"
(root / "supplementary/pgm_example_lyap_checklist.md").write_text(text)
b5_path = root / "state/pgm_b5.json"
b5 = json.loads(b5_path.read_text())
b5["run_status"] = "completed"
b5["completion_status"] = "complete"
b5["final_notebook_sha256"] = audit["sha256"]
b5["final_validation"] = audit
b5["finished_utc"] = datetime.now(timezone.utc).isoformat()
b5["proof_source_hashes"] = {
    name: hashlib.sha256((root / name).read_bytes()).hexdigest()
    for name in [
        "supplementary/b5_cells.py",
        "supplementary/b5_coefficient_derivation.py",
        "supplementary/b5_sign_audit.py",
        "supplementary/b5_theorem.md",
        "supplementary/b5_proof_outline.md",
    ]
}
b5_path.write_text(json.dumps(b5, indent=2, allow_nan=False))
approved_files = [
    "preflight-only.md",
    "allowlist.json",
    "settings.json",
    "clean-room.md",
    "worker-protocol.md",
    "dispatch.md",
    "input.md",
    "plugins/pepflow-workflows/optional/with-clean-room/references/tool-recovery.md",
    "plugins/pepflow-workflows/optional/with-clean-room/scripts/check_static.py",
    "plugins/pepflow-workflows/references/output-layout.md",
]
for skill in [
    "pep-implement",
    "pep-full-proof",
    "lyap-define",
    "lyap-vectors",
    "lyap-closed-form",
]:
    approved_files += [
        f"plugins/pepflow-workflows/skills/{skill}/SKILL.md",
        f"plugins/pepflow-workflows/skills/{skill}/references/workflow.md",
    ]
for module in [
    "__init__",
    "function",
    "pep",
    "pep_runner",
    "parameter",
    "solver",
    "lyapunov_utils",
    "ipython_utils",
    "pep_result",
    "expression_manager",
    "scalar",
    "utils",
]:
    approved_files += [f"pepflow/{module}.py"]
source_record = dict(
    access_control="instruction_only",
    direct_approved_reads=[str(runtime.APPROVED / p) for p in approved_files],
    transitive_imported_sources="Exact approved package manifests and hashes in static/preflight evidence; installed dependencies and pinned interpreter standard library permitted.",
    own_generated_resources="Setup, notebook, state, supplementary scripts, observations, logs and audit artifacts in this attempt only.",
    command_records=[
        "preflight-access-001.json",
        "b1-handoff-access.json",
        "b2-handoff-access.json",
        "b3-revisit-handoff.json",
        "b2-n6-handoff.json",
        "b3-handoff-access.json",
        "b4-handoff-access.json",
        "b5-handoff-access.json",
    ],
    external_resources=[],
    prohibited_sources_used=False,
    prohibited_content_observed=False,
    integrity_exceptions="Ordinary operational/static failures preserved and repaired; no frozen-source edits or gate/tolerance relaxation.",
    observability_limit="Instruction-only restriction; no exhaustive OS filesystem tracing or claim of OS-enforced read isolation. Actual tool transcript and adapter manifests provide bounded evidence.",
)
(root / "supplementary/consulted-sources.json").write_text(
    json.dumps(source_record, indent=2)
)
handoff = dict(
    current_block="B5",
    completion_status="complete",
    next_block=None,
    run_status="completed",
    entry_exit_reason="All required mathematical, notebook, static and clean-kernel gates completed before original deadline",
    operational_status="closed",
    finished_utc=b5["finished_utc"],
    original_deadline_utc="2026-09-23T21:58:02.889281+00:00",
    completed_blocks=["B1", "B2", "B3", "B4", "B5"],
    unresolved_work=[],
    numerical_certificate_verified=True,
    analytic_full_pep_verified=False,
    lyapunov_proof_verified=True,
    analytic_scope="Completed local Lyapunov theorem; no separate global analytic full-PEP claim was required or made.",
    sources_added=[
        "approved lyap-closed-form/references/workflow.md",
        "approved pepflow/scalar.py and utils.py",
        "own B5 derivation, proof and validation artifacts",
    ],
    commands=[
        "Pinned python -I -B derive_b5.py, simplify_b5.py, local_blocks_b5.py, verify_b5.py, finalize_b5.py, repair_b5_source.py, final_execute.py, audit_final.py, close_attempt.py",
        "Pinned approved adapter b5-static-001.json and b5-static-002.json; exact subprocess nbconvert command in b5-final-execution.json",
    ],
    incidents=[
        dict(
            kind="static_lint",
            evidence="b5-static-001.json",
            repair="Split four semicolon-separated assignments; static-002 passed; final clean execution followed",
        )
    ],
    access_control="instruction_only",
    prohibited_content_observed=False,
    access_status="no_prohibited_exposure_observed",
    audit_limit="No exhaustive OS read tracing; see consulted-sources.json.",
    presentation_policy="evaluation-ancillary-v1",
    notebook="pgm_example_lyap.ipynb",
    final_state="state/pgm_b5.json",
    notebook_sha256=audit["sha256"],
)
(root / "supplementary/b5-handoff-access.json").write_text(
    json.dumps(handoff, indent=2)
)
print(
    json.dumps(
        {
            k: handoff[k]
            for k in [
                "current_block",
                "completion_status",
                "next_block",
                "run_status",
                "finished_utc",
                "numerical_certificate_verified",
                "analytic_full_pep_verified",
                "lyapunov_proof_verified",
            ]
        },
        indent=2,
    )
)
