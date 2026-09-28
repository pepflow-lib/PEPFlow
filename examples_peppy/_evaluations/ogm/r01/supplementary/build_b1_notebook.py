import hashlib
import importlib.util
import json
import os
import sys
from pathlib import Path

root = Path(__file__).resolve().parent.parent
spec = importlib.util.spec_from_file_location("attempt_runtime", root / "supplementary/helpers/runtime.py")
assert spec is not None and spec.loader is not None
runtime = importlib.util.module_from_spec(spec)
spec.loader.exec_module(runtime)
import nbformat
from nbclient import NotebookClient

rows = json.loads((root / "supplementary/_sweep_tmp.json").read_text())
for row in rows:
    row["candidate"] = 1 / (2 * row["theta_N"] ** 2)
    row["absolute_error"] = abs(row["candidate"] - row["opt_value"])
assert len(rows) == 7 and all(r["status"] == "optimal" and r["absolute_error"] < 1e-5 for r in rows)
state = {"algo_name": "ogm", "problem_type": "smooth_convex", "obj_tag": "f", "params_json": '{"L": 1, "R": 1}', "performance_metric": "f(x_N) - f(x_star)", "initial_condition": "||x_0-x_star||^2 <= R^2", "conjectured_rate": "L*R^2/(2*theta_N^2)", "setup_file": "ogm_setup.py", "sweep_results": rows, "N_verify": 4, "rate_status": "numerically supported; not yet proved", "coefficient_arithmetic": "double precision theta recurrence for numerical discovery"}
(root / "state").mkdir(exist_ok=True)
(root / "state/ogm_b1.json").write_text(json.dumps(state, indent=2))
nb = nbformat.v4.new_notebook()
m = nbformat.v4.new_markdown_cell
c = nbformat.v4.new_code_cell
setup = (root / "ogm_setup.py").read_text()
nb.cells = [m(r'''# OGM: smooth convex objective-gap discovery
Let $f$ be convex with $L$-Lipschitz gradient, $L>0$, and let $\nabla f(x_\star)=0$. Assume $R\geq0$, $\|x_0-x_\star\|^2\leq R^2$, $z_0=x_0$, and integer $N\geq1$. The performance metric is $f(x_N)-f(x_\star)$.

Set $\theta_{-1}=0$ and
$$\theta_k=\frac{1+\sqrt{1+4\theta_{k-1}^2}}2\quad(0\leq k<N),\qquad \theta_N=\frac{1+\sqrt{1+8\theta_{N-1}^2}}2.$$
For $k=0,\ldots,N-1$,
$$y_{k+1}=x_k-\frac1L\nabla f(x_k),\qquad z_{k+1}=z_k-\frac{2\theta_k}{L}\nabla f(x_k),$$
$$x_{k+1}=\left(1-\frac1{\theta_{k+1}}\right)y_{k+1}+\frac{z_{k+1}}{\theta_{k+1}}.$$
The terminal theta recurrence is distinct and is retained in every numerical instance.'''),m('## Proof statement\nPending Blocks 2–5. The numerical conjecture below is not yet a theorem.'),c('''import sys
from pathlib import Path

notebook_dir = Path.cwd().resolve()
repo_root = notebook_dir / "supplementary" / "approved"
sys.path[:0] = [str(repo_root), str(notebook_dir / "supplementary" / "helpers"), str(notebook_dir)]
import runtime
import json
import matplotlib.pyplot as plt
import pepflow as pf

print("Framework:", pf.__file__)'''),m('## Function and parameter definitions'),c('import math\n\nL = pf.Parameter("L")\nR = pf.Parameter("R")\nf = pf.SmoothConvexFunction(is_basis=True, tags=["f"], L=L)'),m('## Algorithm context and PEP setup'),c(setup[setup.index('def theta_sequence'):]),m('## Numerical evidence\nThe one-time sweep uses CLARABEL defaults with $L=R=1$. Theta coefficients use double precision. The candidate is inferred from the approximately constant product of the objective gap and $\theta_N^2$.'),c('''with (notebook_dir / "state/ogm_b1.json").open() as stream:
    b1 = json.load(stream)
rows = b1["sweep_results"]
for row in rows:
    print(f'N={row["N"]}: PEP={row["opt_value"]:.10f}, candidate={row["candidate"]:.10f}, scaled={row["opt_value"] * row["theta_N"]**2:.10f}, status={row["status"]}')
print("Maximum absolute discrepancy:", max(row["absolute_error"] for row in rows))
plt.plot([r["N"] for r in rows], [r["opt_value"] for r in rows], "o", label="PEP")
plt.plot([r["N"] for r in rows], [r["candidate"] for r in rows], "-", label="1 / (2 theta_N²)")
plt.xlabel("N")
plt.ylabel("Objective gap, L=R=1")
plt.legend()
plt.grid(True)
plt.show()'''),m(r'Numerical conjecture: $f(x_N)-f(x_\star)\leq LR^2/(2\theta_N^2)$. Homogeneity supplies the $LR^2$ scaling. Full certificates, Lyapunov constructions, and exact identities remain pending.'),m('## Dense and relaxed proof solves\nPending Block 2.'),m('## Lambda and S verification\nPending Block 2.'),m('## Partial-sum Lyapunov construction and ranks\nPending Block 3.'),m('## Identify the vectors composing the Lyapunov function\nPending Block 4.'),m('## Coefficients and symbolic identities\nPending Block 5.')]
for cell in nb.cells:
    if cell.cell_type == "markdown":
        cell.source = cell.source.replace("\\\\", "\\").replace("\theta", "\\theta")
bootstrap, imports = nb.cells[2].source.split("import runtime", 1)
nb.cells[2].source = bootstrap
nb.cells.insert(3, c("import runtime" + imports + '\nprint("Runtime:", runtime.ROOT)'))
nb.metadata.kernelspec = {"name": "ogm-attempt", "display_name": "OGM attempt", "language": "python"}
nb_path = root / "ogm_example_lyap.ipynb"
nbformat.write(nb, nb_path)
kdir = runtime.RUNTIME / "jupyter/kernels/ogm-attempt"
kdir.mkdir(parents=True, exist_ok=True)
(kdir / "kernel.json").write_text(json.dumps({"argv": [sys.executable, "-I", "-B", "-m", "ipykernel_launcher", "-f", "{connection_file}"], "display_name": "OGM attempt", "language": "python"}))
os.environ["JUPYTER_PATH"] = str(runtime.RUNTIME / "jupyter")
NotebookClient(nb, timeout=120, kernel_name="ogm-attempt", resources={"metadata": {"path": str(root)}}).execute()
nbformat.write(nb, nb_path)
print("Executed", nb_path)
print("Maximum rate discrepancy", max(r["absolute_error"] for r in rows))
print("Notebook SHA256", hashlib.sha256(nb_path.read_bytes()).hexdigest())



