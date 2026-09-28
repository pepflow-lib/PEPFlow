import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
import runtime
import json
import os
import nbformat as nbf
from nbclient import NotebookClient

root = runtime.ATTEMPT
results = json.loads((root / 'supplementary/b1_sweep.json').read_text())
state = {'algo_name': 'dual_feg', 'problem_type': 'monotone_operator', 'obj_tag': 'A', 'params_json': '{"L": 1, "R": 1}', 'performance_metric': '||A(x_N)||^2', 'initial_condition': '||x_0-x_star||^2 <= R^2; A(x_star)=0; z_0=0', 'conjectured_rate': '4*L**2*R**2/N**2', 'setup_file': 'dual_feg_setup.py', 'sweep_results': results, 'N_verify': 6, 'rate_status': 'numerically supported for N=2..7; N=1 gives approximately 2 rather than 4; theorem unproved'}
(root / 'state').mkdir(exist_ok=True)
(root / 'state/dual_feg_b1.json').write_text(json.dumps(state, indent=2))
nb = nbf.v4.new_notebook()
nb.cells = [nbf.v4.new_markdown_cell(r'''# Dual FEG: residual convergence
Let $A$ be monotone and $L$-Lipschitz on a real finite-dimensional Euclidean space, with $L>0$, $A(x_\star)=0$, $\|x_0-x_\star\|^2\le R^2$, $R\ge0$, and $z_0=0$. Fix an integer $N\ge1$ and $\alpha=1/L$. For $k=0,\ldots,N-1$,
$$x_{k+1/2}=x_k-\alpha z_k-\alpha A(x_k),$$
$$x_{k+1}=x_{k+1/2}-\frac{N-k-1}{N-k}\alpha(A(x_{k+1/2})-A(x_k)),$$
$$z_{k+1}=\frac{N-k-1}{N-k}z_k-\frac{A(x_{k+1/2})}{N-k}.$$
We investigate the squared final residual $\|A(x_N)\|^2$. Pairwise monotonicity and Lipschitz inequalities yield a valid PEP upper-bound relaxation; finite sample agreement alone is not an arbitrary-horizon theorem.'''), nbf.v4.new_markdown_cell('## Proof statement (pending B5)\nCandidate bound: $\\|A(x_N)\\|^2\\le 4L^2R^2/N^2$. Proof certificate, Lyapunov construction, and exact identities remain pending.'), nbf.v4.new_code_cell('''import json
import sys
from pathlib import Path

notebook_dir = Path.cwd().resolve()
repo_root = notebook_dir / "supplementary" / "approved"
REPO_ROOT = repo_root
sys.path[:0] = [str(repo_root), str(notebook_dir / "supplementary" / "helpers")]
import runtime
import pepflow as pf
import sympy as sp
import matplotlib.pyplot as plt
'''), nbf.v4.new_code_cell('''L = pf.Parameter("L")
R = pf.Parameter("R")
A = pf.LipschitzMonotoneOperator(is_basis=True, tags=["A"], L=L)
''')]
source = (root / 'dual_feg_setup.py').read_text(encoding='utf-8-sig')
nb.cells.append(nbf.v4.new_code_cell(source[source.index('def make_ctx_dual_feg'):]))
nb.cells.append(nbf.v4.new_markdown_cell('## Numerical evidence\nOne CLARABEL-default sweep at $L=R=1$. The $N=1$ status was `optimal_inaccurate`; other samples were `optimal`. The proposed $4/N^2$ bound matches the samples for $N\\ge2$, while $N=1$ has a smaller value. No analytic proof is claimed.'))
nb.cells.append(nbf.v4.new_code_cell('''sweep = json.loads((notebook_dir / "supplementary" / "b1_sweep.json").read_text())
ns = [row["N"] for row in sweep]
values = [row["opt_value"] for row in sweep]
for row in sweep:
    print(f"N={row['N']}: {row['opt_value']:.10f}; status={row['status']}")
print("N^2 times PEP:", [round(n*n*v, 8) for n, v in zip(ns, values)])
print("Maximum absolute discrepancy for N>=2:", max(abs(v-4/n**2) for n, v in zip(ns[1:], values[1:])))
plt.figure(figsize=(7, 4))
plt.plot(ns, values, "o-", label="PEP upper-bound values")
plt.plot(ns, [4/n**2 for n in ns], "--", label="Candidate 4/N^2")
plt.xlabel("Horizon N")
plt.ylabel("Squared residual, L=R=1")
plt.legend()
plt.grid(alpha=0.3)
plt.show()
ctx_check, pb_check, _ = get_pep_setup(2, {"L": 1, "R": 1})
print("Executable setup rebuilt for N=2; tracked iterates x_0 through x_2.")
'''))
for heading in ['Dense and relaxed proof solves', 'Lambda and S verification', 'Partial-sum Lyapunov construction and rank profile', 'Special-vector identification', 'Coefficient extraction and closed-form V_k', 'Symbolic step, base, and boundary identities']:
    nb.cells.append(nbf.v4.new_markdown_cell('## ' + heading + '\nPending the corresponding later block.'))
bootstrap, imports = nb.cells[2].source.split("import runtime", 1)
nb.cells[2].source = bootstrap
nb.cells.insert(3, nbf.v4.new_code_cell("import runtime" + imports + "\nassert runtime.ATTEMPT == notebook_dir\n"))
nb.metadata['kernelspec'] = {'display_name':'Attempt Python', 'language':'python', 'name':'dual-feg-attempt'}
path = root / 'dual_feg_example_lyap.ipynb'
nbf.write(nb, path)
kernels = runtime.RUNTIME / 'jupyter' / 'kernels' / 'dual-feg-attempt'
kernels.mkdir(parents=True, exist_ok=True)
(kernels / 'kernel.json').write_text(json.dumps({'argv':[sys.executable, '-I', '-B', '-m', 'ipykernel_launcher', '-f', '{connection_file}'], 'display_name':'Attempt Python', 'language':'python'}))
os.environ['JUPYTER_PATH'] = str(runtime.RUNTIME / 'jupyter')
NotebookClient(nb, timeout=120, kernel_name='dual-feg-attempt', resources={'metadata': {'path': str(root)}}).execute()
nbf.write(nb, path)
print('Notebook executed:', path)


