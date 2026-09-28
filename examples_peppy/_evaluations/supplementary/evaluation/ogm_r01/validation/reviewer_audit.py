import hashlib
import json
import re
from pathlib import Path

root = Path.cwd()
review = root.parent
settings = json.loads((review / "settings.json").read_text(encoding="utf-8-sig"))
original = Path(settings["original_submission"])
bad = [
    name
    for name, digest in settings["submission_hashes"].items()
    if hashlib.sha256((original / name).read_bytes()).hexdigest() != digest
]
nb = json.loads((original / "ogm_example_lyap.ipynb").read_text(encoding="utf-8-sig"))
codes = [c for c in nb["cells"] if c["cell_type"] == "code"]
static = json.loads(
    (original / "supplementary/b5-static-001.json").read_text(encoding="utf-8-sig")
)
report = {
    "frozen_file_count": len(settings["submission_hashes"]),
    "hash_mismatches": bad,
    "code_cells": len(codes),
    "unexecuted_cells": [c["id"] for c in codes if c["execution_count"] is None],
    "error_outputs": [
        c["id"]
        for c in codes
        if any(o["output_type"] == "error" for o in c.get("outputs", []))
    ],
    "embedded_plot": any(
        "image/png" in o.get("data", {}) for c in codes for o in c.get("outputs", [])
    ),
    "code_hash": hashlib.sha256(
        "\n".join("".join(c["source"]) for c in codes).encode()
    ).hexdigest(),
    "static_returncodes": {c["label"]: c["returncode"] for c in static["commands"]},
}
(root / "reviewer-audit.json").write_text(json.dumps(report, indent=2))
print(json.dumps(report, indent=2))
a = json.loads(
    (review / "own-generation-host-access-calls.json").read_text(encoding="utf-8-sig")
)
print("Recorded tool calls:", len(a), "tools:", sorted(set(c["name"] for c in a)))
# Compact inventory of explicitly cited repository absolute paths in available commands.
paths = sorted(
    set(
        p
        for c in a
        for p in re.findall(
            r"C:/Users/Jack/Documents/GitHub/PEPFlow/[^\s\"\x27\\]+", c["arguments"]
        )
    )
)
print(
    "Outside own attempt absolute repository paths:",
    [p for p in paths if "/ogm/r01" not in p],
)
