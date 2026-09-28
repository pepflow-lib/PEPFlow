import hashlib
import importlib.util
import json
from pathlib import Path

import nbformat as nbf
from nbclient import NotebookClient

root = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("runtime", root / "supplementary/helpers/runtime.py")
assert spec is not None and spec.loader is not None
runtime = importlib.util.module_from_spec(spec)
spec.loader.exec_module(runtime)
runtime.configure()
results = json.loads((root / "supplementary/_sweep_tmp.json").read_text())
state = dict(algo_name="pgm", problem_type="composite", obj_tag="f", params_json='{"L": 1, "R": 1}',
             performance_metric="h(x_N)-h(x_star)", initial_condition="||x_0-x_star||^2 <= R^2",
             conjectured_rate="L*R**2/(4*N)", setup_file="pgm_setup.py", sweep_results=results,
             N_verify=4, supplied_assistance="Fixed PGM SOS aid from approved/input.md; unverified in B1",
             numerical_certificate_verified=False, analytic_full_pep_verified=False, lyapunov_proof_verified=False)
(root / "state").mkdir(exist_ok=True)
(root / "state/pgm_b1.json").write_text(json.dumps(state, indent=2))
nb = nbf.v4.new_notebook()
nb.cells = [
nbf.v4.new_markdown_cell(r'''# Proximal gradient method: convergence and Lyapunov discovery
Let $h=f+g$, where $f$ is convex and $L$-smooth and $g$ is closed, proper, and convex on a finite-dimensional real Euclidean space. Assume $L>0$, $R\geq0$, an integer $N\geq1$, a minimizer $x_\star$ of $h$, and $\|x_0-x_\star\|^2\leq R^2$. Proximal evaluations are well-defined.
$$x_{k+1}=\operatorname{prox}_{g/L}\left(x_k-\frac{1}{L}\nabla f(x_k)\right),\qquad k=0,\ldots,N-1.$$
The performance metric is $h(x_N)-h(x_\star)$. Stationarity is imposed on the sum: $\nabla f(x_\star)+s_\star=0$ with $s_\star\in\partial g(x_\star)$.'''),
nbf.v4.new_markdown_cell('## Proof statement (pending Block 5)\nThe numerical conjecture below is not yet a theorem. The fixed SOS candidate in the supplied input is declared assistance; it has not yet been verified against a certificate.'),
nbf.v4.new_code_cell('''from pathlib import Path
import json
import matplotlib.pyplot as plt
import pepflow as pf

notebook_dir = Path.cwd()
repo_root = notebook_dir / "supplementary" / "approved"
assert Path(pf.__file__).resolve().is_relative_to(repo_root.resolve())
print("Approved framework:", pf.__file__)'''),
nbf.v4.new_markdown_cell('## Functions, algorithm, and PEP setup'),
nbf.v4.new_code_cell((root / "pgm_setup.py").read_text(encoding="utf-8-sig").replace('import pepflow as pf\n','')),
nbf.v4.new_code_cell('''ctx, pb, objective_function = get_pep_setup(4, {"L": 1, "R": 1})
print("Created PGM context for N=4 with smooth and convex interpolation groups.")'''),
nbf.v4.new_markdown_cell('## Numerical evidence\nThe single Block 1 sweep uses CLARABEL defaults with $L=R=1$. No sweep is repeated by this notebook; saved results are shown below.'),
nbf.v4.new_code_cell('''b1 = json.loads((notebook_dir / "state" / "pgm_b1.json").read_text())
rows = b1["sweep_results"]
for row in rows:
    n, value = row["N"], row["opt_value"]
    print(f"N={n}: PEP={value:.10f}; 1/PEP={1/value:.7f}; status={row['solver_log'][-1]['status']}")
ns = [row["N"] for row in rows]
values = [row["opt_value"] for row in rows]
candidate = [1/(4*n) for n in ns]
print("Maximum absolute candidate discrepancy:", max(abs(v-c) for v,c in zip(values,candidate)))
fig, ax = plt.subplots()
ax.plot(ns, values, "o", label="PEP")
ax.plot(ns, candidate, "-", label="Candidate 1/(4N)")
ax.set(xlabel="N", ylabel="Normalized objective gap")
ax.legend()
plt.show()'''),
nbf.v4.new_markdown_cell(r'''The reciprocal values are approximately $4N$, suggesting
$$h(x_N)-h(x_\star)\leq\frac{LR^2}{4N}.$$
Scaling $x$ by $R$ and function values by $LR^2$ gives the normalization used in the sweep (the case $R=0$ starts at a minimizer). This bound remains a conjecture. Horizons 6 and 7 have `optimal_inaccurate` solver status; subsequent certificate verification is required.'''),
nbf.v4.new_markdown_cell('## Dense and relaxed proof solves\nPending Block 2.'),
nbf.v4.new_markdown_cell('## Lambda and S verification\nPending Block 2; supplied SOS remains an unverified candidate.'),
nbf.v4.new_markdown_cell('## Partial-sum Lyapunov construction and rank profile\nPending Block 3.'),
nbf.v4.new_markdown_cell('## Identify the vectors composing the Lyapunov function\nPending Block 4.'),
nbf.v4.new_markdown_cell('## Coefficients and closed-form Lyapunov function\nPending Blocks 4 and 5.'),
nbf.v4.new_markdown_cell('## Symbolic step, base, and boundary identities\nPending Block 5.')]
# A private kernelspec bootstraps only the approved package and own helpers.
kernel_dir = runtime.RUNTIME / "jupyter" / "kernels" / "pgm-own"
kernel_dir.mkdir(parents=True, exist_ok=True)
bootstrap = runtime.RUNTIME / "kernel_bootstrap.py"
bootstrap.write_text('import sys\nsys.path[:0] = '+repr([str(runtime.APPROVED), str(root), str(root/'supplementary')])+'\nfrom ipykernel.kernelapp import IPKernelApp\nIPKernelApp.launch_instance()\n')
import os
import sys
os.environ["JUPYTER_PATH"] = str(runtime.RUNTIME / "jupyter")
(kernel_dir / "kernel.json").write_text(json.dumps({"argv":[sys.executable,"-I","-B",str(bootstrap),"-f","{connection_file}"],"display_name":"PGM isolated attempt","language":"python"}))
nb.metadata.kernelspec = {"name":"pgm-own","display_name":"PGM isolated attempt","language":"python"}
path = root / "pgm_example_lyap.ipynb"
nbf.write(nb,path)
NotebookClient(nb, timeout=120, kernel_name="pgm-own", resources={"metadata":{"path":str(root)}}).execute()
nbf.write(nb,path)
for cell in nb.cells:
    if cell.cell_type == 'markdown':
        assert not any(t in cell.source for t in ('\\(', '\\)', '\\[', '\\]', '\x0c', '\r'))
