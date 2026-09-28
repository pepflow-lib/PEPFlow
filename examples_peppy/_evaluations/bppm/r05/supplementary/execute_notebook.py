"""Execute the evolving notebook in an attempt-owned fresh kernel."""

import hashlib
import json
import os
import sys
from pathlib import Path

# optional notebook-generation dependency
import nbformat as nbf  # ty: ignore[unresolved-import]

# optional notebook-generation dependency
from nbclient import NotebookClient  # ty: ignore[unresolved-import]

root = Path(__file__).resolve().parents[1]
runtime = root / "supplementary/.runtime"
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
    "TMPDIR",
    "IPYTHONDIR",
    "MPLCONFIGDIR",
    "JUPYTER_RUNTIME_DIR",
    "JUPYTER_CONFIG_DIR",
    "XDG_CACHE_HOME",
):
    path = runtime / key.lower()
    path.mkdir(parents=True, exist_ok=True)
    os.environ[key] = str(path)
kernel_dir = runtime / "jupyter/kernels/bppm-owned"
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
            "display_name": "BPPM owned kernel",
            "language": "python",
        }
    )
)
os.environ["JUPYTER_PATH"] = str(runtime / "jupyter")
dest = root / "bppm_example_lyap.ipynb"
nb = nbf.read(dest, as_version=4)
block = sys.argv[1]
remaining = []
if block == "B2N6":
    cutoff = next(
        i
        for i, c in enumerate(nb.cells)
        if c.cell_type == "markdown" and c.source.startswith("## Lyapunov partial sums")
    )
    remaining = nb.cells[cutoff:]
    nb.cells = nb.cells[:cutoff]
try:
    NotebookClient(
        nb,
        timeout=120,
        kernel_name="bppm-owned",
        resources={"metadata": {"path": str(root)}},
    ).execute()
finally:
    executed_cells = list(nb.cells)
    nb.cells = executed_cells + remaining
    nbf.write(nb, dest)
    nb.cells = executed_cells
for c in nb.cells:
    if c.cell_type == "markdown":
        assert not any(
            s in c.source for s in ("\\(", "\\)", "\\[", "\\]", "\x0c", "\r")
        )
    else:
        assert c.execution_count is not None
        assert not any(o.output_type == "error" for o in c.outputs)
        for output in c.outputs:
            if output.output_type == "stream":
                print(output.text)
evidence = {
    "block": block,
    "clean_kernel": True,
    "markdown_source_check": "passed",
    "code_cells": sum(c.cell_type == "code" for c in nb.cells),
    "notebook_sha256": hashlib.sha256(dest.read_bytes()).hexdigest(),
    "rendered_review": "omitted_by_evaluation_policy",
}
(root / f"supplementary/{block.lower()}-execution.json").write_text(
    json.dumps(evidence, indent=2)
)
