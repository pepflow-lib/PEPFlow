"""Finalize B4 numerical reconstruction evidence and handoff."""

import hashlib
import json
import re
from pathlib import Path

# optional notebook-generation dependency
import nbformat as nbf  # ty: ignore[unresolved-import]

root = Path(__file__).resolve().parents[1]
assert (
    json.loads((root / "supplementary/b4-static-002.json").read_text())["status"]
    == "passed"
)
nbpath = root / "bppm_example_lyap.ipynb"
nb = nbf.read(nbpath, as_version=4)
for index in (38, 40, 42, 43, 45):
    assert (
        nb.cells[index].cell_type == "code"
        and nb.cells[index].execution_count is not None
    )
assert (
    sum(
        o.output_type in ("display_data", "execute_result")
        for o in nb.cells[42].outputs
    )
    >= 9
)
checkpath = root / "supplementary/bppm_example_lyap_checklist.md"
text = checkpath.read_text()
text = re.sub(r"Last reviewed block: .*", "Last reviewed block: B4", text)
text = re.sub(
    r"SHA-256: [a-f0-9]+",
    "SHA-256: " + hashlib.sha256(nbpath.read_bytes()).hexdigest(),
    text,
)
lines = text.splitlines()
for i, line in enumerate(lines):
    if line.startswith("| 10 |"):
        lines[i] = (
            "| 10 | special-vector identification | verified | 32-40 | Actual candidate filtering and sparse search executed for k=1..N; same four-vector basis, empty k=0 basis; every index independent and reconstructing. |"
        )
    elif line.startswith("| 11 |"):
        lines[i] = (
            "| 11 | coefficient extraction and closed-form V_k | pending | 41-46 | Numerical matrices, meaningful function terms, all-index full reconstruction and formula candidates verified; exact all-horizon formula awaits B5. |"
        )
    elif line.startswith("| 12 |"):
        lines[i] = (
            "| 12 | symbolic step, base, and boundary identities | pending | 47 | B5 |"
        )
checkpath.write_text("\n".join(lines) + "\n")
p = root / "state/bppm_b4.json"
state = json.loads(p.read_text())
state.update(
    completion_status="complete",
    static_evidence="supplementary/b4-static-002.json",
    execution_evidence="supplementary/b4-execution.json",
)
p.write_text(json.dumps(state, indent=2))
audit = {
    "current_block": "B4",
    "access_control": "instruction_only",
    "new_approved_reads": [
        "plugins/pepflow-workflows/skills/lyap-vectors/references/workflow.md",
        "pepflow/lyapunov_utils.py",
    ],
    "generated_reads": [
        "state/bppm_b3.json",
        "supplementary/rank_search.json",
        "supplementary/b4_scan.py",
        "supplementary/b4_basis.py",
        "supplementary/b4_coefficients.py",
        "state/bppm_b4.json",
        "bppm_example_lyap.ipynb",
        "supplementary/bppm_example_lyap_checklist.md",
        "supplementary/b4-static-001.json",
        "supplementary/b4-static-002.json",
    ],
    "commands": [
        "python -I -B supplementary/run_b4.py",
        "python -I -B supplementary/author_b4.py (twice)",
        "python -I -B supplementary/execute_notebook.py B4 (twice)",
        "approved static adapter twice",
        "python -I -B supplementary/finalize_b4.py",
    ],
    "source_hash_reads": "Exact certificate-provenance files only",
    "incidents": [
        {
            "classification": "lint diagnostic",
            "evidence": "b4-static-001.json",
            "repair": "Changed descriptive snippet docstring to comment before notebook import; reran fresh-kernel and static checks.",
        }
    ],
    "prohibited_content_observed": False,
    "audit_limit": "Instruction-only access; no exhaustive OS read trace.",
}
(root / "supplementary/b4-access-record.json").write_text(json.dumps(audit, indent=2))
handoff = {
    "current_block": "B4",
    "completion_status": "complete",
    "next_block": "B5",
    "entry_exit_reason": "All-index independent basis and complete-expression reconstruction verified; candidate coefficients recorded; notebook checks passed",
    "operational_status": "awaiting_same_session_continuation",
    "next_block_started": False,
    "deadline_utc": "2026-09-24T00:34:49.219272+00:00",
}
(root / "supplementary/b4-handoff.json").write_text(json.dumps(handoff, indent=2))
print(json.dumps(handoff))