plot_outputs = [o for c in nb.cells for o in c.get('outputs',[]) if 'image/png' in o.get('data',{})]
assert plot_outputs
items = ['title, problem description, and the algorithm update equations in LaTeX','proof statement placeholder, to be filled with the final theorem and proof outline in Block 5','imports','function/operator definitions','make_ctx_pgm and get_pep_setup','numerical evidence, including a plot comparing the PEP values against the discovered or conjectured rate','dense and relaxed proof solves','lambda and S verification (closed-form when available, otherwise numerical with explicit analytic status)','partial-sum Lyapunov construction and rank profile','special-vector identification','coefficient extraction and closed-form V_k','symbolic step, base, and boundary identities']
verified = {1:'0: assumptions, algorithm, metric inspected',3:'2: executed approved-origin import',4:'4: smooth f and convex g definitions',5:'4,5: recurrence, stationarity, radius and metric; executed',6:'6,7,8: seven values, solver statuses, candidate discrepancy and image/png plot output present'}
lines = ['Notebook: pgm_example_lyap.ipynb','Last reviewed block: B1','SHA-256: '+hashlib.sha256(path.read_bytes()).hexdigest(),'Presentation: evaluation-ancillary-v1; no rendering/image inspection performed. Markdown delimiter/control-character checks passed.','', '| Item | Status | Cells and evidence |','|---|---|---|']
for i,item in enumerate(items,1):
    lines.append(f'| {i}. {item} | {"verified" if i in verified else "pending"} | {verified.get(i,"Later-block requirement")} |')
(root/'supplementary/pgm_example_lyap_checklist.md').write_text('\n'.join(lines))
print('Notebook clean-kernel execution passed; plot output preserved; B1 state saved.')


