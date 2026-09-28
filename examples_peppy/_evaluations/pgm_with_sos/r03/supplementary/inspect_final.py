import json
from pathlib import Path

# optional notebook-generation dependency
import nbformat  # ty: ignore[unresolved-import]

r = Path(__file__).resolve().parents[1]
n = nbformat.read(r / "pgm_example_lyap.ipynb", as_version=4)
for i, c in enumerate(n.cells):
    print(i, c.cell_type, c.source.splitlines()[0][:100])
    if i >= 38:
        for o in c.get("outputs", []):
            t = o.get("text", o.get("data", {}).get("text/plain", ""))
            print(str(t)[:1600])
print("TOP", n.cells[2].source, n.cells[3].source)
b = json.loads((r / "state/pgm_b4.json").read_text())
print("STRUCTURE", json.dumps(b["expression_structure"], indent=2))
