import hashlib
import json
from pathlib import Path

root = Path(__file__).resolve().parent.parent
path = root / "ogm_example_lyap.ipynb"
nb = json.loads(path.read_text(encoding="utf-8"))
for i, cell in enumerate(nb["cells"]):
    source = "".join(cell["source"])
    if cell["cell_type"] == "markdown":
        assert not any(ch in source for ch in ("\t", "\r", "\f", "\x08"))
        assert "\\\\" not in source and "\\(" not in source and "\\[" not in source
        assert source.count("$") % 2 == 0
    else:
        assert cell["execution_count"] is not None
        assert not any(o["output_type"] == "error" for o in cell["outputs"])
outputs = nb["cells"][15]["outputs"]
assert sum(o["output_type"] == "display_data" for o in outputs) == 3
checklist = root / "supplementary/ogm_example_lyap_checklist.md"
lines = checklist.read_text(encoding="utf-8").splitlines()
for i, line in enumerate(lines):
    if line.startswith("Last reviewed block:"):
        lines[i] = "Last reviewed block: B2"
    elif line.startswith("SHA-256:"):
        lines[i] = "SHA-256: " + hashlib.sha256(path.read_bytes()).hexdigest()
    elif line.startswith("| 7."):
        lines[i] = (
            "| 7. dense and relaxed proof solves | verified | 11,12 | Dense/sparse results, active multipliers and preserved-optimum assertion replayed; actual acquisition logs retained. |"
        )
    elif line.startswith("| 8."):
        lines[i] = (
            "| 8. lambda and S verification (closed-form when available, otherwise numerical with explicit analytic status) | verified | 13,14,15 | Executable full-coordinate checks and three labeled matrices; candidate formulas and actual search recorded; analytic claims remain false. |"
        )
    elif line.startswith("| 9."):
        lines[i] = line.replace("| 13 |", "| 16 |")
    elif line.startswith("| 10."):
        lines[i] = line.replace("| 14 |", "| 17 |")
    elif line.startswith("| 11.") or line.startswith("| 12."):
        lines[i] = line.replace("| 15 |", "| 18 |")
checklist.write_text("\n".join(lines), encoding="utf-8")
print("B2 source/output and Markdown inspection passed.")
