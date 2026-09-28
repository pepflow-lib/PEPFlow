import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent / "helpers"))
import os

# optional notebook-generation dependency
import nbformat as nb  # ty: ignore[unresolved-import]

# local helper resolved by the notebook runtime path
import runtime  # ty: ignore[unresolved-import]

# optional notebook-generation dependency
from nbclient import NotebookClient  # ty: ignore[unresolved-import]

root = runtime.ROOT
path = root / "bppm_example_lyap.ipynb"
book = nb.read(path, as_version=4)
md, code = nb.v4.new_markdown_cell, nb.v4.new_code_cell
read = lambda name: (root / f"supplementary/b4_{name}.py").read_text(  # noqa: E731 - retain the archived notebook helper
    encoding="utf-8-sig"
)
cells = [
    md(
        "## Identify the vectors composing the Lyapunov function\nWe use the revalidated Block 3 partial sums and search for a sparse rank-spanning basis. All indices, including the endpoints excluded from rank comparison, are reconstructed."
    ),
    code(
        'b3 = json.loads((notebook_dir / "state/bppm_b3.json").read_text())\nassert certificate["certificate_id"]==b3["certificate_id"]\nassert ranks==b3["rank_profile"]\nprint("Selected rank profile",ranks,"interior 1<=k<=N-1, exceptions k=0,N; confirmed horizons",b3["rank_search"]["confirmed_horizons"])'
    ),
    md(
        "### Candidate-vector scan\nCandidates include iterate-to-solution gaps, kernel gradients, cumulative objective gradients, original basis vectors, and iterate differences. Zero and duplicate coordinate vectors are removed before the column-space scan."
    ),
    code(read("scan")),
    md(
        "### Selected basis pattern\nThe following search tests the actual partial-sum matrices for every nonzero index. The adopted basis reorders the search result to put the current pair first; it keeps the same vectors and sparsity."
    ),
    code(read("search")),
    md(r"""For $1\leq k\leq N$, use
$$[v_1,v_2,v_3,v_4]=[x_k-x_\star,\nabla h(x_k),x_0-x_\star,\nabla h(x_0)].$$
At $k=0$, the potential is identically zero and its basis is empty. The terminal index uses the same four-vector formula as the interior."""),
    code(read("basis")),
    md(r"""### Coefficient matrices
In the displayed basis, the numerical fit is $C_{12}=C_{21}=1/(2\alpha N)$ and $C_{34}=C_{43}=-1/(2\alpha N)$, all other entries zero. Off-diagonal entries count twice in $\sum_{i,j} C_{ij}\langle v_i,v_j\rangle$. The function part is $(k/N)(f(x_k)-f(x_\star))+(h(x_0)-h(x_k))/(\alpha N)$ and the scalar offset is zero. These remain candidate formulas until Block 5."""),
    code(read("coefficients")),
    code(read("structure")),
    md(r"""### Block 4 conclusion
The candidate full expression, reconstructed at every required numerical index, is
$$V_k=\frac{k}{N}(f(x_k)-f(x_\star))+\frac{h(x_0)-h(x_k)+\langle\nabla h(x_k),x_k-x_\star\rangle-\langle\nabla h(x_0),x_0-x_\star\rangle}{\alpha N},\quad k\geq1,$$
with $V_0=0$. Equivalently the kernel part is $(D_h(x_\star,x_k)-D_h(x_\star,x_0))/(\alpha N)$. Numerical reconstruction does not prove the recurrence or signs for arbitrary horizons. Block 5 must establish the exact step, initial and terminal identities."""),
]
book.cells[24:36] = cells
os.environ["JUPYTER_PATH"] = str(root / "supplementary/.runtime")
NotebookClient(
    book,
    timeout=120,
    kernel_name="bppm-owned",
    resources={"metadata": {"path": str(root)}},
).execute()
nb.write(book, path)
print("B4 notebook executed and saved.")
