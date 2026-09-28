"""Expose executed B4 candidate scan, basis search and reconstruction."""

from pathlib import Path

# optional notebook-generation dependency
import nbformat  # ty: ignore[unresolved-import]

root = Path(__file__).resolve().parents[1]
path = root / "ogm_example_lyap.ipynb"
nb = nbformat.read(path, as_version=4)
source = (root / "supplementary/b4_math.py").read_text()
sections = {}
for part in source.split("# CELL: ")[1:]:
    name, body = part.split("\n", 1)
    sections[name] = body
for line in (
    "import inspect\n",
    "from certificate import scalar_coordinates\n",
    "from ogm_setup import theta_sequence\n",
    "from partial_sums import construct, rebuild\n",
    "from runtime import NOTEBOOK_DIR\n",
):
    sections["replay"] = sections["replay"].replace(line, "")
nb.cells[-1].source = nb.cells[-1].source.split(
    "## Identify the vectors composing the Lyapunov function"
)[0]
md, code = nbformat.v4.new_markdown_cell, nbformat.v4.new_code_cell
candidates, filtering = sections["candidates"].split("in_column = {}", 1)
nb.cells += [
    md(
        "## Identify the vectors composing the Lyapunov function\nThe selected numerical partial sums are replayed from the same certificate. The rank-three interior pattern is confirmed at horizons 4 and 6; this section discovers a spanning basis and checks every index of the selected horizon."
    ),
    code(sections["replay"]),
    md(
        "### Candidate-vector scan\nCandidates include tagged iterates, gradients, point differences, the initial displacement, and auxiliary displacements $q_k=z_{k+1}-x_\\star$. Duplicate coordinate vectors and zero vectors are removed."
    ),
    code(candidates),
    code("in_column = {}" + filtering),
    md(
        "### Selected basis pattern\nThe actual sparse-coefficient search below tests the column-space candidates. It selects a consistent pattern; the adopted order matches that search."
    ),
    code(sections["search"]),
    md(r"""For $1\leq k<N$, use the ordered basis
$$\mathcal B_k=(x_0-x_\star,\ z_{k+1}-x_\star,\ g_k).$$
At $k=0$ the quadratic part is zero and the basis is empty. At $k=N$ use only $x_0-x_\star$. All of these cases are checked below."""),
    code(sections["basis"]),
    md(
        "### Coefficient matrices\nMatrices use the stated basis order, with symmetric off-diagonal entries counted twice. Function-gap coefficients and offsets are retained separately. The full structure is assembled explicitly and checked against the original partial sums."
    ),
    code(sections["coefficients"]),
    md(r"""The numerical diagonal matrices suggest
$$C_k=\operatorname{diag}\left(-\frac{L}{2\theta_N^2},\frac{L}{2\theta_N^2},-\frac{\theta_k^2}{L\theta_N^2}\right),\qquad
a_k=\frac{2\theta_k^2}{\theta_N^2}\quad(1\leq k<N).$$
The terminal candidates are $C_N=-L/(2\theta_N^2)$ and $a_N=1$. These are candidate formulas, not yet analytic identities."""),
    code(sections["fit"]),
    md(r"""### Block 4 conclusion
Every selected-horizon index reconstructs in Gram, function-value and constant coordinates. The candidate expression is $V_0=0$, and
$$V_k=\frac{1}{\theta_N^2}\left[2\theta_k^2(f(x_k)-f_\star)
-\frac{\theta_k^2}{L}\|g_k\|^2+\frac L2\|z_{k+1}-x_\star\|^2
-\frac L2\|x_0-x_\star\|^2\right]\quad(1\leq k<N),$$
$$V_N=f(x_N)-f_\star-\frac{L}{2\theta_N^2}\|x_0-x_\star\|^2.$$
The basis and numerical reconstruction are verified. Block 5 must establish the candidate coefficient formulas, one-step identity, initial/terminal transitions and signs for arbitrary horizons.

## Closed-form Lyapunov function and exact proof
Pending Block 5."""),
]
nbformat.write(nb, path)
