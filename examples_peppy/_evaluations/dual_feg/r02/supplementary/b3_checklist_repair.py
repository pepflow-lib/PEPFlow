import json
from pathlib import Path

root = Path(__file__).resolve().parents[1]
check = root / "supplementary/dual_feg_example_lyap_checklist.md"
lines = check.read_text(encoding="cp1252").splitlines()
record = json.loads((root / "supplementary/b3-notebook-execution.json").read_text())
for i, line in enumerate(lines):
    if line.startswith("SHA-256:"):
        lines[i] = "SHA-256: " + record["notebook_sha256"]
check.write_text("\n".join(lines), encoding="utf-8")
