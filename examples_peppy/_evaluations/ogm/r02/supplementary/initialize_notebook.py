"""Author and execute the B1 notebook without repeating its numerical sweep."""

import hashlib
import json
import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RUNTIME = ROOT / "supplementary" / ".runtime"
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
    "IPYTHONDIR",
    "JUPYTER_RUNTIME_DIR",
    "JUPYTER_CONFIG_DIR",
    "MPLCONFIGDIR",
    "XDG_CACHE_HOME",
]:
    location = RUNTIME / key.lower()
    location.mkdir(parents=True, exist_ok=True)
    os.environ[key] = str(location)
kernel_root = RUNTIME / "jupyter"
kernel_dir = kernel_root / "kernels" / "ogm-owned"
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
            "display_name": "OGM owned isolated kernel",
            "language": "python",
        }
    )
)
os.environ["JUPYTER_PATH"] = str(kernel_root)

# optional notebook-generation dependency
import nbformat as nbf  # noqa: E402  # ty: ignore[unresolved-import]

# optional notebook-generation dependency
from nbclient import NotebookClient  # noqa: E402  # ty: ignore[unresolved-import]

sweep = json.loads((ROOT / "supplementary" / "_sweep_tmp.json").read_text())
state = {
    "algo_name": "ogm",
    "problem_type": "smooth_convex",
    "obj_tag": "f",
    "params_json": '{"L": 1, "R": 1}',
    "performance_metric": "f(x_N) - f(x_star)",
    "initial_condition": "||x_0-x_star||^2 <= R^2; z_0=x_0; grad f(x_star)=0",
    "conjectured_rate": "L*R**2/(2*theta_N**2)",
    "setup_file": "ogm_setup.py",
    "sweep_results": sweep,
    "N_verify": 6,
    "analytic_status": "unproved numerical conjecture",
    "theta_representation": "floating-point recurrence for finite PEP samples",
    "presentation_policy": "evaluation-ancillary-v1",
}
(ROOT / "state").mkdir(exist_ok=True)
(ROOT / "state" / "ogm_b1.json").write_text(json.dumps(state, indent=2))

