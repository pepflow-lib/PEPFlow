import json
from pathlib import Path

# optional notebook-generation dependency
import nbformat  # ty: ignore[unresolved-import]

root = Path.cwd()
p = root / "dual_feg_example_lyap.ipynb"
nb = nbformat.read(p, as_version=4)
s = json.loads((root / "state/dual_feg_b3.json").read_text())
nb.cells[21].source = s["certificate_check_code"]
old = nb.cells[23].source
suffix = old[old.index("for k,rank in enumerate(ranks):") :]
nb.cells[23].source = s["grouping_code"] + "\n" + suffix
nbformat.write(nb, p)
