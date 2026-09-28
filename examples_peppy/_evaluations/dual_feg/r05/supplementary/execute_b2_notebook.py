"""Build the initial notebook and execute in the private kernel."""

import json
import os
import sys
from pathlib import Path

# optional notebook-generation dependency
import nbformat  # ty: ignore[unresolved-import]

# optional notebook-generation dependency
from nbclient import NotebookClient  # ty: ignore[unresolved-import]

ROOT = Path(__file__).resolve().parents[1]
SUP = ROOT / "supplementary"
RT = SUP / ".runtime"
for key in [
    "OMP_NUM_THREADS",
    "OPENBLAS_NUM_THREADS",
    "MKL_NUM_THREADS",
    "NUMEXPR_NUM_THREADS",
]:
    os.environ[key] = "1"
for key in [
    "TEMP",
    "TMP",
    "TMPDIR",
    "IPYTHONDIR",
    "MPLCONFIGDIR",
    "JUPYTER_RUNTIME_DIR",
    "JUPYTER_CONFIG_DIR",
]:
    path = RT / key.lower()
    path.mkdir(parents=True, exist_ok=True)
    os.environ[key] = str(path)
kernels = RT / "jupyter" / "kernels" / "attempt"
kernels.mkdir(parents=True, exist_ok=True)
(kernels / "kernel.json").write_text(
    json.dumps(
        {
            "argv": [
                sys.executable,
                "-I",
                "-B",
                "-m",
                "ipykernel_launcher",
                "-f",
                "{connection_file}",
            ],
            "display_name": "Attempt Python",
            "language": "python",
        }
    )
)
os.environ["JUPYTER_PATH"] = str(RT / "jupyter")
path = ROOT / "dual_feg_example_lyap.ipynb"
nb = nbformat.read(path, as_version=4)
NotebookClient(
    nb, timeout=180, kernel_name="attempt", resources={"metadata": {"path": str(ROOT)}}
).execute()
nbformat.write(nb, path)
summary = []
for i, cell in enumerate(nb.cells):
    if cell.cell_type == "markdown":
        assert "\\(" not in cell.source and "\\[" not in cell.source
        assert not any(ord(ch) < 32 and ch not in "\n\t" for ch in cell.source)
    outputs = [
        o.get("text", "") for o in cell.get("outputs", []) if o.output_type == "stream"
    ]
    summary.append(
        {
            "cell": i,
            "id": cell.id,
            "outputs": outputs,
            "has_plot": any(
                "image/png" in o.get("data", {}) for o in cell.get("outputs", [])
            ),
        }
    )
(SUP / "b2-notebook-inspection.json").write_text(json.dumps(summary, indent=2))
print(json.dumps(summary[12:], indent=2))
