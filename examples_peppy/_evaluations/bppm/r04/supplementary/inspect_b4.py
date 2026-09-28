import hashlib
import json
from pathlib import Path

root = Path(__file__).resolve().parents[1]
p = root / "bppm_example_lyap.ipynb"
nb = json.loads(p.read_text())
for i, c in enumerate(nb["cells"]):
    s = "".join(c["source"])
    assert not any(x in s for x in ("\x0c", "\x08", "\r"))
    if c["cell_type"] == "code":
        assert c["execution_count"] is not None
        assert all(o["output_type"] != "error" for o in c["outputs"])
    else:
        assert "\\(" not in s and "\\[" not in s
    if i >= 22:
        print(i, c["cell_type"], s.splitlines()[0])
q = root / "supplementary/bppm_example_lyap_checklist.md"
lines = q.read_text().splitlines()
for i, line in enumerate(lines):
    if line.startswith("Last reviewed block:"):
        lines[i] = "Last reviewed block: B4"
    if line.startswith("SHA-256:"):
        lines[i] = "SHA-256: " + hashlib.sha256(p.read_bytes()).hexdigest()
    if line.startswith("|10|"):
        lines[i] = (
            "|10|special-vector identification|verified|22-29|Actual candidate scan and sparse search executed for k=1..N; four-vector template independently reconstructs every nonzero quadratic part; V0 uses empty basis.|"
        )
    if line.startswith("|11|"):
        lines[i] = (
            "|11|coefficient extraction and closed-form V_k|pending|30-34|B4 coefficient matrices and all-component reconstructions verified including endpoints; candidate formula errors below 6.7e-10. Exact closed form remains due in B5.|"
        )
    if line.startswith("|12|"):
        lines[i] = (
            "|12|symbolic step, base, and boundary identities|pending|35|B5 not entered.|"
        )
q.write_text("\n".join(lines))
record = {
    "phase": "B4",
    "approved_sources": [
        "plugins/pepflow-workflows/skills/lyap-vectors/references/workflow.md",
        "pepflow/lyapunov_utils.py",
        "pepflow/expression_manager.py (definition-name scan only)",
    ],
    "own_sources": "B3 certificate and exact replay sources; generated b4 candidate/filter/search/basis/coefficient/structure/fit scripts; discovery and finalization runner; notebook update and inspection scripts.",
    "evidence": [
        "supplementary/b4_discovery.console.txt",
        "supplementary/b4_finalization.console.txt",
        "supplementary/b4_notebook.console.txt",
        "supplementary/b4-static-001.json",
    ],
    "access_control": "instruction_only",
    "incidents": [],
    "prohibited_content_observed": False,
    "audit_limit": "No exhaustive OS filesystem tracing.",
}
(root / "supplementary/b4-consulted-sources.json").write_text(
    json.dumps(record, indent=2)
)
record = {
    "current_block": "B4",
    "completion_status": "complete",
    "next_block": "B5",
    "entry_exit_reason": "Interpretable basis, independence, and all-index full-expression reconstruction verified; notebook/static checks passed.",
    "operational_status": "awaiting_same_session_continuation",
    "run_status": "in_progress",
    "deadline_utc": "2026-09-23T22:42:59.899868+00:00",
}
(root / "supplementary/b4-handoff.json").write_text(json.dumps(record, indent=2))
