import contextlib
import datetime
import hashlib
import json
import os
import shutil
from pathlib import Path

root = Path.cwd().resolve()
original = root.parents[3] / "dual_feg/r04"
assert root.name == "validation" and original.name == "r04"
for name in (
    "TEMP",
    "TMP",
    "TMPDIR",
    "MPLCONFIGDIR",
    "IPYTHONDIR",
    "JUPYTER_RUNTIME_DIR",
    "JUPYTER_CONFIG_DIR",
    "XDG_CACHE_HOME",
):
    p = root / ".runtime" / name.lower()
    p.mkdir(parents=True, exist_ok=True)
    os.environ[name] = str(p)
for name in (
    "OMP_NUM_THREADS",
    "OPENBLAS_NUM_THREADS",
    "MKL_NUM_THREADS",
    "NUMEXPR_NUM_THREADS",
):
    os.environ[name] = "1"
os.environ["MPLBACKEND"] = "Agg"
for rel in ["dual_feg_setup.py", "dual_feg_example_lyap.ipynb"]:
    shutil.copy2(original / rel, root / rel)
for rel in [
    "state",
    "supplementary/approved/pepflow",
    "supplementary/helpers",
    "supplementary/n8",
]:
    shutil.copytree(
        original / rel,
        root / rel,
        dirs_exist_ok=True,
        ignore=shutil.ignore_patterns("__pycache__", ".runtime"),
    )
for name in [
    "b3_certificate_check.py",
    "b3_decomposition.py",
    "b3_grouping.py",
    "rank_search.json",
]:
    shutil.copy2(original / "supplementary" / name, root / "supplementary" / name)
nb = json.loads((original / "dual_feg_example_lyap.ipynb").read_text(encoding="utf-8"))
cells = {c["id"]: "".join(c["source"]) for c in nb["cells"]}
selected = [
    "b1-02",
    "b1-03",
    "b1-05",
    "b1-07",
    "b1-08",
    "b3-01",
    "b3-02",
    "b4-01",
    "b4-03",
    "b4-05",
    "b4-07",
    "b4-09",
    "b4-11",
    "b5-01",
    "b5-04",
    "b5-07",
    "b5-10",
    "b5-13",
    "b5-15",
]
ns = {"__name__": "__main__"}
with (
    (root / "replay-output.txt").open("w", encoding="utf-8") as stream,
    contextlib.redirect_stdout(stream),
):
    for cid in selected:
        print("REPLAY", cid, flush=True)
        exec(compile(cells[cid], "submitted#" + cid, "exec"), ns)
    results = {
        "utc": datetime.datetime.now(datetime.timezone.utc).isoformat(),
        "cells": selected,
        "exact_identity_results": ns["exact_identity_results"],
        "proof_checks": ns["proof_checks"],
        "rank_samples": ns["rank_samples"],
        "component_residuals": ns["component_residuals"],
        "coefficient_residuals": ns["coefficient_residuals"],
        "formula_residuals": ns["formula_residuals"],
        "independence": ns["independence"],
        "original_notebook_hash": hashlib.sha256(
            (original / "dual_feg_example_lyap.ipynb").read_bytes()
        ).hexdigest(),
    }
    (root / "replay-results.json").write_text(
        json.dumps(results, indent=2), encoding="utf-8"
    )
print("All selected submitted checks passed.")