setup = (ROOT / "ogm_setup.py").read_text()
definitions = setup[setup.index("L = pf.Parameter") : setup.index("def theta_sequence")]
builders = setup[setup.index("def theta_sequence") :]
imports = """import json
import sys
from math import sqrt
from pathlib import Path

notebook_dir = Path.cwd().resolve()
repo_root = notebook_dir / "supplementary" / "approved"
sys.path[:0] = [str(repo_root), str(notebook_dir), str(notebook_dir / "supplementary")]
import matplotlib.pyplot as plt  # noqa: E402 -- approved source path must be set first
import numpy as np  # noqa: E402
import pepflow as pf  # noqa: E402

assert Path(pf.__file__).resolve().parent == repo_root / "pepflow"
print("Framework:", pf.__file__)
"""
intro = r"""# OGM: smooth convex minimization

Let $f$ be convex and $L$-smooth on a finite-dimensional Euclidean space, with $L>0$ and $R\ge0$.
Assume $\nabla f(x_\star)=0$, $\|x_0-x_\star\|^2\le R^2$, and $z_0=x_0$.
For integer $N\ge1$, the metric is $f(x_N)-f(x_\star)$.
Set $\theta_{-1}=0$ and
$$\theta_k=\frac{1+\sqrt{1+4\theta_{k-1}^2}}2\quad(0\le k<N),\qquad
\theta_N=\frac{1+\sqrt{1+8\theta_{N-1}^2}}2.$$
For $k=0,\ldots,N-1$, perform
$$y_{k+1}=x_k-\frac1L\nabla f(x_k),\qquad
z_{k+1}=z_k-\frac{2\theta_k}{L}\nabla f(x_k),$$
$$x_{k+1}=\left(1-\frac1{\theta_{k+1}}\right)y_{k+1}+\frac{z_{k+1}}{\theta_{k+1}}.$$
The special terminal recurrence is part of the algorithm. Finite PEP samples use floating-point theta values; arbitrary-horizon proof remains a later obligation.
"""
evidence = """b1 = json.loads((notebook_dir / "state" / "ogm_b1.json").read_text())
rows = b1["sweep_results"]
Ns = np.array([r["N"] for r in rows])
values = np.array([r["opt_value"] for r in rows])
candidate = np.array([1 / (2 * theta_sequence(r["N"])[-1]**2) for r in rows])
for row, guess in zip(rows, candidate):
    print(f'N={row["N"]}: PEP={row["opt_value"]:.10f}, candidate={guess:.10f}, status={row["status"]}')
error = float(np.max(np.abs(values - candidate)))
print("Maximum absolute discrepancy:", error)
assert error < 1e-5
fig, ax = plt.subplots(figsize=(6, 3.5))
ax.plot(Ns, values, "o", label="PEP (CLARABEL defaults)")
ax.plot(Ns, candidate, "-", label=r"Conjecture $1/(2\\theta_N^2)$")
ax.set(xlabel="N", ylabel="Worst-case function gap", title="OGM numerical evidence, L=R=1")
ax.legend()
ax.grid(alpha=0.25)
plt.show()
"""
cells = [
    nbf.v4.new_markdown_cell(intro, id="b1-algorithm"),
    nbf.v4.new_markdown_cell(
        "## Proof statement (pending Block 5)\nThe conjectured bound will be proved only after certificate and Lyapunov verification.",
        id="proof-placeholder",
    ),
    nbf.v4.new_code_cell(imports, id="b1-imports"),
    nbf.v4.new_code_cell(definitions, id="b1-functions"),
    nbf.v4.new_code_cell(builders, id="b1-setup"),
    nbf.v4.new_code_cell(
        'sample_ctx, sample_pb, sample_f = get_pep_setup(6, {"L": 1, "R": 1})\nprint("Context and metric constructed:", sample_pb.performance_metric)\n',
        id="b1-setup-check",
    ),
    nbf.v4.new_markdown_cell(
        "## Numerical evidence\nThis is the saved single B1 sweep, not a repeated solve. Every solve used CLARABEL defaults and returned optimal.",
        id="b1-evidence-heading",
    ),
    nbf.v4.new_code_cell(evidence, id="b1-evidence"),
    nbf.v4.new_markdown_cell(
        r"The numerics suggest $f(x_N)-f(x_\star)\le LR^2/(2\theta_N^2)$. Scaling follows by normalizing distances by $R$ and function values by $LR^2$ when $R>0$; $R=0$ starts at a stationary minimizer. This remains a conjecture until proved. The next blocks will supply the certificate, Lyapunov construction, and exact identities.",
        id="b1-conjecture",
    ),
    nbf.v4.new_markdown_cell(
        "## Full PEP proof certificate (Block 2 pending)", id="b2-placeholder"
    ),
    nbf.v4.new_markdown_cell(
        "## Lyapunov partial sums (Block 3 pending)", id="b3-placeholder"
    ),
    nbf.v4.new_markdown_cell(
        "## Special vectors and coefficients (Block 4 pending)", id="b4-placeholder"
    ),
    nbf.v4.new_markdown_cell(
        "## Exact Lyapunov theorem and identities (Block 5 pending)",
        id="b5-placeholder",
    ),
]
notebook = nbf.v4.new_notebook(cells=cells)
notebook.metadata["kernelspec"] = {
    "name": "ogm-owned",
    "display_name": "OGM owned isolated kernel",
    "language": "python",
}
notebook.metadata["language_info"] = {"name": "python", "version": "3.11.13"}
path = ROOT / "ogm_example_lyap.ipynb"
nbf.write(notebook, path)
NotebookClient(
    notebook,
    timeout=120,
    kernel_name="ogm-owned",
    resources={"metadata": {"path": str(ROOT)}},
).execute()
nbf.write(notebook, path)
for cell in notebook.cells:
    if cell.cell_type == "markdown":
        assert not any(
            char in cell.source for char in ["\x0c", "\r", "\\(", "\\)", "\\[", "\\]"]
        )
plot_outputs = [
    o
    for c in notebook.cells
    for o in c.get("outputs", [])
    if "image/png" in o.get("data", {})
]
assert plot_outputs
print(
    json.dumps(
        {
            "notebook": str(path),
            "sha256": hashlib.sha256(path.read_bytes()).hexdigest(),
            "clean_kernel_execution": "passed",
            "plot_outputs": len(plot_outputs),
            "markdown_source_checks": "passed",
            "rendered_inspection": "omitted per evaluation policy",
        }
    )
)
