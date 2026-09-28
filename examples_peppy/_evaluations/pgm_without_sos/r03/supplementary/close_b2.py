import hashlib
import json
from pathlib import Path

root = Path.cwd()
p = root / "pgm_example_lyap.ipynb"
b = json.loads(p.read_text())
cell = b["cells"][9]
assert cell["execution_count"] is not None
assert not any(
    o["output_type"] == "error"
    for c in b["cells"]
    if c["cell_type"] == "code"
    for o in c["outputs"]
)
text = "".join("".join(o.get("text", [])) for o in cell["outputs"])
for marker in (
    "Complete numerical checks:",
    "Candidate multiplier maximum error:",
    "Candidate S error:",
    "Analytic status:",
):
    assert marker in text
    print(next(line for line in text.splitlines() if marker in line))
pcheck = root / "supplementary/pgm_example_lyap_checklist.md"
s = pcheck.read_text().replace("Last reviewed block: B1", "Last reviewed block: B2")
s = "\n".join(
    "SHA-256: " + hashlib.sha256(p.read_bytes()).hexdigest()
    if line.startswith("SHA-256:")
    else line
    for line in s.splitlines()
)
s = s.replace(
    "| 7 | dense and relaxed proof solves | pending | 8 | Due B2. |",
    "| 7 | dense and relaxed proof solves | verified | 8,9 | Both CLARABEL optimal; 2.34e-10 objective gap; all owners summarized; relaxation and dual inventory preserved. |",
)
s = s.replace(
    "| 8 | lambda and S verification (closed-form when available, otherwise numerical with explicit analytic status) | pending | 8 | Due B2. |",
    "| 8 | lambda and S verification (closed-form when available, otherwise numerical with explicit analytic status) | verified | 8,9 | Complete identity, PSD, sign and decomposition reconstruction checks executed; labeled candidates and residual matrix; initial search recorded; global analytic status unresolved. |",
)
s = (
    s.replace("| pending | 9 | Due B3.", "| pending | 10 | Due B3.")
    .replace("| pending | 10 | Due B4.", "| pending | 11 | Due B4.")
    .replace("| pending | 10,11 | Due B4/B5.", "| pending | 11,12 | Due B4/B5.")
    .replace("| pending | 11 | Due B5.", "| pending | 12 | Due B5.")
)
pcheck.write_text(s)
record = {
    "current_block": "B2",
    "completion_status": "complete",
    "next_block": "B3",
    "entry_exit_reason": "Complete coherent numerical certificate verified and initial closed-form search performed",
    "run_status": "awaiting_same_session_continuation",
    "numerical_certificate_verified": True,
    "analytic_full_pep_verified": False,
    "lyapunov_proof_verified": False,
    "unresolved_work": "All-horizon certificate PSD/identity proof; B3-B5 Lyapunov construction and proof",
    "consulted_sources": [
        "approved pep-full-proof/SKILL.md",
        "approved pep-full-proof/references/workflow.md",
        "approved pepflow/pep_result.py",
        "approved pepflow/expression_manager.py",
        "approved pepflow/ipython_utils.py",
        "own B1/B2 artifacts",
        "approved framework files listed in state certificate source hashes (imported/hashed)",
    ],
    "access_control": "instruction_only",
    "prohibited_material_observed": False,
    "observability": "No exhaustive OS access trace",
    "recovery": [
        "Ruff E731 repaired by def; ty numeric annotations satisfied with exact SymPy integers; notebook reexecuted."
    ],
}
(root / "supplementary/b2-handoff.json").write_text(json.dumps(record, indent=2))
