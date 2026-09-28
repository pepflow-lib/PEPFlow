"""Author and execute the first block's evolving notebook."""
import hashlib
import json
import os
from pathlib import Path
import sys

import nbformat as nbf
from nbclient import NotebookClient

root = Path.cwd()
notebook = root / "feg_example_lyap.ipynb"
results = json.loads((root / "supplementary/_sweep_tmp.json").read_text())
state = {
    "algo_name": "feg", "problem_type": "monotone_operator", "obj_tag": "A",
    "params_json": '{"L": 1, "R": 1}', "performance_metric": "||A(x_N)||^2",
    "initial_condition": "||x_0-x_star||^2 <= R^2; A(x_star)=0",
    "conjectured_rate": "4*L**2*R**2/N**2", "setup_file": "feg_setup.py",
    "sweep_results": results, "N_verify": 6,
    "numerical_certificate_verified": False, "analytic_full_pep_verified": False,
    "lyapunov_proof_verified": False,
    "rate_note": "N=2..7 matches candidate; N=1 has value 2 versus candidate 4 at L=R=1.",
}
(root / "state").mkdir(exist_ok=True)
(root / "state/feg_b1.json").write_text(json.dumps(state, indent=2))
setup = (root / "feg_setup.py").read_text()
definitions, context = setup.split("def make_ctx_feg", 1)
definitions = "\n".join(definitions.splitlines()[1:])
cells = [
    nbf.v4.new_markdown_cell(r"""# FEG: residual convergence for a monotone Lipschitz operator

Let $A$ be monotone and $L$-Lipschitz on a real finite-dimensional Euclidean space, with $L>0$, $A(x_\star)=0$, and $\|x_0-x_\star\|^2\le R^2$ for $R\ge0$. The horizon is an integer $N\ge1$. We study $\|A(x_N)\|^2$ for
$$x_{k+1/2}=x_k+\frac{x_0-x_k}{k+1}-\frac{k}{(k+1)L}A(x_k),$$
$$x_{k+1}=x_k+\frac{x_0-x_k}{k+1}-\frac1L A(x_{k+1/2}),\qquad 0\le k<N.$$
At $k=0$, $x_{1/2}=x_0$ is the same point and operator evaluation.

The pairwise monotonicity and Lipschitz inequalities define the numerical PEP relaxation used here; numerical optimality alone is not an arbitrary-horizon proof."""),
    nbf.v4.new_markdown_cell("## Proof statement (pending Block 5)\nThe numerical candidate is $\\|A(x_N)\\|^2\\le4L^2R^2/N^2$. The certificate, Lyapunov construction, and exact proof remain pending."),
    nbf.v4.new_code_cell('from pathlib import Path\nimport sys\nimport json\nimport matplotlib.pyplot as plt\nnotebook_dir = Path.cwd()\nREPO_ROOT = notebook_dir / "supplementary" / "approved"\nsys.path[:0] = [str(REPO_ROOT), str(notebook_dir), str(notebook_dir / "supplementary" / "helpers")]\n'),
    nbf.v4.new_code_cell(definitions),
    nbf.v4.new_code_cell("def make_ctx_feg" + context),
    nbf.v4.new_markdown_cell("## Block 1: numerical evidence\nThe required sweep was run once with CLARABEL defaults, $L=R=1$. The saved sweep is reused below. The candidate is tight numerically for $N=2,\\ldots,7$ and conservative at $N=1$."),
    nbf.v4.new_code_cell('sweep = json.loads((notebook_dir / "state/feg_b1.json").read_text())["sweep_results"]\nns = [row["N"] for row in sweep]\nvalues = [row["opt_value"] for row in sweep]\nfor row in sweep:\n    print(f"N={row[\'N\']}: {row[\'opt_value\']:.10f}; status={row[\'status\']}")\nprint("N^2 times PEP:", [round(n*n*v, 7) for n, v in zip(ns, values)])\nplt.figure(figsize=(6, 4))\nplt.plot(ns, values, "o-", label="PEP relaxation")\nplt.plot(ns, [4/n**2 for n in ns], "--", label="Candidate 4/NÂ²")\nplt.xlabel("N")\nplt.ylabel("Squared residual, L=R=1")\nplt.legend()\nplt.grid(alpha=0.3)\nplt.tight_layout()\nplt.show()'),
    nbf.v4.new_markdown_cell("## Block 2: full PEP certificate\nPending."),
    nbf.v4.new_markdown_cell("## Block 3: Lyapunov partial sums\nPending."),
    nbf.v4.new_markdown_cell("## Block 4: special vectors and coefficients\nPending."),
    nbf.v4.new_markdown_cell("## Block 5: exact identities and theorem\nPending."),
]
for i, cell in enumerate(cells):
    cell.id = f"b1-{i:02d}"
