import sys
from pathlib import Path

root = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(root / "supplementary/helpers"))
import os  # noqa: E402 - imports follow runtime or notebook setup

import nbformat  # ty: ignore[unresolved-import]  # optional notebook-generation dependency  # noqa: E402 - imports follow runtime or notebook setup
import runtime  # noqa: E402 - imports follow runtime or notebook setup
from nbclient import (  # ty: ignore[unresolved-import]  # optional notebook-generation dependency  # noqa: E402 - imports follow runtime or notebook setup
    NotebookClient,
)

path = root / "ogm_example_lyap.ipynb"
nb = nbformat.read(path, as_version=4)
nb.cells[18].source = nb.cells[18].source.replace(
    "from pepflow.utils import Comparator\n", ""
)
nbformat.write(nb, path)
os.environ["JUPYTER_PATH"] = str(runtime.RUNTIME / "jupyter")
NotebookClient(
    nb,
    timeout=120,
    kernel_name="ogm-attempt",
    resources={"metadata": {"path": str(root)}},
).execute()
nbformat.write(nb, path)
print("Notebook fresh-kernel execution passed.")
