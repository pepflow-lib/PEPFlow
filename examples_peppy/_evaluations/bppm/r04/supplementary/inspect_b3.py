import hashlib
import json
from pathlib import Path

root = Path(__file__).resolve().parents[1]
p = root / "bppm_example_lyap.ipynb"
nb = json.loads(p.read_text())
for i, c in enumerate(nb["cells"]):
    source = "".join(c["source"])
    assert not any(x in source for x in ("\x0c", "\x08", "\r"))
    if c["cell_type"] == "code":
        assert c["execution_count"] is not None
        assert all(o["output_type"] != "error" for o in c["outputs"])
    else:
        assert "\\(" not in source and "\\[" not in source
    if i >= 19:
        print(i, c["cell_type"], source.splitlines()[0])
q = root / "supplementary/bppm_example_lyap_checklist.md"
s = q.read_text().splitlines()
for i, line in enumerate(s):
    if line.startswith("Last reviewed block:"):
        s[i] = "Last reviewed block: B3"
    if line.startswith("SHA-256:"):
        s[i] = "SHA-256: " + hashlib.sha256(p.read_bytes()).hexdigest()
    if line.startswith("|9|"):
        s[i] = (
            "|9|partial-sum Lyapunov construction and rank profile|verified|19,20,21|Both complete certificates revalidated; literal partial-sum construction, full-coordinate coverage, sign and rank checks executed. Rank 4 across N=4,6 with fixed exclusions (1,1), absolute tolerance 1e-4.|"
        )
    if line.startswith("|10|"):
        s[i] = line.replace("|20|", "|22|")
    if line.startswith("|11|"):
        s[i] = line.replace("|20,21|", "|22,23|")
    if line.startswith("|12|"):
        s[i] = line.replace("|21|", "|23|")
q.write_text("\n".join(s))
record = {
    "phase": "B3_confirmation",
    "new_external_sources": [],
    "own_sources": [
        "supplementary/run_b3_N6.py",
        "supplementary/b3_rank_N6.json",
        "supplementary/finalize_b3.py",
        "supplementary/b3_assess.py",
        "supplementary/update_b3_notebook.py",
        "supplementary/inspect_b3.py",
        "state/bppm_b3.json",
    ],
    "checks": [
        "supplementary/b3_N6.console.txt",
        "supplementary/b3_finalization.console.txt",
        "supplementary/b3_notebook.console.txt",
        "supplementary/b3-static-001.json",
    ],
    "access_control": "instruction_only",
    "incidents": [],
    "prohibited_content_observed": False,
    "audit_limit": "No exhaustive OS tracing.",
}
(root / "supplementary/b3-confirmation-consulted-sources.json").write_text(
    json.dumps(record, indent=2)
)
record = {
    "current_block": "B3",
    "completion_status": "complete",
    "next_block": "B4",
    "entry_exit_reason": "Both saved certificates reconstructed; consistent rank and full-coordinate coverage confirmed; notebook/static checks passed.",
    "operational_status": "awaiting_same_session_continuation",
    "run_status": "in_progress",
    "deadline_utc": "2026-09-23T22:42:59.899868+00:00",
}
(root / "supplementary/b3-handoff-002.json").write_text(json.dumps(record, indent=2))
