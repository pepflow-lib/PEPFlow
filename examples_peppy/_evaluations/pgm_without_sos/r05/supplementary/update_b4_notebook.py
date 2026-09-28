import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent / "helpers"))
# local helper resolved by the notebook runtime path
from owned_runtime import ROOT, configure  # ty: ignore[unresolved-import]

configure()
import hashlib  # noqa: E402 - imports follow runtime or notebook setup
import os  # noqa: E402 - imports follow runtime or notebook setup

import nbformat  # ty: ignore[unresolved-import]  # optional notebook-generation dependency  # noqa: E402 - imports follow runtime or notebook setup
from nbclient import (  # ty: ignore[unresolved-import]  # optional notebook-generation dependency  # noqa: E402 - imports follow runtime or notebook setup
    NotebookClient,
)

os.environ["JUPYTER_PATH"] = str(ROOT / "supplementary/.runtime/jupyter")
path = ROOT / "pgm_example_lyap.ipynb"
nb = nbformat.read(path, as_version=4)
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
sections = (
    (ROOT / "supplementary/b4_cells.py")
    .read_text(encoding="utf-8-sig")
    .split("# CELL\n")[1:]
)
md = nbformat.v4.new_markdown_cell
code = nbformat.v4.new_code_cell
new = [
    md(
        "## Identify the vectors composing the Lyapunov function\n\nWe use the same verified partial sums and rank-5 interior from Block 3. Every index, including both endpoints, must have an independent reconstructing basis."
    ),
    code(sections[0]),
    md(
        r"### Candidate-vector scan"
        + "\n\n"
        + r"Candidates are point-to-solution gaps $d_j=x_j-x_\star$, smooth gradients, and proximal subgradients. Zero and duplicate coordinate vectors are removed. The preliminary richer pairwise-difference scan is retained in supplementary evidence."
    ),
    code(sections[1]),
    code(sections[2]),
    md("### Selected basis pattern"),
    code(sections[3]),
    md(r"""The sparse search consistently selects
$$v_k=\left(d_0,\nabla f(x_k),d_{k+1},s_{k+1},\nabla f(x_\star)\right),\qquad 1\le k\le N-1,$$
where $s_{k+1}\in\partial g(x_{k+1})$ is the subgradient used by the proximal step. The initial quadratic basis is empty, and the terminal basis is $(d_0)$."""),
    code(sections[4]),
    md(
        "### Coefficient matrices\n\nMatrices use the displayed basis order and the convention $\\sum_{i,j}C_{ij}\\langle v_i,v_j\\rangle$; symmetric off-diagonal entries count twice. Function gaps and offsets are retained separately."
    ),
    code(sections[5]),
    code(sections[6]),
    md(r"""### Block 4 conclusion

Every $V_k$ reconstructs numerically in all scalar coordinates, including $V_0$ and $V_N$. The observed interior structure is
$$V_k=\sum_{i,j=0}^4 c_{ij}(k,N,L)\langle v_{k,i},v_{k,j}\rangle+a_k[f(x_k)-f(x_\star)]+b_k[g(x_k)-g(x_\star)],$$
with symmetric unknown coefficients $c_{ij}=c_{ji}$. The function-weight candidates are $a_k=(k+1)/(2N-k)$ and $b_k=k/(2N-k)$. The endpoint candidates are $V_0=0$ and
$$V_N=h(x_N)-h(x_\star)-\frac{L}{4N}\|d_0\|^2.$$
No constant term is observed. These numerical identities do not establish an analytic theorem. Block 5 must derive the remaining coefficients and verify exact step, initial and terminal identities with their signs and domains."""),
]
nb.cells[start:end] = new
nbformat.write(nb, path)
NotebookClient(
    nb,
    timeout=180,
    kernel_name="pgm-owned",
    resources={"metadata": {"path": str(ROOT)}},
).execute()
nbformat.write(nb, path)
for i, c in enumerate(nb.cells):
    if c.cell_type == "markdown":
        assert not any(x in c.source for x in ("\x0c", "\x0b", "\r", r"\(", r"\["))
    if i >= start:
        for out in c.get("outputs", []):
            if out.output_type == "stream":
                print("CELL", i, out.text)
checklist = ROOT / "supplementary/pgm_example_lyap_checklist.md"
lines = checklist.read_text(encoding="utf-8").splitlines()
for i, line in enumerate(lines):
    if line.startswith("Last reviewed block:"):
        lines[i] = "Last reviewed block: B4"
    if line.startswith("SHA-256:"):
        lines[i] = "SHA-256: " + hashlib.sha256(path.read_bytes()).hexdigest()
    if line.startswith("| 10 |"):
        lines[i] = (
            f"| 10 | special-vector identification | verified | {start}–{start + 11} | Candidate scan and sparse search visible and executed; fixed basis pattern, independence, labeled matrices and every-index full reconstruction pass. |"
        )
    if line.startswith("| 11 |"):
        lines[i] = (
            f"| 11 | coefficient extraction and closed-form V_k | pending | {start + 9}–{start + 12} | Numerical coefficients extracted; closed form deferred to B5 with named unknowns. |"
        )
    if line.startswith("| 12 |"):
        lines[i] = (
            f"| 12 | symbolic step, base, and boundary identities | pending | {start + 13} | B5 obligation. |"
        )
checklist.write_text("\n".join(lines) + "\n", encoding="utf-8")
print("B4 notebook fresh kernel and Markdown checks passed.")
