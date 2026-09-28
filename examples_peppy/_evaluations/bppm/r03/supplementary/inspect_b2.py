import hashlib
import json
from pathlib import Path

root = Path(__file__).resolve().parents[1]
path = root / "bppm_example_lyap.ipynb"
book = json.loads(path.read_text())
for cell in book["cells"]:
    source = "".join(cell["source"])
    assert not any(ord(c) < 32 and c not in "\n\t" for c in source)
    assert not any(o.get("output_type") == "error" for o in cell.get("outputs", []))
    if cell["cell_type"] == "markdown":
        assert all(x not in source for x in ("\\(", "\\)", "\\[", "\\]"))
checklist = root / "supplementary/bppm_example_lyap_checklist.md"
lines = checklist.read_text().splitlines()
for i, line in enumerate(lines):
    if line.startswith("Last reviewed block:"):
        lines[i] = "Last reviewed block: B2"
    if line.startswith("SHA-256:"):
        lines[i] = "SHA-256: " + hashlib.sha256(path.read_bytes()).hexdigest()
    if line.startswith("| 7."):
        lines[i] = (
            "| 7. dense and relaxed proof solves | verified | 10–11 | Captured single-solve complete inventories; objectives 0.249999999673264 and 0.249999999988954; all groups and relaxation displayed. |"
        )
    if line.startswith("| 8."):
        lines[i] = (
            "| 8. lambda and S verification (closed-form when available, otherwise numerical with explicit analytic status) | verified | 10–17 | Candidate matrices, full spectral S reconstruction, executed Gram/function/offset and sign checks; max identity residual 8.90e-10; analytic statuses explicit. |"
        )
    if line.startswith("| 9."):
        lines[i] = line.replace("| 11 |", "| 18 |")
    if line.startswith("| 10.") or line.startswith("| 11."):
        lines[i] = line.replace("| 12 |", "| 19 |")
    if line.startswith("| 12."):
        lines[i] = line.replace("| 13 |", "| 20 |")
checklist.write_text("\n".join(lines))
record = {
    "current_block": "B2",
    "completion_status": "complete",
    "next_block": "B3",
    "entry_exit_reason": "Complete verified numerical certificate and initial closed-form search; notebook execution and static checks passed.",
    "consulted_sources": [
        "state/bppm_b1.json",
        "supplementary/approved/plugins/pepflow-workflows/skills/pep-full-proof/SKILL.md",
        "supplementary/approved/plugins/pepflow-workflows/skills/pep-full-proof/references/workflow.md",
        "supplementary/approved/pepflow/pep_context.py",
        "supplementary/approved/pepflow/pep_result.py",
        "supplementary/approved/pepflow/ipython_utils.py",
        "supplementary/approved/pepflow/solver.py",
    ],
    "commands": "Scoped reads/rg; run_b2_dense.py; run_b2_relaxed.py; update_b2_notebook.py; approved check_static.py evidence b2-static-001.json; inspect_b2.py. Own generated outputs read as needed.",
    "access_control": "instruction_only",
    "prohibited_content_observed": False,
    "incidents": [],
    "audit_limit": "No exhaustive filesystem tracing. Framework import and staging source evidence are in static check evidence.",
    "operational_status": "awaiting same-session continuation",
    "analytic_full_pep_verified": False,
    "lyapunov_proof_verified": False,
}
(root / "supplementary/b2-access.json").write_text(json.dumps(record, indent=2))
print("B2 source/output inspection complete; checklist and operational handoff saved.")
