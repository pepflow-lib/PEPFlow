import importlib.util
import os
from pathlib import Path

# optional notebook-generation dependency
import nbformat  # ty: ignore[unresolved-import]

# optional notebook-generation dependency
from nbclient import NotebookClient  # ty: ignore[unresolved-import]

root = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location(
    "runtime", root / "supplementary/helpers/runtime.py"
)
assert spec is not None and spec.loader is not None
runtime = importlib.util.module_from_spec(spec)
spec.loader.exec_module(runtime)
runtime.configure()
os.environ["JUPYTER_PATH"] = str(runtime.RUNTIME / "jupyter")
path = root / "pgm_example_lyap.ipynb"
nb = nbformat.read(path, as_version=4)
NotebookClient(
    nb, timeout=120, kernel_name="pgm-own", resources={"metadata": {"path": str(root)}}
).execute()
nbformat.write(nb, path)
print("Clean-kernel notebook execution passed")
