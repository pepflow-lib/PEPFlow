import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent / "helpers"))
import json

# optional notebook-generation dependency
import nbformat as nbf  # ty: ignore[unresolved-import]

# local helper resolved by the notebook runtime path
from runtime import ATTEMPT  # ty: ignore[unresolved-import]

path = ATTEMPT / "bppm_example_lyap.ipynb"
nb = nbf.read(path, as_version=4)
start = next(
    i
    for i, c in enumerate(nb.cells)
    if c.cell_type == "markdown" and c.source.startswith("## Identify the vectors")
)
end = next(
    i
    for i, c in enumerate(nb.cells)
    if c.cell_type == "markdown" and c.source.startswith("## Symbolic step")
)
content = json.loads((ATTEMPT / "supplementary/b4_cells.json").read_text())
nb.cells[start:end] = [
    nbf.v4.new_code_cell(c["source"])
    if c["kind"] == "code"
    else nbf.v4.new_markdown_cell(c["source"])
    for c in content
]
nbf.write(nb, path)
print("Updated notebook through B4.")
