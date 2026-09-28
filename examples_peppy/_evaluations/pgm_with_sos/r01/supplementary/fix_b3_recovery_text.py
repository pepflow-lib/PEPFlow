import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent / "helpers"))
import hashlib
import re

# optional notebook-generation dependency
import nbformat as nb  # ty: ignore[unresolved-import]
import runtime

root = runtime.ATTEMPT
path = root / "pgm_example_lyap.ipynb"
book = nb.read(path, as_version=4)
s = book.cells[13].source.replace(
    r"\sum_{i=1}^{k}\sum_{r=1}^{3}c_{r,i}\|u_{r,i}\|^2", r"\sum_{i=1}^{k}Q_i"
)
s = s.replace(
    r"Nonnegative multipliers and square coefficients give $V_{k+1}\le V_k$ in the exact target identity.",
    r"Nonnegative multipliers and PSD step blocks give the intended nonincreasing direction. Block PSD is checked numerically here; exact signs remain a B5 obligation.",
)
book.cells[13].source = s
nb.write(book, path)
p = root / "supplementary/pgm_example_lyap_checklist.md"
t = p.read_text()
t = re.sub(
    r"SHA-256: [a-f0-9]+",
    "SHA-256: " + hashlib.sha256(path.read_bytes()).hexdigest(),
    t,
)
t = t.replace(
    "| failed | 15 | Candidate scan failed required span tolerance at k=5 and k=6; recovery returns to B3. |",
    "| pending | 15 | B3 slack allocation recovered; B4 search and all-index reconstruction must be rerun. |",
)
p.write_text(t)
