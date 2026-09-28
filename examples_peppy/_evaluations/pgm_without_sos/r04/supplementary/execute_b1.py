import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent / "helpers"))
import json

# optional notebook-generation dependency
import nbformat as nbf  # ty: ignore[unresolved-import]
import runtime

# optional notebook-generation dependency
from nbclient import NotebookClient  # ty: ignore[unresolved-import]

root = runtime.ATTEMPT
path = root / "pgm_example_lyap.ipynb"
nb = nbf.read(path, as_version=4)
cell = nb.cells[2]
bootstrap, imports = cell.source.split("import runtime", 1)
cell.source = bootstrap.strip()
nb.cells.insert(
    3,
    nbf.v4.new_code_cell(
        "import runtime"
        + imports.replace(
            "assert Path(pf.__file__)",
            "assert runtime.ATTEMPT == notebook_dir\nassert Path(pf.__file__)",
        )
    ),
)
kernels = runtime.RUNTIME / "jupyter" / "kernels" / "pgm-attempt"
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
            "display_name": "Pinned Python",
            "language": "python",
        }
    )
)
import os  # noqa: E402 - imports follow runtime or notebook setup

os.environ["JUPYTER_PATH"] = str(runtime.RUNTIME / "jupyter")
nbf.write(nb, path)
NotebookClient(
    nb,
    timeout=120,
    kernel_name="pgm-attempt",
    resources={"metadata": {"path": str(root)}},
).execute()
nbf.write(nb, path)
for i, cell in enumerate(nb.cells):
    if cell.cell_type == "markdown":
        assert "\\(" not in cell.source and "\\[" not in cell.source
        assert not any(ord(c) < 32 and c not in "\n\t" for c in cell.source)
    for output in cell.get("outputs", []):
        if output.output_type == "error":
            raise RuntimeError(output)
        if output.output_type == "stream":
            print(i, output.text)
plot_outputs = nb.cells[9].get("outputs", [])
assert any("image/png" in o.get("data", {}) for o in plot_outputs)
print("Fresh kernel passed; plot output present; markdown delimiters checked.")
