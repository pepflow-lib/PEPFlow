"""Attempt-local runtime configuration, applied before numerical imports."""

import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
APPROVED = ROOT / "supplementary" / "approved"
RUNTIME = ROOT / "supplementary" / ".runtime"
for name in (
    "OMP_NUM_THREADS",
    "OPENBLAS_NUM_THREADS",
    "MKL_NUM_THREADS",
    "NUMEXPR_NUM_THREADS",
):
    os.environ[name] = "1"
for name in (
    "TEMP",
    "TMP",
    "TMPDIR",
    "IPYTHONDIR",
    "MPLCONFIGDIR",
    "JUPYTER_RUNTIME_DIR",
    "JUPYTER_CONFIG_DIR",
    "XDG_CACHE_HOME",
):
    location = RUNTIME / name.lower()
    location.mkdir(parents=True, exist_ok=True)
    os.environ[name] = str(location)
sys.path[:0] = [str(APPROVED), str(ROOT), str(ROOT / "supplementary")]
