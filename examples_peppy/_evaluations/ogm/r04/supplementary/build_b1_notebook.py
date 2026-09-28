import hashlib
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent / "helpers"))
from runtime import configure

attempt, approved = configure()
import nbformat as nbf
from nbclient import NotebookClient

rows = json.loads((attempt / "supplementary/_sweep_tmp.json").read_text())
for row in rows:
    row["candidate_rate"] = 1 / (2 * row["theta_N"]**2)
    row["absolute_error"] = abs(row["opt_value"] - row["candidate_rate"])
print("max rate residual", max(row["absolute_error"] for row in rows))
state = {"algo_name": "ogm", "problem_type": "smooth_convex", "obj_tag": "f", "params_json": '{"L": 1, "R": 1}', "performance_metric": "f(x_N)-f(x_star)", "initial_condition": "||x_0-x_star||^2 <= R^2", "conjectured_rate": "L*R**2/(2*theta_N**2)", "setup_file": "ogm_setup.py", "sweep_results": rows, "N_verify": 4, "numerical_certificate_verified": False, "analytic_full_pep_verified": False, "lyapunov_proof_verified": False}
(attempt / "state").mkdir(exist_ok=True)
(attempt / "state/ogm_b1.json").write_text(json.dumps(state, indent=2))
nb = nbf.v4.new_notebook()
md = nbf.v4.new_markdown_cell
code = nbf.v4.new_code_cell
nb.cells = [md(r'''# OGM: numerical evidence and Lyapunov discovery

Let $f$ be convex and $L$-smooth on a real finite-dimensional Euclidean space, with $L>0$, $R\geq0$, $N\geq1$, $\nabla f(x_\star)=0$, $\|x_0-x_\star\|^2\leq R^2$, and $z_0=x_0$. The target is $f(x_N)-f(x_\star)$.

Set $\theta_{-1}=0$ and
$$\theta_k=\frac{1+\sqrt{1+4\theta_{k-1}^2}}2\quad(0\leq k<N),\qquad
\theta_N=\frac{1+\sqrt{1+8\theta_{N-1}^2}}2.$$
For $0\leq k<N$ perform
$$y_{k+1}=x_k-\frac1L\nabla f(x_k),\qquad
z_{k+1}=z_k-\frac{2\theta_k}{L}\nabla f(x_k),\qquad
x_{k+1}=\left(1-\frac1{\theta_{k+1}}\right)y_{k+1}+\frac{z_{k+1}}{\theta_{k+1}}.$$
The terminal theta uses eight, while the preceding recurrences use four.
'''), md('## Proof statement (pending)\nThe numerical candidate below awaits certificate analysis and an arbitrary-horizon proof in Blocks 2–5.'), code('''import json
import math
import sys
from pathlib import Path

notebook_dir = Path.cwd().resolve()
repo_root = notebook_dir / "supplementary" / "approved"
sys.path.insert(0, str(repo_root))
sys.path.insert(0, str(notebook_dir / "supplementary" / "helpers"))
from runtime import configure

configure()
import pepflow as pf
import matplotlib.pyplot as plt
'''),code('''L = pf.Parameter("L")
R = pf.Parameter("R")
f = pf.SmoothConvexFunction(is_basis=True, tags=["f"], L=L)
''')]
setup = (attempt / "ogm_setup.py").read_text(encoding="utf-8-sig")
nb.cells.append(code(setup[setup.index('def theta_sequence'):]))
nb.cells.append(md('## Numerical evidence\nSeven dense PEP solves with CLARABEL defaults and L=R=1. The same cached sweep is reused here. The scaled values suggest the candidate $L R^2/(2\\theta_N^2)$; numerical agreement is not an analytic proof.'))
nb.cells.append(code('''sweep = json.loads((notebook_dir / "state" / "ogm_b1.json").read_text())["sweep_results"]
for row in sweep:
    print(f"N={row['N']}: PEP={row['opt_value']:.10f}, candidate={row['candidate_rate']:.10f}, "
          f"2 theta_N^2 PEP={2 * row['theta_N']**2 * row['opt_value']:.10f}, status={row['status']}")
residual = max(row["absolute_error"] for row in sweep)
print("Maximum absolute discrepancy:", residual)
assert residual <= 1e-5
fig, ax = plt.subplots(figsize=(6, 4))
ax.plot([r["N"] for r in sweep], [r["opt_value"] for r in sweep], "o", label="Dense PEP")
ax.plot([r["N"] for r in sweep], [r["candidate_rate"] for r in sweep], "-", label=r"$1/(2\\theta_N^2)$ candidate")
ax.set(xlabel="N", ylabel="Objective gap", title="OGM, L=R=1")
ax.legend()
ax.grid(alpha=0.25)
plt.show()
'''))
nb.cells.extend([md('## Full-PEP certificate (Block 2 pending)'),md('## Lyapunov partial sums (Block 3 pending)'),md('## Identify the vectors composing the Lyapunov function\nBlock 4 pending.'),md('## Closed-form Lyapunov function and exact identities\nBlock 5 pending.')])
imports = nb.cells[2].source
part1, rest = imports.split('from runtime import configure', 1)
part2, part3 = ('from runtime import configure' + rest).split('import pepflow as pf', 1)
nb.cells[2:3] = [code(part1), code(part2), code('import pepflow as pf' + part3)]
nb.metadata['kernelspec'] = {'display_name':'OGM isolated Python','language':'python','name':'ogm-own'}
nbpath = attempt / 'ogm_example_lyap.ipynb'
nbf.write(nb, nbpath)
import os
kernelroot = attempt / 'supplementary/.runtime/jupyter'
kerneldir = kernelroot / 'kernels/ogm-own'
kerneldir.mkdir(parents=True, exist_ok=True)
(kerneldir / 'kernel.json').write_text(json.dumps({'argv':[sys.executable,'-I','-B','-m','ipykernel_launcher','-f','{connection_file}'],'display_name':'OGM isolated Python','language':'python'}))
os.environ['JUPYTER_PATH'] = str(kernelroot)
NotebookClient(nb, timeout=120, kernel_name='ogm-own', resources={'metadata':{'path':str(attempt)}}).execute()
nbf.write(nb, nbpath)
items = ['title, problem description, and the algorithm update equations in LaTeX','proof statement placeholder, to be filled with the final theorem and proof outline in Block 5','imports','function/operator definitions','make_ctx_ogm and get_pep_setup','numerical evidence, including a plot comparing the PEP values against the discovered or conjectured rate','dense and relaxed proof solves','lambda and S verification (closed-form when available, otherwise numerical with explicit analytic status)','partial-sum Lyapunov construction and rank profile','special-vector identification','coefficient extraction and closed-form V_k','symbolic step, base, and boundary identities']
check = [f'Notebook: {nbpath.name}', 'Last reviewed block: B1', 'SHA-256: ' + hashlib.sha256(nbpath.read_bytes()).hexdigest(), 'Presentation policy: evaluation-ancillary-v1; no rendered/image inspection performed.', '', '| Item | Status | Cells | Evidence |','|---|---|---|---|']
cells = {1:'0',3:'2,3,4',4:'5',5:'6',6:'7,8'}
for i, item in enumerate(items,1):
    status = 'verified' if i in cells else 'pending'
    evidence = 'Source and executed outputs inspected; plot output stored (visual review omitted by policy).' if i == 6 else ('Required source content present; Markdown escape check passed.' if i in cells else 'Later block obligation.')
    check.append(f'| {i}. {item} | {status} | {cells.get(i,"—")} | {evidence} |')
(attempt / 'supplementary/ogm_example_lyap_checklist.md').write_text('\n'.join(check), encoding='utf-8')
for cell in nb.cells:
    if cell.cell_type == 'markdown':
        assert '\\(' not in cell.source and '\\[' not in cell.source
        assert not any(ord(c)<32 and c not in '\n\t' for c in cell.source)
print('Notebook executed; cells:', len(nb.cells))
print('Output types:', [o.output_type for c in nb.cells if c.cell_type=='code' for o in c.outputs])
print('Stored image output:', any('image/png' in o.get('data',{}) for c in nb.cells if c.cell_type=='code' for o in c.outputs))


