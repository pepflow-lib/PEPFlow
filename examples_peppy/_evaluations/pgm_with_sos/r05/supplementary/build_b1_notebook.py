"""Build and execute this attempt's evolving notebook."""

import hashlib
import json
import os
import sys
from pathlib import Path

# optional notebook-generation dependency
import nbformat as nbf  # ty: ignore[unresolved-import]

# optional notebook-generation dependency
from nbclient import NotebookClient  # ty: ignore[unresolved-import]

ROOT = Path(__file__).resolve().parents[1]
RUNTIME = ROOT / "supplementary" / ".runtime"
for variable in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS"):
    os.environ[variable] = "1"
for variable in (
    "TEMP",
    "TMP",
    "IPYTHONDIR",
    "MPLCONFIGDIR",
    "JUPYTER_RUNTIME_DIR",
    "JUPYTER_CONFIG_DIR",
):
    folder = RUNTIME / variable.lower()
    folder.mkdir(parents=True, exist_ok=True)
    os.environ[variable] = str(folder)
kernel_root = RUNTIME / "jupyter"
kernel_dir = kernel_root / "kernels" / "attempt-pgm"
kernel_dir.mkdir(parents=True, exist_ok=True)
os.environ["JUPYTER_PATH"] = str(kernel_root)
kernel_dir.joinpath("kernel.json").write_text(
    json.dumps(
        {
            "argv": [
                str(Path(sys.executable)),
                "-I",
                "-B",
                "-m",
                "ipykernel_launcher",
                "-f",
                "{connection_file}",
            ],
            "display_name": "Attempt PGM",
            "language": "python",
        }
    )
)

sweep = json.loads((ROOT / "supplementary" / "b1_sweep.json").read_text())
state = {
    "algo_name": "pgm",
    "problem_type": "composite",
    "obj_tag": "f",
    "params_json": '{"L": 1, "R": 1}',
    "performance_metric": "h(x_N)-h(x_star)",
    "initial_condition": "||x_0-x_star||^2 <= R^2",
    "conjectured_rate": "L*R**2/(4*N)",
    "rate_status": "numerical_conjecture",
    "setup_file": "pgm_setup.py",
    "sweep_results": sweep,
    "N_verify": 4,
    "supplied_assistance": "Fixed SOS aid in approved/input.md; not used or verified in B1",
    "numerical_certificate_verified": False,
    "analytic_full_pep_verified": False,
    "lyapunov_proof_verified": False,
}
(ROOT / "state").mkdir(exist_ok=True)
(ROOT / "state" / "pgm_b1.json").write_text(json.dumps(state, indent=2))
setup = (ROOT / "pgm_setup.py").read_text()
definition_start = setup.index("L = pf.Parameter")
builder_start = setup.index("def make_ctx_pgm")
nb = nbf.v4.new_notebook()
md = nbf.v4.new_markdown_cell
code = nbf.v4.new_code_cell
nb.cells = [
    md(r"""# Proximal gradient: Lyapunov discovery

Let $f$ be convex and $L$-smooth with $L>0$, and let $g$ be closed, proper and convex on a finite-dimensional Euclidean space. Put $h=f+g$. Suppose $x_\star$ minimizes $h$, $R\geq0$, and $\|x_0-x_\star\|^2\leq R^2$. For integer $N\geq1$, the updates are
$$x_{k+1}=\operatorname{prox}_{g/L}\left(x_k-\frac1L\nabla f(x_k)\right),\qquad k=0,\ldots,N-1.$$
The performance metric is $h(x_N)-h(x_\star)$. The associated proximal subgradient is
$$s_{k+1}=L(x_k-x_{k+1})-\nabla f(x_k)\in\partial g(x_{k+1}).$$
"""),
    md(
        "## Proof statement (pending)\nThe all-horizon theorem and proof will be completed in Block 5. The rate below is currently a numerical conjecture. The fixed SOS aid was supplied in the case packet and has not yet been verified."
    ),
    code(
        "from pathlib import Path\nimport sys\nimport json\n\nnotebook_dir = Path.cwd().resolve()\nrepo_root = notebook_dir / 'supplementary' / 'approved'\nREPO_ROOT = repo_root\nsys.path[:0] = [str(repo_root), str(notebook_dir), str(notebook_dir / 'supplementary')]"
    ),
    code(
        "import pepflow as pf\nimport numpy as np\nimport matplotlib.pyplot as plt\n\nassert Path(pf.__file__).resolve().is_relative_to(repo_root)\nprint('Approved framework:', pf.__file__)"
    ),
    code(setup[definition_start:builder_start].strip()),
    code(setup[builder_start:].strip()),
    md(
        "## Numerical evidence\nA single sweep uses CLARABEL defaults with $L=R=1$. We retain its cached results rather than repeat the solve. Horizons 6 and 7 returned `optimal_inaccurate`; all others returned `optimal`. The largest deviation from $1/(4N)$ is printed below."
    ),
    code(
        "sweep = json.loads((notebook_dir / 'supplementary' / 'b1_sweep.json').read_text())\nns = np.array([row['N'] for row in sweep])\nvalues = np.array([row['opt_value'] for row in sweep])\nfor row in sweep:\n    print(f\"N={row['N']}: {row['opt_value']:.10f} ({row['status']})\")\nprint('Reciprocals:', 1 / values)\nprint('Reciprocal differences:', np.diff(1 / values))\nprint('Maximum candidate residual:', np.max(np.abs(values - 1 / (4 * ns))))\nfig, ax = plt.subplots()\nax.plot(ns, values, 'o', label='PEP sweep')\nax.plot(ns, 1 / (4 * ns), '-', label='Candidate 1/(4N)')\nax.set(xlabel='N', ylabel='h(x_N)-h(x_star)', title='Proximal-gradient numerical evidence, L=R=1')\nax.legend()\nplt.show()"
    ),
    md(r"""The reciprocal increments are approximately $4$, suggesting the conjecture
$$h(x_N)-h(x_\star)\leq\frac{LR^2}{4N}.$$
The $LR^2$ factor follows by scaling distances by $R$ and objective values by $LR^2$ when $R>0$. For $R=0$ the iteration starts at a minimizer and remains there. The numerical sweep is evidence, not an arbitrary-horizon proof. Blocks 2–5 will derive and verify the certificate and Lyapunov construction.
"""),
    md("## Full-PEP certificate (Block 2 pending)"),
    md("## Lyapunov partial sums (Block 3 pending)"),
    md("## Identify the vectors composing the Lyapunov function (Block 4 pending)"),
    md("## Closed form and symbolic proof identities (Block 5 pending)"),
]
nb.metadata["kernelspec"] = {
    "display_name": "Attempt PGM",
    "language": "python",
    "name": "attempt-pgm",
}
notebook = ROOT / "pgm_example_lyap.ipynb"
nbf.write(nb, notebook)
NotebookClient(
    nb,
    timeout=120,
    kernel_name="attempt-pgm",
    resources={"metadata": {"path": str(ROOT)}},
).execute()
nbf.write(nb, notebook)
for cell in nb.cells:
    if cell.cell_type == "markdown":
        assert "\\(" not in cell.source and "\\[" not in cell.source
        assert not any(ord(c) < 32 and c not in "\n\t" for c in cell.source)
