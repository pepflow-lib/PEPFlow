"""Build the initial notebook and execute in the private kernel."""

import hashlib
import json
import os
import sys
from pathlib import Path

# optional notebook-generation dependency
import nbformat  # ty: ignore[unresolved-import]

# optional notebook-generation dependency
from nbclient import NotebookClient  # ty: ignore[unresolved-import]

ROOT = Path(__file__).resolve().parents[1]
SUP = ROOT / "supplementary"
RT = SUP / ".runtime"
for key in [
    "OMP_NUM_THREADS",
    "OPENBLAS_NUM_THREADS",
    "MKL_NUM_THREADS",
    "NUMEXPR_NUM_THREADS",
]:
    os.environ[key] = "1"
for key in [
    "TEMP",
    "TMP",
    "TMPDIR",
    "IPYTHONDIR",
    "MPLCONFIGDIR",
    "JUPYTER_RUNTIME_DIR",
    "JUPYTER_CONFIG_DIR",
]:
    path = RT / key.lower()
    path.mkdir(parents=True, exist_ok=True)
    os.environ[key] = str(path)
kernels = RT / "jupyter" / "kernels" / "attempt"
kernels.mkdir(parents=True, exist_ok=True)
(kernels / "kernel.json").write_text(
    json.dumps(
        {
            "argv": [
                sys.executable,
                "-I",
                "-B",
                "-m",
                "ipykernel_launcher",
                "-f",
                "{connection_file}",
            ],
            "display_name": "Attempt Python",
            "language": "python",
        }
    )
)
os.environ["JUPYTER_PATH"] = str(RT / "jupyter")
results = json.loads((SUP / "_sweep_tmp.json").read_text())
assert len(results) == 7
state = {
    "algo_name": "dual_feg",
    "problem_type": "monotone_operator",
    "obj_tag": "A",
    "params_json": json.dumps({"L": 1, "R": 1}),
    "performance_metric": "||A(x_N)||^2",
    "initial_condition": "A(x_star)=0, ||x_0-x_star||^2 <= R^2, z_0=0",
    "conjectured_rate": "4*L**2*R**2/N**2",
    "rate_note": "N=2..7 match; N=1 numerical value is 2*L**2*R**2 (optimal_inaccurate).",
    "setup_file": "dual_feg_setup.py",
    "sweep_results": results,
    "N_verify": 6,
    "presentation_policy": "evaluation-ancillary-v1",
}
(ROOT / "state").mkdir(exist_ok=True)
(ROOT / "state" / "dual_feg_b1.json").write_text(json.dumps(state, indent=2))
source = (ROOT / "dual_feg_setup.py").read_text(encoding="utf-8-sig")
defs = source[source.index("L = pf.Parameter") : source.index("def make_ctx")]
algorithm = source[source.index("def make_ctx") :]
nb = nbformat.v4.new_notebook()
md = nbformat.v4.new_markdown_cell
code = nbformat.v4.new_code_cell
nb.cells = [
    md(r"""# Dual FEG: convergence discovery

Let $A$ be monotone and $L$-Lipschitz on a real finite-dimensional Euclidean space, with $L>0$, $R\geq0$, integer $N\geq1$, $A(x_\star)=0$, and $\|x_0-x_\star\|^2\leq R^2$. Set $z_0=0$ and $\alpha=1/L$. For $k=0,\ldots,N-1$,
$$x_{k+1/2}=x_k-\alpha z_k-\alpha A(x_k),$$
$$x_{k+1}=x_{k+1/2}-\frac{N-k-1}{N-k}\alpha\bigl(A(x_{k+1/2})-A(x_k)\bigr),$$
$$z_{k+1}=\frac{N-k-1}{N-k}z_k-\frac{A(x_{k+1/2})}{N-k}.$$
We select the terminal squared residual $\|A(x_N)\|^2$ as metric. Pairwise monotonicity and Lipschitz constraints give a valid PEP relaxation; interpolation sufficiency is not assumed."""),
    md(
        "## Proof statement (pending)\nThe conjectured bound is $4L^2R^2/N^2$. Later blocks must establish a certificate and exact Lyapunov proof."
    ),
    code("""import json
import sys
from pathlib import Path
import matplotlib.pyplot as plt
import numpy as np

NOTEBOOK_DIR = Path.cwd()
REPO_ROOT = NOTEBOOK_DIR / "supplementary" / "approved"
sys.path[:0] = [str(REPO_ROOT), str(NOTEBOOK_DIR / "supplementary"), str(NOTEBOOK_DIR)]
"""),
    code("""import pepflow as pf
import sympy as sp
print("Framework origin:", pf.__file__)"""),
    md("## Operator and parameters"),
    code(defs),
    md("## Algorithm and PEP setup"),
    code(algorithm),
    code("""ctx_check, pb_check, operator_check = get_pep_setup(2, {"L": 1, "R": 1})
assert ctx_check["z_0"].equiv_by_randomness(pf.Vector.zero())
print("Setup constructed; z_0 is zero.")"""),
    md("## Numerical evidence"),
    code("""state = json.loads((NOTEBOOK_DIR / "state" / "dual_feg_b1.json").read_text())
rows = state["sweep_results"]
for row in rows:
    print(f"N={row['N']}: {row['opt_value']:.10f}, {row['status']}")
ns = np.array([row["N"] for row in rows])
values = np.array([row["opt_value"] for row in rows])
candidate = 4.0 / ns**2
print("Maximum absolute fit residual for N>=2:", np.max(np.abs(values[1:] - candidate[1:])))
plt.plot(ns, values, "o-", label="PEP relaxation")
plt.plot(ns, candidate, "--", label="Conjecture 4/N^2")
plt.xlabel("Horizon N")
plt.ylabel("Squared residual, L=R=1")
plt.legend()
plt.grid(True)
plt.show()"""),
    md(
        r"The data suggest $\|A(x_N)\|^2\leq4L^2R^2/N^2$. At $N=1$ the numerical value is approximately $2L^2R^2$ and the status is optimal_inaccurate. Remaining sweep statuses are optimal. Numerical evidence is not an arbitrary-horizon proof."
    ),
    md("## Full PEP certificate\nPending Block 2."),
    md("## Lyapunov partial sums\nPending Block 3."),
    md("## Special vectors and coefficients\nPending Block 4."),
    md("## Exact Lyapunov theorem and identities\nPending Block 5."),
]
path = ROOT / "dual_feg_example_lyap.ipynb"
nbformat.write(nb, path)
NotebookClient(
    nb, timeout=180, kernel_name="attempt", resources={"metadata": {"path": str(ROOT)}}
).execute()
nbformat.write(nb, path)
summary = []
for i, cell in enumerate(nb.cells):
    texts = [
        o.get("text", "") for o in cell.get("outputs", []) if o.output_type == "stream"
    ]
    summary.append(
        {
            "cell": i,
            "id": cell.id,
            "type": cell.cell_type,
            "outputs": texts,
            "has_plot": any(
                "image/png" in o.get("data", {}) for o in cell.get("outputs", [])
            ),
        }
    )
    if cell.cell_type == "markdown":
        assert "\\(" not in cell.source and "\\[" not in cell.source
        assert not any(ord(ch) < 32 and ch not in "\n\t" for ch in cell.source)
