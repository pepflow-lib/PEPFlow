import runpy
from pathlib import Path

runpy.run_path(str(Path(__file__).with_name("runtime.py")))
import os  # noqa: E402 - imports follow runtime or notebook setup

import nbformat  # ty: ignore[unresolved-import]  # optional notebook-generation dependency  # noqa: E402 - imports follow runtime or notebook setup
from nbclient import (  # ty: ignore[unresolved-import]  # optional notebook-generation dependency  # noqa: E402 - imports follow runtime or notebook setup
    NotebookClient,
)

root = Path.cwd()
os.environ["JUPYTER_PATH"] = str(root / "supplementary/.runtime/jupyter")
p = root / "pgm_example_lyap.ipynb"
book = nbformat.read(p, as_version=4)
for c in book.cells:
    if c.cell_type == "markdown":
        c.source = c.source.replace("\\\\", "\\")
        assert "\\(" not in c.source and "\\[" not in c.source
        assert not any(ord(x) < 32 and x not in "\n\t" for x in c.source)
NotebookClient(
    book,
    timeout=120,
    kernel_name="pgm-own",
    resources={"metadata": {"path": str(root)}},
).execute()
nbformat.write(book, p)
print("Fresh kernel notebook passed.")
