import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent / "helpers"))
import hashlib

# optional notebook-generation dependency
import nbformat as nbf  # ty: ignore[unresolved-import]

# local helper resolved by the notebook runtime path
import runtime  # ty: ignore[unresolved-import]

# optional notebook-generation dependency
from nbclient import NotebookClient  # ty: ignore[unresolved-import]

root = runtime.ROOT
path = root / "feg_example_lyap.ipynb"
nb = nbf.read(path, as_version=4)
start = next(i for i, c in enumerate(nb.cells) if c.source.startswith("## Identify"))
end = next(i for i, c in enumerate(nb.cells) if c.source.startswith("## Symbolic"))
md = nbf.v4.new_markdown_cell
code = nbf.v4.new_code_cell
sources = {
    name: (root / f"supplementary/b4_{name}.py").read_text(encoding="utf-8-sig")
    for name in (
        "scan",
        "search",
        "basis",
        "coefficients",
        "structure",
        "fit",
        "components",
    )
}
cells = [
    md(r"""## Identify the vectors composing the Lyapunov function
Starting from the verified B3 partial sums, search for interpretable spanning vectors. The selected horizon is $N=4$; retained indices are $1,2,3$, with $0,4$ treated explicitly as boundaries. The rank-two structure was separately confirmed at $N=6$."""),
    code("""b3 = json.loads((notebook_dir/"state/feg_b3.json").read_text())
assert certificate["certificate_id"] == b3["certificate_id"]
assert certificate_checked and grouping_checked
assert ranks == b3["rank_profile"]
assert len(lyap) == N_int+1
for k,value in enumerate(lyap):
    current = pm.eval_scalar(value)
    assert np.allclose(current.inner_prod_coords,b3["lyap_inner_prod_coords"][k],atol=1e-4,rtol=1e-5)
    assert np.allclose(current.func_coords,b3["lyap_func_coords"][k],atol=1e-4,rtol=1e-5)
    assert abs(float(current.offset)-b3["lyap_offsets"][k])<=1e-4
print("Selected partial sums rechecked; endpoints included in reconstruction.")"""),
    md(
        "### Candidate-vector scan\nCandidates include operator outputs, tagged iterates, anchor and solution gaps, basis vectors, and pairwise differences. Zero vectors and coordinate duplicates are removed. Every positive index, including the terminal one, is scanned."
    ),
    code(sources["scan"]),
    md(
        "### Selected basis pattern\nThe sparse search below is executed on the actual partial sums. At k=1 it selects a diagonal coefficient representation; the uniform operator-output/anchor-gap basis is adopted for its consistent recurrence interpretation and is independently checked."
    ),
    code(sources["search"]),
    md(r"""Use the ordered basis
$$\mathcal B_k=[g_k,\ x_k-x_0]\qquad(1\le k\le N).$$
At $k=0$, the quadratic expression is zero and the basis is empty. This includes the terminal index without an additional vector."""),
    code(sources["basis"]),
    md(
        "### Coefficient matrices\nThe matrix is symmetric, so off-diagonal entries contribute twice. Each numerical matrix below is reconstructed using the adopted basis; function-value coordinates and constants are checked separately."
    ),
    code(sources["coefficients"]),
    code(sources["fit"]),
    code(sources["structure"] + "\n" + sources["components"]),
    md(r"""### Block 4 conclusion
The complete observed expression has no function-value or constant terms. For $1\le k\le N$, the candidate is
$$V_k=\frac{2k^2}{N^2}\|g_k\|^2+\frac{4kL}{N^2}\langle g_k,x_k-x_0\rangle,$$
with $V_0=0$. The coefficient formula agrees with the selected numerical sample within the frozen comparison tolerance. Every numerical partial sum, including $V_N$, is reconstructed with its extracted coefficients. B5 must establish exact coefficients, local step identities, signs and the boundary bound for arbitrary horizons."""),
]
nb.cells[start:end] = cells
nbf.write(nb, path)
NotebookClient(
    nb,
    timeout=120,
    kernel_name="feg-private",
    resources={"metadata": {"path": str(root)}},
).execute()
nbf.write(nb, path)
for cell in nb.cells:
    if cell.cell_type == "markdown":
        assert "\\(" not in cell.source and "\\[" not in cell.source
        assert all(ord(ch) >= 32 or ch in "\n\t" for ch in cell.source)
    assert all(out.output_type != "error" for out in cell.get("outputs", []))
check = root / "supplementary/feg_example_lyap_checklist.md"
lines = check.read_text().splitlines()
for i, line in enumerate(lines):
    if line.startswith("Last reviewed block:"):
        lines[i] = "Last reviewed block: B4"
    if line.startswith("SHA-256:"):
        lines[i] = "SHA-256: " + hashlib.sha256(path.read_bytes()).hexdigest()
    if line.startswith("| 10 |"):
        lines[i] = (
            f"| 10 | special-vector identification | verified | {start}-{start + 7} | Actual candidate scan and sparse search executed for k=1..N; adopted uniform two-vector basis independent at every positive index; initial zero case explicit. |"
        )
    if line.startswith("| 11 |"):
        lines[i] = (
            f"| 11 | coefficient extraction and closed-form V_k | pending | {start + 8}-{start + 12} | Full numerical reconstruction and candidate formula checks passed at every index; arbitrary-horizon closed form remains B5. |"
        )
    if line.startswith("| 12 |"):
        parts = line.split("|")
        parts[4] = (
            " "
            + str(
                next(
                    j
                    for j, c in enumerate(nb.cells)
                    if c.source.startswith("## Symbolic")
                )
            )
            + " "
        )
        lines[i] = "|".join(parts)
check.write_text("\n".join(lines) + "\n")
print("B4 notebook executed:", len(nb.cells), "cells")
