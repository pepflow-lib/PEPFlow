import hashlib
import json
import os
import sys
from pathlib import Path

import nbformat
from nbclient import NotebookClient

root = Path(__file__).resolve().parents[1]
runtime = root / "supplementary" / ".runtime"
for key in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS", "NUMEXPR_NUM_THREADS"):
    os.environ[key] = "1"
for key in ("TEMP", "TMP", "TMPDIR", "MPLCONFIGDIR", "IPYTHONDIR", "JUPYTER_RUNTIME_DIR", "JUPYTER_CONFIG_DIR", "XDG_CACHE_HOME"):
    location = runtime / key.lower()
    location.mkdir(parents=True, exist_ok=True)
    os.environ[key] = str(location)
kernels = runtime / "jupyter" / "kernels" / "pgm-owned"
kernels.mkdir(parents=True, exist_ok=True)
(kernels / "kernel.json").write_text(json.dumps({"argv": [sys.executable, "-I", "-B", "-m", "ipykernel_launcher", "-f", "{connection_file}"], "display_name": "PGM owned", "language": "python"}))
os.environ["JUPYTER_PATH"] = str(runtime / "jupyter")
results = json.loads((root / "supplementary" / "_sweep_tmp.json").read_text())
state = {
    "algo_name": "pgm", "problem_type": "composite", "obj_tag": "f",
    "additional_obj_tags": ["g"], "params_json": '{"L": 1, "R": 1}',
    "performance_metric": "h(x_N)-h(x_star)",
    "initial_condition": "||x_0-x_star||^2 <= R^2",
    "conjectured_rate": "L*R**2/(4*N)", "setup_file": "pgm_setup.py",
    "sweep_results": results, "N_verify": 4,
    "rate_status": "numerical conjecture; arbitrary-horizon proof pending",
    "presentation_policy": "evaluation-ancillary-v1",
}
(root / "state").mkdir(exist_ok=True)
(root / "state" / "pgm_b1.json").write_text(json.dumps(state, indent=2))
setup = (root / "pgm_setup.py").read_text(encoding="utf-8-sig")
setup_def = setup[setup.index('L = pf.Parameter'):setup.index('def make_ctx_pgm')]
setup_body = setup[setup.index('def make_ctx_pgm'):]
md = nbformat.v4.new_markdown_cell
code = nbformat.v4.new_code_cell
nb = nbformat.v4.new_notebook(cells=[
    md(r'''# Proximal gradient method: Lyapunov discovery

Let $f$ be convex and $L$-smooth, $L>0$, and let $g$ be closed, proper and convex on a finite-dimensional real Euclidean space. Put $h=f+g$. Assume $x_\star$ minimizes $h$ and $\|x_0-x_\star\|^2\le R^2$, where $R\ge0$. The proximal updates are well-defined. For integer $N\ge1$,
$$x_{k+1}=\operatorname{prox}_{g/L}\left(x_k-\frac{1}{L}\nabla f(x_k)\right),\qquad k=0,\ldots,N-1.$$
We investigate $h(x_N)-h(x_\star)$. Only the composite objective is stationary at $x_\star$; neither summand is required to be stationary there.'''),
    md('## Proof statement (pending Block 5)\n\nThe sweep suggests $h(x_N)-h(x_\\star)\\le LR^2/(4N)$. This is a conjecture here; certificate and exact proof obligations remain open.'),
    code('from pathlib import Path\nimport json\nimport sys\n\nnotebook_dir = Path.cwd().resolve()\nrepo_root = notebook_dir / "supplementary" / "approved"\nsys.path[:0] = [str(repo_root), str(notebook_dir), str(notebook_dir / "supplementary" / "helpers")]\n'),
    code('import pepflow as pf\nimport matplotlib.pyplot as plt'),
    code(setup_def),
    code(setup_body + '\nctx, pb, obj = get_pep_setup(4, {"L": 1, "R": 1})\nassert len(ctx.func_to_triplets) == 2\nprint("PGM setup ready; both interpolation groups retained.")'),
    md('## Numerical evidence\n\nOne sweep, $N=1,\\ldots,7$, used CLARABEL defaults with $L=R=1$. Values and solver statuses are preserved below. The last two solves report `optimal_inaccurate`; numerical agreement is evidence for a conjecture only.'),
    code('state = json.loads((notebook_dir / "state" / "pgm_b1.json").read_text())\nrows = state["sweep_results"]\nfor row in rows:\n    print(f"N={row[\'N\']}: {row[\'opt_value\']:.10f} ({row[\'status\']})")\nns = [row["N"] for row in rows]\nvalues = [row["opt_value"] for row in rows]\ncandidate = [1 / (4*n) for n in ns]\nresidual = max(abs(v-c) for v,c in zip(values, candidate))\nprint("Maximum candidate discrepancy:", residual)\nprint("Reciprocal values:", [round(1/v, 6) for v in values])\nassert residual < 1e-5\nfig, ax = plt.subplots()\nax.plot(ns, values, "o", label="PEP values")\nax.plot(ns, candidate, "--", label="Conjecture 1/(4N)")\nax.set(xlabel="N", ylabel="Objective gap", title="PGM numerical evidence")\nax.legend()\nplt.show()'),
    md('## Dense and relaxed proof solves\n\nPending Block 2.'),
    md('## Lambda and S verification\n\nPending Block 2.'),
    md('## Partial-sum Lyapunov construction and rank profile\n\nPending Block 3.'),
    md('## Identify the vectors composing the Lyapunov function\n\nPending Block 4.'),
    md('## Coefficient extraction and closed-form Lyapunov function\n\nPending Blocks 4–5.'),
    md('## Symbolic step, base, and boundary identities\n\nPending Block 5.'),
])
nb.metadata.kernelspec = {"name": "pgm-owned", "display_name": "PGM owned", "language": "python"}
path = root / "pgm_example_lyap.ipynb"
nbformat.write(nb, path)
NotebookClient(nb, timeout=120, kernel_name="pgm-owned", resources={"metadata": {"path": str(root)}}).execute()
nbformat.write(nb, path)
for cell in nb.cells:
    if cell.cell_type == "markdown":
        assert all(c not in cell.source for c in ('\x0c', '\x0b', '\r'))
        assert r'\(' not in cell.source and r'\[' not in cell.source
