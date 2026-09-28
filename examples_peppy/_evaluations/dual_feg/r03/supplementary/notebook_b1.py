"""Build and execute the attempt's Block 1 notebook without repeating the sweep."""
import hashlib
import json
import os
from pathlib import Path

import nbformat as nbf
from nbclient import NotebookClient

ROOT = Path(__file__).resolve().parents[1]
RUNTIME = ROOT / "supplementary" / ".runtime"
for key in ["OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS", "NUMEXPR_NUM_THREADS"]:
    os.environ[key] = "1"
for key in ["TEMP", "TMP", "TMPDIR", "IPYTHONDIR", "MPLCONFIGDIR", "JUPYTER_RUNTIME_DIR", "JUPYTER_CONFIG_DIR", "XDG_CACHE_HOME"]:
    path = RUNTIME / key.lower()
    path.mkdir(parents=True, exist_ok=True)
    os.environ[key] = str(path)
kernel_root = RUNTIME / "jupyter"
os.environ["JUPYTER_PATH"] = str(kernel_root)
kernel = kernel_root / "kernels" / "attempt-kernel"
kernel.mkdir(parents=True, exist_ok=True)
settings = json.loads((ROOT / "supplementary/approved/settings.json").read_text())
(kernel / "kernel.json").write_text(json.dumps({
    "argv": [settings["python"], "-I", "-B", "-m", "ipykernel_launcher", "-f", "{connection_file}"],
    "display_name": "Attempt pinned Python", "language": "python"}))
setup = (ROOT / "dual_feg_setup.py").read_text()
defs = setup[setup.index("def make_ctx_dual_feg"):]
results = json.loads((ROOT / "supplementary/b1_sweep.json").read_text())
state = {
    "algo_name": "dual_feg", "problem_type": "monotone_operator", "obj_tag": "A",
    "params_json": '{"L": 1, "R": 1}', "performance_metric": "||A(x_N)||^2",
    "initial_condition": "A(x_star)=0; ||x_0-x_star||^2 <= R^2; z_0=0",
    "conjectured_rate": "4*L**2*R**2/N**2", "setup_file": "dual_feg_setup.py",
    "sweep_results": results, "N_verify": 4,
    "metric_selection": "Final operator residual; selected during B1 because input metric was unknown.",
    "rate_status": "numerical conjecture, not an analytic proof",
    "N1_note": "PEP value is 2*L**2*R**2, below the proposed uniform 4*L**2*R**2/N**2 bound.",
    "solver_policy": "CLARABEL defaults; fallback SCS only upon solver failure",
    "presentation_policy": "evaluation-ancillary-v1"
}
(ROOT / "state").mkdir(exist_ok=True)
(ROOT / "state/dual_feg_b1.json").write_text(json.dumps(state, indent=2))
md, code = nbf.v4.new_markdown_cell, nbf.v4.new_code_cell
cells = [md(r"""# Dual-FEG: numerical evidence and Lyapunov discovery

Let $A$ be monotone and $L$-Lipschitz on a real finite-dimensional Euclidean space, with $L>0$, $R\geq0$, $A(x_\star)=0$, and $\|x_0-x_\star\|^2\leq R^2$. Fix an integer horizon $N\geq1$, set $z_0=0$ and $\alpha=1/L$. For $k=0,\ldots,N-1$:
$$x_{k+1/2}=x_k-\alpha z_k-\alpha A(x_k),$$
$$x_{k+1}=x_{k+1/2}-\frac{N-k-1}{N-k}\alpha\big(A(x_{k+1/2})-A(x_k)\big),$$
$$z_{k+1}=\frac{N-k-1}{N-k}z_k-\frac{A(x_{k+1/2})}{N-k}.$$

The input leaves the performance metric unknown. We select the natural final residual $\|A(x_N)\|^2$ and investigate a uniform bound $4L^2R^2/N^2$. The PEP uses pairwise monotonicity and Lipschitz inequalities; its optimum is an upper relaxation bound, with no interpolation sufficiency claim."""),
md("## Proof statement (pending Block 5)\nThe candidate rate is numerical evidence only. Certificate, Lyapunov construction, and exact all-horizon proof remain pending."),
code('import sys\nfrom pathlib import Path\n\nnotebook_dir = Path.cwd().resolve()\nREPO_ROOT = notebook_dir / "supplementary" / "approved"\nsys.path[:0] = [str(REPO_ROOT), str(notebook_dir), str(notebook_dir / "supplementary")]'),
code('import json\nimport numpy as np\nimport matplotlib.pyplot as plt\nimport pepflow as pf\nimport sympy as sp'),
md("## Operator and parameters"),
code('L = pf.Parameter("L")\nR = pf.Parameter("R")\nA = pf.LipschitzMonotoneOperator(is_basis=True, tags=["A"], L=L)'),
md("## Algorithm and PEP setup\nThe exact rational recurrence below includes the terminal zero factor and the squared radius normalization."),
code(defs),
code('ctx, pb, operator = get_pep_setup(4, {"L": 1, "R": 1})\nprint("Context built for N=4; metric:", pb.performance_metric)\nprint("Initial normalization:", pb.init_conditions[0])'),
md("## Numerical evidence\nThe required sweep was run once at $L=R=1$, with CLARABEL defaults. This cell reuses that sweep. Scaling of the recurrence and residual gives the proposed $L^2R^2$ factor. The $N=2$ solve returned `optimal_inaccurate`; all other horizons returned `optimal`."),
code('sweep = json.loads((notebook_dir / "supplementary/b1_sweep.json").read_text())\nns = np.array([row["N"] for row in sweep])\nvalues = np.array([row["opt_value"] for row in sweep])\nfor row in sweep:\n    print(f"N={row[\'N\']}: {row[\'opt_value\']:.10f} ({row[\'solver_status\']})")\nprint("N^2 times PEP values:", ns**2 * values)\nplt.figure(figsize=(7, 4))\nplt.plot(ns, values, "o-", label="PEP relaxation")\nplt.plot(ns, 4 / ns**2, "--", label="Conjecture: 4/N^2")\nplt.xlabel("Horizon N")\nplt.ylabel("Squared final residual, L=R=1")\nplt.grid(alpha=0.3)\nplt.legend()\nplt.tight_layout()\nplt.show()'),
md(r"""The observed values are $2,1,4/9,1/4,4/25,1/9,4/49$ up to solver accuracy. For $N\geq2$ in this sweep they match $4/N^2$; $N=1$ lies strictly below that curve. We retain the simple uniform conjecture
$$\|A(x_N)\|^2\leq\frac{4L^2R^2}{N^2}.$$
This is not yet a theorem. The subsequent blocks must verify its certificate and exact Lyapunov proof."""),
md("## Full-PEP certificate (pending Block 2)"),
md("## Lyapunov partial sums and ranks (pending Block 3)"),
md("## Identify the vectors composing the Lyapunov function (pending Block 4)"),
md("## Closed-form Lyapunov function and symbolic identities (pending Block 5)")]
nb = nbf.v4.new_notebook(cells=cells, metadata={"kernelspec": {
    "name": "attempt-kernel", "display_name": "Attempt pinned Python", "language": "python"}})
