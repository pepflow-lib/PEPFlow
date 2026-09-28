import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent / "helpers"))
import json
import os

# optional notebook-generation dependency
import nbformat  # ty: ignore[unresolved-import]

# optional notebook-generation dependency
from nbclient import NotebookClient  # ty: ignore[unresolved-import]

# local helper resolved by the notebook runtime path
from runtime import ATTEMPT, RUNTIME  # ty: ignore[unresolved-import]

kernel_dir = RUNTIME / "jupyter" / "kernels" / "bppm-r02"
kernel_dir.mkdir(parents=True, exist_ok=True)
(kernel_dir / "kernel.json").write_text(
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
            "display_name": "BPPM r02 isolated",
            "language": "python",
        }
    )
)
os.environ["JUPYTER_PATH"] = str(RUNTIME / "jupyter")
path = ATTEMPT / "bppm_example_lyap.ipynb"
nb = nbformat.read(path, as_version=4)
NotebookClient(
    nb,
    timeout=120,
    kernel_name="bppm-r02",
    resources={"metadata": {"path": str(ATTEMPT)}},
).execute()
nbformat.write(nb, path)
summary = []
for i, cell in enumerate(nb.cells):
    if cell.cell_type == "markdown":
        assert not any(c in cell.source for c in ("\x0c", "\r", "\x08"))
        assert "\\(" not in cell.source and "\\[" not in cell.source
    else:
        outputs = cell.get("outputs", [])
        summary.append(
            {
                "cell": i,
                "execution_count": cell.execution_count,
                "output_types": [o.output_type for o in outputs],
                "text": [
                    o.get("text", "") for o in outputs if o.output_type == "stream"
                ],
                "has_plot": any("image/png" in o.get("data", {}) for o in outputs),
            }
        )
(
    ATTEMPT
    / (
        "supplementary/"
        + (sys.argv[1] if len(sys.argv) > 1 else "b1")
        + "-notebook-execution.json"
    )
).write_text(json.dumps(summary, indent=2))
print(json.dumps(summary, indent=2))
