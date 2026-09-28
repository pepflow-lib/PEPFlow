"""Attempt-local runtime configuration, without repository-root imports."""
import os
import sys
from pathlib import Path


def configure():
    attempt = Path(__file__).resolve().parents[2]
    approved = attempt / "supplementary" / "approved"
    for key in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS", "NUMEXPR_NUM_THREADS"):
        os.environ[key] = "1"
    for key in ("TEMP", "TMP", "TMPDIR", "IPYTHONDIR", "MPLCONFIGDIR", "JUPYTER_RUNTIME_DIR", "JUPYTER_CONFIG_DIR", "XDG_CACHE_HOME"):
        path = attempt / "supplementary" / ".runtime" / key.lower()
        path.mkdir(parents=True, exist_ok=True)
        os.environ[key] = str(path)
    for path in (approved, attempt / "supplementary" / "helpers", attempt):
        if str(path) not in sys.path:
            sys.path.insert(0, str(path))
    return attempt, approved

