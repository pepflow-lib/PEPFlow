import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent / "helpers"))
import runtime
import json
import hashlib
import nbformat as nb
from nbclient import NotebookClient

root = runtime.ATTEMPT
results = json.loads((root / 'supplementary/_sweep_tmp.json').read_text())
residual = max(abs(row['opt_value'] - 1 / (4 * row['N'])) for row in results)
assert residual < 1e-5
(root / 'state').mkdir(exist_ok=True)
state = dict(algo_name='pgm', problem_type='composite', obj_tag='h',
             params_json='{"L": 1, "R": 1}', performance_metric='h(x_N) - h(x_star)',
             initial_condition='||x_0-x_star||^2 <= R^2', conjectured_rate='L*R^2/(4*N)',
             setup_file='pgm_setup.py', sweep_results=results, N_verify=4,
             supplied_assistance='Fixed PGM SOS aid in approved/input.md; not yet verified or used as solver constraint',
             rate_status='numerical conjecture', max_rate_residual=residual,
             presentation_policy='evaluation-ancillary-v1')
(root / 'state/pgm_b1.json').write_text(json.dumps(state, indent=2))
setup = (root / 'pgm_setup.py').read_text()
functions = setup[setup.index('def make_ctx_pgm'):]
notebook = nb.v4.new_notebook()
notebook.cells = [
nb.v4.new_markdown_cell(r'''# Proximal gradient: composite convex objective gap
Let $f$ be convex and $L$-smooth, $L>0$, and let $g$ be closed, proper, and convex in a real finite-dimensional Euclidean space. Write $h=f+g$. Assume $x_\star$ minimizes $h$, $R\ge0$, $N\ge1$ is an integer, and $\|x_0-x_\star\|^2\le R^2$. Proximal steps and evaluations are well-defined.
$$x_{k+1}=\operatorname{prox}_{g/L}\left(x_k-\frac{1}{L}\nabla f(x_k)\right),\qquad k=0,\ldots,N-1.$$
The performance metric is $h(x_N)-h(x_\star)$.
The input supplies a candidate SOS decomposition, to be verified in subsequent certificate work; it is not imposed in this numerical model.'''),
nb.v4.new_markdown_cell('## Theorem and proof\nPending Block 5. Numerical evidence below is a conjecture, not an arbitrary-horizon theorem.'),
nb.v4.new_code_cell(f'''import sys
import json
from pathlib import Path

notebook_dir = Path({str(root)!r})
repo_root = notebook_dir / "supplementary" / "approved"
sys.path[:0] = [str(repo_root), str(notebook_dir), str(notebook_dir / "supplementary" / "helpers")]
import runtime  # noqa: E402 -- initialize private runtime after path bootstrap
import pepflow as pf  # noqa: E402 -- approved source path set above
import numpy as np  # noqa: E402
import matplotlib.pyplot as plt  # noqa: E402
assert runtime.ATTEMPT == notebook_dir
'''),
nb.v4.new_code_cell('''L = pf.Parameter("L")
R = pf.Parameter("R")
f = pf.SmoothConvexFunction(is_basis=True, tags=["f"], L=L)
g = pf.ConvexFunction(is_basis=True, tags=["g"])
h = (f + g).add_tag("h")'''),
nb.v4.new_code_cell(functions + '\nctx, pb, objective = get_pep_setup(1, {"L": 1, "R": 1})\nprint("Setup built:", len(ctx.basis_vectors()), "basis vectors")'),
nb.v4.new_markdown_cell(r'''## Numerical evidence
The saved, newly generated sweep uses CLARABEL with default settings at $L=R=1$. Its inverse values grow by approximately $4$ per step, suggesting
$$h(x_N)-h(x_\star)\le \frac{LR^2}{4N}.$$
Scaling the spatial coordinate by $R$ and function values by $LR^2$ gives this normalized candidate for $R>0$; $R=0$ starts at a minimizer. The solver statuses, including `optimal_inaccurate` at horizons 6 and 7, are retained below.'''),
nb.v4.new_code_cell('''state = json.loads((notebook_dir / "state/pgm_b1.json").read_text())
rows = state["sweep_results"]
ns = np.array([row["N"] for row in rows])
values = np.array([row["opt_value"] for row in rows])
for row in rows:
    print(f"N={row['N']}: {row['opt_value']:.10f}; {row['status']}")
print("Inverse values:", 1 / values)
print("Inverse increments:", np.diff(1 / values))
print("Maximum absolute rate residual:", np.max(np.abs(values - 1 / (4 * ns))))
assert np.max(np.abs(values - 1 / (4 * ns))) < 1e-5
plt.plot(ns, values, "o", label="PEP values")
plt.plot(ns, 1 / (4 * ns), "-", label="Candidate 1/(4N)")
plt.xlabel("N")
plt.ylabel("Objective gap, L=R=1")
plt.legend()
plt.grid(alpha=0.3)
plt.show()'''),
nb.v4.new_markdown_cell('## Dense and relaxed proof solves\nPending Block 2.'),
nb.v4.new_markdown_cell('## Lambda and S verification\nPending Block 2; supplied SOS remains unverified.'),
nb.v4.new_markdown_cell('## Lyapunov partial sums and ranks\nPending Block 3.'),
nb.v4.new_markdown_cell('## Identify the vectors composing the Lyapunov function\nPending Block 4.'),
nb.v4.new_markdown_cell('## Coefficients and exact identities\nPending Blocks 4 and 5.')]
notebook.metadata.kernelspec = dict(display_name='Python 3 (attempt)', language='python', name='pgm-attempt')
path = root / 'pgm_example_lyap.ipynb'
nb.write(notebook, path)
kdir = runtime.RUNTIME / 'jupyter/kernels/pgm-attempt'
kdir.mkdir(parents=True, exist_ok=True)
(kdir / 'kernel.json').write_text(json.dumps(dict(argv=[sys.executable, '-I', '-B', '-m', 'ipykernel_launcher', '-f', '{connection_file}'], display_name='Python 3 (attempt)', language='python')))
import os
os.environ['JUPYTER_PATH'] = str(runtime.RUNTIME / 'jupyter')
NotebookClient(notebook, timeout=120, kernel_name='pgm-attempt', resources={'metadata': {'path': str(root)}}).execute()
nb.write(notebook, path)
assert all(o.output_type != 'error' for c in notebook.cells if c.cell_type == 'code' for o in c.outputs)
assert any('image/png' in o.get('data', {}) for o in notebook.cells[6].outputs)
for c in notebook.cells:
    if c.cell_type == 'markdown':
        assert not any(x in c.source for x in ('\\(', '\\)', '\\[', '\\]', '\x0c', '\r'))
