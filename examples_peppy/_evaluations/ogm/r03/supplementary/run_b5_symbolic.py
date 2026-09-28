"""Run the exact notebook-bound symbolic source in the approved environment."""

import json
import os
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
for key in (
    "OMP_NUM_THREADS",
    "OPENBLAS_NUM_THREADS",
    "MKL_NUM_THREADS",
    "NUMEXPR_NUM_THREADS",
):
    os.environ[key] = "1"
for key in ("TEMP", "TMP", "MPLCONFIGDIR"):
    directory = ROOT / "supplementary" / ".runtime" / key.lower()
    directory.mkdir(parents=True, exist_ok=True)
    os.environ[key] = str(directory)
sys.path[:0] = [
    str(ROOT / "supplementary" / "approved"),
    str(ROOT),
    str(ROOT / "supplementary" / "helpers"),
]
import numpy as np  # noqa: E402
import sympy as sp  # noqa: E402

import pepflow as pf  # noqa: E402

ns: dict[str, Any] = dict(np=np, pf=pf, sp=sp)
source = (ROOT / "supplementary" / "b5_symbolic_cells.py").read_text()
exec(compile(source, "b5_symbolic_cells.py", "exec"), ns)
(ROOT / "supplementary" / "b5-symbolic-results.json").write_text(
    json.dumps(ns["symbolic_results"], indent=2)
)
