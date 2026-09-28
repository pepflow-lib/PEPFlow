"""Attempt-local notebook execution configuration; no mathematical content."""
import hashlib
import json
import os
from pathlib import Path


def execute_notebook(path: Path, block: str):
    root = path.parent
    runtime = root / "supplementary/.runtime"
    for key in ["OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS", "NUMEXPR_NUM_THREADS"]:
        os.environ[key] = "1"
    for key in ["TEMP", "TMP", "IPYTHONDIR", "JUPYTER_RUNTIME_DIR", "JUPYTER_CONFIG_DIR", "MPLCONFIGDIR", "XDG_CACHE_HOME"]:
        location = runtime / key.lower()
        location.mkdir(parents=True, exist_ok=True)
        os.environ[key] = str(location)
    os.environ["JUPYTER_PATH"] = str(runtime / "jupyter")
    import nbformat as nbf
    from nbclient import NotebookClient
    notebook = nbf.read(path, as_version=4)
    NotebookClient(notebook, timeout=120, kernel_name="ogm-owned", resources={"metadata":{"path":str(root)}}).execute()
    nbf.write(notebook,path)
    for cell in notebook.cells:
        if cell.cell_type == "markdown":
            assert not any(char in cell.source for char in ["\x0c", "\r", "\\(", "\\)", "\\[", "\\]"])
        if cell.id.startswith(block+"-"):
            for output in cell.get("outputs",[]):
                if output.get("output_type") == "stream":
                    print(output["text"])
    print(json.dumps({"clean_kernel_execution":"passed","sha256":hashlib.sha256(path.read_bytes()).hexdigest()}))
