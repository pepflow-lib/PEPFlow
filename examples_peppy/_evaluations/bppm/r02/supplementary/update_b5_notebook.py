import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent / "helpers"))
import json

# optional notebook-generation dependency
import nbformat as nbf  # ty: ignore[unresolved-import]

# local helper resolved by the notebook runtime path
from runtime import ATTEMPT  # ty: ignore[unresolved-import]

path = ATTEMPT / "bppm_example_lyap.ipynb"
nb = nbf.read(path, as_version=4)
start = next(
    i
    for i, c in enumerate(nb.cells)
    if c.cell_type == "markdown" and c.source.startswith("## Symbolic step")
)
content = json.loads((ATTEMPT / "supplementary/b5_cells.json").read_text())
nb.cells[start:] = [
    nbf.v4.new_code_cell(c["source"])
    if c["kind"] == "code"
    else nbf.v4.new_markdown_cell(c["source"])
    for c in content
]
nb.cells[
    16
].source += '\nprint("Saved numerical S (all entries retained):")\npf.pprint_labeled_matrix(pf.MatrixWithNames(S_array, b2["S_row_names"], b2["S_col_names"]))\n'
proof = [
    nbf.v4.new_markdown_cell("## Proof Statement"),
    nbf.v4.new_markdown_cell(r"""### Theorem
Under the assumptions stated above, let $\alpha>0$, $R\ge0$, and integer $N\ge1$, and let the exact Bregman proximal iterates satisfy $D_h(x_{\star},x_{0})\le R$. Define, for $0\le k\le N$,
$$V_{k}=\frac{k}{N}\bigl(f(x_{k})-f(x_{\star})\bigr)+\frac{D_h(x_{\star},x_{k})-D_h(x_{\star},x_{0})}{\alpha N}.$$
Then $V_{0}=0$ and $V_{k}$ is nonincreasing. Consequently,
$$0\le f(x_{N})-f(x_{\star})\le\frac{R}{\alpha N}.$$
Equivalently, the unshifted potential is $\Phi_{k}=V_{k}+D_h(x_{\star},x_{0})/(\alpha N)$. The result includes $N=1$ and $R=0$."""),
    nbf.v4.new_markdown_cell(r"""### Proof outline
For a convex function $q$, define the nonpositive residual
$$C^q_{u,v}=q(v)-q(u)+\langle\nabla q(v),u-v\rangle\le0.$$
Use the potential
$$V_{k}=\frac{k}{N}(f(x_{k})-f(x_{\star}))+\frac{D_h(x_{\star},x_{k})-D_h(x_{\star},x_{0})}{\alpha N}.$$
At the base, $V_{0}=0$. Exact proximal optimality gives $\nabla h(x_j)=\nabla h(x_{j-1})-\alpha\nabla f(x_j)$. Expanding the Bregman terms yields, for every $1\le j\le N$,
$$V_j-V_{j-1}=\frac1N C^f_{x_{\star},x_j}+\frac{j-1}{N}C^f_{x_{j-1},x_j}
+\frac{j}{\alpha N}C^h_{x_j,x_{j-1}}+\frac{j-1}{\alpha N}C^h_{x_{j-1},x_j}\le0.$$
Every coefficient is nonnegative; the terms with $j-1$ vanish at the first step. No additional square or matrix residual appears in this exact local identity. Hence $V_N\le0$.

Finally,
$$f(x_N)-f(x_{\star})-\frac{R}{\alpha N}=V_N+\frac{D_h(x_{\star},x_0)-R}{\alpha N}+\frac{C^h_{x_{\star},x_N}}{\alpha N}\le0.$$
The initial assumption controls the middle term and $C^h_{x_{\star},x_N}=-D_h(x_{\star},x_N)\le0$ by convexity. Thus the bound uses radius $R$, not $R^2$. The executable symbolic checks below verify these identities with symbolic indices and parameters in all scalar components."""),
]
nb.cells[1:2] = proof
nbf.write(nb, path)
print("Final theorem, detailed proof outline and symbolic cells added.")
