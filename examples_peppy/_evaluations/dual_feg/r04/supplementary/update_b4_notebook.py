"""Execute visible basis search and reconstruction; persist state outside delivery cells."""

import hashlib
import os
from pathlib import Path

# optional notebook-generation dependency
import nbformat  # ty: ignore[unresolved-import]

# optional notebook-generation dependency
from nbclient import NotebookClient  # ty: ignore[unresolved-import]

ROOT = Path(__file__).resolve().parents[1]
runtime = ROOT / "supplementary/.runtime"
for key in (
    "OMP_NUM_THREADS",
    "OPENBLAS_NUM_THREADS",
    "MKL_NUM_THREADS",
    "NUMEXPR_NUM_THREADS",
):
    os.environ[key] = "1"
for key in (
    "TEMP",
    "TMP",
    "TMPDIR",
    "MPLCONFIGDIR",
    "IPYTHONDIR",
    "JUPYTER_RUNTIME_DIR",
    "JUPYTER_CONFIG_DIR",
    "XDG_CACHE_HOME",
):
    p = runtime / key.lower()
    p.mkdir(parents=True, exist_ok=True)
    os.environ[key] = str(p)
os.environ["JUPYTER_PATH"] = str(runtime / "jupyter")
path = ROOT / "dual_feg_example_lyap.ipynb"
nb = nbformat.read(path, as_version=4)
md, code = nbformat.v4.new_markdown_cell, nbformat.v4.new_code_cell


def source(name):
    return (ROOT / "supplementary" / name).read_text()


cells = [
    md(
        "## Identify the vectors composing the Lyapunov function\nStart from the selected $N=6$ certificate and recheck the complete B3 construction. The interior rank is four; $k=0$ and $k=N$ require separate bases."
    ),
    code(source("b4_rebuild.py")),
    md(
        "### Candidate-vector scan\nCandidates include terminal residuals, auxiliary vectors $z_k$, tagged iterates, point-to-terminal and point-to-solution gaps, framework basis vectors, and pairwise differences. Zero and duplicate vectors are removed by evaluated coordinates."
    ),
    code(source("b4_scan.py")),
    md(
        "### Selected basis pattern\nThe search fixes the terminal residual and the initial-to-terminal anchor gap, which appear throughout the terminal-star construction, and searches the remaining vectors for sparse coefficients. We then adopt a uniform basis tied directly to the recurrence; the independent reconstruction below verifies this choice."
    ),
    code(source("b4_search.py")),
    md(r"""For $1\leq k<N$, the adopted ordered basis is
$$[A(x_N),\ x_0-x_N,\ x_k-x_N,\ z_k].$$
At $k=0$ the basis is empty and $V_0=0$. At $k=N$ use $[A(x_N),x_0-x_N]$. This uniform basis avoids changing the recurrence variables to incidental pairwise differences chosen by sparsity scoring."""),
    code(source("b4_basis.py")),
    md(r"""### Coefficient matrices
The matrices use the basis order above and the convention $V_k=\sum_{i,j}C_{ij}\langle v_i,v_j\rangle$, so off-diagonal terms count twice. Function-value and constant terms are checked separately at every index."""),
    code(source("b4_coefficients.py")),
    md(
        "The following rational coefficient pattern matches the selected numerical sample. It remains a candidate until the arbitrary-horizon identities are proved."
    ),
    code(
        source("b4_formula.py")
        + "\n"
        + source("b4_structure.py")
        + "\n"
        + source("b4_verify.py")
    ),
    md(r"""### Block 4 conclusion
With $g=A(x_N)$, $a=x_0-x_N$, $b_k=x_k-x_N$, and normalized $L=1$, the candidate interior expression is
$$V_k=-\frac4N\langle g,a\rangle+\frac4{N-k}\langle g,b_k\rangle-4\langle g,z_k\rangle+\frac4{N-k}\langle b_k,z_k\rangle-2\|z_k\|^2.$$
The endpoint candidates are $V_0=0$ and $V_N=2\|g\|^2-\frac4N\langle g,a\rangle$. There are no function-value or constant terms. Every numerical partial sum reconstructs, including both endpoints. Block 5 must establish parameter scaling, exact step/base/boundary identities, and the residual theorem; neither numerical reconstruction nor the coefficient fit establishes that theorem."""),
]
for i, cell in enumerate(cells):
    cell.id = f"b4-{i:02d}"
    if cell.cell_type == "markdown":
        assert not any(c in cell.source for c in ("\x0c", "\r", "\x08"))
        assert "\\(" not in cell.source and "\\[" not in cell.source
nb.cells = [
    c for c in nb.cells if c.id not in {"b1-14", "b1-15"} and not c.id.startswith("b4-")
]
index = next(i for i, c in enumerate(nb.cells) if c.id == "b1-16")
nb.cells[index:index] = cells
nbformat.write(nb, path)
save_cell = code(source("b4_save.py"))
save_cell.id = "temporary-save-b4"
nb.cells.append(save_cell)
NotebookClient(
    nb,
    timeout=180,
    kernel_name="dual-feg-owned",
    resources={"metadata": {"path": str(ROOT)}},
).execute()
nb.cells.pop()
nbformat.write(nb, path)
for cell in cells:
    for out in cell.get("outputs", []):
        if out.output_type == "stream":
            print(out.text)
checkpath = ROOT / "supplementary/dual_feg_example_lyap_checklist.md"
lines = checkpath.read_text().splitlines()
for i, line in enumerate(lines):
    if line.startswith("Last reviewed block:"):
        lines[i] = "Last reviewed block: B4"
    elif line.startswith("SHA-256:"):
        lines[i] = "SHA-256: " + hashlib.sha256(path.read_bytes()).hexdigest()
    elif line.startswith("| 10."):
        lines[i] = (
            "| 10. special-vector identification | verified | b4-00 through b4-07 | Candidate scan and actual sparse search executed; uniform basis independently verified at every index. |"
        )
    elif line.startswith("| 11."):
        lines[i] = (
            "| 11. coefficient extraction and closed-form V_k | pending | b4-08 through b4-12 | All numerical coefficients and full-component reconstructions pass; candidate formula matches N=6; exact formula proof remains B5. |"
        )
checkpath.write_text("\n".join(lines), encoding="utf-8")
print("B4 numerical structure complete; exact proof remains pending.")
