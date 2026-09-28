import sys
from pathlib import Path

root = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(root / "supplementary/helpers"))
import os  # noqa: E402 - imports follow runtime or notebook setup

import nbformat  # ty: ignore[unresolved-import]  # optional notebook-generation dependency  # noqa: E402 - imports follow runtime or notebook setup
import runtime  # noqa: E402 - imports follow runtime or notebook setup
from nbclient import (  # ty: ignore[unresolved-import]  # optional notebook-generation dependency  # noqa: E402 - imports follow runtime or notebook setup
    NotebookClient,
)

path = root / "ogm_example_lyap.ipynb"
nb = nbformat.read(path, as_version=4)
m, c = nbformat.v4.new_markdown_cell, nbformat.v4.new_code_cell
scan = (root / "supplementary/b4_scan.py").read_text(encoding="utf-8-sig")
scan = (
    scan.replace("import sympy as sp\n", "")
    .replace("from ogm_setup import theta_sequence\n", "")
    .replace(", find_symmetric_coefficient_matrix", "")
)
scan = scan.replace("    print('C',C)\n", "").replace(
    "    print('function',np.asarray(pm.eval_scalar(lyap[k]).func_coords,dtype=float))\n",
    "",
)
first, tail = scan.split("filtered={}", 1)
filtering, search = tail.split("sparse_basis_by_k={}", 1)
coeff = (
    (root / "supplementary/b4_coefficients.py")
    .read_text(encoding="utf-8-sig")
    .replace("from ogm_setup import theta_sequence\n", "")
    .replace("import sympy as sp\n", "")
)
new = [
    m(
        "## Identify the vectors composing the Lyapunov function\nThe selected B3 partial sums are reconstructed above. We search for interpretable bases, retain the fixed interior domain 1 through N-1, and check both exceptional endpoints."
    ),
    c("""with (notebook_dir / "state/ogm_b3.json").open() as stream:
    b3 = json.load(stream)
certificate = b3
assert certificate_digest(b3) == b3["certificate_id"]
assert ranks == b3["rank_profile"]
print("Selected ranks:", ranks, "confirmed horizons:", b3["rank_search"]["confirmed_horizons"])
"""),
    m(
        "### Candidate-vector scan\nCandidates include tagged iterates, gradients, auxiliary displacements, the initial displacement, the terminal square vector, and pairwise differences. Zero vectors and coordinate duplicates are removed."
    ),
    c(first),
    c("filtered={}" + filtering),
    m(
        "### Selected basis pattern\nThe following exhaustive sparse-basis search is executed for every nonzero-rank index, including the terminal case."
    ),
    c("sparse_basis_by_k={}" + search),
    m(r"""The search selects the interior basis
$$[x_0-x_\star,\ g_k,\ z_{k+1}-x_\star],\qquad 1\leq k<N.$$
At $k=N$ it selects $[x_0-x_\star,\ z_N-x_\star-\theta_Ng_N]$ for the normalized sample $L=1$. At $k=0$ the quadratic part is zero and uses the empty basis. Independence and full reconstruction are checked below."""),
    c((root / "supplementary/b4_basis.py").read_text(encoding="utf-8-sig")),
    m(
        "### Coefficient matrices\nThe basis order is the displayed order above. Each symmetric matrix uses the convention that off-diagonal entries contribute twice. We also extract the function-gap coefficient and retain the constant term."
    ),
    c(coeff),
    c((root / "supplementary/b4_structure.py").read_text(encoding="utf-8-sig")),
    m(
        "The diagonal coefficient pattern below is compared against every extracted matrix and function coefficient. It remains a numerical candidate."
    ),
    c((root / "supplementary/b4_coeff_candidate.py").read_text(encoding="utf-8-sig")),
    m(r"""### Block 4 conclusion
For the normalized sample, the supported interior expression is
$$V_k=\frac{2\theta_k^2}{\theta_N^2}(f(x_k)-f_\star)-\frac{\theta_k^2}{\theta_N^2}\|g_k\|^2+\frac{\|z_{k+1}-x_\star\|^2-\|x_0-x_\star\|^2}{2\theta_N^2},\quad 1\leq k<N.$$
The endpoint expressions are $V_0=0$ and
$$V_N=f(x_N)-f_\star+\frac{\|z_N-x_\star-\theta_Ng_N\|^2-\|x_0-x_\star\|^2}{2\theta_N^2}.$$
Every quadratic, function, and constant component is numerically reconstructed, including endpoints. These formulas are candidates at this stage. B5 must restore general scaling and prove the step, base, and terminal identities with the necessary sign conditions."""),
    m("## Symbolic step, base, and boundary identities\nPending Block 5."),
]
nb.cells = nb.cells[:22] + new
nbformat.write(nb, path)
os.environ["JUPYTER_PATH"] = str(runtime.RUNTIME / "jupyter")
NotebookClient(
    nb,
    timeout=120,
    kernel_name="ogm-attempt",
    resources={"metadata": {"path": str(root)}},
).execute()
nbformat.write(nb, path)
print("B4 notebook executed, including actual sparse-basis searches.")