nb = nbf.v4.new_notebook(cells=cells)
nb.metadata.kernelspec = {"display_name": "Attempt Python", "language": "python", "name": "attempt"}
kernel_dir = Path(os.environ["JUPYTER_PATH"]) / "kernels/attempt"
kernel_dir.mkdir(parents=True, exist_ok=True)
(kernel_dir / "kernel.json").write_text(json.dumps({"argv": [sys.executable, "-I", "-B", "-m", "ipykernel_launcher", "-f", "{connection_file}"], "display_name": "Attempt Python", "language": "python"}))
nbf.write(nb, notebook)
NotebookClient(nb, timeout=120, kernel_name="attempt", resources={"metadata": {"path": str(root)}}).execute()
nbf.write(nb, notebook)
markdown = "\n".join(c.source for c in nb.cells if c.cell_type == "markdown")
assert not any(x in markdown for x in ("\\(", "\\)", "\\[", "\\]", "\x0c", "\r"))
assert any("image/png" in o.get("data", {}) for o in nb.cells[6].outputs)
items = [
    ("title, problem description, and the algorithm update equations in LaTeX", "verified", "b1-00", "Source formulas inspected; presentation override, no rendering."),
    ("proof statement placeholder, to be filled with the final theorem and proof outline in Block 5", "pending", "b1-01", "Candidate only; theorem pending."),
    ("imports", "verified", "b1-02", "Fresh kernel execution passed; explicit approved paths."),
    ("function/operator definitions", "verified", "b1-03", "LipschitzMonotoneOperator, symbolic L and R."),
    ("make_ctx_feg and get_pep_setup", "verified", "b1-04", "Visible recursion, shared first half-step, RÂ² initial condition, residual metric."),
    ("numerical evidence, including a plot comparing the PEP values against the discovered or conjectured rate", "verified", "b1-06", "Seven printed values and image/png plot output present; not visually inspected per override."),
    ("dense and relaxed proof solves", "pending", "b1-07", "B2 not started."),
    ("lambda and S verification (closed-form when available, otherwise numerical with explicit analytic status)", "pending", "b1-07", "B2 not started."),
    ("partial-sum Lyapunov construction and rank profile", "pending", "b1-08", "B3 not started."),
    ("special-vector identification", "pending", "b1-09", "B4 not started."),
    ("coefficient extraction and closed-form V_k", "pending", "b1-09", "B4/B5 pending."),
    ("symbolic step, base, and boundary identities", "pending", "b1-10", "B5 not started."),
]
digest = hashlib.sha256(notebook.read_bytes()).hexdigest()
header = f"Notebook: {notebook.name}\nLast reviewed block: B1\nSHA-256: {digest}\nPresentation policy: evaluation-ancillary-v1; no rendered/image inspection.\n\n| # | Item | Status | Cells | Evidence |\n|---|---|---|---|---|\n"
body = "\n".join(f"| {i} | {label} | {status} | {cell} | {evidence} |" for i, (label, status, cell, evidence) in enumerate(items, 1))
(root / "supplementary/feg_example_lyap_checklist.md").write_text(header + body)
print(json.dumps({"notebook": str(notebook), "sha256": digest, "fresh_kernel": "passed", "math_delimiters": "passed", "plot_output_present": True}))

