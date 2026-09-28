import hashlib
import json
from pathlib import Path

root = Path(__file__).resolve().parents[1]
p = root / "dual_feg_example_lyap.ipynb"
nb = json.loads(p.read_text())
for i, c in enumerate(nb["cells"]):
    src = "".join(c["source"])
    if c["cell_type"] == "markdown":
        assert "\\(" not in src and "\\[" not in src
        assert not any(ord(ch) < 32 and ch not in "\n\t\r" for ch in src)
    for o in c.get("outputs", []):
        assert o["output_type"] != "error"
        if i >= 13 and "text" in o:
            print(i, "".join(o["text"]))
check = root / "supplementary/dual_feg_example_lyap_checklist.md"
lines = check.read_text().splitlines()
lines[1] = "Last reviewed block: B3"
lines[2] = "SHA-256: " + hashlib.sha256(p.read_bytes()).hexdigest()
for i, line in enumerate(lines):
    if line.startswith("| 9."):
        lines[i] = (
            "| 9. partial-sum Lyapunov construction and rank profile | verified | 13,14,15,16,17,18 | Visible revalidation, full dual extraction, complete Gram piece, construction and sign convention, ranks and coverage. N=6 and N=8 share rank 4 for indices 1..N-1; absolute tolerance 1e-4; no near-threshold values. |"
        )
    for no, index in [(10, 19), (11, 20), (12, 21)]:
        if line.startswith(f"| {no}."):
            parts = line.split("|")
            parts[3] = f" {index} "
            lines[i] = "|".join(parts)
check.write_text("\n".join(lines))
record = json.loads((root / "supplementary/b3-access-record.json").read_text())
record["status"] = "complete"
record["generated_files"] += [
    "supplementary/run_b3_trial_n8.py",
    "supplementary/b3-trial-n8.json",
    "supplementary/b3_assess.py",
    "supplementary/finalize_b3.py",
    "supplementary/update_b3_notebook.py",
    "supplementary/review_b3.py",
    "state/dual_feg_b3.json",
    "supplementary/rank_search.json",
]
(root / "supplementary/b3-access-record.json").write_text(json.dumps(record, indent=2))