items = [
    "title, problem description, and the algorithm update equations in LaTeX",
    "proof statement placeholder, to be filled with the final theorem and proof outline in Block 5",
    "imports",
    "function/operator definitions",
    "make_ctx_pgm and get_pep_setup",
    "numerical evidence, including a plot comparing the PEP values against the discovered or conjectured rate",
    "dense and relaxed proof solves",
    "lambda and S verification (closed-form when available, otherwise numerical with explicit analytic status)",
    "partial-sum Lyapunov construction and rank profile",
    "special-vector identification",
    "coefficient extraction and closed-form V_k",
    "symbolic step, base, and boundary identities",
]
evidence = {
    1: (
        "0",
        "Assumptions, metric, recurrence and proximal inclusion checked as source.",
    ),
    3: ("2,3", "Executed approved framework import and origin assertion."),
    4: ("4", "Smooth convex f, convex g, h=f+g and parameters."),
    5: ("5", "Executed full context builder and PEP setup definitions."),
    6: (
        "6,7,8",
        "Cached sweep printed; reciprocal increments and residual printed; matplotlib image output present.",
    ),
}
assert any("image/png" in out.get("data", {}) for out in nb.cells[7].outputs)
lines = [
    f"Notebook: {notebook}\nLast reviewed block: B1\nSHA-256: {hashlib.sha256(notebook.read_bytes()).hexdigest()}\n",
    "Presentation policy: evaluation-ancillary-v1; no rendered/image review performed. Source math delimiter checks passed.\n",
    "| Item | Requirement | Status | Cells | Evidence |",
    "|---|---|---|---|---|",
]
for i, item in enumerate(items, 1):
    cells, note = evidence.get(i, ("", "Pending owning block."))
    lines.append(
        f"| {i} | {item} | {'verified' if i in evidence else 'pending'} | {cells} | {note} |"
    )
(ROOT / "supplementary" / "pgm_example_lyap_checklist.md").write_text(
    "\n".join(lines), encoding="utf-8"
)
print(
    json.dumps(
        {
            "notebook_executed": True,
            "max_rate_residual": max(
                abs(row["opt_value"] - 1 / (4 * row["N"])) for row in sweep
            ),
        }
    )
)
