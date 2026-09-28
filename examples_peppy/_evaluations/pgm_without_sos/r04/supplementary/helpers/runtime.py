"""Attempt-owned isolation/runtime configuration."""

import os
import sys
from pathlib import Path

ATTEMPT = Path(__file__).resolve().parents[2]
APPROVED = ATTEMPT / "supplementary" / "approved"
RUNTIME = ATTEMPT / "supplementary" / ".runtime"
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
    directory = RUNTIME / name.lower()
    directory.mkdir(parents=True, exist_ok=True)
    os.environ[name] = str(directory)
sys.path[:0] = [str(APPROVED), str(ATTEMPT), str(ATTEMPT / "supplementary" / "helpers")]
