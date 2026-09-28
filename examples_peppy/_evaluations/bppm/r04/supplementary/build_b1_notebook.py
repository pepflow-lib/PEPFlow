import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent / "helpers"))
import runtime
import json
import nbformat as nbf
from nbclient import NotebookClient

root = runtime.ATTEMPT
results = json.loads((root / "supplementary/b1_sweep.json").read_text())
state = {"algo_name": "bppm", "problem_type": "convex_bregman", "obj_tag": "f", "params_json": '{"alpha": 1, "R": 1}', "performance_metric": "f(x_N)-f(x_star)", "initial_condition": "D_h(x_star,x_0)<=R", "conjectured_rate": "R/(alpha*N)", "setup_file": "bppm_setup.py", "sweep_results": results, "N_verify": 4, "numerical_certificate_verified": False, "analytic_full_pep_verified": False, "lyapunov_proof_verified": False}
(root / "state").mkdir(exist_ok=True)
(root / "state/bppm_b1.json").write_text(json.dumps(state, indent=2))
nb = nbf.v4.new_notebook()
md = nbf.v4.new_markdown_cell
code = nbf.v4.new_code_cell
setup = (root / "bppm_setup.py").read_text(encoding="utf-8-sig")
nb.cells = [
md(r'''# Bregman proximal point minimization
Work in a real finite-dimensional Euclidean space. The functions $f,h$ are closed, proper, convex and differentiable as specified in the input, all stated evaluations and updates exist, $\alpha>0$, $R\ge0$, and $N\ge1$ is an integer. Let $x_\star$ minimize $f$ and assume $D_h(x_\star,x_0)\le R$.
$$D_h(u,v)=h(u)-h(v)-\langle\nabla h(v),u-v\rangle.$$
$$x_{k+1}\in\arg\min_x\{\alpha f(x)+D_h(x,x_k)\},\qquad k=0,\ldots,N-1.$$
The optimality relation used by the setup is
$$\nabla h(x_{k+1})=\nabla h(x_k)-\alpha\nabla f(x_{k+1}).$$
The performance metric is $f(x_N)-f(x_\star)$, with supplied conjecture $R/(\alpha N)$. Convex interpolation gives a relaxation valid for the differentiable class; the numerical results alone are not an arbitrary-horizon proof.'''),
md('## Proof statement\nPending Block 5. The supplied rate remains a conjecture at this stage.'),
code('from pathlib import Path\nimport sys\nnotebook_dir = Path.cwd().resolve()\nREPO_ROOT = notebook_dir / "supplementary" / "approved"\nsys.path[:0] = [str(REPO_ROOT), str(notebook_dir / "supplementary" / "helpers"), str(notebook_dir)]\nimport runtime\nimport json\nimport pepflow as pf\nimport matplotlib.pyplot as plt'),
md('## Functions, parameters, and algorithm setup\nBoth functions use convex interpolation; each proximal step encodes the exact optimality equation.'),
code(setup[setup.index('alpha ='):setup.index('\n\ndef make_ctx')]),
code(setup[setup.index('def make_ctx'):]),
md('## Numerical evidence\nCLARABEL defaults, with $\\alpha=R=1$. The saved sweep was generated once from the setup above.'),
code('results = json.loads((notebook_dir / "state/bppm_b1.json").read_text())["sweep_results"]\nfor row in results:\n    print(f"N={row[\'N\']}: PEP={row[\'opt_value\']:.10f}, conjecture={row[\'conjecture\']:.10f}, status={row[\'status\']}")\nprint("Maximum absolute error:", max(row["absolute_error"] for row in results))\nns = [row["N"] for row in results]\nplt.plot(ns, [row["opt_value"] for row in results], "o", label="PEP")\nplt.plot(ns, [1/n for n in ns], "--", label="R/(alpha N), alpha=R=1")\nplt.xlabel("Horizon N")\nplt.ylabel("Final objective gap")\nplt.legend()\nplt.grid(True)\nplt.show()'),
md('The numerical values match the supplied conjecture to better than $10^{-5}$. Initial certificate horizon: $N=4$. The certificate, Lyapunov construction, and exact identities remain to be established.'),
md('## Dense and relaxed proof solves\nPending Block 2.'),
md('## Lambda and S verification\nPending Block 2.'),
md('## Lyapunov partial sums and rank profile\nPending Block 3.'),
md('## Special vectors and coefficient reconstruction\nPending Block 4.'),
md('## Closed form and exact identities\nPending Block 5.')]
parts = nb.cells[2].source.split("import runtime")
nb.cells[2].source = parts[0]
nb.cells.insert(3, code("from numbers import Number\nfrom typing import cast\nimport runtime" + parts[1] + "\nassert runtime.APPROVED == REPO_ROOT"))
nb.metadata.kernelspec = {"display_name":"Attempt Python", "language":"python", "name":"bppm-attempt"}
kernels = runtime.RUNTIME / "jupyter" / "kernels" / "bppm-attempt"
kernels.mkdir(parents=True, exist_ok=True)
(kernels / "kernel.json").write_text(json.dumps({"argv":[sys.executable,"-I","-B","-m","ipykernel_launcher","-f","{connection_file}"],"display_name":"Attempt Python","language":"python"}))
import os
os.environ["JUPYTER_PATH"] = str(runtime.RUNTIME / "jupyter")
path = root / "bppm_example_lyap.ipynb"
nbf.write(nb, path)
NotebookClient(nb, timeout=120, kernel_name="bppm-attempt", resources={"metadata":{"path":str(root)}}).execute()
nbf.write(nb, path)
print('Notebook saved and executed in a fresh isolated kernel:', path)


