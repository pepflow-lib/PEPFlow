"""Attempt-owned execution environment and explicit frozen solver policy."""
import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
APPROVED = ROOT / "supplementary" / "approved"
RUNTIME = ROOT / "supplementary" / ".runtime"
for name in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS", "NUMEXPR_NUM_THREADS"):
    os.environ[name] = "1"
for name in ("TEMP", "TMP", "TMPDIR", "MPLCONFIGDIR", "IPYTHONDIR", "JUPYTER_RUNTIME_DIR", "JUPYTER_CONFIG_DIR"):
    directory = RUNTIME / name.lower()
    directory.mkdir(parents=True, exist_ok=True)
    os.environ[name] = str(directory)
sys.path[:0] = [str(APPROVED), str(ROOT), str(ROOT / "supplementary" / "helpers")]