(SUP / "b1-notebook-inspection.json").write_text(json.dumps(summary, indent=2))
items = [
    "title, problem description, and the algorithm update equations in LaTeX",
    "proof statement placeholder, to be filled with the final theorem and proof outline in Block 5",
    "imports",
    "function/operator definitions",
    "make_ctx_dual_feg and get_pep_setup",
    "numerical evidence, including a plot comparing the PEP values against the discovered or conjectured rate",
    "dense and relaxed proof solves",
    "lambda and S verification (closed-form when available, otherwise numerical with explicit analytic status)",
    "partial-sum Lyapunov construction and rank profile",
    "special-vector identification",
    "coefficient extraction and closed-form V_k",
    "symbolic step, base, and boundary identities",
]
verified = {1: "0", 3: "2,3", 4: "5", 5: "7,8", 6: "10,11"}
lines = [
    f"# Evidence checklist\nNotebook: {path.name}\nLast reviewed block: B1\nSHA-256: {hashlib.sha256(path.read_bytes()).hexdigest()}\nPresentation policy: evaluation-ancillary-v1; source and executed outputs inspected; no visual rendering review.\n",
    "| Item | Status | Cells (zero-based) | Evidence |",
    "|---|---|---|---|",
]
for i, item in enumerate(items, 1):
    status = "verified" if i in verified else "pending"
    evidence = (
        "Executed source/output inspected; see b1-notebook-inspection.json."
        if i in verified
        else "Later-block requirement."
    )
    lines.append(f"| {i}. {item} | {status} | {verified.get(i, '')} | {evidence} |")
(SUP / "dual_feg_example_lyap_checklist.md").write_text("\n".join(lines))
print(json.dumps(summary, indent=2))
