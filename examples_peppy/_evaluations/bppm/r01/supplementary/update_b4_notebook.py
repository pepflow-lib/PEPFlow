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
start = next(
    i
    for i, c in enumerate(nb.cells)
    if c.cell_type == "markdown"
    and (
        c.source.startswith("## Special vectors")
        or c.source.startswith("## Identify the vectors")
    )
)
end = next(
    i
    for i, c in enumerate(nb.cells)
    if c.cell_type == "markdown" and c.source.startswith("## Exact step")
)


def source(name):
    return (root / "supplementary" / name).read_text(encoding="utf-8-sig")


nb.cells[start:end] = [
    md(
        "## Identify the vectors composing the Lyapunov function\n\nStarting from the reconstructed Block 3 certificate, search for interpretable vectors spanning the quadratic part. The selected horizon is N=4; the interior rank was independently confirmed at N=6. Both endpoints remain required."
    ),
    code(source("b4_sanity.py")),
    md(
        "### Candidate-vector scan\n\nCandidates include point-to-solution gaps, kernel gradients, basis vectors, and pairwise differences. Coordinates remove duplicate and zero vectors; meaningful gap labels precede incidental equivalents."
    ),
    code(source("b4_candidates.py")),
    md(
        "### Selected basis pattern\n\nThe following is the actual sparse subset search, including the terminal index. The initial quadratic part is zero and needs no nonzero basis."
    ),
    code(source("b4_search.py")),
    md(r"""The search selects the same ordered template for $1\le k\le N$:
$$[x_0-x_\star,\nabla h(x_0),x_k-x_\star,\nabla h(x_k)].$$
For $k=0$, use an empty basis and the verified zero expression. The terminal basis follows the same template; it is not exempted from reconstruction."""),
    code(source("b4_basis.py")),
    md(r"""### Coefficient matrices

Use the basis order displayed above. The symmetric convention is $V_k^{\mathrm{quad}}=\sum_{i,j}C_{ij}\langle v_i,v_j\rangle$, so off-diagonal entries contribute twice. The function terms are $f(x_k)-f(x_\star)$ and $h(x_0)-h(x_k)$. Their numerical coefficients are obtained independently from the function-coordinate arrays."""),
    code(source("b4_coefficients.py")),
    code(source("b4_structure.py")),
    code(
        source("b4_fit.py")
        + "\npf.pprint_labeled_matrix(pf.MatrixWithNames(np.array(coeff_pattern(1,N_int,sp.S(1)),dtype=object),V_k_basis_labels(1),V_k_basis_labels(1)))\n"
    ),
    md(r"""### Block 4 conclusion

The numerical structure suggests, for $1\le k\le N$,
$$V_k=\frac{k}{N}(f(x_k)-f(x_\star))+\frac{h(x_0)-h(x_k)-\langle\nabla h(x_0),x_0-x_\star\rangle+\langle\nabla h(x_k),x_k-x_\star\rangle}{\alpha N}.$$
Equivalently, the candidate is $[\alpha k(f(x_k)-f(x_\star))+D_h(x_\star,x_k)-D_h(x_\star,x_0)]/(\alpha N)$, with $V_0=0$.

The candidate matrix has $C_{01}=C_{10}=-1/(2\alpha N)$ and $C_{23}=C_{32}=1/(2\alpha N)$, with other entries zero. This formula agrees with every selected numerical coefficient and with the reconstructed function/constant components. Its arbitrary-horizon status is still a candidate. Block 5 must establish the exact step, base, and terminal identities and all sign assumptions."""),
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
    if i >= start:
        for o in c.get("outputs", []):
            if o.output_type == "stream":
                print(i, o.text)
print("B4 notebook fresh-kernel execution passed.")
