import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent / "helpers"))
import runtime
import hashlib
import json
import nbformat as nbf
from nbclient import NotebookClient
from jupyter_client import KernelManager

root = runtime.ATTEMPT
results = json.loads((root / 'supplementary/_sweep_tmp.json').read_text())
assert len(results) == 7 and all(r['status'] == 'optimal' for r in results)
state = dict(algo_name='feg', problem_type='monotone_operator', obj_tag='A', params_json=json.dumps({'L':1,'R':1}), performance_metric='||A(x_N)||^2', initial_condition='||x_0-x_star||^2 <= R^2', conjectured_rate='4*L**2*R**2/N**2', setup_file='feg_setup.py', sweep_results=results, N_verify=6, rate_status='numerical conjecture; N=1 has observed sharper value 2*L**2*R**2', numerical_certificate_verified=False, analytic_full_pep_verified=False, lyapunov_proof_verified=False)
(root / 'state').mkdir(exist_ok=True)
(root / 'state/feg_b1.json').write_text(json.dumps(state, indent=2))
nb = nbf.v4.new_notebook()
md = nbf.v4.new_markdown_cell
code = nbf.v4.new_code_cell
nb.cells = [md(r'''# FEG: residual convergence for monotone Lipschitz operators
Let $A$ be monotone and $L$-Lipschitz on a real finite-dimensional Euclidean space, with $L>0$, $R\geq0$, $A(x_\star)=0$ and $\|x_0-x_\star\|^2\leq R^2$. For integer $N\geq1$, measure $\|A(x_N)\|^2$ after the updates
$$x_{k+1/2}=x_k+\frac{x_0-x_k}{k+1}-\frac{k}{(k+1)L}A(x_k),$$
$$x_{k+1}=x_k+\frac{x_0-x_k}{k+1}-\frac{1}{L}A(x_{k+1/2}),\qquad 0\leq k<N.$$
At $k=0$, $x_{1/2}=x_0$ is one shared point and evaluation. The model imposes pairwise monotonicity and Lipschitz inequalities on every evaluated point.
'''), md('## Proof statement (pending)\nThe numerical candidate is $\\|A(x_N)\\|^2\\leq4L^2R^2/N^2$. A theorem and proof will be supplied only after the certificate and symbolic identities are verified.'), code('''from pathlib import Path
import sys
notebook_dir = Path.cwd().resolve()
repo_root = notebook_dir / "supplementary" / "approved"
sys.path[:0] = [str(repo_root), str(notebook_dir / "supplementary" / "helpers")]
'''), code('''import runtime
import json
import pepflow as pf
import sympy as sp
import matplotlib.pyplot as plt
print("Framework:", pf.__file__, "Approved root:", runtime.APPROVED)
''')]
setup = (root / 'feg_setup.py').read_text(encoding='utf-8-sig')
nb.cells.append(code(setup[setup.index('L = pf.Parameter'):setup.index('def make_ctx_feg')]))
nb.cells.append(code(setup[setup.index('def make_ctx_feg'):]))
nb.cells += [md('## Numerical evidence\nCLARABEL with default options, $L=R=1$. The saved sweep was produced from the displayed setup; it is reused here without repeating solves. These SDP values support a conjecture, not an arbitrary-horizon proof.'), code('''sweep = json.loads((notebook_dir / "state" / "feg_b1.json").read_text())["sweep_results"]
for row in sweep:
    print(f'N={row["N"]}: PEP={row["opt_value"]:.10f}; candidate={4 / row["N"]**2:.10f}; status={row["status"]}')
ns = [row["N"] for row in sweep]
values = [row["opt_value"] for row in sweep]
plt.figure(figsize=(6, 4))
plt.plot(ns, values, "o-", label="PEP upper bound")
plt.plot(ns, [4 / n**2 for n in ns], "--", label=r"Candidate $4/N^2$")
plt.yscale("log")
plt.xlabel("Horizon N")
plt.ylabel("Squared residual, L=R=1")
plt.legend()
plt.grid(alpha=0.25)
plt.tight_layout()
plt.show()
print("Max candidate discrepancy for N>=2:", max(abs(row["opt_value"] - 4 / row["N"]**2) for row in sweep[1:]))
print("Initial half-step alias verified:", all(row["initial_half_is_x0"] for row in sweep))
'''), md(r'''For $N\geq2$, the observed values agree with $4/N^2$ to numerical solver precision. At $N=1$, the SDP gives $2$, so the uniform candidate is loose there. Scaling the variables by $R$ and the operator by $L$ gives the candidate $4L^2R^2/N^2$; the zero-radius case is stationary. No analytic proof is claimed in Block 1.

## Dense and relaxed proof solves
Pending Block 2.

## Lambda and S verification
Pending Block 2.

## Partial-sum Lyapunov construction
Pending Block 3.

## Identify the vectors composing the Lyapunov function
Pending Block 4.

## Closed-form Lyapunov function and symbolic identities
Pending Block 5.
''')]
nb.metadata.kernelspec = {'name':'feg-private','display_name':'FEG private Python','language':'python'}
nb.metadata.language_info = {'name':'python','version':'3.11.13'}
nbpath = root / 'feg_example_lyap.ipynb'
nbf.write(nb, nbpath)
ksroot = runtime.RUNTIME / 'jupyter' / 'kernels' / 'feg-private'
ksroot.mkdir(parents=True, exist_ok=True)
(ksroot / 'kernel.json').write_text(json.dumps({'argv':[sys.executable,'-I','-B','-m','ipykernel_launcher','-f','{connection_file}'],'display_name':'FEG private Python','language':'python'}))
km = KernelManager(kernel_name='feg-private')
km.kernel_spec_manager.kernel_dirs = [str(ksroot.parent)]
NotebookClient(nb, km=km, timeout=120, resources={'metadata':{'path':str(root)}}).execute()
nbf.write(nb, nbpath)
items = ['title, problem description, and the algorithm update equations in LaTeX','proof statement placeholder, to be filled with the final theorem and proof outline in Block 5','imports','function/operator definitions','make_ctx_feg and get_pep_setup','numerical evidence, including a plot comparing the PEP values against the discovered or conjectured rate','dense and relaxed proof solves','lambda and S verification (closed-form when available, otherwise numerical with explicit analytic status)','partial-sum Lyapunov construction and rank profile','special-vector identification','coefficient extraction and closed-form V_k','symbolic step, base, and boundary identities']
assert not any(o.output_type == 'error' for c in nb.cells if c.cell_type == 'code' for o in c.outputs)
assert any('image/png' in o.get('data', {}) for o in nb.cells[7].outputs)
for cell in nb.cells:
    if cell.cell_type == 'markdown':
        assert '\\(' not in cell.source and '\\[' not in cell.source
        assert not any(ch in cell.source for ch in ('\x0c', '\r', '\x08'))
checked = {1: '0: assumptions, both updates, alias and metric inspected',3:'2-3: explicit approved imports executed',4:'4: L, R and LipschitzMonotoneOperator',5:'5: recurrence, shared initial half-step, R**2 and final metric',6:'6-8: seven printed values, candidate comparison, embedded PNG plot, alias assertion; source/output inspection only'}
lines = [f'# Notebook evidence checklist\nNotebook: {nbpath.name}\nLast reviewed block: B1\nSHA-256: {hashlib.sha256(nbpath.read_bytes()).hexdigest()}\nPresentation: evaluation-ancillary-v1; no rendering or image inspection performed.\n', '| Item | Status | Cells and evidence |','|---|---|---|']
for i,item in enumerate(items, 1):
    lines.append(f'| {i}. {item} | {"verified" if i in checked else "pending"} | {checked.get(i, "Later-block obligation; placeholder only")} |')
(root / 'supplementary/feg_example_lyap_checklist.md').write_text('\n'.join(lines))
print(json.dumps({'notebook_execution':'passed','math_delimiters':'passed','plot_output':'present, not visually inspected','candidate':'4*L**2*R**2/N**2','values':[r['opt_value'] for r in results]}))


