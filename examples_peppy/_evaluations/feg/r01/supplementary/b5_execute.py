"""Final required nbconvert execution with attempt-owned configuration."""

import sys
from pathlib import Path

# optional notebook-generation dependency
from nbconvert.nbconvertapp import main  # ty: ignore[unresolved-import]

root = Path.cwd()
config = root / "supplementary/.runtime/final_nbconvert_config.py"
config.write_text("# Explicit empty attempt-owned nbconvert configuration.\n")
sys.argv = [
    "jupyter-nbconvert",
    "--config",
    str(config),
    "--to",
    "notebook",
    "--execute",
    "--ExecutePreprocessor.timeout=180",
    "--ExecutePreprocessor.kernel_name=attempt",
    "--output",
    "feg_example_lyap.ipynb",
    "--output-dir",
    str(root),
    str(root / "feg_example_lyap.ipynb"),
]
main()