destination = ROOT / "dual_feg_example_lyap.ipynb"
nbf.write(nb, destination)
NotebookClient(nb, timeout=120, kernel_name="attempt-kernel", resources={"metadata": {"path": str(ROOT)}}).execute()
nbf.write(nb, destination)
for i, cell in enumerate(nb.cells):
    if cell.cell_type == "markdown":
        assert not any(c in cell.source for c in ["\x0c", "\r", "\\(", "\\)", "\\[", "\\]"])
    for output in cell.get("outputs", []):
        assert output.output_type != "error"
        if output.output_type == "stream":
            print(i, output.text)
plot_count = sum("image/png" in output.get("data", {}) for cell in nb.cells for output in cell.get("outputs", []))
assert plot_count > 0
checklist_items = [
"title, problem description, and the algorithm update equations in LaTeX",
"proof statement placeholder, to be filled with the final theorem and proof outline in Block 5",
"imports", "function/operator definitions", "make_ctx_dual_feg and get_pep_setup",
"numerical evidence, including a plot comparing the PEP values against the discovered or conjectured rate",
"dense and relaxed proof solves", "lambda and S verification (closed-form when available, otherwise numerical with explicit analytic status)",
"partial-sum Lyapunov construction and rank profile", "special-vector identification",
"coefficient extraction and closed-form V_k", "symbolic step, base, and boundary identities"]
indices = {1: "0", 3: "2,3", 4: "5", 5: "7,8", 6: "9,10,11"}
header = f"Notebook: {destination.name}\nLast reviewed block: B1\nSHA-256: {hashlib.sha256(destination.read_bytes()).hexdigest()}\n\nPresentation policy: evaluation-ancillary-v1. No rendered/image inspection performed. Markdown delimiters/control characters checked; executed plot output is retained.\n\n| Item | Requirement | Status | Cell indices | Evidence |\n|---|---|---|---|---|\n"
rows = []
for i, item in enumerate(checklist_items, 1):
    status = "verified" if i in indices else "pending"
    evidence = "Source content and fresh-kernel execution inspected" if i in indices else "Later-block obligation"
    if i == 6:
        evidence += f"; sweep printed and {plot_count} PNG plot output retained; presentation review omitted by policy"
    rows.append(f"| {i} | {item} | {status} | {indices.get(i, '')} | {evidence} |")
(ROOT / "supplementary/dual_feg_example_lyap_checklist.md").write_text(header + "\n".join(rows))
print("Notebook execution, plot presence and Markdown checks passed")
