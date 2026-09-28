import hashlib
import json
import re
from pathlib import Path

r = Path.cwd().parent
s = json.loads((r / "settings.json").read_text())
o = Path(s["original_submission"])
mismatch = [
    k
    for k, v in s["submission_hashes"].items()
    if hashlib.sha256((o / k).read_bytes()).hexdigest() != v
]
a = json.loads((r / "own-generation-host-access-calls.json").read_text())
print("hash mismatches", mismatch, "host access calls", len(a))
for x in a:
    arg = x.get("arguments", "")
    if re.search(
        r"web__|https?://|git (show|log|diff)|_references[/\\]|pgm_without_sos", arg
    ):
        print("AUDIT MATCH", x["timestamp"], arg[:1200])
n = json.loads((o / "pgm_example_lyap.ipynb").read_text())
st = json.loads((o / "supplementary/b5-static-001.json").read_text())
res = {
    "hash_mismatches": mismatch,
    "host_access_call_count": len(a),
    "code_cells": sum(c["cell_type"] == "code" for c in n["cells"]),
    "unexecuted": [
        c["id"]
        for c in n["cells"]
        if c["cell_type"] == "code" and c["execution_count"] is None
    ],
    "errors": [
        c["id"]
        for c in n["cells"]
        if any(t["output_type"] == "error" for t in c.get("outputs", []))
    ],
    "static_commands": [
        {"label": c["label"], "returncode": c["returncode"]} for c in st["commands"]
    ],
    "static_status": st["status"],
}
Path("delivery-audit.json").write_text(json.dumps(res, indent=2))
print(json.dumps(res, indent=2))
