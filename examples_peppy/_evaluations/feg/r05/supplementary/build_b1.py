import importlib.util
import json
import os
from pathlib import Path

spec = importlib.util.spec_from_file_location("runtime", Path(__file__).parent / "helpers/runtime.py")
assert spec is not None and spec.loader is not None
runtime = importlib.util.module_from_spec(spec)
spec.loader.exec_module(runtime)
import nbformat as nbf
from nbclient import NotebookClient

root = runtime.ROOT
results = json.loads((root / "supplementary/_sweep_tmp.json").read_text())
assert len(results) == 7 and all(r["status"] == "optimal" for r in results)
state = {"algo_name": "feg", "problem_type": "monotone_operator", "obj_tag": "A",
         "params_json": '{"L": 1, "R": 1}', "performance_metric": "||A(x_N)||^2",
         "initial_condition": "||x_0-x_star||^2 <= R^2", "conjectured_rate": "4*L**2*R**2/N**2",
         "setup_file": "feg_setup.py", "sweep_results": results, "N_verify": 6,
         "rate_note": "N=1 has sharper numerical value 2; 4/N^2 matches N=2..7.",
         "numerical_certificate_verified": False, "analytic_full_pep_verified": False,
         "lyapunov_proof_verified": False}
(root / "state").mkdir(exist_ok=True)
(root / "state/feg_b1.json").write_text(json.dumps(state, indent=2))
setup = (root / "feg_setup.py").read_text(encoding="utf-8-sig")
imports = '''from pathlib import Path
import sys
import json
import pepflow as pf
import sympy as sp
import matplotlib.pyplot as plt
import runtime
assert runtime.ROOT == notebook_dir
'''
bootstrap = f'''from pathlib import Path
import sys
notebook_dir = Path({str(root)!r})
repo_root = notebook_dir / "supplementary" / "approved"
sys.path[:0] = [str(repo_root), str(notebook_dir), str(notebook_dir / "supplementary" / "helpers")]
'''
nb = nbf.v4.new_notebook()
nb.cells = [nbf.v4.new_markdown_cell(r'''# Fast extragradient: convergence discovery
Let $A$ be a monotone, $L$-Lipschitz operator on a finite-dimensional real Euclidean space, with $L>0$, $A(x_\star)=0$, and $\|x_0-x_\star\|^2\le R^2$, $R\ge0$.
For $k=0,\ldots,N-1$, use
$$x_{k+1/2}=x_k+\frac{x_0-x_k}{k+1}-\frac{k}{(k+1)L}A(x_k),$$
$$x_{k+1}=x_k+\frac{x_0-x_k}{k+1}-\frac1L A(x_{k+1/2}).$$
The first intermediate point is exactly $x_{1/2}=x_0$. The target is $\|A(x_N)\|^2$ for integer $N\ge1$.'''),
nbf.v4.new_markdown_cell('## Proof statement (pending)\nThe numerical candidate below remains a conjecture; later blocks will establish the certificate and Lyapunov proof.'),
nbf.v4.new_code_cell(bootstrap), nbf.v4.new_code_cell(imports),
nbf.v4.new_markdown_cell('## Operator and parameters'),
nbf.v4.new_code_cell(setup[setup.index('L = pf.Parameter'):setup.index('def make_ctx_feg')]),
nbf.v4.new_markdown_cell('## Algorithm and PEP setup'),
nbf.v4.new_code_cell(setup[setup.index('def make_ctx_feg'):]),
nbf.v4.new_markdown_cell('## Numerical evidence\nPairwise monotonicity and Lipschitz inequalities give a PEP relaxation. The saved sweep used CLARABEL defaults, with all seven statuses optimal.'),
nbf.v4.new_code_cell('''evidence = json.loads((notebook_dir / "state/feg_b1.json").read_text())
rows = evidence["sweep_results"]
for row in rows:
    print(f"N={row['N']}: {row['opt_value']:.10f}; {row['status']}")
ns = [row["N"] for row in rows]
values = [row["opt_value"] for row in rows]
plt.plot(ns, values, "o-", label="PEP relaxation")
plt.plot(ns, [4/n**2 for n in ns], "--", label="candidate 4/N²")
plt.xlabel("N")
plt.ylabel("squared residual, L=R=1")
plt.legend()
plt.grid(True)
plt.show()
assert all(row["first_half_same_point"] for row in rows)
assert max(abs(row["opt_value"] - 4/row["N"]**2) for row in rows[1:]) < 1e-5
print("First-half alias and candidate-rate numerical checks passed.")'''),
nbf.v4.new_markdown_cell(r'''The conjectured bound is $\|A(x_N)\|^2\le 4L^2R^2/N^2$. It matches the relaxation for $N=2,\ldots,7$; the first-horizon value is $2L^2R^2$. Scaling follows from $x=Ry$ and $A(x)=LRB(y)$ for $R>0$; $R=0$ gives a stationary sequence. No all-horizon proof is claimed yet.'''),
nbf.v4.new_markdown_cell('## Full-PEP certificate (pending Block 2)'),
nbf.v4.new_markdown_cell('## Lyapunov partial sums (pending Block 3)'),
nbf.v4.new_markdown_cell('## Identify the vectors composing the Lyapunov function (pending Block 4)'),
nbf.v4.new_markdown_cell('## Closed-form Lyapunov theorem and exact identities (pending Block 5)')]
nb.metadata.kernelspec = {"name": "feg-private", "display_name": "FEG private Python", "language": "python"}
path = root / 'feg_example_lyap.ipynb'
nbf.write(nb, path)
kdir = runtime.RUNTIME / 'jupyter/kernels/feg-private'
kdir.mkdir(parents=True, exist_ok=True)
(kdir / 'kernel.json').write_text(json.dumps({"argv": [str(Path(os.sys.executable)), '-I', '-B', '-m', 'ipykernel_launcher', '-f', '{connection_file}'], "display_name": "FEG private Python", "language": "python"}))
os.environ['JUPYTER_PATH'] = str(runtime.RUNTIME / 'jupyter')
NotebookClient(nb, timeout=120, kernel_name='feg-private', resources={"metadata": {"path": str(root)}}).execute()
nbf.write(nb, path)
print('Notebook executed:', path)


