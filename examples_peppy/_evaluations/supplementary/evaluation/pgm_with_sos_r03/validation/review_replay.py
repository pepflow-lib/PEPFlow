from typing import Any

# Keep typing metadata separate from the recorded import sequence.
# isort: split

import contextlib
import hashlib
import json
import os
import traceback
from pathlib import Path

root = Path.cwd().resolve()
assert root.name == "validation"
for key in (
    "TEMP",
    "TMP",
    "TMPDIR",
    "IPYTHONDIR",
    "MPLCONFIGDIR",
    "JUPYTER_RUNTIME_DIR",
    "JUPYTER_CONFIG_DIR",
    "XDG_CACHE_HOME",
    "JUPYTER_PATH",
):
    p = root / "review-runtime" / key.lower()
    p.mkdir(parents=True, exist_ok=True)
    os.environ[key] = str(p)
os.environ["MPLBACKEND"] = "Agg"
nb = json.loads((root / "pgm_example_lyap.ipynb").read_text(encoding="utf-8"))
settings = json.loads((root.parent / "settings.json").read_text(encoding="utf-8"))
original = Path(settings["original_submission"])
hash_results = {
    p: hashlib.sha256((original / p).read_bytes()).hexdigest() == h
    for p, h in settings["submission_hashes"].items()
}
assert all(hash_results.values())
result = {
    "hashes_checked": len(hash_results),
    "all_frozen_hashes_match": True,
    "cells": [],
    "adaptations": [
        "Cell 10 plotting section omitted; numerical checks retained. No other cell-source changes. Fresh isolated Python process, not Jupyter."
    ],
}
ns: dict[str, Any] = {"__name__": "__main__"}
with (
    (root / "review-replay.log").open("w", encoding="utf-8") as log,
    contextlib.redirect_stdout(log),
    contextlib.redirect_stderr(log),
):
    try:
        for idx, cell in enumerate(nb["cells"]):
            if cell["cell_type"] != "code":
                continue
            source = "".join(cell["source"])
            if idx == 10:
                source = source.split("fig, ax = plt.subplots()")[0]
            print("CELL", idx, cell["id"], flush=True)
            exec(compile(source, f"notebook-cell-{cell['id']}", "exec"), ns)
            result["cells"].append({"index": idx, "id": cell["id"], "status": "PASS"})
            if idx == 19:
                result["b2_checks"] = ns["checks"]
                result["aid_S_reconstruction"] = ns["maxabs"](
                    ns["S_candidate"] - ns["np"].array(ns["b2"]["S_matrix"])
                )
            if idx == 24:
                result["rank_samples"] = [
                    {
                        k: s[k]
                        for k in (
                            "N",
                            "rank_profile",
                            "rank_credible",
                            "coverage_residual",
                            "piece_residual",
                            "step_residuals",
                            "certificate_checks",
                            "singular_values",
                        )
                    }
                    for s in ns["rank_samples"]
                ]
        result["proof_results"] = ns["proof_results"]
        result["status"] = "PASS"
    except Exception:
        traceback.print_exc()
        result["status"] = "FAIL"
        result["failed_cell"] = idx
(root / "review-replay.json").write_text(json.dumps(result, indent=2), encoding="utf-8")
print(
    json.dumps(
        {k: v for k, v in result.items() if k not in ("cells", "rank_samples")},
        indent=2,
    )
)
