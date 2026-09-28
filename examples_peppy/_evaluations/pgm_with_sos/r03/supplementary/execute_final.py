import os
import runpy
import sys
from pathlib import Path

r = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(r / "supplementary/helpers"))
from runtime import (  # ty: ignore[unresolved-import]  # local helper resolved by the notebook runtime path  # noqa: E402 - imports follow runtime or notebook setup
    configure,
)

configure()
os.environ["JUPYTER_PATH"] = str(r / "supplementary/.runtime")
sys.argv = [
    "jupyter-nbconvert",
    "--to",
    "notebook",
    "--execute",
    "--inplace",
    str(r / "pgm_example_lyap.ipynb"),
    "--ExecutePreprocessor.kernel_name=attempt",
    "--ExecutePreprocessor.timeout=300",
]
runpy.run_module("nbconvert", run_name="__main__")
