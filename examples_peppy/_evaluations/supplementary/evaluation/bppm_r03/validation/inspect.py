import hashlib
import json
from pathlib import Path

root = Path.cwd()
review = root.parent
settings = json.loads((review / "settings.json").read_text(encoding="utf-8-sig"))
origin = Path(settings["original_submission"])
errors = []
for rel, digest in settings["submission_hashes"].items():
    actual = hashlib.sha256((origin / rel).read_bytes()).hexdigest()
    if actual != digest:
        errors.append(rel)
nb = json.loads((origin / "bppm_example_lyap.ipynb").read_text(encoding="utf-8-sig"))
codes = [c for c in nb["cells"] if c["cell_type"] == "code"]
static = json.loads(
    (origin / "supplementary/b5-static-002.json").read_text(encoding="utf-8-sig")
)
checks = [
    {"label": x["label"], "returncode": x["returncode"], "stdout": x["stdout"]}
    for x in static["commands"]
    if x["label"] in ("source_ruff", "source_ty")
]
access = json.loads(
    (review / "own-generation-host-access-calls.json").read_text(encoding="utf-8-sig")
)
reads = []
for a in access:
    t = a["arguments"]
    if "Get-Content" in t or "rg " in t:
        reads.append({"line": a["line"], "argument_prefix": t[:800]})
summary = {
    "frozen_hashes_checked": len(settings["submission_hashes"]),
    "hash_mismatches": errors,
    "code_cells": len(codes),
    "execution_counts": [c.get("execution_count") for c in codes],
    "error_outputs": [
        c["id"]
        for c in codes
        if any(o.get("output_type") == "error" for o in c.get("outputs", []))
    ],
    "plot_output_present": any(
        "image/png" in o.get("data", {}) for c in codes for o in c.get("outputs", [])
    ),
    "static_checks": checks,
    "checklist_hash_matches": hashlib.sha256(
        (origin / "bppm_example_lyap.ipynb").read_bytes()
    ).hexdigest()
    in (origin / "supplementary/bppm_example_lyap_checklist.md").read_text(
        encoding="cp1252"
    ),
    "access_call_count": len(access),
}
assert not errors
(root / "inspection-results.json").write_text(
    json.dumps(summary, indent=2), encoding="utf-8"
)
print(json.dumps(summary, indent=2))
