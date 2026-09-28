import hashlib
import json
import os
from pathlib import Path

root = Path.cwd()
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
    p = root / "review-runtime" / name.lower()
    p.mkdir(parents=True, exist_ok=True)
    os.environ[name] = str(p)
for name in (
    "OMP_NUM_THREADS",
    "OPENBLAS_NUM_THREADS",
    "MKL_NUM_THREADS",
    "NUMEXPR_NUM_THREADS",
):
    os.environ[name] = "1"
os.environ["MPLBACKEND"] = "Agg"
nb = json.loads((root / "pgm_example_lyap.ipynb").read_text(encoding="utf-8"))
print(
    "Notebook sha256",
    hashlib.sha256((root / "pgm_example_lyap.ipynb").read_bytes()).hexdigest(),
    flush=True,
)
g = {}
for j, c in enumerate(nb["cells"]):
    if c["cell_type"] != "code" or j in (9, 24):
        continue
    print("REPLAY CELL", j, c["id"], flush=True)
    exec(compile("".join(c["source"]), f"notebook-cell-{c['id']}", "exec"), g)
print("ALL SELECTED CELLS PASSED", flush=True)
