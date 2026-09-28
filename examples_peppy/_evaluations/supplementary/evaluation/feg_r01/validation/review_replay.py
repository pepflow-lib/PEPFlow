import json
import os
import sys
from contextlib import redirect_stderr, redirect_stdout
from datetime import datetime, timezone
from pathlib import Path

root = Path.cwd().resolve()
runtime = root / "review_runtime"
runtime.mkdir(exist_ok=True)
for key in (
    "TEMP",
    "TMP",
    "TMPDIR",
    "MPLCONFIGDIR",
    "XDG_CACHE_HOME",
    "JUPYTER_CONFIG_DIR",
    "JUPYTER_DATA_DIR",
    "JUPYTER_RUNTIME_DIR",
    "IPYTHONDIR",
):
    target = runtime / key
    target.mkdir(exist_ok=True)
    os.environ[key] = str(target)
os.environ["MPLBACKEND"] = "Agg"
os.environ["PYTHONDONTWRITEBYTECODE"] = "1"
sys.path[:0] = [
    str(root / "supplementary/approved"),
    str(root),
    str(root / "supplementary/helpers"),
]
import matplotlib.pyplot as plt  # noqa: E402 -- Initialize paths and runtime environment before importing.

plt.show = lambda *args, **kwargs: plt.close("all")  # ty: ignore[invalid-assignment]  # Review replay replaces interactive plotting with figure cleanup.
nb = json.loads((root / "feg_example_lyap.ipynb").read_text(encoding="utf-8"))
result = {
    "started_at": datetime.now(timezone.utc).isoformat(),
    "mode": "fresh isolated Python process; notebook source cells replayed sequentially; plot display suppressed; no new solves",
    "cells": [],
}
with (
    (root / "review-replay.log").open("w", encoding="utf-8") as log,
    redirect_stdout(log),
    redirect_stderr(log),
):
    scope = {"__name__": "__main__"}
    for cell in nb["cells"]:
        if cell["cell_type"] != "code":
            continue
        print("\nCELL", cell["id"], flush=True)
        exec(compile("".join(cell["source"]), "<" + cell["id"] + ">", "exec"), scope)
        result["cells"].append(cell["id"])
    result["selected_certificate_checks"] = scope["checks"]
    result["selected_ranks"] = scope["ranks"]
    result["coefficient_residuals"] = scope["coefficient_residuals"]
    result["component_residuals"] = scope["component_residuals"]
    result["exact_identities"] = {
        key: scope[key]
        for key in ("step_verified", "base_verified", "boundary_verified")
    }
    scope["b2"] = json.loads((root / "supplementary/sample-N4/feg_b2.json").read_text())
    scope["N_int"] = 4
    for index in (19, 20, 21):
        cell = nb["cells"][index]
        print("\nN4 REPLAY", cell["id"], flush=True)
        exec(compile("".join(cell["source"]), "<N4-" + cell["id"] + ">", "exec"), scope)
    result["N4_certificate_checks"] = scope["checks"]
    result["N4_ranks"] = scope["ranks"]
    result["N4_singular_values"] = scope["singular_values"]
    result["stopped_at"] = datetime.now(timezone.utc).isoformat()
(root / "review-replay.json").write_text(json.dumps(result, indent=2), encoding="utf-8")
print(json.dumps(result, indent=2))
