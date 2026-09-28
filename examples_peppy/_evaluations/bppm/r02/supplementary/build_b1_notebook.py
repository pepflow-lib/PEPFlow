from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).resolve().parent / "helpers"))
from runtime import ATTEMPT
import json
import nbformat as nbf

sweep = json.loads((ATTEMPT / "supplementary/_sweep_tmp.json").read_text())
state = {"algo_name": "bppm", "problem_type": "convex_bregman", "obj_tag": "f",
         "params_json": json.dumps({"alpha": 1, "R": 1}),
         "performance_metric": "f(x_N) - f(x_star)", "initial_condition": "D_h(x_star,x_0) <= R",
         "conjectured_rate": "R/(alpha*N)", "setup_file": "bppm_setup.py", "sweep_results": sweep,
         "N_verify": 4, "presentation_policy": "evaluation-ancillary-v1",
         "rate_check_atol": 1e-5, "max_rate_error": max(r["absolute_error"] for r in sweep)}
(ATTEMPT / "state").mkdir(exist_ok=True)
(ATTEMPT / "state/bppm_b1.json").write_text(json.dumps(state, indent=2))
setup = (ATTEMPT / "bppm_setup.py").read_text(encoding="utf-8-sig")
definitions = setup[setup.index('alpha ='):setup.index('\ndef make_ctx')]
builders = setup[setup.index('def make_ctx'):]
nb = nbf.v4.new_notebook()
nb.cells = [
nbf.v4.new_markdown_cell(r'''# Bregman proximal point minimization

Let $f$ and $h$ be closed, proper, convex functions on a real finite-dimensional Euclidean space, with the differentiability stipulated in the input; $h$ is a differentiable Bregman kernel. Let $x_\star$ minimize $f$, $\alpha>0$, $R\ge0$, and $N\ge1$ be an integer. All iterates and evaluations are well-defined.

$$D_h(u,v)=h(u)-h(v)-\langle\nabla h(v),u-v\rangle,$$
$$x_{k+1}\in\mathop{\rm argmin}_x\{\alpha f(x)+D_h(x,x_k)\},\quad k=0,\ldots,N-1.$$

The model uses the exact optimality relation
$$\nabla h(x_{k+1})=\nabla h(x_k)-\alpha\nabla f(x_{k+1}).$$
The initial condition is $D_h(x_\star,x_0)\le R$ (not $R^2$), and the metric is $f(x_N)-f(x_\star)$. Convex interpolation gives an upper-bound PEP relaxation for the supplied differentiable class; no extra smoothness or strong convexity is imposed.'''),
nbf.v4.new_markdown_cell(r'''## Proof statement (pending)

The input supplies the conjecture $f(x_N)-f(x_\star)\le R/(\alpha N)$. Block 1 checks numerical consistency only. The full certificate, Lyapunov construction and exact proof will be developed in later blocks.'''),
nbf.v4.new_code_cell('''from pathlib import Path
import sys
notebook_dir = Path.cwd().resolve()
repo_root = notebook_dir / "supplementary" / "approved"
sys.path[:0] = [str(repo_root), str(notebook_dir), str(notebook_dir / "supplementary")]
import json
import pepflow as pf
import matplotlib.pyplot as plt
'''),
nbf.v4.new_markdown_cell('## Function and parameter definitions'),
nbf.v4.new_code_cell(definitions),
nbf.v4.new_markdown_cell('## Algorithm and PEP setup'),
nbf.v4.new_code_cell(builders + '\nctx_b1, pb_b1, obj_b1 = get_pep_setup(4, {"alpha": 1, "R": 1})\nprint("Built four exact Bregman proximal steps.")'),
nbf.v4.new_markdown_cell('## Numerical evidence\nThe saved sweep uses CLARABEL defaults, with alpha = R = 1, and one numerical thread. Each solve includes convex interpolation for both f and h.'),
nbf.v4.new_code_cell('''sweep = json.loads((notebook_dir / "state/bppm_b1.json").read_text())["sweep_results"]
for row in sweep:
    print(f"N={row['N']}: PEP={row['opt_value']:.10f}; conjecture={row['conjecture']:.10f}; status={row['solver_attempts'][-1]['status']}")
error = max(row["absolute_error"] for row in sweep)
assert error <= 1e-5
print(f"Maximum absolute discrepancy: {error:.3e} (tolerance 1e-5)")
fig, ax = plt.subplots(figsize=(6, 4))
ax.plot([r["N"] for r in sweep], [r["opt_value"] for r in sweep], "o", label="PEP optimum")
ax.plot([r["N"] for r in sweep], [r["conjecture"] for r in sweep], "-", label="R/(alpha N)")
ax.set(xlabel="N", ylabel="Function-value gap", title="Bregman proximal point: numerical evidence")
ax.legend()
ax.grid(True, alpha=0.3)
plt.show()'''),
nbf.v4.new_markdown_cell(r'''The observed values match $R/(\alpha N)$ at the normalized parameters. This is numerical evidence, not an arbitrary-horizon proof.'''),
nbf.v4.new_markdown_cell('## Dense and relaxed proof solves\nPending Block 2.'),
nbf.v4.new_markdown_cell('## Lambda and S verification\nPending Block 2.'),
nbf.v4.new_markdown_cell('## Partial-sum Lyapunov construction and rank profile\nPending Block 3.'),
nbf.v4.new_markdown_cell('## Identify the vectors composing the Lyapunov function\nPending Block 4.'),
nbf.v4.new_markdown_cell('## Coefficients and closed-form Lyapunov function\nPending Blocks 4 and 5.'),
nbf.v4.new_markdown_cell('## Symbolic step, base, and boundary identities\nPending Block 5.')]
nb.cells[2].source = nb.cells[2].source.split("import json")[0]
nb.cells.insert(3, nbf.v4.new_code_cell("import json\nfrom numbers import Number\nfrom typing import cast\nimport pepflow as pf\nimport matplotlib.pyplot as plt"))
nb.metadata.kernelspec = {"display_name": "Python 3 (attempt isolated)", "language": "python", "name": "bppm-r02"}
nbf.write(nb, ATTEMPT / "bppm_example_lyap.ipynb")
print("Saved B1 state and notebook.")


