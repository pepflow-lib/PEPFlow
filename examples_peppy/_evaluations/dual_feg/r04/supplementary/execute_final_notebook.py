"""Final required nbconvert execution with pinned isolated kernel and private caches."""

import os
import runpy
import sys
from pathlib import Path

root = Path(__file__).resolve().parents[1]
runtime = root / "supplementary/.runtime"
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
    p = runtime / key.lower()
    p.mkdir(parents=True, exist_ok=True)
    os.environ[key] = str(p)
os.environ["JUPYTER_PATH"] = str(runtime / "jupyter")
os.environ["JUPYTER_NO_CONFIG"] = "1"
config = runtime / "nbconvert_config.py"
config.write_text("# Explicit empty attempt-owned configuration.\n")
sys.argv = [
    "jupyter-nbconvert",
    "--to",
    "notebook",
    "--execute",
    "--inplace",
    "--ExecutePreprocessor.timeout=180",
    "--ExecutePreprocessor.kernel_name=dual-feg-owned",
    "--config",
    str(config),
    str(root / "dual_feg_example_lyap.ipynb"),
]
print("Executing:", sys.argv, flush=True)
runpy.run_module("nbconvert", run_name="__main__")
