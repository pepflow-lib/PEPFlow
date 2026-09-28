import hashlib
import importlib.util
import json
from pathlib import Path

root = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("runtime", root / "supplementary/helpers/runtime.py")
assert spec is not None and spec.loader is not None
runtime = importlib.util.module_from_spec(spec)
spec.loader.exec_module(runtime)
import nbformat as nbf
from nbclient import NotebookClient
from jupyter_client.kernelspec import KernelSpecManager

results = json.loads((root / "supplementary/_sweep_tmp.json").read_text())
assert len(results) == 7
state = {"algo_name": "dual_feg", "problem_type": "monotone_operator", "obj_tag": "A",
         "params_json": '{"L": 1, "R": 1}', "performance_metric": "||A(x_N)||^2",
         "initial_condition": "A(x_star)=0; ||x_0-x_star||^2 <= R^2; z_0=0",
         "conjectured_rate": "4*L**2*R**2/N**2", "setup_file": "dual_feg_setup.py",
         "sweep_results": results, "N_verify": 6,
         "rate_note": "N=2..7 match 4/N^2; N=1 gives approximately 2 with optimal_inaccurate status. The uniform conjecture is an upper bound, not equality at N=1."}
(root / "state").mkdir(exist_ok=True)
(root / "state/dual_feg_b1.json").write_text(json.dumps(state, indent=2))
nb = nbf.v4.new_notebook()
nb.cells = [nbf.v4.new_markdown_cell(r'''# Dual FEG: terminal residual and Lyapunov discovery
Let $A$ be a monotone, $L$-Lipschitz operator on a finite-dimensional real Euclidean space, with $L>0$, $A(x_\star)=0$, $\|x_0-x_\star\|^2\le R^2$, $R\ge0$, and $z_0=0$. For an integer horizon $N\ge1$ and $\alpha=1/L$:
$$y_k=x_k-\alpha z_k-\alpha A(x_k),$$
$$x_{k+1}=y_k-\frac{N-k-1}{N-k}\alpha(A(y_k)-A(x_k)),$$
$$z_{k+1}=\frac{N-k-1}{N-k}z_k-\frac{A(y_k)}{N-k},\qquad 0\le k<N.$$
The selected performance metric is $\|A(x_N)\|^2$. We investigate the conjectured upper bound $4L^2R^2/N^2$.'''),
nbf.v4.new_markdown_cell('## Proof statement (pending Block 5)\nThe rate is currently numerical evidence only. No arbitrary-horizon proof is claimed.'),
nbf.v4.new_code_cell('''import sys
from pathlib import Path
notebook_dir = Path.cwd().resolve()
repo_root = notebook_dir / "supplementary" / "approved"
sys.path[:0] = [str(repo_root), str(notebook_dir / "supplementary" / "helpers")]
import runtime
import json
import matplotlib.pyplot as plt
import pepflow as pf
import sympy as sp
assert runtime.NOTEBOOK_DIR == notebook_dir
assert Path(pf.__file__).resolve().is_relative_to(repo_root)
'''),
nbf.v4.new_code_cell('''L = pf.Parameter("L")
R = pf.Parameter("R")
A = pf.LipschitzMonotoneOperator(is_basis=True, tags=["A"], L=L)'''),
nbf.v4.new_code_cell((root / 'dual_feg_setup.py').read_text(encoding='utf-8-sig').split('def make_ctx_dual_feg',1)[1].join(['def make_ctx_dual_feg',''])),
nbf.v4.new_markdown_cell('## Numerical evidence\nA single CLARABEL-default sweep was performed for $N=1,\\ldots,7$. The $N=1$ status was `optimal_inaccurate`; all remaining statuses were `optimal`. The conjecture is an upper bound and is not tight at $N=1$.'),
nbf.v4.new_code_cell('''evidence = json.loads((notebook_dir / "state/dual_feg_b1.json").read_text())
rows = evidence["sweep_results"]
for row in rows:
    print(f'N={row["N"]}: {row["opt_value"]:.10f}; {row["status"]}; N^2 value={row["N"]**2*row["opt_value"]:.10f}')
ns = [row["N"] for row in rows]
plt.plot(ns, [row["opt_value"] for row in rows], "o-", label="PEP squared residual")
plt.plot(ns, [4/n**2 for n in ns], "--", label="Conjecture 4/N^2")
plt.xlabel("N")
plt.ylabel("Squared residual, L=R=1")
plt.legend()
plt.grid(True)
plt.show()
ctx, pb, obj = get_pep_setup(2, {"L": 1, "R": 1})
print("Setup reconstruction available:", len(ctx.basis_vectors()), "basis vectors")'''),
nbf.v4.new_markdown_cell('## Dense and relaxed proof solves\nPending Block 2.'),
nbf.v4.new_markdown_cell('## Lambda and S verification\nPending Block 2; analytic status unresolved.'),
nbf.v4.new_markdown_cell('## Partial-sum Lyapunov construction and rank profile\nPending Block 3.'),
nbf.v4.new_markdown_cell('## Identify the vectors composing the Lyapunov function\nPending Block 4.'),
nbf.v4.new_markdown_cell('## Coefficients and closed-form Lyapunov function\nPending Blocks 4–5.'),
nbf.v4.new_markdown_cell('## Symbolic step, base, and boundary identities\nPending Block 5.')]
bootstrap, imports = nb.cells[2].source.split('import runtime', 1)
nb.cells[2].source = bootstrap
nb.cells.insert(3, nbf.v4.new_code_cell('import runtime' + imports))
nb.metadata.kernelspec = {'name': 'attempt-python', 'display_name': 'Attempt Python', 'language': 'python'}
kdir = root / 'supplementary/.runtime/kernels/attempt-python'
kdir.mkdir(parents=True, exist_ok=True)
(kdir / 'kernel.json').write_text(json.dumps({'argv':[str(Path(runtime.sys.executable)), '-I', '-B', '-m', 'ipykernel_launcher', '-f', '{connection_file}'], 'display_name':'Attempt Python', 'language':'python'}))
ksm = KernelSpecManager(kernel_dirs=[str(kdir.parent)])
from jupyter_client import KernelManager
km = KernelManager(kernel_name='attempt-python', kernel_spec_manager=ksm)
path = root / 'dual_feg_example_lyap.ipynb'
nbf.write(nb, path)
NotebookClient(nb, timeout=120, km=km, resources={'metadata':{'path':str(root)}}).execute()
nbf.write(nb, path)
for cell in nb.cells:
    if cell.cell_type == 'markdown':
        assert '\\(' not in cell.source and '\\[' not in cell.source
        assert not any(ord(c)<32 and c not in '\n\t' for c in cell.source)
