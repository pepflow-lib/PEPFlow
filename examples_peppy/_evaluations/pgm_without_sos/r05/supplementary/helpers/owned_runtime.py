"""Attempt-owned execution bootstrap; no mathematical content."""

import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
APPROVED = ROOT / "supplementary" / "approved"


def configure():
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
        "MPLCONFIGDIR",
        "IPYTHONDIR",
        "JUPYTER_RUNTIME_DIR",
        "JUPYTER_CONFIG_DIR",
        "XDG_CACHE_HOME",
    ):
        location = ROOT / "supplementary" / ".runtime" / key.lower()
        location.mkdir(parents=True, exist_ok=True)
        os.environ[key] = str(location)
    sys.path[:0] = [str(APPROVED), str(ROOT), str(ROOT / "supplementary" / "helpers")]
