import hashlib
import json
from pathlib import Path

root = Path.cwd()
p = root / "pgm_example_lyap.ipynb"
b = json.loads(p.read_text())
cell = b["cells"][11]
text = "".join("".join(o.get("text", [])) for o in cell["outputs"])
assert "Cross-horizon interior rank confirmed" in text
assert all(
    o["output_type"] != "error"
    for c in b["cells"]
    if c["cell_type"] == "code"
    for o in c["outputs"]
)
print(text)
check = root / "supplementary/pgm_example_lyap_checklist.md"
s = check.read_text().replace("Last reviewed block: B2", "Last reviewed block: B3")
s = "\n".join(
    "SHA-256: " + hashlib.sha256(p.read_bytes()).hexdigest()
    if line.startswith("SHA-256:")
    else line
    for line in s.splitlines()
)
s = s.replace(
    "| 9 | partial-sum Lyapunov construction and rank profile | pending | 10 | Due B3. |",
    "| 9 | partial-sum Lyapunov construction and rank profile | verified | 10,11 | Complete saved-certificate revalidation, visible decomposition and partial-sum loop; rank four at N4/N6 with fixed exclusions 1,1; full coverage and step checks; fresh kernel passed. |",
)
s = (
    s.replace("| pending | 11 | Due B4.", "| pending | 12 | Due B4.")
    .replace("| pending | 11,12 | Due B4/B5.", "| pending | 12,13 | Due B4/B5.")
    .replace("| pending | 12 | Due B5.", "| pending | 13 | Due B5.")
)
check.write_text(s)
record = {
    "current_block": "B3",
    "completion_status": "complete",
    "next_block": "B4",
    "entry_exit_reason": "Cross-horizon rank and complete coverage confirmed; notebook/static verification passed",
    "run_status": "awaiting_same_session_continuation",
    "selected_state": "state/pgm_b3.json",
    "evidence": "supplementary/rank_search.json",
    "unresolved_work": "Basis reconstruction and analytic all-horizon proof (B4/B5)",
    "access_control": "instruction_only",
    "prohibited_material_observed": False,
    "consulted_sources": [
        "own B2/B3 files",
        "previously allowlisted generic framework imports",
    ],
    "recovery": [
        "Unused generic import removed; numeric dictionary annotation aligned with framework; notebook section replacement corrected and reexecuted."
    ],
}
(root / "supplementary/b3-complete-handoff.json").write_text(
    json.dumps(record, indent=2)
)
