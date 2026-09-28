import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent / "helpers"))
import os

# optional notebook-generation dependency
import nbformat  # ty: ignore[unresolved-import]
import runtime

# optional notebook-generation dependency
from nbclient import NotebookClient  # ty: ignore[unresolved-import]

root = runtime.ATTEMPT
path = root / "dual_feg_example_lyap.ipynb"
nb = nbformat.read(path, as_version=4)
start = next(
    i
    for i, c in enumerate(nb.cells)
    if c.cell_type == "markdown" and c.source.startswith("## Dense and relaxed")
)
end = next(
    i
    for i, c in enumerate(nb.cells)
    if c.cell_type == "markdown" and c.source.startswith("## Partial-sum")
)
intro = nbformat.v4.new_markdown_cell(r"""## Dense and relaxed proof solves
The dense CLARABEL-default primal solve and the sparse primal solve were executed independently at $N=6$, $L=R=1$. Their complete dual records are preserved under `state/dual_feg_dense.json` and `supplementary/b2_sparse_candidate.json`. The following cells replay their checks without a new solve.

The sparse support retains monotonicity between $x_N$ and $x_\star,y_0,\ldots,y_{N-2}$, and Lipschitz continuity between $x_k,y_k$ for $k=0,\ldots,N-2$, plus $x_{N-1},x_N$. Here $y_k=x_{k+1/2}$. At the last iteration $x_N=y_{N-1}$, so the last pair avoids a redundant evaluated endpoint. Every omitted constraint has a stored null dual, and every retained multiplier and the Gram remainder come from one live solve.

## Lambda and S verification
Rational inspection suggests initial multiplier $4/N^2$, monotonicity multipliers $4/N$ for $(x_N,x_\star)$ and $4/((N-k)(N-k-1))$ for $(x_N,y_k)$, and Lipschitz multipliers $2/(N-k)^2$ (with final value $2$). A rank-one candidate is $S=\|2(x_0-x_\star)/N-A(x_N)\|^2$ at $L=1$.

These are candidates, checked exactly only at this fixed horizon. Arbitrary-horizon validity and the Lyapunov theorem remain unresolved. The numerical certificate uses every original numerical multiplier and a complete reverse LDL decomposition, retaining tiny factors and any off-diagonal blocks. The residual convention is $r\le0$ and the checked identity is $\mathrm{metric}-\mathrm{bound}-\sum_i\lambda_i r_i+S=0$; nonnegative multipliers and $S\ge0$ imply the stated fixed-sample upper bound.
""")
code = (root / "supplementary/b2_certificate_cells.py").read_text(encoding="utf-8-sig")
code = code[: code.index("\nstate={")]
code = code.replace("import hashlib\n", "").replace("import sympy as sp\n", "")
relaxation = """keep = {f"A monotone:x_{n},x_star"}
keep.update(f"A monotone:x_{n},y_{k}" for k in range(n-1))
keep.update(f"A Lipschitz:x_{k},y_{k}" for k in range(n-1))
keep.add(f"A Lipschitz:x_{n-1},x_{n}")
expected_drop = {name for name, meta in dense["constraint_metadata"].items() if meta["origin"] == "interpolation" and name not in keep}
assert expected_drop == set(selected["relaxed_constraints"])
print("All retained interpolation constraints:", sorted(keep))
for group in selected["lambda_groups"]:
    names = [name for name in keep if selected["constraint_metadata"][name]["group"] == group]
    vals = np.array([[float(lambda_candidate(name,n)) for name in names]])
    pf.pprint_labeled_matrix(pf.MatrixWithNames(vals, ["candidate multiplier"], names))
print("Initial closed-form search:", search)
print("Numerical certificate verified:", passed)
print("Analytic full-PEP verified: False; Lyapunov proof verified: False")
"""
nb.cells[start:end] = [
    intro,
    nbformat.v4.new_code_cell(code),
    nbformat.v4.new_code_cell(relaxation),
]
nbformat.write(nb, path)
os.environ["JUPYTER_PATH"] = str(runtime.RUNTIME / "jupyter")
NotebookClient(
    nb,
    timeout=120,
    kernel_name="dual-feg-attempt",
    resources={"metadata": {"path": str(root)}},
).execute()
nbformat.write(nb, path)
print("B2 notebook executed successfully")
