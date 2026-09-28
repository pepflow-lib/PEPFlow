"""Initialize B1 notebook and execute in an isolated fresh kernel."""
import hashlib
import json
import os
from pathlib import Path
import sys

import nbformat
from nbclient import NotebookClient

ROOT = Path(__file__).resolve().parents[1]
runtime = ROOT / "supplementary" / ".runtime"
for key in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS", "NUMEXPR_NUM_THREADS"):
    os.environ[key] = "1"
for key in ("TEMP", "TMP", "TMPDIR", "MPLCONFIGDIR", "IPYTHONDIR", "JUPYTER_RUNTIME_DIR", "JUPYTER_CONFIG_DIR", "XDG_CACHE_HOME"):
    private = runtime / key.lower()
    private.mkdir(parents=True, exist_ok=True)
    os.environ[key] = str(private)
os.environ["JUPYTER_PATH"] = str(runtime / "jupyter")
kernel = runtime / "jupyter" / "kernels" / "dual-feg-owned"
kernel.mkdir(parents=True, exist_ok=True)
(kernel / "kernel.json").write_text(json.dumps({
    "argv": [sys.executable, "-I", "-B", "-m", "ipykernel_launcher", "-f", "{connection_file}"],
    "display_name": "Dual FEG private kernel", "language": "python"}))

results = json.loads((ROOT / "supplementary" / "_sweep_tmp.json").read_text())
assert len(results) == 7 and all(r["solver_status"] == "optimal" for r in results)
state = {
    "algo_name": "dual_feg", "problem_type": "monotone_operator", "obj_tag": "A",
    "params_json": '{"L": 1, "R": 1}',
    "performance_metric": "||A(x_N)||^2", "initial_condition": "||x_0-x_star||^2 <= R^2; A(x_star)=0; z_0=0",
    "conjectured_rate": "4*L**2*R**2/N**2", "setup_file": "dual_feg_setup.py",
    "sweep_results": results, "N_verify": 6,
    "rate_status": "Numerical conjecture; N=2..7 matches 4/N^2, N=1 equals 2 rather than 4.",
    "metric_selection": "Terminal squared residual is a natural root-finding accuracy measure, selected here because the supplied metric was unknown.",
    "presentation_policy": "evaluation-ancillary-v1"}
(ROOT / "state").mkdir(exist_ok=True)
(ROOT / "state" / "dual_feg_b1.json").write_text(json.dumps(state, indent=2))

md = nbformat.v4.new_markdown_cell
code = nbformat.v4.new_code_cell
cells = [md(r"""# Dual FEG: residual decay for monotone Lipschitz operators

Let $A$ be monotone and $L$-Lipschitz on a real finite-dimensional Euclidean space, with $L>0$, $R\geq0$, $A(x_\star)=0$ and $\|x_0-x_\star\|^2\leq R^2$. For a fixed integer $N\geq1$, set $z_0=0$ and $\alpha=1/L$. For $k=0,\ldots,N-1$, run
$$x_{k+1/2}=x_k-\alpha z_k-\alpha A(x_k),$$
$$x_{k+1}=x_{k+1/2}-\frac{N-k-1}{N-k}\alpha\bigl(A(x_{k+1/2})-A(x_k)\bigr),$$
$$z_{k+1}=\frac{N-k-1}{N-k}z_k-\frac{A(x_{k+1/2})}{N-k}.$$
We select $\|A(x_N)\|^2$ as the performance metric. The conjectured bound is $4L^2R^2/N^2$. Pairwise monotonicity and Lipschitz inequalities define the PEP relaxation; numerical values alone do not prove an arbitrary-horizon theorem.
"""), md("## Proof statement (pending Block 5)\nThe certificate, Lyapunov construction and exact proof remain to be derived."),
code("import sys\nfrom pathlib import Path\nnotebook_dir = Path.cwd().resolve()\nrepo_root = notebook_dir / 'supplementary' / 'approved'\nsys.path[:0] = [str(repo_root), str(notebook_dir / 'supplementary' / 'helpers'), str(notebook_dir)]"),
code("import json\nimport matplotlib.pyplot as plt\nimport numpy as np\nimport pepflow as pf\nimport sympy as sp\nassert Path(pf.__file__).resolve().is_relative_to(repo_root)\nprint('Framework origin:', pf.__file__)"),
md("## Operator and parameter definitions"),
code('L = pf.Parameter("L")\nR = pf.Parameter("R")\nA = pf.LipschitzMonotoneOperator(is_basis=True, tags=["A"], L=L)'),
md("## Algorithm and performance estimation setup"),
code((ROOT / "dual_feg_setup.py").read_text().split('def make_ctx_dual_feg', 1)[1].join(['def make_ctx_dual_feg', ''])),
code("ctx_check, pb_check, operator_check = get_pep_setup(2, {'L': 1, 'R': 1})\nprint('Setup constructed; terminal metric:', pb_check.performance_metric)"),
md(r"""## Numerical evidence
The saved sweep uses CLARABEL with its default options, $L=R=1$, and one solve for each $N=1,\ldots,7$. The inverse-square candidate agrees with $N=2,\ldots,7$; at $N=1$ the relaxation gives $2$ rather than $4$. Scaling $A$ by $L$ and the coordinates by $R$ motivates the factor $L^2R^2$ (the $R=0$ case starts at a zero). The proof is pending.
"""),
code("state = json.loads((notebook_dir / 'state' / 'dual_feg_b1.json').read_text())\nrows = state['sweep_results']\nns = np.array([r['N'] for r in rows])\nvalues = np.array([r['opt_value'] for r in rows])\ncandidate = 4.0 / ns**2\nfor r, guess in zip(rows, candidate):\n    print(f\"N={r['N']}: PEP={r['opt_value']:.10f}, candidate={guess:.10f}, status={r['solver_status']}\")\nprint('Maximum absolute discrepancy for N>=2:', np.max(np.abs(values[1:] - candidate[1:])))\nassert np.max(np.abs(values[1:] - candidate[1:])) < 1e-5\nfig, ax = plt.subplots(figsize=(6, 4))\nax.loglog(ns, values, 'o-', label='PEP upper bound')\nax.loglog(ns, candidate, '--', label='Candidate 4/NÂ²')\nax.set(xlabel='N', ylabel='Squared terminal residual', title='Dual FEG: numerical rate evidence')\nax.legend()\nax.grid(True, which='both', alpha=0.25)\nplt.show()"),
md("## Dense and relaxed proof solves\nPending Block 2."),
md("## Lambda and S verification\nPending Block 2; no analytic certificate claimed."),
md("## Partial-sum Lyapunov construction and rank profile\nPending Block 3."),
md("## Identify the vectors composing the Lyapunov function\nPending Block 4."),
md("## Coefficient extraction and closed-form Lyapunov function\nPending Blocks 4â€“5."),
md("## Symbolic step, base, and boundary identities\nPending Block 5.")]
for i, cell in enumerate(cells):
    cell.id = f"b1-{i:02d}"
    if cell.cell_type == "markdown":
        assert not any(ch in cell.source for ch in ('\x0c', '\r', '\x08'))
        assert '\\(' not in cell.source and '\\[' not in cell.source
