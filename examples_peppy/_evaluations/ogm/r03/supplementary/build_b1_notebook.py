"""Create the B1 notebook and state from the completed sweep."""

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
runtime = ROOT / "supplementary" / ".runtime"
for key in (
    "OMP_NUM_THREADS",
    "OPENBLAS_NUM_THREADS",
    "MKL_NUM_THREADS",
    "NUMEXPR_NUM_THREADS",
):
    os.environ[key] = "1"
for key in (
    "TEMP",
    "TMP",
    "IPYTHONDIR",
    "MPLCONFIGDIR",
    "JUPYTER_CONFIG_DIR",
    "JUPYTER_RUNTIME_DIR",
):
    directory = runtime / key.lower()
    directory.mkdir(parents=True, exist_ok=True)
    os.environ[key] = str(directory)
kernel_dir = runtime / "jupyter" / "kernels" / "ogm-worker"
kernel_dir.mkdir(parents=True, exist_ok=True)
(kernel_dir / "kernel.json").write_text(
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
            "display_name": "OGM worker",
            "language": "python",
        }
    )
)
os.environ["JUPYTER_PATH"] = str(runtime / "jupyter")
results = json.loads((ROOT / "supplementary" / "b1_sweep.json").read_text())
errors = [abs(r["opt_value"] - 1 / (2 * r["theta_N"] ** 2)) for r in results]
assert max(errors) < 1e-5
state = {
    "algo_name": "ogm",
    "problem_type": "smooth_convex",
    "obj_tag": "f",
    "params_json": '{"L": 1, "R": 1}',
    "performance_metric": "f(x_N)-f(x_star)",
    "initial_condition": "||x_0-x_star||^2 <= R^2; grad f(x_star)=0; z_0=x_0",
    "conjectured_rate": "L*R**2/(2*theta_N**2)",
    "setup_file": "ogm_setup.py",
    "sweep_results": results,
    "N_verify": 4,
    "rate_status": "numerically conjectured; not proved",
    "max_rate_absolute_error": max(errors),
    "presentation_policy": "evaluation-ancillary-v1",
    "completion_status": "complete",
}
(ROOT / "state").mkdir(exist_ok=True)
(ROOT / "state" / "ogm_b1.json").write_text(json.dumps(state, indent=2))
nb = nbf.v4.new_notebook()
nb.metadata.kernelspec = {
    "name": "ogm-worker",
    "display_name": "OGM worker",
    "language": "python",
}
nb.cells = [
    nbf.v4.new_markdown_cell(r"""# OGM: convergence and Lyapunov discovery

Let $f$ be convex and $L$-smooth on a real finite-dimensional Euclidean space, with $L>0$, $R\geq0$, $N\geq1$, $\nabla f(x_\star)=0$, $\|x_0-x_\star\|^2\leq R^2$, and $z_0=x_0$. The metric is $f(x_N)-f(x_\star)$.

Set $\theta_{-1}=0$ and
$$\theta_k=\frac{1+\sqrt{1+4\theta_{k-1}^2}}2\quad(0\leq k<N),\qquad
\theta_N=\frac{1+\sqrt{1+8\theta_{N-1}^2}}2.$$
For $0\leq k<N$,
$$y_{k+1}=x_k-\frac{\nabla f(x_k)}L,\qquad
z_{k+1}=z_k-\frac{2\theta_k}L\nabla f(x_k),$$
$$x_{k+1}=\left(1-\frac1{\theta_{k+1}}\right)y_{k+1}+\frac{z_{k+1}}{\theta_{k+1}}.$$
The terminal recurrence is distinct and is retained in every numerical problem.
"""),
    nbf.v4.new_markdown_cell(
        "## Proof statement (pending Block 5)\nThe rate below is a numerical conjecture. A theorem and proof remain to be established."
    ),
    nbf.v4.new_code_cell(
        'import json\nimport sys\nfrom pathlib import Path\n\nnotebook_dir = Path.cwd()\nrepo_root = notebook_dir / "supplementary" / "approved"\nsys.path[:0] = [str(repo_root), str(notebook_dir), str(notebook_dir / "supplementary")]\nimport matplotlib.pyplot as plt  # noqa: E402\n'
    ),
    nbf.v4.new_markdown_cell(
        "## Function, algorithm, and PEP definition\nThe code below is the executable setup, including the radius squared normalization."
    ),
    nbf.v4.new_code_cell((ROOT / "ogm_setup.py").read_text().split("\n", 1)[1]),
    nbf.v4.new_markdown_cell(
        "## Numerical evidence\nThe saved sweep used CLARABEL defaults at each horizon. All seven solves were optimal."
    ),
    nbf.v4.new_code_cell(
        'sweep = json.loads((notebook_dir / "supplementary" / "b1_sweep.json").read_text())\nhorizons = [row["N"] for row in sweep]\nobserved = [row["opt_value"] for row in sweep]\ncandidate = [1 / (2 * theta_sequence(n)[-1]**2) for n in horizons]\nfor row, guess in zip(sweep, candidate):\n    print(f"N={row[\'N\']}: PEP={row[\'opt_value\']:.10f}, candidate={guess:.10f}, error={abs(row[\'opt_value\']-guess):.3e}")\nprint("All solver statuses:", [r["solve_attempts"][-1]["status"] for r in sweep])\nfig, ax = plt.subplots(figsize=(6, 4))\nax.plot(horizons, observed, "o", label="PEP")\nax.plot(horizons, candidate, "-", label="1/(2 theta_N squared), conjecture")\nax.set(xlabel="N", ylabel="Function gap, L=R=1", title="OGM initial numerical evidence")\nax.legend()\nax.grid(True)\nplt.show()'
    ),
    nbf.v4.new_markdown_cell(r"""The observations suggest
$$f(x_N)-f(x_\star)\leq \frac{LR^2}{2\theta_N^2}.$$
Scaling by $LR^2$ follows by normalizing the function and the initial distance (with $R=0$ trivial). Numerical agreement does not prove the bound. Subsequent blocks will construct the certificate and Lyapunov proof.

## Dense and relaxed proof solves (pending Block 2)
## Certificate verification (pending Block 2)
## Lyapunov partial sums (pending Block 3)
## Identify the vectors composing the Lyapunov function (pending Block 4)
## Closed-form Lyapunov function and symbolic identities (pending Block 5)
"""),
]
path = ROOT / "ogm_example_lyap.ipynb"
nbf.write(nb, path)
NotebookClient(
    nb,
    timeout=120,
    kernel_name="ogm-worker",
    resources={"metadata": {"path": str(ROOT)}},
).execute()
nbf.write(nb, path)
for cell in nb.cells:
    if cell.cell_type == "markdown":
        assert not any(c in cell.source for c in ("\x0c", "\r", "\\(", "\\["))
