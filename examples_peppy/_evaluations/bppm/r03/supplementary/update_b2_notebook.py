from typing import cast

# Preserve the recorded import initialization order.
# isort: split
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent / "helpers"))
import ast
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
source = (root / "supplementary/helpers/certificate.py").read_text(encoding="utf-8-sig")
tree = ast.parse(source)
proof_functions = "\n\n".join(
    cast(str, ast.get_source_segment(source, node))
    for node in tree.body
    if isinstance(node, ast.FunctionDef)
    and node.name in ("inventory", "max_abs", "verify")
)
md, code = nb.v4.new_markdown_cell, nb.v4.new_code_cell
cells = [
    md(r"""## Full PEP certificate (Block 2)
The dense and sparse primal SDP solves at $N=4$, $\alpha=R=1$ use CLARABEL defaults. Their complete dual inventories were captured from their respective single solves. We load those immutable solve results and rebuild the same context to audit every constraint contribution; no dual components are mixed.
With $Q^f_{u,v}=f(v)-f(u)+\langle\nabla f(v),u-v\rangle\leq0$ (similarly for $h$), the sparse candidate keeps optimum-to-iterate $f$ pairs, forward adjacent $f$ pairs, both orientations of adjacent $h$ pairs where their coefficients are positive, and $Q^h_{\star,N}$.
Candidate weights are $\lambda^f_{\star,i}=1/N$, $\lambda^f_{i-1,i}=(i-1)/N$ for $i\geq2$, $\lambda^h_{i,i-1}=i/(\alpha N)$, $\lambda^h_{i-1,i}=(i-1)/(\alpha N)$ for $i\geq2$, and $\lambda^h_{\star,N}=\tau=1/(\alpha N)$. The candidate is $S=0$. These are fitted candidates here; an exact all-horizon proof remains pending."""),
    code(
        'from pepflow.utils import Comparator\nAPPROVED = repo_root\nb2 = json.loads((notebook_dir / "state/bppm_b2.json").read_text())\ndense = json.loads((notebook_dir / "state/bppm_dense.json").read_text())\nparams = json.loads(b2["params_json"])\nN_verify = b2["N_verify"]\nctx, pb, obj = get_pep_setup(N_verify, params)\npb.set_relaxed_constraints(b2["relaxed_constraints"])\nprint("dense",dense["opt_value"], "relaxed",b2["opt_value"])\nprint("basis", b2["basis_vectors"])\nprint("relaxed constraints", b2["relaxed_constraints"])\nfor label, saved in (("dense",dense),("selected",b2)):\n    print(label, saved["certificate_provenance"]["solver"])\n    for owner in ("f", "h"):\n        print(owner, {name:round(value,8) for name,value in saved["named_dual_values"].items() if name.startswith(owner+":") and value is not None and abs(value)>1e-6})\n    print("S rank at 1e-4", np.linalg.matrix_rank(np.array(saved["S_matrix"]),tol=1e-4))'
    ),
    code((root / "supplementary/helpers/formulas.py").read_text(encoding="utf-8-sig")),
    code(
        'candidate = candidate_duals(N_verify, params["alpha"])\nfor owner in ("f", "h"):\n    labels = sorted({tag for name in candidate if name.startswith(owner+":") for tag in name.split(":")[1].split(",")})\n    matrix = np.array([[candidate.get(f"{owner}:{row},{col}",0.0) for col in labels] for row in labels])\n    print("candidate multiplier matrix", owner)\n    pf.pprint_labeled_matrix(matrix, labels)\nlambda_error = max(abs(value-candidate.get(name,0)) for name,value in b2["named_dual_values"].items() if value is not None)\nprint("candidate lambda max error",lambda_error)\nassert lambda_error <= 1e-4'
    ),
    md(r"""### Numerical $S$ decomposition and complete identity
The original numerical $S$ is retained, including its small entries. Its direct spectral factors satisfy $S=E^TDE$; all eigenvalues are retained. Zero is only an analytic candidate, not a replacement for this numerical certificate. We check
$$f(x_N)-f(x_\star)-p_N-\sum_c d_c Q_c+S_{\rm numeric}=0,$$
including the initial constraint's constant, all $f$ and $h$ inequalities, and every coordinate."""),
    code(proof_functions),
    code(
        'checks = verify(ctx, pb, params, b2, dense["opt_value"])\nprint("complete certificate checks", checks)\nS_array = np.array(b2["S_matrix"])\nE = np.array(b2["numerical_decomposition"]["ell_coords"])\nD = np.array(b2["numerical_decomposition"]["D"])\nprint("spectral diagonal",np.diag(D))\npf.pprint_labeled_matrix(D, [f"ell_{i}" for i in range(len(D))], precision=12)\nprint("S reconstruction residual")\npf.pprint_labeled_matrix(E.T @ D @ E - S_array, b2["basis_vectors"], precision=12)\nprint("candidate zero S max error",np.max(np.abs(S_array)))\nassert np.max(np.abs(S_array)) <= 1e-4\nprint("Numerical certificate verified; analytic full-PEP and Lyapunov proofs pending.")'
    ),
    code(
        'pm = pf.ExpressionManager(ctx, resolve_parameters=params)\nweighted = pf.Scalar.zero()\nfor constraint, *_ in inventory(ctx, pb):\n    multiplier = b2["named_dual_values"][constraint.name]\n    if multiplier is not None:\n        weighted += multiplier * (constraint.lhs-constraint.rhs)\nbasis = ctx.basis_vectors()\nS_numeric = sum((float(S_array[i,j])*basis[i]*basis[j] for i,j in np.ndindex(S_array.shape)),pf.Scalar.zero())\nresidual = pm.eval_scalar(pb.performance_metric-b2["opt_value"]-weighted+S_numeric)\npf.pprint_labeled_matrix(np.asarray(residual.inner_prod_coords,dtype=float),b2["basis_vectors"],precision=12)\nprint("function coordinate residual",np.asarray(residual.func_coords,dtype=float))\nprint("offset residual",residual.offset)\nprint("initial closed-form search", b2["closed_form_search"])'
    ),
]
book.cells[10:11] = cells
os.environ["JUPYTER_PATH"] = str(root / "supplementary/.runtime")
NotebookClient(
    book,
    timeout=120,
    kernel_name="bppm-owned",
    resources={"metadata": {"path": str(root)}},
).execute()
nb.write(book, path)
print("B2 notebook updated and executed.")
