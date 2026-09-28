"""Create and execute the B1 notebook using the saved sweep."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent / "helpers"))
from runtime import configure, NOTEBOOK_DIR  # noqa: E402

configure()
import json  # noqa: E402
import nbformat as nbf  # noqa: E402
from nbclient import NotebookClient  # noqa: E402
from jupyter_client.kernelspec import KernelSpecManager  # noqa: E402
from jupyter_client import KernelManager  # noqa: E402

results = json.loads((NOTEBOOK_DIR / "supplementary/_sweep_tmp.json").read_text())
state = {
    "algo_name": "pgm", "problem_type": "composite", "obj_tag": "f",
    "params_json": json.dumps({"L": 1, "R": 1}),
    "performance_metric": "h(x_N) - h(x_star)",
    "initial_condition": "||x_0-x_star||^2 <= R^2",
    "conjectured_rate": "L*R**2/(4*N)",
    "setup_file": "pgm_setup.py", "sweep_results": results, "N_verify": 4,
    "assistance": "Fixed PGM SOS aid from approved/input.md; candidate, unverified",
    "presentation_policy": "evaluation-ancillary-v1",
    "rate_status": "Numerical conjecture; analytic proof pending",
}
(NOTEBOOK_DIR / "state").mkdir(exist_ok=True)
(NOTEBOOK_DIR / "state/pgm_b1.json").write_text(json.dumps(state, indent=2))
nb = nbf.v4.new_notebook()
cells = []
def md(s):
    cells.append(nbf.v4.new_markdown_cell(s))
def code(s):
    cells.append(nbf.v4.new_code_cell(s))
md(r"""# Proximal gradient: Lyapunov discovery

Let $f$ be convex and $L$-smooth, and let $g$ be closed, proper, and convex, on a finite-dimensional Euclidean space. Let $h=f+g$, $L>0$, $R\geq0$, and integer $N\geq1$. The minimizer $x_\star$ satisfies $\|x_0-x_\star\|^2\leq R^2$. Proximal updates and evaluations are well-defined.

$$x_{k+1}=\operatorname{prox}_{g/L}\left(x_k-\frac1L\nabla f(x_k)\right),\qquad k=0,\ldots,N-1.$$

The performance metric is $h(x_N)-h(x_\star)$. The rate was unknown at dispatch.
""")
md(r"""## Proof statement (pending)

Numerical conjecture: $h(x_N)-h(x_\star)\leq LR^2/(4N)$. A theorem and proof will be added only after the required certificate and exact Lyapunov checks.

Declared assistance: the fixed SOS candidate in the supplied packet. Its compatibility with the certificate remains unverified. No aid formulas are imposed on this numerical sweep.
""")
code('''import sys
from pathlib import Path

notebook_dir = Path.cwd().resolve()
repo_root = notebook_dir / "supplementary" / "approved"
sys.path[:0] = [str(repo_root), str(notebook_dir), str(notebook_dir / "supplementary" / "helpers")]
''')
code('''from runtime import configure
configure()''')
code('''
import json
import pepflow as pf
import numpy as np
import matplotlib.pyplot as plt
''')
setup = (NOTEBOOK_DIR / "pgm_setup.py").read_text()
code(setup[setup.index('L = pf.Parameter'):setup.index('def make_ctx_pgm')].strip())
code(setup[setup.index('def make_ctx_pgm'):])
md("## Numerical evidence")
code('''state = json.loads((notebook_dir / "state" / "pgm_b1.json").read_text())
sweep = state["sweep_results"]
horizons = np.array([row["N"] for row in sweep])
values = np.array([row["opt_value"] for row in sweep])
candidate = 1 / (4 * horizons)
for row in sweep:
    print(f"N={row['N']}: {row['opt_value']:.10f} ({row['status']}, {row['solver']})")
print("Inverse values:", 1 / values)
print("Maximum absolute discrepancy:", np.max(np.abs(values - candidate)))
assert np.max(np.abs(values - candidate)) <= 1e-5
assert all(row["status"] == "optimal" for row in sweep)
fig, ax = plt.subplots()
ax.plot(horizons, values, "o", label="PEP: CLARABEL defaults")
ax.plot(horizons, candidate, "-", label="Conjecture 1/(4N)")
ax.set(xlabel="N", ylabel="Objective gap, L=R=1")
ax.legend()
ax.grid(True)
plt.show()
''')
md(r"""The observed inverse values are approximately $4,8,\ldots,28$. Homogeneity in $L$ and in the squared radius gives the conjecture $LR^2/(4N)$. This is numerical evidence; later blocks must establish the certificate and exact proof.

## Full-PEP certificate (pending)
## Lyapunov partial sums (pending)
## Special vectors (pending)
## Closed-form coefficients and exact identities (pending)
""")
nb.cells = cells
nb.metadata.kernelspec = {"display_name": "Attempt Python", "language": "python", "name": "attempt"}
path = NOTEBOOK_DIR / "pgm_example_lyap.ipynb"
nbf.write(nb, path)
kernel_dir = NOTEBOOK_DIR / "supplementary/.runtime/kernels/attempt"
kernel_dir.mkdir(parents=True, exist_ok=True)
(kernel_dir / "kernel.json").write_text(json.dumps({
    "argv": [sys.executable, "-I", "-B", "-m", "ipykernel_launcher", "-f", "{connection_file}"],
    "display_name": "Attempt Python", "language": "python"}))
ksm = KernelSpecManager(kernel_dirs=[str(kernel_dir.parent)])
km = KernelManager(kernel_name="attempt", kernel_spec_manager=ksm)
NotebookClient(nb, km=km, timeout=120,
    resources={"metadata": {"path": str(NOTEBOOK_DIR)}}).execute()
nbf.write(nb, path)
print("Notebook executed:", path)

