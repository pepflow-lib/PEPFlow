import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent / "helpers"))
import os

# optional notebook-generation dependency
import nbformat as nbf  # ty: ignore[unresolved-import]
import runtime

# optional notebook-generation dependency
from nbclient import NotebookClient  # ty: ignore[unresolved-import]

root = runtime.ATTEMPT
path = root / "bppm_example_lyap.ipynb"
nb = nbf.read(path, as_version=4)
md = nbf.v4.new_markdown_cell
code = nbf.v4.new_code_cell
core = (root / "supplementary/b2_core.py").read_text(encoding="utf-8-sig")
new = [
    md(
        "## Dense and relaxed proof solves\nThe dense sample and selected relaxed sample each come from a single primal solve. CLARABEL defaults were used. The saved data include both function families and every initial multiplier. The code below makes the solve/capture and complete numerical verification reproducible; notebook execution revalidates the saved coherent sample without replacing it."
    ),
    code(
        core[core.index("import hashlib") :].replace(
            "from bppm_setup import get_pep_setup\n", ""
        )
    ),
    code(
        'dense = json.loads((notebook_dir / "state/bppm_dense.json").read_text())\nb2 = json.loads((notebook_dir / "state/bppm_b2.json").read_text())\nprint("Dense bound:", dense["opt_value"])\nprint("Basis vectors:", dense["basis_vectors"])\nfor owner in ("f", "h"):\n    print(owner, "dense active:", [(n, round(v,7)) for n,v in dense["named_dual_values"].items() if n.startswith(owner+":") and v is not None and abs(v)>1e-6])\nprint("Dense S maximum:", max_abs(dense["S_matrix"]))\nN = b2["N_verify"]\nparams = json.loads(b2["params_json"])\ncandidate = candidate_weights(N, params["alpha"])\nrelaxed = [n for n in dense["constraint_metadata"] if n not in candidate]\nassert relaxed == b2["relaxed_constraints"]\nprint("Dropped constraints:", len(relaxed))\nprint("Selected bound:", b2["opt_value"], "preserved gap:", abs(dense["opt_value"]-b2["opt_value"]))\nfor owner in ("f", "h"):\n    print(owner, "selected active:", [(n,round(v,7)) for n,v in b2["named_dual_values"].items() if n.startswith(owner+":") and v is not None and abs(v)>1e-6])'
    ),
    md(r"""## Lambda and S verification
Convex interpolation residuals are $r^q_{i,j}=q(x_j)-q(x_i)+\langle\nabla q(x_j),x_i-x_j\rangle\le0$.
The initial formula search used the dense support and then the consecutive-pair relaxation. For $1\le k\le N$, the candidate $f$ weights are $\lambda^f_{\star,k}=1/N$ and $\lambda^f_{k-1,k}=(k-1)/N$. The latter vanishes for $k=1$.
The candidate $h$ weights are $\lambda^h_{k,k-1}=k/(\alpha N)$ and $\lambda^h_{k-1,k}=(k-1)/(\alpha N)$, together with $\lambda^h_{\star,N}=1/(\alpha N)$ and initial multiplier $1/(\alpha N)$. All other multipliers vanish. The candidate Gram remainder is $S=0$.
These are **numerically supported candidates**. No all-horizon analytic full-PEP proof is claimed here. The actual small numerical $S$ is retained exactly as saved and reconstructed through its eigendecomposition."""),
    code(
        'for owner in ("f", "h"):\n    labels = ["x_star"] + [f"x_{k}" for k in range(N+1)]\n    matrix = np.array([[candidate.get(f"{owner}:{i},{j}",0.0) for j in labels] for i in labels])\n    print(owner, "candidate multiplier matrix")\n    pf.pprint_labeled_matrix(pf.MatrixWithNames(matrix,labels,labels))\nerror = max(abs(v-candidate[name]) for name,v in b2["named_dual_values"].items() if v is not None)\nassert error < 1e-4\nprint("Candidate multiplier error:",error)\nprint("Candidate S=0 error:",max_abs(b2["S_matrix"]))\nassert max_abs(b2["S_matrix"]) < 1e-4\nprint("Candidate S matrix:")\npf.pprint_labeled_matrix(pf.MatrixWithNames(np.zeros_like(b2["S_matrix"]),b2["S_row_names"],b2["S_col_names"]))'
    ),
    md(r"""For each scalar constraint use its actual normalized residual $r\le0$. With the selected numerical multipliers and its original $S$, check
$$\mathrm{metric}-\mathrm{bound}-\sum_c d_c r_c+\sum_{i,j}S_{ij}\langle b_i,b_j\rangle=0.$$
The executable verifier above checks every scalar coordinate, the sign of every active multiplier, PSD of $S$, its factor reconstruction, and preservation of the dense optimum. No active small multiplier or remainder is silently removed."""),
    code(
        'ctx, pb, obj = get_pep_setup(N, params)\npb.set_relaxed_constraints(b2["relaxed_constraints"])\nassert [str(v) for v in ctx.basis_vectors()] == b2["basis_vectors"]\nassert [str(v) for v in ctx.basis_scalars()] == b2["basis_scalars"]\nfor relative, expected in b2["certificate_provenance"]["source_hashes"].items():\n    assert hashlib.sha256((notebook_dir/relative).read_bytes()).hexdigest() == expected\nchecked = verify_certificate(ctx, pb, b2, dense["opt_value"])\nprint("Numerical S decomposition: full eigenbasis, all eigenvalues retained")\nprint("Diagonal D:",np.diag(np.asarray(b2["numerical_decomposition"]["D"])))\nprint("Gram identity residual:")\npf.pprint_labeled_matrix(pf.MatrixWithNames(np.asarray(checked.inner_prod_coords,dtype=float),b2["basis_vectors"],b2["basis_vectors"]))\nprint("Function coordinates:",checked.func_coords)\nprint("Constant:",checked.offset)\nprint("Search record:",b2["closed_form_search"])\nprint("Numerical certificate verified:",b2["numerical_certificate_verified"])\nprint("Analytic full-PEP verified:",b2["analytic_full_pep_verified"])\nprint("Lyapunov proof verified:",b2["lyapunov_proof_verified"])'
    ),
]
end = next(
    i
    for i, c in enumerate(nb.cells)
    if c.cell_type == "markdown" and c.source.startswith("## Lyapunov partial sums")
)
nb.cells[10:end] = new
os.environ["JUPYTER_PATH"] = str(runtime.RUNTIME / "jupyter")
nbf.write(nb, path)
NotebookClient(
    nb,
    timeout=120,
    kernel_name="bppm-attempt",
    resources={"metadata": {"path": str(root)}},
).execute()
nbf.write(nb, path)
print("B2 notebook executed and saved")
