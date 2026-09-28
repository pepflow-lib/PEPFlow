import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent / "helpers"))
import runtime
import json
import nbformat as nb
from nbclient import NotebookClient

root = runtime.ROOT
results = json.loads((root / 'supplementary/_sweep_tmp.json').read_text())
state = {'algo_name':'bppm','problem_type':'convex_bregman','obj_tag':'f',
         'params_json':json.dumps({'alpha':1,'R':1}), 'performance_metric':'f(x_N)-f(x_star)',
         'initial_condition':'D_h(x_star,x_0)<=R','conjectured_rate':'R/(alpha*N)',
         'setup_file':'bppm_setup.py','sweep_results':results,'N_verify':4}
(root / 'state').mkdir(exist_ok=True)
(root / 'state/bppm_b1.json').write_text(json.dumps(state, indent=2))
source = (root / 'bppm_setup.py').read_text(encoding='utf-8-sig')
def md(s):
    return nb.v4.new_markdown_cell(s)
def code(s):
    return nb.v4.new_code_cell(s)
notebook = nb.v4.new_notebook(cells=[
md(r'''# Bregman proximal point minimization
In a real finite-dimensional Euclidean space, let $f$ be closed, proper and convex, differentiable relative to the closed, proper, convex differentiable kernel $h$. Let $x_\star$ minimize $f$, $\alpha>0$, $R\geq0$, and $N\geq1$. All stated evaluations and proximal updates are well-defined.
$$D_h(u,v)=h(u)-h(v)-\langle\nabla h(v),u-v\rangle,\qquad D_h(x_\star,x_0)\leq R.$$
For $k=0,\ldots,N-1$,
$$x_{k+1}\in\mathop{\rm argmin}_x\{\alpha f(x)+D_h(x,x_k)\},\qquad \nabla h(x_{k+1})=\nabla h(x_k)-\alpha\nabla f(x_{k+1}).$$
The performance metric is $f(x_N)-f(x_\star)$. The supplied conjecture is $R/(\alpha N)$; this is not yet a proved theorem.'''),
md('## Proof statement\nPending Blocks 2–5: full certificate, Lyapunov construction, and exact proof.'),
code('from pathlib import Path\nimport sys\nimport json\nimport numpy as np\nimport matplotlib.pyplot as plt'),
code(f'notebook_dir = Path({str(root)!r})\nrepo_root = notebook_dir / "supplementary" / "approved"\nsys.path[:0] = [str(repo_root), str(notebook_dir), str(notebook_dir / "supplementary")]'),
code('import pepflow as pf'),
code(source[source.index('f = pf.'):source.index('\n\ndef make_ctx')]),
code(source[source.index('def make_ctx'):]),
md('## Numerical evidence\nOne CLARABEL sweep, with default solver options and alpha=R=1. Convex interpolation provides an upper model for the supplied differentiable class. No additional strong convexity or relative smoothness assumptions are imposed.'),
code('sweep = json.loads((notebook_dir / "supplementary/_sweep_tmp.json").read_text())\nns = np.array([row["N"] for row in sweep])\nvalues = np.array([row["opt_value"] for row in sweep])\nfor row in sweep:\n    print(row["N"], row["opt_value"], row["status"])\nprint("maximum rate discrepancy:", np.max(np.abs(values - 1 / ns)))\nprint("reciprocal increments:", np.diff(1 / values))\nassert np.allclose(values, 1 / ns, atol=1e-5, rtol=0)\nplt.plot(ns, values, "o", label="PEP")\nplt.plot(ns, 1 / ns, "-", label="R/(alpha N)")\nplt.xlabel("N")\nplt.ylabel("objective gap")\nplt.legend()\nplt.grid(True)\nplt.show()'),
md(r'The numerical evidence matches the supplied conjecture $R/(\alpha N)$. It does not constitute an all-horizon proof.'),
md('## Full PEP certificate\nPending Block 2.'),
md('## Partial-sum Lyapunov construction\nPending Block 3.'),
md('## Special vectors and coefficients\nPending Block 4.'),
md('## Closed-form Lyapunov theorem and exact identities\nPending Block 5.')])
kernels = root / 'supplementary/.runtime/kernels'
location = kernels / 'bppm-owned'
location.mkdir(parents=True, exist_ok=True)
(location / 'kernel.json').write_text(json.dumps({'argv':[sys.executable,'-I','-B','-m','ipykernel_launcher','-f','{connection_file}'],'display_name':'BPPM owned','language':'python'}))
import os
os.environ['JUPYTER_PATH'] = str(kernels.parent)
notebook.metadata.kernelspec = {'name':'bppm-owned','display_name':'BPPM owned','language':'python'}
NotebookClient(notebook, timeout=120, kernel_name='bppm-owned', resources={'metadata':{'path':str(root)}}).execute()
nb.write(notebook, root / 'bppm_example_lyap.ipynb')
print('Saved executed notebook and B1 state.')

