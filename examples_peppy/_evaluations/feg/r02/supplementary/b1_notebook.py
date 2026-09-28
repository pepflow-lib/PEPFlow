import runpy
from pathlib import Path
runpy.run_path(str(Path(__file__).with_name("runtime.py")))
import json
import os
import sys
import nbformat as nbf
from nbclient import NotebookClient

root = Path(__file__).resolve().parents[1]
results = json.loads((root / "supplementary/_sweep_tmp.json").read_text())
state = dict(algo_name="feg", problem_type="monotone_operator", obj_tag="A", params_json='{"L": 1, "R": 1}', performance_metric="||A(x_N)||^2", initial_condition="||x_0-x_star||^2 <= R^2", conjectured_rate="4*L**2*R**2/N**2", setup_file="feg_setup.py", sweep_results=results, N_verify=6, rate_status="numerical conjecture; N=1 value 2 is below bound 4", numerical_certificate_verified=False, analytic_full_pep_verified=False, lyapunov_proof_verified=False)
(root / "state").mkdir(exist_ok=True)
(root / "state/feg_b1.json").write_text(json.dumps(state, indent=2))
source = (root / "feg_setup.py").read_text(encoding="utf-8-sig")
nb = nbf.v4.new_notebook()
md = nbf.v4.new_markdown_cell
code = nbf.v4.new_code_cell
nb.cells = [md(r'''# FEG: residual convergence for monotone Lipschitz operators

Let $A$ be monotone and $L$-Lipschitz on a real finite-dimensional Euclidean space, with $L>0$, $A(x_\star)=0$, and $\|x_0-x_\star\|^2\le R^2$, $R\ge0$. For integer $N\ge1$, the metric is $\|A(x_N)\|^2$.

For $k=0,\ldots,N-1$,
$$x_{k+1/2}=x_k+\frac{x_0-x_k}{k+1}-\frac{k}{(k+1)L}A(x_k),$$
$$x_{k+1}=x_k+\frac{x_0-x_k}{k+1}-\frac1L A(x_{k+1/2}).$$
At $k=0$, $x_{1/2}=x_0$ is one shared point.'''), md('## Proof statement (pending)\nThe candidate uniform bound is $4L^2R^2/N^2$. Blocks 2–5 will investigate certificates and an exact Lyapunov proof.'), code('import sys\nfrom pathlib import Path\nimport json\n\nnotebook_dir = Path.cwd()\nrepo_root = notebook_dir / "supplementary" / "approved"\nsys.path[:0] = [str(repo_root), str(notebook_dir), str(notebook_dir / "supplementary")]\nimport pepflow as pf\nimport sympy as sp\nimport matplotlib.pyplot as plt\nprint("Framework origin:", pf.__file__)'), md('## Operator and parameter definitions'), code(source[source.index('L = pf.Parameter'):source.index('def make_ctx_feg')]), md('## Algorithm and PEP setup'), code(source[source.index('def make_ctx_feg'):]), code('ctx, pb, op = get_pep_setup(6, {})\nassert ctx["x_0"] is ctx["x_1/2"]\nprint("Shared initial point verified; basis dimension:", len(ctx.basis_vectors()))'), md('## Numerical evidence\nCLARABEL defaults; all seven solves returned optimal. Pairwise monotonicity and Lipschitz constraints provide the PEP relaxation used here. Numerical evidence does not establish an arbitrary-horizon theorem.'), code('state = json.loads((notebook_dir / "state/feg_b1.json").read_text())\nrows = state["sweep_results"]\nfor row in rows:\n    print(f"N={row[\'N\']}: {row[\'opt_value\']:.10f}; N^2*value={row[\'N\']**2*row[\'opt_value\']:.8f}; {row[\'status\']}")\nns = [row["N"] for row in rows]\nvalues = [row["opt_value"] for row in rows]\nplt.plot(ns, values, "o-", label="PEP relaxation")\nplt.plot(ns, [4/n**2 for n in ns], "--", label="Conjecture: 4/N²")\nplt.xlabel("N")\nplt.ylabel("Squared residual (L=R=1)")\nplt.legend()\nplt.grid(True)\nplt.show()'), md('For $N=2,\\ldots,7$, the values agree with $4/N^2$ to within $10^{-8}$. At $N=1$, the PEP value is $2$. Thus $4L^2R^2/N^2$ is the uniform candidate bound; its tightness at $N=1$ is not conjectured. Scaling $x$ by $R$ and $A$ by $LR$ accounts for the factor $L^2R^2$ when $R>0$; $R=0$ is stationary.'), md('## Dense and relaxed proof solves\nPending Block 2.'), md('## Lambda and S verification\nPending Block 2.'), md('## Lyapunov partial sums and rank profile\nPending Block 3.'), md('## Identify the vectors composing the Lyapunov function\nPending Block 4.'), md('## Closed-form Lyapunov function and exact identities\nPending Block 5.')]
bootstrap, imports = nb.cells[2].source.split('import pepflow as pf', 1)
nb.cells[2].source = bootstrap
nb.cells.insert(3, code('import pepflow as pf' + imports))
nb.metadata['kernelspec'] = dict(name='feg-owned', display_name='FEG owned Python', language='python')
path = root / 'feg_example_lyap.ipynb'
nbf.write(nb, path)
jupyter = root / 'supplementary/.runtime/jupyter'
kdir = jupyter / 'kernels/feg-owned'
kdir.mkdir(parents=True, exist_ok=True)
(kdir / 'kernel.json').write_text(json.dumps(dict(argv=[sys.executable, '-I', '-B', '-m', 'ipykernel_launcher', '-f', '{connection_file}'], display_name='FEG owned Python', language='python')))
os.environ['JUPYTER_PATH'] = str(jupyter)
NotebookClient(nb, timeout=120, kernel_name='feg-owned', resources={'metadata': {'path': str(root)}}).execute()
nbf.write(nb, path)
print('Notebook executed in fresh owned kernel:', path)

