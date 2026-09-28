import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent / "helpers"))
import os
import re
import runpy

# optional notebook-generation dependency
import nbformat  # ty: ignore[unresolved-import]

# local helper resolved by the notebook runtime path
import runtime  # ty: ignore[unresolved-import]

path = runtime.ROOT / "pgm_example_lyap.ipynb"
nb = nbformat.read(path, as_version=4)
for cell in nb.cells:
    if cell.cell_type == "markdown":
        cell.source = cell.source.replace(
            "authorized assistance, awaiting certificate verification.",
            "authorized assistance; its certificate role is verified in the exact proof below.",
        )
        cell.source = cell.source.replace(
            "The arbitrary-horizon identity and Lyapunov theorem remain unproved and are carried forward explicitly.",
            "At this discovery stage the arbitrary-horizon identity and Lyapunov theorem remained open; the final symbolic sections below resolve them.",
        )
        cell.source = re.sub(r"_([A-Za-z0-9])", r"_{\1}", cell.source)
        cell.source = re.sub(r"\^([0-9])", r"^{\1}", cell.source)
        cell.source = cell.source.replace("_\\star", "_{\\star}")
        assert "\\(" not in cell.source and "\\[" not in cell.source
        assert not any(ord(c) < 32 and c not in "\n\t" for c in cell.source)
nbformat.write(nb, path)
os.environ["JUPYTER_PATH"] = str(runtime.RUNTIME / "jupyter")
sys.argv = [
    "nbconvert",
    "--to",
    "notebook",
    "--execute",
    str(path),
    "--output",
    path.name,
    "--output-dir",
    str(runtime.ROOT),
    "--ExecutePreprocessor.kernel_name=attempt-python",
    "--ExecutePreprocessor.timeout=240",
]
runpy.run_module("nbconvert", run_name="__main__")
