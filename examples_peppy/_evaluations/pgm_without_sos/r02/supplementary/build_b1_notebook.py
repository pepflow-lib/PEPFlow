import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent / "helpers"))
import runtime
import json
import os
import nbformat as nbf
from nbclient import NotebookClient

root = runtime.ROOT
results = json.loads((root / "supplementary/_sweep_tmp.json").read_text())
state = {"algo_name": "pgm", "problem_type": "composite", "obj_tag": "f",
         "params_json": '{"L": 1, "R": 1}',
         "performance_metric": "h(x_N) - h(x_star)",
         "initial_condition": "||x_0-x_star||^2 <= R^2",
         "conjectured_rate": "L*R**2/(4*N)", "setup_file": "pgm_setup.py",
         "sweep_results": results, "N_verify": 4,
         "rate_status": "numerical_conjecture", "presentation_policy": "evaluation-ancillary-v1"}
(root / "state").mkdir(exist_ok=True)
(root / "state/pgm_b1.json").write_text(json.dumps(state, indent=2))
nb = nbf.v4.new_notebook()
md = nbf.v4.new_markdown_cell
code = nbf.v4.new_code_cell
source = (root / "pgm_setup.py").read_text(encoding="utf-8-sig")
definitions = source[source.index('L ='):source.index('def make_ctx')]
builder = source[source.index('def make_ctx'):]
nb.cells = [md(r'''# Proximal gradient method
Let $f$ be convex and $L$-smooth, $g$ closed, proper and convex, and $h=f+g$.
We work in a real finite-dimensional Euclidean space, with $L>0$, $R\geq0$, and integer $N\geq1$.
Let $x_\star$ minimize $h$ and assume $\|x_0-x_\star\|^2\leq R^2$.
The well-defined updates are
$$x_{k+1}=\operatorname{prox}_{g/L}\left(x_k-\frac{1}{L}\nabla f(x_k)\right),\qquad 0\leq k<N.$$
The metric is $h(x_N)-h(x_\star)$. Composite stationarity is encoded as $0\in\nabla f(x_\star)+\partial g(x_\star)$.
'''), md('## Proof statement\nPending the certificate and Lyapunov analysis; no theorem is asserted in Block 1.'),
code('''import sys
from pathlib import Path
notebook_dir = Path.cwd().resolve()
repo_root = notebook_dir / "supplementary" / "approved"
sys.path[:0] = [str(repo_root), str(notebook_dir / "supplementary" / "helpers")]
import runtime
import json
import pepflow as pf
import numpy as np
import matplotlib.pyplot as plt
'''), md('## Function definitions'), code(definitions), md('## Algorithm and PEP setup'),code(builder),
md('## Numerical evidence'), code('''sweep = json.loads((notebook_dir / "state/pgm_b1.json").read_text())["sweep_results"]
ns = np.array([row["N"] for row in sweep])
values = np.array([row["opt_value"] for row in sweep])
candidate = 1 / (4 * ns)
for row in sweep:
    print(f'N={row["N"]}: {row["opt_value"]:.10f} ({row["status"]})')
print("Inverse values:", 1 / values)
print("Successive inverse differences:", np.diff(1 / values))
print("Maximum absolute candidate discrepancy:", np.max(np.abs(values - candidate)))
fig, ax = plt.subplots()
ax.plot(ns, values, "o", label="PEP values")
ax.plot(ns, candidate, "-", label="Conjecture 1/(4N)")
ax.set(xlabel="N", ylabel="Objective gap", title="PGM: L=R=1")
ax.legend()
plt.show()
'''), md(r'''The inverse values increase by approximately $4$. Scaling suggests the numerical conjecture
$$h(x_N)-h(x_\star)\leq\frac{LR^2}{4N}.$$
The sweep uses CLARABEL defaults. Horizons 6 and 7 returned `optimal_inaccurate`; all candidate discrepancies remain below $10^{-8}$. This numerical evidence does not prove the conjecture.
'''), md('## Dense and relaxed proof solves\nPending Block 2.'), md('## Lambda and S verification\nPending Block 2.'), md('## Partial-sum Lyapunov construction and rank profile\nPending Block 3.'), md('## Special-vector identification\nPending Block 4.'), md('## Coefficient extraction and closed-form V_k\nPending Blocks 4–5.'),md('## Symbolic step, base, and boundary identities\nPending Block 5.')]
bootstrap, imports = nb.cells[2].source.split('import runtime', 1)
nb.cells[2].source = bootstrap
nb.cells.insert(3, code('import runtime' + imports + '\nassert runtime.ROOT == notebook_dir\n'))
nb.metadata['kernelspec'] = {"display_name": "PGM private pinned Python", "language": "python", "name": "pgm-private"}
kernels = runtime.RUNTIME / "jupyter" / "kernels" / "pgm-private"
kernels.mkdir(parents=True, exist_ok=True)
(kernels / "kernel.json").write_text(json.dumps({"argv": [sys.executable, "-I", "-B", "-m", "ipykernel_launcher", "-f", "{connection_file}"], "display_name": "PGM private pinned Python", "language": "python"}))
os.environ['JUPYTER_PATH'] = str(runtime.RUNTIME / "jupyter")
path = root / "pgm_example_lyap.ipynb"
nbf.write(nb, path)
NotebookClient(nb, timeout=120, kernel_name='pgm-private', resources={'metadata': {'path': str(root)}}).execute()
nbf.write(nb, path)
print('Notebook executed:', path)


