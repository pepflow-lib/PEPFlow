import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent / "helpers"))
import re

# optional notebook-generation dependency
import nbformat  # ty: ignore[unresolved-import]
import runtime

root = runtime.ATTEMPT
replacements = {
    "; b_alg=": "\nb_alg=",
    "; bn_alg=": "\nbn_alg=",
    "; b_step =": "\nb_step =",
    "; b_end =": "\nb_end =",
}
for name in ("b5_cells.py", "b5_coefficient_derivation.py"):
    path = root / "supplementary" / name
    text = path.read_text(encoding="utf-8-sig")
    for old, new in replacements.items():
        text = text.replace(old, new)
    path.write_text(text)
path = root / "pgm_example_lyap.ipynb"
nb = nbformat.read(path, as_version=4)


def normalize_math(match):
    return re.sub(
        r"_(\\[A-Za-z]+|[A-Za-z0-9])", lambda m: "_{" + m.group(1) + "}", match.group(0)
    )


for cell in nb.cells:
    if cell.cell_type == "code":
        for old, new in replacements.items():
            cell.source = cell.source.replace(old, new)
    else:
        cell.source = re.sub(
            r"\$\$[\s\S]*?\$\$|\$[^$]*?\$", normalize_math, cell.source
        )
        assert "\\(" not in cell.source and "\\[" not in cell.source
        assert not any(ord(c) < 32 and c not in "\n\t" for c in cell.source)
nbformat.write(nb, path)
print("Four statement-separation fixes applied; Markdown source checked.")
