import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent / "helpers"))
import os
import runpy

import runtime

os.environ["JUPYTER_PATH"] = str(runtime.RUNTIME / "jupyter")
sys.argv = [
    "jupyter-nbconvert",
    "--to",
    "notebook",
    "--execute",
    str(runtime.ATTEMPT / "bppm_example_lyap.ipynb"),
    "--inplace",
    "--ExecutePreprocessor.timeout=120",
    "--ExecutePreprocessor.kernel_name=bppm-attempt",
]
runpy.run_module("nbconvert", run_name="__main__")
