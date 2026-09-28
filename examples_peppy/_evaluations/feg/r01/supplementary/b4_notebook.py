"""Expose B4 search, adopted basis, and all-index reconstruction."""

import hashlib
import json
from pathlib import Path

# optional notebook-generation dependency
import nbformat as nbf  # ty: ignore[unresolved-import]

# optional notebook-generation dependency
from nbclient import NotebookClient  # ty: ignore[unresolved-import]

root = Path.cwd()
source = (root / "supplementary/b4_discover.py").read_text()


def block(label):
    return source.split(f"# BEGIN {label}\n")[1].split(f"# END {label}")[0]


cells = [
    nbf.v4.new_markdown_cell(
        "## Identify the vectors composing the Lyapunov function\nThe selected B3 certificate and partial sums are replayed above. We seek interpretable vectors spanning each quadratic form, including the terminal index. Rank zero at the initial index uses an empty basis."
    ),
    nbf.v4.new_code_cell(
        'from pepflow.lyapunov_utils import (vectors_in_column_space, find_basis_with_sparsest_coefficients, find_symmetric_coefficient_matrix)\nb3 = json.loads((notebook_dir / "state/feg_b3.json").read_text())\nassert certificate_checked and grouping_checked\nassert ranks == b3["rank_profile"]\nassert b3["rank_search"]["confirmed_horizons"] == [4, 6]\nfor k, Vk in enumerate(lyap):\n    evaluated = pm.eval_scalar(Vk)\n    assert np.allclose(evaluated.inner_prod_coords, b3["lyap_inner_prod_coords"][k], atol=1e-4, rtol=1e-5)\n    assert np.allclose(evaluated.func_coords, b3["lyap_func_coords"][k], atol=1e-4, rtol=1e-5)\n    assert abs(evaluated.offset-b3["lyap_offsets"][k]) <= 1e-4\nprint("Reconstructed B3 data agree; interior 1..N-1, exceptions 0 and N.")'
    ),
    nbf.v4.new_markdown_cell(
        "### Candidate-vector scan\nCandidates include tagged full and half iterates, operator outputs, original coordinate vectors, anchor gaps, and pairwise differences. Duplicates and zero vectors are removed by coordinates, preferring the meaningful anchor-gap labels."
    ),
    nbf.v4.new_code_cell(block("CANDIDATES")),
    nbf.v4.new_markdown_cell(
        "### Selected basis pattern\nThe actual sparsity search is retained below for every nonzero index."
    ),
    nbf.v4.new_code_cell(block("SEARCH")),
    nbf.v4.new_markdown_cell(r"""The sparsest interior coordinates involve the next half iterate. For a single pattern valid through the terminal index, adopt the equally spanning basis
$$v_{1,k}=A(x_k),\qquad v_{2,k}=x_k-x_0,\qquad 1\le k\le N.$$
The initial quadratic part $V_0=0$ uses the empty basis. Independence and reconstruction of this adopted basis are checked below, so this change of coordinates is not inferred from the sparse search alone."""),
    nbf.v4.new_code_cell(block("BASIS")),
    nbf.v4.new_markdown_cell(r"""### Coefficient matrices
The ordered basis is $[A(x_k),x_k-x_0]$ for every $1\le k\le N$. With symmetric $C$, the expression is $\sum_{i,j} C_{ij}\langle v_i,v_j\rangle$; off-diagonal entries contribute twice. Empty function-coordinate arrays and zero offsets are verified rather than discarded."""),
    nbf.v4.new_code_cell(block("COEFFICIENTS")),
    nbf.v4.new_code_cell(block("STRUCTURE")),
    nbf.v4.new_markdown_cell(r"""### Block 4 conclusion
The observed complete structure is $V_0=0$ and
$$V_k=c_{00}(k,N,L)\|A(x_k)\|^2+2c_{01}(k,N,L)\langle A(x_k),x_k-x_0\rangle+c_{11}(k,N,L)\|x_k-x_0\|^2,$$
for $1\le k\le N$, with no function-value or constant terms. All required numerical reconstructions pass, including both endpoints. The coefficient functions are explicitly unresolved; B5 must derive them and prove the exact step, base, and boundary identities. No analytic proof is claimed here."""),
]
for i, c in enumerate(cells):
    c.id = f"b4-{i:02d}"
path = root / "feg_example_lyap.ipynb"
nb = nbf.read(path, as_version=4)
start = next(i for i, c in enumerate(nb.cells) if c.id in ("b1-09", "b4-00"))
end = next(i for i, c in enumerate(nb.cells) if c.id == "b1-10")
nb.cells[start:end] = cells
nbf.write(nb, path)
NotebookClient(
    nb, timeout=180, kernel_name="attempt", resources={"metadata": {"path": str(root)}}
).execute()
nbf.write(nb, path)
markdown = "\n".join(c.source for c in nb.cells if c.cell_type == "markdown")
assert not any(x in markdown for x in ("\\(", "\\)", "\\[", "\\]", "\x0c", "\r"))
checklist = root / "supplementary/feg_example_lyap_checklist.md"
lines = checklist.read_text().splitlines()
for i, line in enumerate(lines):
    if line.startswith("Last reviewed block:"):
        lines[i] = "Last reviewed block: B4"
    elif line.startswith("SHA-256:"):
        lines[i] = "SHA-256: " + hashlib.sha256(path.read_bytes()).hexdigest()
    elif line.startswith("| 10 |"):
        lines[i] = (
            "| 10 | special-vector identification | verified | b4-00 through b4-07 | Actual candidate scan and sparse search outputs, adopted basis and all-index independence checks. |"
        )
    elif line.startswith("| 11 |"):
        lines[i] = (
            "| 11 | coefficient extraction and closed-form V_k | pending | b4-08 through b4-11 | Numerical matrices and complete all-index reconstructions verified; named coefficient functions await B5 analytic derivation. |"
        )
checklist.write_text("\n".join(lines) + "\n")
print(
    json.dumps(
        {
            "fresh_kernel": "passed",
            "math_delimiters": "passed",
            "sha256": hashlib.sha256(path.read_bytes()).hexdigest(),
        }
    )
)
