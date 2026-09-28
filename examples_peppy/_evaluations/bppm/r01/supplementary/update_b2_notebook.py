import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent / "helpers"))
import os

# optional notebook-generation dependency
import nbformat as nbf  # ty: ignore[unresolved-import]
import runtime

# optional notebook-generation dependency
from nbclient import NotebookClient  # ty: ignore[unresolved-import]

root = runtime.ROOT
path = root / "bppm_example_lyap.ipynb"
nb = nbf.read(path, as_version=4)
md, code = nbf.v4.new_markdown_cell, nbf.v4.new_code_cell
summary = code("""dense = json.loads((notebook_dir / "state/bppm_dense.json").read_text())
selected = json.loads((notebook_dir / "state/bppm_relaxed.json").read_text())
print("Dense bound:", dense["opt_value"])
print("Selected sparse bound:", selected["opt_value"])
print("Basis:", dense["basis_vectors"])
print("Dense active groups (threshold 1e-6 used for display/sparsity proposal):")
for owner in ("f", "h"):
    print(owner, [(name,value) for name,value in dense["named_dual_values"].items() if name.startswith(owner+":") and value is not None and abs(value)>1e-6])
print("Selected active multipliers:", {name:value for name,value in selected["named_dual_values"].items() if value is not None})
print("Dropped constraints:", selected["relaxed_constraints"])
""")
explanation = md(r"""## Full-PEP certificate

At $N=4$ and $\alpha=R=1$, the dense solve gives the conjectured value. Dropping multipliers below $10^{-6}$ and restricting remaining interpolation edges to consecutive iterates preserves the optimum. Every multiplier retained below comes from the same sparse CLARABEL solve, using default options; no components are replaced by rounded candidates.

The sparse pattern keeps $f:(x_\star,x_k)$, $f:(x_{k-1},x_k)$ for $k\ge2$, $h:(x_k,x_{k-1})$, $h:(x_{k-1},x_k)$ for $k\ge2$, and $h:(x_\star,x_N)$. The ordered pair $(u,v)$ denotes $f(v)-f(u)+\langle\nabla f(v),u-v\rangle\le0$, and likewise for $h$.

The complete numerical identity checked below is performance minus bound minus weighted inequality residuals plus the Gram remainder equals zero. Gram, function-value, and constant coordinates are checked separately, together with multiplier signs and semidefiniteness.

The actual numerical $S$ is retained via its complete spectral decomposition $S=E^TDE$, including small eigenvalues. The initial closed-form search inspected rational approximations of all active groups and used the proximal relation to propose
$$\lambda^f_{\star,k}=1/N,\quad \lambda^f_{k-1,k}=(k-1)/N,$$
$$\lambda^h_{k,k-1}=k/(\alpha N),\quad \lambda^h_{k-1,k}=(k-1)/(\alpha N),\quad \lambda^h_{\star,N}=1/(\alpha N),$$
with initial multiplier $1/(\alpha N)$ and candidate $S=0$. Zero-weight $k=1$ predecessor terms are absent. These are candidate formulas: numerical agreement and a fixed-horizon exact identity do not yet establish arbitrary-horizon validity. No external or pre-existing proof reference was consulted.""")
end = next(
    i
    for i, c in enumerate(nb.cells)
    if c.cell_type == "markdown" and c.source.startswith("## Lyapunov partial sums")
)
nb.cells[11:end] = [
    explanation,
    summary,
    code((root / "supplementary/b2_verification.py").read_text(encoding="utf-8-sig")),
]
os.environ["JUPYTER_PATH"] = str(runtime.RUNTIME / "jupyter")
nbf.write(nb, path)
NotebookClient(
    nb,
    timeout=120,
    kernel_name="bppm-owned",
    resources={"metadata": {"path": str(root)}},
).execute()
nbf.write(nb, path)
for i, c in enumerate(nb.cells):
    for o in c.get("outputs", []):
        if o.output_type == "stream":
            print(i, o.text)
print("B2 notebook execution passed.")
