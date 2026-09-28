import json
from pathlib import Path

path = Path("feg_example_lyap.ipynb")
nb = json.loads(path.read_text())
for cell in nb["cells"]:
    if cell["cell_type"] == "code":
        source = "".join(cell["source"])
        if "unknown_symbols={name:sp.Function(name)" in source:
            source = Path("supplementary/b5_derivation.py").read_text(
                encoding="utf-8-sig"
            )
            cell["source"] = source.splitlines(keepends=True)
path.write_text(json.dumps(nb, indent=1, ensure_ascii=False) + "\n")
