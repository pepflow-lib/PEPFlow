import hashlib
import json
import re
from pathlib import Path

r = Path.cwd()
settings = json.loads((r.parent / "settings.json").read_text())
o = Path(settings["original_submission"])
hashes = {
    name: hashlib.sha256((o / name).read_bytes()).hexdigest() == h
    for name, h in settings["submission_hashes"].items()
}
calls = json.loads((r.parent / "own-generation-host-access-calls.json").read_text())
paths = set()
for c in calls:
    for p in re.findall(r'(?:C:[/\\][^\s\'"`<>]+)', c.get("arguments", "")):
        if "pgm_without_sos" not in p and ".venv" not in p and "uv" not in p:
            paths.add(p)
print(
    "HASHES", len(hashes), all(hashes.values()), [k for k, v in hashes.items() if not v]
)
print("CALLS", len(calls), "NONSTANDARD PATH TOKENS", sorted(paths))
print("TOOLS", sorted(set(c["name"] for c in calls)))
static = json.loads((r / "supplementary/b5-static-006.json").read_text())
print("STATIC KEYS", list(static))
print(
    "STATIC SUMMARY",
    {
        k: v
        for k, v in static.items()
        if k
        not in (
            "commands",
            "source_files",
            "staged_files",
            "approved_sources",
            "approved_files",
        )
        and len(str(v)) < 2000
    },
)
for c in static["commands"]:
    if c["label"] in ("source_ruff", "source_ty"):
        print(c["label"], c["returncode"], c["stdout"], c["stderr"])
nb = json.loads((r / "pgm_example_lyap.ipynb").read_text())
codes = [c for c in nb["cells"] if c["cell_type"] == "code"]
summary = {
    "hash_count": len(hashes),
    "all_submission_hashes_match": all(hashes.values()),
    "generation_access_call_count": len(calls),
    "nonstandard_path_tokens": sorted(paths),
    "code_cells": len(codes),
    "executed_code_cells": sum(c["execution_count"] is not None for c in codes),
    "error_outputs": [
        x for c in codes for x in c.get("outputs", []) if x["output_type"] == "error"
    ],
    "static_commands": [
        {k: c.get(k) for k in ("label", "returncode", "stdout", "stderr")}
        for c in static["commands"]
        if c["label"] in ("source_ruff", "source_ty")
    ],
}
(r / "audit_results.json").write_text(json.dumps(summary, indent=2))