assert any('image/png' in out.get('data', {}) for cell in nb.cells for out in cell.get('outputs', []))
items = [
    'title, problem description, and the algorithm update equations in LaTeX',
    'proof statement placeholder, to be filled with the final theorem and proof outline in Block 5',
    'imports', 'function/operator definitions', 'make_ctx_pgm and get_pep_setup',
    'numerical evidence, including a plot comparing the PEP values against the discovered or conjectured rate',
    'dense and relaxed proof solves',
    'lambda and S verification (closed-form when available, otherwise numerical with explicit analytic status)',
    'partial-sum Lyapunov construction and rank profile', 'special-vector identification',
    'coefficient extraction and closed-form V_k', 'symbolic step, base, and boundary identities',
]
cells = ['0','1','2–3','4','5','6–7','8','9','10','11','12','13']
verified = {0,2,3,4,5}
checklist = f'# Notebook evidence checklist\n\nNotebook: {path.name}\nLast reviewed block: B1\nSHA-256: {hashlib.sha256(path.read_bytes()).hexdigest()}\nPresentation: evaluation-ancillary-v1; no visual rendering performed.\n\n| Item | Requirement | Status | Cells | Evidence |\n|---|---|---|---|---|\n'
for i, item in enumerate(items):
    status = 'verified' if i in verified else 'pending'
    evidence = 'Source inspected; fresh-kernel execution passed.' if i in verified else 'Later block obligation.'
    if i == 5:
        evidence += ' Printed sweep, discrepancy and embedded PNG output present; image not inspected under presentation override.'
    checklist += f'| {i+1} | {item} | {status} | {cells[i]} | {evidence} |\n'
(root / 'supplementary' / 'pgm_example_lyap_checklist.md').write_text(checklist, encoding='utf-8')
print(json.dumps({"notebook": str(path), "fresh_kernel": "passed", "markdown_checks": "passed", "plot_output_present": True, "candidate_max_error": max(abs(row['opt_value']-1/(4*row['N'])) for row in results)}))