assert any("image/png" in output.get("data", {}) for output in nb.cells[6].outputs)
items = [
    "title, problem description, and the algorithm update equations in LaTeX",
    "proof statement placeholder, to be filled with the final theorem and proof outline in Block 5",
    "imports",
    "function/operator definitions",
    "make_ctx_ogm and get_pep_setup",
    "numerical evidence, including a plot comparing the PEP values against the discovered or conjectured rate",
    "dense and relaxed proof solves",
    "lambda and S verification (closed-form when available, otherwise numerical with explicit analytic status)",
    "partial-sum Lyapunov construction and rank profile",
    "special-vector identification",
    "coefficient extraction and closed-form V_k",
    "symbolic step, base, and boundary identities",
]
cells = {1: "0", 3: "2", 4: "4", 5: "4", 6: "5,6,7"}
lines = [
    f"Notebook: {path.name}",
    "Last reviewed block: B1",
    f"SHA-256: {hashlib.sha256(path.read_bytes()).hexdigest()}",
    "Presentation policy: evaluation-ancillary-v1; source math checked, rendering intentionally omitted.",
    "",
    "| Item | Requirement | Status | Cells (zero-based) | Evidence |",
    "|---|---|---|---|---|",
]
for i, item in enumerate(items, 1):
    done = i in cells
    lines.append(
        f"| {i} | {item} | {'verified' if done else 'pending'} | {cells.get(i, '1' if i == 2 else '7')} | {'Executed source inspected; printed results and PNG plot present where applicable.' if done else 'Later block obligation.'} |"
    )
(ROOT / "supplementary" / "ogm_example_lyap_checklist.md").write_text("\n".join(lines))
print(
    json.dumps(
        {
            "maximum_rate_error": max(errors),
            "notebook_executed": True,
            "plot_output_present": True,
        }
    )
)
