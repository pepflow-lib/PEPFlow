"""Execute the current notebook using its pinned private kernel."""

import hashlib
import os
from pathlib import Path

# optional notebook-generation dependency
import nbformat  # ty: ignore[unresolved-import]

# optional notebook-generation dependency
from nbclient import NotebookClient  # ty: ignore[unresolved-import]

ROOT = Path(__file__).resolve().parents[1]
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
    "IPYTHONDIR",
    "MPLCONFIGDIR",
    "JUPYTER_CONFIG_DIR",
    "JUPYTER_RUNTIME_DIR",
):
    directory = ROOT / "supplementary" / ".runtime" / key.lower()
    directory.mkdir(parents=True, exist_ok=True)
    os.environ[key] = str(directory)
os.environ["JUPYTER_PATH"] = str(ROOT / "supplementary" / ".runtime" / "jupyter")
path = ROOT / "ogm_example_lyap.ipynb"
nb = nbformat.read(path, as_version=4)
NotebookClient(
    nb,
    timeout=120,
    kernel_name="ogm-worker",
    resources={"metadata": {"path": str(ROOT)}},
).execute()
for cell in nb.cells:
    if cell.cell_type == "markdown":
        assert not any(s in cell.source for s in ("\x0c", "\r", "\\(", "\\["))
    else:
        assert not any(o.output_type == "error" for o in cell.outputs)
nbformat.write(nb, path)
checklist = ROOT / "supplementary" / "ogm_example_lyap_checklist.md"
lines = checklist.read_text().splitlines()
lines[2] = "SHA-256: " + hashlib.sha256(path.read_bytes()).hexdigest()
checklist.write_text("\n".join(lines))
print("Clean-kernel execution and source math checks passed.")
