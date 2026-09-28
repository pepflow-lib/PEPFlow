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
new_cells = [
    m(
        "## Dense and relaxed proof solves\nThe saved solves use the approved primal solver with CLARABEL defaults. We reuse these complete results instead of solving again during replay. Every selected multiplier and S entry comes from the same sparse solve."
    ),
    c("""import numpy as np

with (notebook_dir / "state/ogm_dense.json").open() as stream:
    dense = json.load(stream)
with (notebook_dir / "state/ogm_b2.json").open() as stream:
    b2 = json.load(stream)
print("Dense value:", dense["opt_value"], "basis:", dense["basis_vectors"])
print("Dense S eigenvalues:", np.linalg.eigvalsh(dense["S_matrix"]))
for name, value in dense["named_dual_values"].items():
    if abs(value) > 1e-6:
        print("Dense active:", name, value)
# Keep star-to-iterate and consecutive-forward interpolation constraints.
def point_index(tag):
    return 0 if tag == "z_0" else -1 if tag == "x_star" else int(tag.split("_")[1])
expected_dropped = []
for name, meta in dense["constraint_metadata"].items():
    if meta["origin"] == "interpolation":
        left, right = name.split(":")[1].split(",")
        i, j = point_index(left), point_index(right)
        if not (i == -1 or j == i + 1):
            expected_dropped.append(name)
assert expected_dropped == b2["relaxed_constraints"]
print("Relaxed value:", b2["opt_value"], "dropped constraints:", len(expected_dropped))
assert abs(dense["opt_value"] - b2["opt_value"]) < 1e-5
print("Dense optimum preserved:", True)
for name, value in b2["named_dual_values"].items():
    if value is not None:
        print("Selected active:", name, value)"""),
    m(r"""## Lambda and S verification
The initial search suggests, for $i<N$,
$$\lambda_{\star,i}=\frac{2\theta_i}{\theta_N^2},\qquad
\lambda_{i,i+1}=\frac{2\theta_i^2}{\theta_N^2},\qquad
\lambda_{\star,N}=\frac1{\theta_N}.$$
The candidate remainder is
$$S=\frac{L}{2\theta_N^2}\left\|z_N-x_\star-\frac{\theta_N}{L}g_N\right\|^2.$$
These are candidates supported by the selected numerical sample, not yet an arbitrary-horizon proof. At $L=R=1$, the following code reassembles every active scalar constraint and verifies the identity
$$f(x_N)-f(x_\star)-B-\sum_c d_cR_c+S=0,$$
where each $R_c\leq0$. The code checks the Gram, function-value, and constant components, multiplier signs, and the full saved matrix reconstruction."""),
    c("""assert certificate_digest(b2) == b2["certificate_id"]
ctx, pb, pm, residual, S_candidate, lambda_candidates, decomposition, checks = verify_certificate(b2)
print("Complete numerical certificate checks:", checks)
print("Numerical certificate verified:", checks["passed"])
print("Analytic full-PEP proof verified:", b2["analytic_full_pep_verified"])
print("Lyapunov proof verified:", b2["lyapunov_proof_verified"])
names = b2["lambda_row_names"]
lambda_candidate_matrix = np.array([[lambda_candidates.get(f"f:{a},{b}", 0.0) for b in names] for a in names])
print("Candidate lambda matrix:")
pf.pprint_labeled_matrix(lambda_candidate_matrix, names, precision=7)
print("Candidate Gram remainder:")
pf.pprint_labeled_matrix(S_candidate, b2["basis_vectors"], precision=7)
print("Gram identity residual:")
pf.pprint_labeled_matrix(np.asarray(residual.inner_prod_coords, dtype=float), b2["basis_vectors"], precision=10)
print("Function identity residual:", np.asarray(residual.func_coords, dtype=float))
print("Offset identity residual:", residual.offset)
print("Initial formula search:")
for attempt in b2["closed_form_search"]["attempts"]:
    print(attempt)
print("Still unresolved:", b2["closed_form_search"]["unresolved_components"])"""),
    m("## Partial-sum Lyapunov construction and rank profile\nPending Block 3."),
    m("## Identify the vectors composing the Lyapunov function\nPending Block 4."),
    m("## Coefficients and symbolic identities\nPending Block 5."),
]
check_source = (root / "supplementary/helpers/certificate_checks.py").read_text(
    encoding="utf-8-sig"
)
check_source = chr(10).join(
    line
    for line in check_source.splitlines()[1:]
    if not line.startswith("from ogm_setup import")
)
new_cells.insert(3, c(check_source))
nb.cells = nb.cells[:11] + new_cells
nbformat.write(nb, path)
os.environ["JUPYTER_PATH"] = str(runtime.RUNTIME / "jupyter")
NotebookClient(
    nb,
    timeout=120,
    kernel_name="ogm-attempt",
    resources={"metadata": {"path": str(root)}},
).execute()
nbformat.write(nb, path)
print("B2 notebook executed and saved.")
