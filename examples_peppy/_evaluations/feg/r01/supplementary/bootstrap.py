"""Run this attempt's scripts with approved imports and private caches."""
import os
from pathlib import Path
import runpy
import sys

ROOT = Path(__file__).resolve().parents[1]
APPROVED = ROOT / "supplementary" / "approved"
for key in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS", "NUMEXPR_NUM_THREADS"):
    os.environ[key] = "1"
for key in ("TEMP", "TMP", "TMPDIR", "XDG_CACHE_HOME", "IPYTHONDIR", "MPLCONFIGDIR", "JUPYTER_RUNTIME_DIR", "JUPYTER_CONFIG_DIR", "JUPYTER_PATH"):
    value = ROOT / "supplementary" / ".runtime" / key.lower()
    value.mkdir(parents=True, exist_ok=True)
    os.environ[key] = str(value)
sys.path[:0] = [str(APPROVED), str(ROOT), str(ROOT / "supplementary" / "helpers")]
os.chdir(ROOT)
target = Path(sys.argv[1]).resolve()
target.relative_to(ROOT)
sys.argv = sys.argv[1:]
runpy.run_path(str(target), run_name="__main__")

