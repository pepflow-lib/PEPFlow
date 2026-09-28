"""Create the evolving notebook and B1 state from the saved sweep."""
import json
from pathlib import Path

import nbformat as nbf

root = Path(__file__).resolve().parent.parent
sweep = json.loads((root / "supplementary/sweep.json").read_text())
state = {
    "algo_name": "pgm", "problem_type": "composite", "obj_tag": "f",
    "params_json": '{"L": 1, "R": 1}',
    "performance_metric": "h(x_N)-h(x_star)",
    "initial_condition": "||x_0-x_star||^2 <= R^2",
    "conjectured_rate": "L*R**2/(4*N)", "setup_file": "pgm_setup.py",
    "sweep_results": sweep, "N_verify": 4,
    "numerical_certificate_verified": False,
    "analytic_full_pep_verified": False, "lyapunov_proof_verified": False,
    "presentation_policy": "evaluation-ancillary-v1",
}
(root / "state").mkdir(exist_ok=True)
(root / "state/pgm_b1.json").write_text(json.dumps(state, indent=2))
nb = nbf.v4.new_notebook()
nb.metadata.kernelspec = {
    "name": "pgm-own", "display_name": "PGM attempt", "language": "python"
}
setup = (root / "pgm_setup.py").read_text()
definitions = setup[setup.index('L = pf.Parameter'):setup.index('def make_ctx_pgm')]
builders = setup[setup.index('def make_ctx_pgm'):]
nb.cells = [
nbf.v4.new_markdown_cell(r"""# Proximal gradient: convergence and Lyapunov discovery

Let $f$ be convex and $L$-smooth with $L>0$, and let $g$ be closed, proper and convex in a real finite-dimensional Euclidean space. Let $h=f+g$, let $x_\star$ minimize $h$, and suppose $\|x_0-x_\star\|^2\le R^2$, $R\ge0$. Updates and evaluations are well-defined. For an integer $N\ge1$,
$$x_{k+1}=\operatorname{prox}_{g/L}\left(x_k-\frac{1}{L}\nabla f(x_k)\right),\qquad 0\le k<N.$$
We study $h(x_N)-h(x_\star)$. Composite stationarity imposes $\nabla f(x_\star)+s_\star=0$ with $s_\star\in\partial g(x_\star)$."""),
nbf.v4.new_markdown_cell("## Theorem and proof outline\n\nPending Block 5. The numerical conjecture below is not yet a theorem."),
nbf.v4.new_code_cell(
"import sys\nimport json\nfrom pathlib import Path\n"
"notebook_dir = Path.cwd().resolve()\n"
"repo_root = notebook_dir / 'supplementary' / 'approved'\n"
"sys.path[:0] = [str(repo_root), str(notebook_dir / 'supplementary')]\n"
"import pepflow as pf\nimport matplotlib.pyplot as plt\n"
"assert Path(pf.__file__).resolve().is_relative_to(repo_root)\n"),
nbf.v4.new_markdown_cell("## Function and parameter definitions"),
nbf.v4.new_code_cell(definitions),
nbf.v4.new_markdown_cell("## Algorithm and performance estimation setup"),
nbf.v4.new_code_cell(builders),
nbf.v4.new_markdown_cell("## Numerical evidence\n\nOne sweep at $L=R=1$ with CLARABEL defaults. The final two solves reported optimal_inaccurate; all observed errors from the candidate are below $5\\times10^{-9}$. These finite samples suggest $LR^2/(4N)$; arbitrary-horizon proof remains pending."),
nbf.v4.new_code_cell(
"sweep = json.loads((notebook_dir / 'supplementary/sweep.json').read_text())\n"
"for row in sweep:\n"
"    n, value = row['N'], row['opt_value']\n"
"    print(f\"N={n}: PEP={value:.10f}, candidate={1/(4*n):.10f}, status={row['status']}\")\n"
"ns = [row['N'] for row in sweep]\n"
"values = [row['opt_value'] for row in sweep]\n"
"print('inverse PEP values:', [round(1/value, 6) for value in values])\n"
"print('maximum candidate residual:', max(abs(value-1/(4*n)) for n,value in zip(ns,values)))\n"
"plt.figure(figsize=(7, 4))\n"
"plt.plot(ns, values, 'o', label='PEP sweep')\n"
"plt.plot(ns, [1/(4*n) for n in ns], '-', label='candidate 1/(4N)')\n"
"plt.xlabel('N')\nplt.ylabel('objective gap, L=R=1')\nplt.legend()\nplt.grid(alpha=0.3)\nplt.show()\n"),
nbf.v4.new_markdown_cell("## Full PEP certificate\n\nPending Block 2."),
nbf.v4.new_markdown_cell("## Lyapunov partial sums\n\nPending Block 3."),
nbf.v4.new_markdown_cell("## Identify the vectors composing the Lyapunov function\n\nPending Block 4."),
nbf.v4.new_markdown_cell("## Closed-form coefficients and symbolic identities\n\nPending Block 5."),
]
import_source = nb.cells[2].source
split = import_source.index("import pepflow")
nb.cells[2].source = import_source[:split]
nb.cells.insert(3, nbf.v4.new_code_cell(import_source[split:]))
nbf.write(nb, root / "pgm_example_lyap.ipynb")
