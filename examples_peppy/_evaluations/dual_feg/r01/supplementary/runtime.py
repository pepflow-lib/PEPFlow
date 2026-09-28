"""Attempt-local runtime bootstrap; imports only approved framework and own code."""

import os
import sys
from pathlib import Path

ATTEMPT = Path(__file__).resolve().parents[1]
APPROVED = ATTEMPT / "supplementary" / "approved"
RUNTIME = ATTEMPT / "supplementary" / ".runtime"
for key in (
    "OMP_NUM_THREADS",
    "OPENBLAS_NUM_THREADS",
    "MKL_NUM_THREADS",
    "NUMEXPR_NUM_THREADS",
):
    os.environ[key] = "1"
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
    path = RUNTIME / key.lower()
    path.mkdir(parents=True, exist_ok=True)
    os.environ[key] = str(path)
sys.path[:0] = [str(APPROVED), str(ATTEMPT), str(ATTEMPT / "supplementary")]
