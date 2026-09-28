import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent / "helpers"))
import json
from fractions import Fraction

# optional notebook-generation dependency
import nbformat as nbf  # ty: ignore[unresolved-import]
import runtime

root = runtime.ATTEMPT
results = json.loads((root / "supplementary/_sweep_tmp.json").read_text())
opts = [r["opt_value"] for r in results]
print("Fractions:", [str(Fraction(v).limit_denominator(1000)) for v in opts])
print("Inverse differences:", [1 / opts[i + 1] - 1 / opts[i] for i in range(6)])
state = dict(
    algo_name="pgm",
    problem_type="composite",
    obj_tag="f",
    params_json=json.dumps({"L": 1, "R": 1}),
    performance_metric="h(x_N)-h(x_star)",
    initial_condition="||x_0-x_star||^2 <= R^2",
    conjectured_rate="L*R**2/(4*N)",
    setup_file="pgm_setup.py",
    sweep_results=results,
    N_verify=4,
    numerical_certificate_verified=False,
    analytic_full_pep_verified=False,
    lyapunov_proof_verified=False,
)
(root / "state").mkdir(exist_ok=True)
(root / "state/pgm_b1.json").write_text(json.dumps(state, indent=2))
setup = (root / "pgm_setup.py").read_text(encoding="utf-8-sig")
objects = setup[setup.index("L =") : setup.index("\ndef make_ctx")]
functions = setup[setup.index("def make_ctx") :]
nb = nbf.v4.new_notebook()
nb.cells = [
    nbf.v4.new_markdown_cell(r"""# Proximal gradient: composite convex minimization
Let $f$ be convex and $L$-smooth, $L>0$, and let $g$ be closed, proper and convex on a finite-dimensional real Euclidean space. Write $h=f+g$. Assume $x_\star$ minimizes $h$, $R\geq0$, and $\|x_0-x_\star\|^2\leq R^2$. For integer $N\geq1$, perform
$$x_{k+1}=\operatorname{prox}_{g/L}\left(x_k-\frac1L\nabla f(x_k)\right),\qquad k=0,\ldots,N-1.$$
The performance metric is $h(x_N)-h(x_\star)$. Proximal optimality is encoded as $L(x_k-x_{k+1})-\nabla f(x_k)\in\partial g(x_{k+1})$. Stationarity is imposed on the sum, not separately on its components."""),
    nbf.v4.new_markdown_cell(
        "## Proof statement\nPending Blocks 2–5: the numerical conjecture below is not yet a theorem."
    ),
    nbf.v4.new_code_cell(
        'from pathlib import Path\nimport sys\nimport json\nnotebook_dir = Path.cwd().resolve()\nrepo_root = notebook_dir / "supplementary" / "approved"\nsys.path[:0] = [str(repo_root), str(notebook_dir), str(notebook_dir / "supplementary" / "helpers")]\nimport runtime\nimport pepflow as pf\nimport numpy as np\nimport matplotlib.pyplot as plt\nassert Path(pf.__file__).resolve().is_relative_to(repo_root)\nprint("Framework:", pf.__file__)'
    ),
    nbf.v4.new_markdown_cell("## Function and parameter definitions"),
    nbf.v4.new_code_cell(objects.strip()),
    nbf.v4.new_markdown_cell("## Algorithm and PEP setup"),
    nbf.v4.new_code_cell(
        functions.strip()
        + '\n\nctx_check, pb_check, obj_check = get_pep_setup(4, {"L": 1, "R": 1})\nprint("Setup built for N=4; metric:", pb_check.performance_metric)'
    ),
    nbf.v4.new_markdown_cell(
        "## Numerical evidence\nThe required N=1,…,7 sweep uses CLARABEL with default options and normalized L=R=1. The saved results below come from this attempt. Status `optimal_inaccurate` at N=6 and N=7 is retained. The reciprocal values increase by approximately four."
    ),
    nbf.v4.new_code_cell(
        'b1 = json.loads((notebook_dir / "state/pgm_b1.json").read_text())\nrows = b1["sweep_results"]\nns = np.array([r["N"] for r in rows])\nvalues = np.array([r["opt_value"] for r in rows])\nguess = 1 / (4 * ns)\nfor row in rows:\n    print(f"N={row[\'N\']}: {row[\'opt_value\']:.10f} ({row[\'solver_status\']})")\nprint("Maximum discrepancy from candidate:", np.max(np.abs(values - guess)))\nprint("Reciprocal differences:", np.diff(1 / values))\nfig, ax = plt.subplots(figsize=(6, 3.6))\nax.plot(ns, values, "o", label="PEP optimum")\nax.plot(ns, guess, "-", label="Candidate 1/(4N)")\nax.set(xlabel="N", ylabel="Objective gap", title="Proximal-gradient numerical evidence")\nax.legend()\nax.grid(alpha=0.25)\nplt.show()'
    ),
    nbf.v4.new_markdown_cell(r"""The numerical conjecture, restoring objective and distance scaling, is
$$h(x_N)-h(x_\star)\leq\frac{LR^2}{4N}.$$
This is numerical evidence only. The certificate, Lyapunov construction, basis and exact identities remain pending."""),
    nbf.v4.new_markdown_cell("## Dense and relaxed proof solves\nPending Block 2."),
    nbf.v4.new_markdown_cell("## Lambda and S verification\nPending Block 2."),
    nbf.v4.new_markdown_cell(
        "## Partial-sum Lyapunov construction and ranks\nPending Block 3."
    ),
    nbf.v4.new_markdown_cell(
        "## Identify the vectors composing the Lyapunov function\nPending Block 4."
    ),
    nbf.v4.new_markdown_cell(
        "## Coefficient extraction and closed-form Lyapunov function\nPending Blocks 4–5."
    ),
    nbf.v4.new_markdown_cell(
        "## Symbolic step, base and boundary identities\nPending Block 5."
    ),
]
nb.metadata.kernelspec = dict(
    display_name="Pinned Python", language="python", name="pgm-attempt"
)
nbf.write(nb, root / "pgm_example_lyap.ipynb")