nb = nbformat.v4.new_notebook(cells=cells)
nb.metadata.kernelspec = {"name": "dual-feg-owned", "display_name": "Dual FEG private kernel", "language": "python"}
path = ROOT / "dual_feg_example_lyap.ipynb"
nbformat.write(nb, path)
NotebookClient(nb, timeout=120, kernel_name='dual-feg-owned', resources={"metadata": {"path": str(ROOT)}}).execute()
nbformat.write(nb, path)
for cell in nb.cells:
    for output in cell.get("outputs", []):
        if output.output_type == "stream":
            print(output.text)
assert any('image/png' in out.get('data', {}) for cell in nb.cells for out in cell.get('outputs', []))
items = [
    'title, problem description, and the algorithm update equations in LaTeX',
    'proof statement placeholder, to be filled with the final theorem and proof outline in Block 5',
    'imports', 'function/operator definitions', 'make_ctx_dual_feg and get_pep_setup',
    'numerical evidence, including a plot comparing the PEP values against the discovered or conjectured rate',
    'dense and relaxed proof solves',
    'lambda and S verification (closed-form when available, otherwise numerical with explicit analytic status)',
    'partial-sum Lyapunov construction and rank profile', 'special-vector identification',
    'coefficient extraction and closed-form V_k', 'symbolic step, base, and boundary identities']
locations = ['b1-00', 'b1-01', 'b1-02,b1-03', 'b1-05', 'b1-07,b1-08', 'b1-09,b1-10', 'b1-11', 'b1-12', 'b1-13', 'b1-14', 'b1-15', 'b1-16']
lines = ['Notebook: dual_feg_example_lyap.ipynb', 'Last reviewed block: B1',
         'SHA-256: ' + hashlib.sha256(path.read_bytes()).hexdigest(),
         'Presentation policy: evaluation-ancillary-v1. No rendering/image inspection performed. Markdown delimiter/control-character checks passed; embedded plot output checked structurally.',
         '', '| Item | Status | Cells | Evidence |', '| --- | --- | --- | --- |']
for i, (item, location) in enumerate(zip(items, locations), 1):
    verified = i in {1, 3, 4, 5, 6}
    evidence = 'Saved content inspected; fresh-kernel execution passed.' if verified else 'Pending owning block.'
    if i == 6:
        evidence += ' Seven optimal sweep values, residual comparison, embedded matplotlib PNG.'
    lines.append(f"| {i}. {item} | {'verified' if verified else 'pending'} | {location} | {evidence} |")
(ROOT / 'supplementary' / 'dual_feg_example_lyap_checklist.md').write_text('\n'.join(lines), encoding='utf-8')
print('Notebook execution and B1 evidence checks passed.')

