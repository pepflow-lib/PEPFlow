"""Execute the main notebook in an attempt-owned fresh isolated kernel."""
import json
import os
import sys
from pathlib import Path

root = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(root / "supplementary" / "h"))


def main():
    from runtime import configure
    configure()
    import nbformat
    from nbclient import NotebookClient
    directory = root / "supplementary/.runtime/jupyter/kernels/pgm-own"
    directory.mkdir(parents=True, exist_ok=True)
    (directory / "kernel.json").write_text(json.dumps({
        "argv": [sys.executable, "-I", "-B", "-m", "ipykernel_launcher",
                 "-f", "{connection_file}"],
        "display_name": "PGM attempt", "language": "python"
    }))
    os.environ["JUPYTER_PATH"] = str(directory.parent.parent)
    path = root / "pgm_example_lyap.ipynb"
    nb = nbformat.read(path, as_version=4)
    NotebookClient(nb, timeout=120, kernel_name="pgm-own",
                   resources={"metadata": {"path": str(root)}}).execute()
    nbformat.write(nb, path)
    print(json.dumps({"status": "passed", "code_cells": sum(
        cell.cell_type == "code" for cell in nb.cells)}))


if __name__ == "__main__":
    main()


