import runpy
from pathlib import Path
runpy.run_path(str(Path(__file__).with_name("runtime.py")))
import json
import os
import sys
import nbformat as nb
from nbclient import NotebookClient
root = Path(__file__).resolve().parents[1]
results = json.loads((root / "supplementary/sweep.json").read_text())
state = {"algo_name": "pgm", "problem_type": "composite", "obj_tag": "f", "obj_tags": ["f", "g"], "params_json": '{"L": 1, "R": 1}', "performance_metric": "h(x_N)-h(x_star)", "initial_condition": "||x_0-x_star||^2 <= R^2", "conjectured_rate": "L*R**2/(4*N)", "setup_file": "pgm_setup.py", "sweep_results": results, "N_verify": 4, "analytic_status": "conjecture from numerical evidence only", "presentation_policy": "evaluation-ancillary-v1"}
(root / "state").mkdir(exist_ok=True)
(root / "state/pgm_b1.json").write_text(json.dumps(state, indent=2))
setup = (root / "pgm_setup.py").read_text(encoding="utf-8-sig")
functions = setup[setup.index('L = pf.Parameter'):]
book = nb.v4.new_notebook()
book.cells = [
nb.v4.new_markdown_cell(r'''# Proximal gradient: composite convex minimization
Let $f$ be convex and $L$-smooth, $L>0$, and $g$ closed, proper and convex on a finite-dimensional real Euclidean space. Let $h=f+g$, $x_\star\in\arg\min h$, and $\|x_0-x_\star\|^2\le R^2$ for $R\ge0$. Proximal updates are well-defined. For integer $N\ge1$, the metric is $h(x_N)-h(x_\star)$.
$$x_{k+1}=\operatorname{prox}_{g/L}\left(x_k-\frac1L\nabla f(x_k)\right),\qquad 0\le k<N.$$
Equivalently, $L(x_k-x_{k+1})-\nabla f(x_k)\in\partial g(x_{k+1})$.
'''),
nb.v4.new_markdown_cell('## Proof statement (pending Block 5)\nThe numerical conjecture below is not yet an all-horizon theorem.'),
nb.v4.new_code_cell('from pathlib import Path\nimport sys\nimport json\nimport numpy as np\nimport matplotlib.pyplot as plt\nNOTEBOOK_DIR = Path.cwd()\nREPO_ROOT = NOTEBOOK_DIR / "supplementary" / "approved"\nsys.path[:0] = [str(REPO_ROOT), str(NOTEBOOK_DIR / "supplementary")]\nimport pepflow as pf'),
nb.v4.new_code_cell(functions),
nb.v4.new_markdown_cell('## B1 numerical evidence\nCLARABEL defaults; normalized $L=R=1$. Status `optimal_inaccurate` at horizons 6 and 7 is retained explicitly. These values support a conjecture, not a certificate.'),
nb.v4.new_code_cell('data = json.loads((NOTEBOOK_DIR / "state/pgm_b1.json").read_text())\nrows = data["sweep_results"]\nns = np.array([r["N"] for r in rows])\nvalues = np.array([r["opt_value"] for r in rows])\nfor row in rows:\n    print(row)\nprint("Reciprocal values:", 1 / values)\nprint("Reciprocal differences:", np.diff(1 / values))\nprint("Maximum discrepancy:", np.max(np.abs(values - 1 / (4 * ns))))\nplt.plot(ns, values, "o", label="PEP")\nplt.plot(ns, 1 / (4 * ns), "--", label="Conjecture 1/(4N)")\nplt.xlabel("N")\nplt.ylabel("Objective gap")\nplt.legend()\nplt.grid(True)\nplt.show()'),
nb.v4.new_markdown_cell(r'Candidate rate: $h(x_N)-h(x_\star)\le LR^2/(4N)$. Scaling restores $L$ and $R^2$. Certificate discovery and verification remain pending.'),
nb.v4.new_markdown_cell('## B2 dense and relaxed proof solves\nPending.\n\n## Lambda and S verification\nPending.'),
nb.v4.new_markdown_cell('## B3 partial-sum Lyapunov construction and rank profile\nPending.'),
nb.v4.new_markdown_cell('## B4 special vectors and coefficient extraction\nPending.'),
nb.v4.new_markdown_cell('## B5 closed form and exact step, base, boundary identities\nPending.')]
book.cells[2].source = book.cells[2].source.replace("\nimport pepflow as pf", "")
book.cells.insert(3, nb.v4.new_code_cell("import pepflow as pf"))
book.metadata['kernelspec'] = {"name": "pgm-own", "display_name": "Attempt Python", "language": "python"}
path = root / "pgm_example_lyap.ipynb"
nb.write(book, path)
kernels = root / "supplementary/.runtime/jupyter/kernels/pgm-own"
kernels.mkdir(parents=True, exist_ok=True)
(kernels / "kernel.json").write_text(json.dumps({"argv": [sys.executable, "-I", "-B", "-m", "ipykernel_launcher", "-f", "{connection_file}"], "display_name": "Attempt Python", "language": "python"}))
os.environ["JUPYTER_PATH"] = str(kernels.parents[1])
NotebookClient(book, timeout=120, kernel_name="pgm-own", resources={"metadata": {"path": str(root)}}).execute()
nb.write(book, path)
print('Fresh kernel execution passed; notebook saved.')

