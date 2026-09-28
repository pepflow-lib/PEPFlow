import hashlib
import json
from pathlib import Path

root = Path.cwd()
settings = json.loads((root.parent / "settings.json").read_text())
original = Path(settings["original_submission"])
miss = []
for rel, digest in settings["submission_hashes"].items():
    p = original / rel
    if hashlib.sha256(p.read_bytes()).hexdigest() != digest:
        miss.append(rel)
nb = json.loads((original / "dual_feg_example_lyap.ipynb").read_text())
static = json.loads((original / "supplementary/b5-static-001.json").read_text())
execution = json.loads(
    (original / "supplementary/b5-nbconvert-execution.json").read_text()
)
summary = {
    "frozen_hashes_checked": len(settings["submission_hashes"]),
    "hash_mismatches": miss,
    "notebook_sha256": hashlib.sha256(
        (original / "dual_feg_example_lyap.ipynb").read_bytes()
    ).hexdigest(),
    "saved_execution_returncode": execution["returncode"],
    "saved_execution_hash_matches": execution["sha256"]
    == settings["submission_hashes"]["dual_feg_example_lyap.ipynb"],
    "saved_static_returns": {c["label"]: c["returncode"] for c in static["commands"]},
    "notebook_code_cells": sum(c["cell_type"] == "code" for c in nb["cells"]),
    "notebook_error_outputs": sum(
        o.get("output_type") == "error"
        for c in nb["cells"]
        for o in c.get("outputs", [])
    ),
    "notebook_png_outputs": sum(
        "image/png" in o.get("data", {})
        for c in nb["cells"]
        for o in c.get("outputs", [])
    ),
}
assert not miss and summary["saved_execution_hash_matches"]
(root / "integrity-delivery.json").write_text(json.dumps(summary, indent=2))
print(json.dumps(summary, indent=2))
