import importlib.util
import os
import runpy
import sys
from pathlib import Path

root = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location(
    "runtime", root / "supplementary/helpers/runtime.py"
)
assert spec is not None and spec.loader is not None
runtime = importlib.util.module_from_spec(spec)
spec.loader.exec_module(runtime)
os.environ["JUPYTER_PATH"] = str(root / "supplementary/.runtime")
os.environ["JUPYTER_NO_CONFIG"] = "1"
sys.argv = [
    "jupyter-nbconvert",
    "--to",
    "notebook",
    "--execute",
    str(root / "dual_feg_example_lyap.ipynb"),
    "--inplace",
    "--ExecutePreprocessor.kernel_name=attempt-python",
    "--ExecutePreprocessor.timeout=180",
]
runpy.run_module("nbconvert", run_name="__main__")
