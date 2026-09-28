"""Execute the evolving notebook using a new isolated pinned kernel."""

import json
import os
import sys
from pathlib import Path


def main():
    sys.path.insert(0, str(Path(__file__).resolve().parent / "helpers"))
    # local helper resolved by the notebook runtime path
    from runtime import NOTEBOOK_DIR, configure  # ty: ignore[unresolved-import]

    configure()
    # optional notebook-generation dependency
    import nbformat  # ty: ignore[unresolved-import]

    # optional notebook-generation dependency
    from nbclient import NotebookClient  # ty: ignore[unresolved-import]

    kernel_root = NOTEBOOK_DIR / "supplementary/.runtime/jupyter"
    kernel_dir = kernel_root / "kernels/ogm-isolated"
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
                "display_name": "OGM isolated",
                "language": "python",
            }
        ),
        encoding="utf-8",
    )
    os.environ["JUPYTER_PATH"] = str(kernel_root)
    path = NOTEBOOK_DIR / "ogm_example_lyap.ipynb"
    nb = nbformat.read(path, as_version=4)
    NotebookClient(
        nb,
        timeout=120,
        kernel_name="ogm-isolated",
        resources={"metadata": {"path": str(NOTEBOOK_DIR)}},
    ).execute()
    nbformat.write(nb, path)
    for i, cell in enumerate(nb.cells):
        for output in cell.get("outputs", []):
            if output.output_type == "stream":
                print(f"Cell {i}: {output.text}")
    print("Fresh-kernel execution passed.")


if __name__ == "__main__":
    main()
