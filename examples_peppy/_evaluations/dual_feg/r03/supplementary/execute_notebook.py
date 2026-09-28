"""Execute the evolving notebook in the attempt-owned pinned kernel."""

import hashlib
import json
import os
from pathlib import Path

# optional notebook-generation dependency
import nbformat  # ty: ignore[unresolved-import]

# optional notebook-generation dependency
from nbclient import NotebookClient  # ty: ignore[unresolved-import]

ROOT = Path(__file__).resolve().parents[1]


def execute(block):
    runtime = ROOT / "supplementary/.runtime"
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
        "XDG_CACHE_HOME",
    ]:
        dest = runtime / key.lower()
        dest.mkdir(parents=True, exist_ok=True)
        os.environ[key] = str(dest)
    os.environ["JUPYTER_PATH"] = str(runtime / "jupyter")
    os.environ["JUPYTER_NO_CONFIG"] = "1"
    destination = ROOT / "dual_feg_example_lyap.ipynb"
    nb = nbformat.read(destination, as_version=4)
    NotebookClient(
        nb,
        timeout=180,
        kernel_name="attempt-kernel",
        resources={"metadata": {"path": str(ROOT)}},
    ).execute()
    nbformat.write(nb, destination)
    streams = []
    for i, cell in enumerate(nb.cells):
        if cell.cell_type == "markdown":
            assert not any(
                c in cell.source for c in ["\x0c", "\r", "\\(", "\\)", "\\[", "\\]"]
            )
        for output in cell.get("outputs", []):
            assert output.output_type != "error"
            if output.output_type == "stream":
                streams.append(dict(cell=i, text=output.text))
    evidence = dict(
        block=block,
        status="passed",
        kernel="attempt-kernel",
        plot_count=sum(
            "image/png" in o.get("data", {})
            for c in nb.cells
            for o in c.get("outputs", [])
        ),
        sha256=hashlib.sha256(destination.read_bytes()).hexdigest(),
        streams=streams,
        presentation_policy="evaluation-ancillary-v1",
        rendered_review=False,
    )
    (ROOT / f"supplementary/{block.lower()}-notebook-execution.json").write_text(
        json.dumps(evidence, indent=2)
    )
    print(json.dumps(evidence, indent=2))
    return nb, evidence
