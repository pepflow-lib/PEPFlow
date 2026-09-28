from pathlib import Path

# optional notebook-generation dependency
import nbformat  # ty: ignore[unresolved-import]

root = Path(__file__).resolve().parents[1]
path = root / "pgm_example_lyap.ipynb"
nb = nbformat.read(path, as_version=4)
cell = next(
    c
    for c in nb.cells
    if c.cell_type == "markdown" and c.source.startswith("## Partial-sum Lyapunov")
)
cell.source += r"""

**Numerical decomposition recovery.** The unaligned supplied pieces had a small reconstruction error that failed the later terminal basis gate. Assigning the full discrepancy to the final piece produced an indefinite remainder and was rejected. Instead, write the supplied factor matrix as $U$ and use the positive square root $S^{1/2}$ of this same saved numerical slack. The rectangular polar factor $Q$ of $US^{1/2}$ has orthonormal columns; set $W=QS^{1/2}$. Then $W^TW=S$. Each row of $W$ defines a nonnegative square, kept under the same family/step labels. The code checks this identity directly before grouping. This numerical alignment is a finite-sample construction; the original supplied analytic SOS remains a candidate for the eventual exact proof. Certificate components are unchanged. The prior grouping and rejected remainder evidence are archived in supplementary files."""
nbformat.write(nb, path)
