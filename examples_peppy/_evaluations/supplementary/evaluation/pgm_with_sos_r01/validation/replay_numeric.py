"""Replay inspected read-only notebook cells. Skip authoring, plots, runtime helpers."""

from typing import Any

# Keep typing metadata separate from the recorded import sequence.
# isort: split


import contextlib
import hashlib
import json
import os
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ORIGINAL = HERE.parents[3] / "pgm_with_sos" / "r01"
for key in (
    "TEMP",
    "TMP",
    "TMPDIR",
    "IPYTHONDIR",
    "MPLCONFIGDIR",
    "JUPYTER_RUNTIME_DIR",
    "JUPYTER_CONFIG_DIR",
    "XDG_CACHE_HOME",
):
    path = HERE / "runtime" / key.lower()
    path.mkdir(parents=True, exist_ok=True)
    os.environ[key] = str(path)
for key in (
    "OMP_NUM_THREADS",
    "OPENBLAS_NUM_THREADS",
    "MKL_NUM_THREADS",
    "NUMEXPR_NUM_THREADS",
):
    os.environ[key] = "1"
sys.path.insert(0, str(ORIGINAL / "supplementary" / "approved"))
import numpy as np  # noqa: E402 -- Initialize paths and runtime environment before importing.

import pepflow as pf  # noqa: E402 -- Initialize paths and runtime environment before importing.

nb = json.loads((ORIGINAL / "pgm_example_lyap.ipynb").read_text(encoding="utf-8"))
env: dict[str, Any] = dict(
    notebook_dir=ORIGINAL, pf=pf, np=np, Path=Path, json=json, hashlib=hashlib
)
selected = [5, 6, 10, 12, 13, 16, 18, 25, 27]
with (
    (HERE / "numeric-replay.log").open("w", encoding="utf-8") as log,
    contextlib.redirect_stdout(log),
):
    for index in selected:
        print("REPLAY CELL", index, nb["cells"][index]["id"], flush=True)
        exec(
            compile(
                "".join(nb["cells"][index]["source"]), f"notebook-cell-{index}", "exec"
            ),
            env,
        )
    strict = {}
    for k in range(env["N"] + 1):
        diff = env["pm"].eval_scalar(env["V_k_structure"](k) - env["lyap"][k])
        strict[str(k)] = {
            key: env["maxabs"](value)
            for key, value in [
                ("gram", diff.inner_prod_coords),
                ("function", diff.func_coords),
                ("offset", diff.offset),
            ]
        }
        assert max(strict[str(k)].values()) <= 1e-5
    result = {
        "replayed_cells": selected,
        "certificate_id": env["b2"]["certificate_id"],
        "rank_profile": env["ranks"],
        "coverage_residual": env["coverage_residual"],
        "increment_residuals": env["increment_residuals"],
        "strict_component_atol": 1e-5,
        "component_residuals": strict,
        "saved_S_identity_residuals": {
            key: env["maxabs"](value)
            for key, value in [
                ("gram", env["saved_identity"].inner_prod_coords),
                ("function", env["saved_identity"].func_coords),
                ("offset", env["saved_identity"].offset),
            ]
        },
        "Q_min_eigenvalues": [
            float(np.linalg.eigvalsh(np.asarray(Q)).min())
            for Q in env["allocation"]["Q"]
        ],
        "S_piece_reconstruction": env["maxabs"](env["piece_diff"].inner_prod_coords),
    }
(HERE / "numeric-results.json").write_text(
    json.dumps(result, indent=2), encoding="utf-8"
)
print(json.dumps(result, indent=2))
