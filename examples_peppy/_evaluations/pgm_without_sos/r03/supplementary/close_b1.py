import hashlib
import json
from pathlib import Path

root = Path(__file__).resolve().parents[1]
p = root / "pgm_example_lyap.ipynb"
b = json.loads(p.read_text())
for c in b["cells"]:
    if c["cell_type"] == "markdown":
        s = "".join(c["source"]).replace("\\\\", "\\")
        assert not any(ord(x) < 32 and x not in "\n\t" for x in s)
        assert "\\(" not in s and "\\[" not in s
        c["source"] = s.splitlines(keepends=True)
p.write_text(json.dumps(b, indent=1))
items = [
    (
        "title, problem description, and the algorithm update equations in LaTeX",
        "verified",
        "0",
        "Assumptions, update and metric inspected; Markdown delimiters/control characters checked.",
    ),
    (
        "proof statement placeholder, to be filled with the final theorem and proof outline in Block 5",
        "pending",
        "1",
        "Placeholder retained; final theorem due B5.",
    ),
    ("imports", "verified", "2,3", "Approved import path; fresh kernel passed."),
    (
        "function/operator definitions",
        "verified",
        "4",
        "Smooth convex f, convex g, composite h inspected.",
    ),
    (
        "make_ctx_pgm and get_pep_setup",
        "verified",
        "4",
        "Recursion, stationarity, squared radius and metric exposed.",
    ),
    (
        "numerical evidence, including a plot comparing the PEP values against the discovered or conjectured rate",
        "verified",
        "5,6,7",
        "Seven printed values; maximum discrepancy 4.31910757159315e-09; image/png output present. No image inspection under override.",
    ),
    ("dense and relaxed proof solves", "pending", "8", "Due B2."),
    (
        "lambda and S verification (closed-form when available, otherwise numerical with explicit analytic status)",
        "pending",
        "8",
        "Due B2.",
    ),
    ("partial-sum Lyapunov construction and rank profile", "pending", "9", "Due B3."),
    ("special-vector identification", "pending", "10", "Due B4."),
    ("coefficient extraction and closed-form V_k", "pending", "10,11", "Due B4/B5."),
    ("symbolic step, base, and boundary identities", "pending", "11", "Due B5."),
]
lines = [
    "Notebook: pgm_example_lyap.ipynb",
    "Last reviewed block: B1",
    "SHA-256: " + hashlib.sha256(p.read_bytes()).hexdigest(),
    "Presentation policy: evaluation-ancillary-v1. Source/output inspection only; no rendering or image review.",
    "",
    "| Item | Requirement | Status | Cell indices | Evidence |",
    "|---|---|---|---|---|",
]
lines += [
    f"| {i} | {a} | {status} | {cells} | {e} |"
    for i, (a, status, cells, e) in enumerate(items, 1)
]
(root / "supplementary/pgm_example_lyap_checklist.md").write_text("\n".join(lines))
record = {
    "current_block": "B1",
    "completion_status": "complete",
    "next_block": "B2",
    "entry_exit_reason": "Numerical sweep and notebook initialization complete; request boundary",
    "run_status": "awaiting_same_session_continuation",
    "access_control": "instruction_only",
    "prohibited_material_observed": False,
    "observability": "No exhaustive OS tracing; declaration limited to observed reads and tool outputs",
    "consulted_sources": [
        "dispatch.md",
        "input.md",
        "worker-protocol.md",
        "pep-implement/SKILL.md",
        "pep-implement/references/workflow.md",
        "references/output-layout.md",
        "approved/pepflow/__init__.py",
        "approved/pepflow/function.py",
        "approved/pepflow/pep.py",
        "approved/pepflow/pep_runner.py",
        "approved static adapter",
        "own generated files",
    ],
    "incidents": [
        "Sweep assertion interrupted after N6 optimal_inaccurate; preserved values and resumed at N7 without re-solving prior samples. N6/N7 are rate evidence only.",
        "Static staging path length failure repaired using supplementary/helpers; preflight-002 passed.",
        "Ruff E402 fixed by splitting notebook import cell; static-003 passed.",
    ],
    "unresolved_work": "B2-B5 certificate, Lyapunov discovery and exact proof; no mathematical next-block work started.",
}
(root / "supplementary/b1-handoff.json").write_text(json.dumps(record, indent=2))
print("Markdown checks and checklist completed.")