print('Notebook clean-kernel execution passed; plot output present; Markdown delimiter checks passed.')
items = [
('title, problem description, and the algorithm update equations in LaTeX','verified','0','Assumptions, metric and recurrence inspected; source delimiters checked.'),
('proof statement placeholder, to be filled with the final theorem and proof outline in Block 5','pending','1','Final theorem due in B5.'),
('imports','verified','2','Executed in fresh kernel using approved source root.'),
('function/operator definitions','verified','3','Smooth-convex f, convex g, h=f+g; L and R.'),
('make_ctx_{ALGO_NAME} and get_pep_setup','verified','4','Visible proximal recurrence, stationarity, radius squared and objective; executed.'),
('numerical evidence, including a plot comparing the PEP values against the discovered or conjectured rate','verified','5,6','Seven saved solver outputs, inverse differences, rate residual and PNG plot output inspected structurally; visual inspection excluded by policy.'),
('dense and relaxed proof solves','pending','7','Due B2.'),
('lambda and S verification (closed-form when available, otherwise numerical with explicit analytic status)','pending','8','Due B2.'),
('partial-sum Lyapunov construction and rank profile','pending','9','Due B3.'),
('special-vector identification','pending','10','Due B4.'),
('coefficient extraction and closed-form V_k','pending','11','Due B4/B5.'),
('symbolic step, base, and boundary identities','pending','11','Due B5.')]
text = f'Notebook: {path.name}\nLast reviewed block: B1\nSHA-256: {hashlib.sha256(path.read_bytes()).hexdigest()}\nPresentation policy: evaluation-ancillary-v1; no rendering or image inspection performed.\n\n| # | Item | Status | Cells (zero based) | Evidence |\n|---|---|---|---|---|\n'
text += '\n'.join(f'| {i} | {name} | {status} | {cells} | {evidence} |' for i, (name,status,cells,evidence) in enumerate(items,1))
(root / 'supplementary/pgm_example_lyap_checklist.md').write_text(text)