items = ['title, problem description, and the algorithm update equations in LaTeX', 'proof statement placeholder, to be filled with the final theorem and proof outline in Block 5', 'imports', 'function/operator definitions', 'make_ctx_dual_feg and get_pep_setup', 'numerical evidence, including a plot comparing the PEP values against the discovered or conjectured rate', 'dense and relaxed proof solves', 'lambda and S verification (closed-form when available, otherwise numerical with explicit analytic status)', 'partial-sum Lyapunov construction and rank profile', 'special-vector identification', 'coefficient extraction and closed-form V_k', 'symbolic step, base, and boundary identities']
cells = [0,1,3,4,5,7,8,9,10,11,12,13]
lines = [f'Notebook: {path.name}\nLast reviewed block: B1\nSHA-256: {hashlib.sha256(path.read_bytes()).hexdigest()}\nPresentation: evaluation-ancillary-v1; no rendering or image inspection performed. Source math checks and execution passed.\n', '| Item | Status | Cell index | Evidence |', '|---|---|---|---|']
for i, (item, cell) in enumerate(zip(items, cells), 1):
    status = 'verified' if i in (1,3,4,5,6) else 'pending'
    evidence_text = 'Source inspected; clean-kernel execution passed.' if status == 'verified' else 'Later-block obligation.'
    if i == 6:
        assert any('image/png' in o.get('data', {}) for o in nb.cells[cell].get('outputs', []))
        evidence_text = 'Seven printed values and stored matplotlib PNG output; no visual review under presentation override.'
    lines.append(f'| {i}. {item} | {status} | {cell} | {evidence_text} |')
(root / 'supplementary/dual_feg_example_lyap_checklist.md').write_text('\n'.join(lines))
(root / 'supplementary/b1-notebook-execution.json').write_text(json.dumps({'status':'passed', 'kernel':'fresh attempt-python', 'python':runtime.sys.executable, 'notebook_sha256':hashlib.sha256(path.read_bytes()).hexdigest(), 'markdown_source_checks':'passed', 'rendered_review':'omitted by evaluation-ancillary-v1'}, indent=2))
print('Notebook executed and source checked; state saved.')



