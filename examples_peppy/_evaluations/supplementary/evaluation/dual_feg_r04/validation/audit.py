import hashlib
import json
from pathlib import Path

root = Path.cwd()
review = root.parent
settings = json.loads((review / "settings.json").read_text())
original = Path(settings["original_submission"])
mismatches = []
for path, expected in settings["submission_hashes"].items():
    if hashlib.sha256((original / path).read_bytes()).hexdigest() != expected:
        mismatches.append(path)
nb = json.loads((original / "dual_feg_example_lyap.ipynb").read_text(encoding="utf-8"))
code = [c for c in nb["cells"] if c["cell_type"] == "code"]
code_hash = hashlib.sha256(
    "\n".join("".join(c["source"]) for c in code).encode()
).hexdigest()
audit = json.loads((original / "supplementary/b5-final-audit.json").read_text())
static = json.loads((original / "supplementary/b5-static-001.json").read_text())
replay = json.loads((root / "replay-results.json").read_text())
result = {
    "frozen_hashes_checked": len(settings["submission_hashes"]),
    "frozen_hash_mismatches": mismatches,
    "code_count": len(code),
    "all_cells_executed": all(c["execution_count"] is not None for c in code),
    "execution_errors": [
        c["id"] for c in code if any(o["output_type"] == "error" for o in c["outputs"])
    ],
    "code_hash": code_hash,
    "code_hash_matches_executed_audit": code_hash == audit["executed_code_sha256"],
    "plot_present": any(
        "image/png" in o.get("data", {}) for c in code for o in c["outputs"]
    ),
    "static_checks": [
        {k: c[k] for k in ["label", "returncode", "stdout"]}
        for c in static["commands"]
        if c["label"] in ["source_ruff", "source_ty"]
    ],
    "b4_stricter_component_atol_1e_5_passed": all(
        v <= 1e-5
        for row in replay["component_residuals"].values()
        for v in row.values()
    ),
}
assert (
    not mismatches
    and result["code_hash_matches_executed_audit"]
    and not result["execution_errors"]
)
(root / "audit-results.json").write_text(json.dumps(result, indent=2))
print(json.dumps(result, indent=2))
