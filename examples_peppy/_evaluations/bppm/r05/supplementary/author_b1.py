"""Author and execute B1 notebook; no additional numerical sweep."""
import hashlib
import json
import os
from pathlib import Path
import sys

import nbformat as nbf
from nbclient import NotebookClient

root = Path(__file__).resolve().parents[1]
runtime = root / "supplementary" / ".runtime"
for key in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS", "NUMEXPR_NUM_THREADS"):
    os.environ[key] = "1"
for key in ("TEMP", "TMP", "TMPDIR", "IPYTHONDIR", "MPLCONFIGDIR", "JUPYTER_RUNTIME_DIR", "JUPYTER_CONFIG_DIR", "XDG_CACHE_HOME"):
    path = runtime / key.lower()
    path.mkdir(parents=True, exist_ok=True)
    os.environ[key] = str(path)
kernel_dir = runtime / "jupyter" / "kernels" / "bppm-owned"
kernel_dir.mkdir(parents=True, exist_ok=True)
(kernel_dir / "kernel.json").write_text(json.dumps({"argv": [sys.executable, "-I", "-B", "-m", "ipykernel_launcher", "-f", "{connection_file}"], "display_name": "BPPM owned kernel", "language": "python"}))
os.environ["JUPYTER_PATH"] = str(runtime / "jupyter")
md = nbf.v4.new_markdown_cell
code = nbf.v4.new_code_cell
setup_source = (root / "bppm_setup.py").read_text()
definition_start = setup_source.index('f = pf.ConvexFunction')
builder_start = setup_source.index('def make_ctx_bppm')
nb = nbf.v4.new_notebook(cells=[
    md(r"""# Bregman proximal point minimization

Let $f$ and $h$ be closed, proper, convex and differentiable on the relevant domain in a real finite-dimensional Euclidean space. Let $x_\star$ minimize $f$, $\alpha>0$, $R\geq0$, and integer $N\geq1$. Assume all updates and evaluations are well-defined. Define
$$D_h(u,v)=h(u)-h(v)-\langle\nabla h(v),u-v\rangle.$$
The initial condition is $D_h(x_\star,x_0)\leq R$ (the radius is not squared). The update and its optimality equation are
$$x_{k+1}\in\operatorname*{argmin}_x\{\alpha f(x)+D_h(x,x_k)\},\qquad
\nabla h(x_{k+1})=\nabla h(x_k)-\alpha\nabla f(x_{k+1}),\quad 0\leq k<N.$$
The performance metric is $f(x_N)-f(x_\star)$. The supplied conjecture is $R/(\alpha N)$.

The PEP uses convex interpolation for both functions, providing an outer relaxation of the differentiable problem class. No extra curvature assumption is introduced.
"""),
    md("## Proof statement\n\nPending Blocks 2â€“5: certificate, Lyapunov construction, and exact proof. Numerical agreement in Block 1 is not an arbitrary-horizon proof."),
    code("from pathlib import Path\nimport sys\nimport json\n\nnotebook_dir = Path.cwd().resolve()\nrepo_root = notebook_dir / 'supplementary' / 'approved'\nREPO_ROOT = repo_root\nsys.path[:0] = [str(repo_root), str(notebook_dir / 'supplementary' / 'helpers')]"),
    code("from runtime import OWNED_HELPER\nimport pepflow as pf\nimport matplotlib.pyplot as plt\nimport numpy as np\n\nassert OWNED_HELPER\nassert Path(pf.__file__).resolve().is_relative_to(repo_root)\nprint('Framework:', pf.__file__)"),
    md("## Function and parameter definitions\n\nBoth functions use the approved convex interpolation API. The Bregman expression below uses its stated orientation."),
    code(setup_source[definition_start:builder_start].strip()),
    md("## Algorithm and PEP setup"),
    code(setup_source[builder_start:].strip()),
    code("ctx, pb, objective = get_pep_setup(4, {'alpha': 1, 'R': 1})\nprint('Initial certificate horizon:', 4)\nprint('Tagged terminal iterate:', ctx['x_4'])"),
    md("## Numerical evidence\n\nOne sweep, $N=1,\\ldots,7$, with $\\alpha=R=1$, using CLARABEL defaults. The saved results are reused here without repeating the sweep."),
    code("state = json.loads((notebook_dir / 'state' / 'bppm_b1.json').read_text())\nrows = state['sweep_results']\nfor row in rows:\n    print(f\"N={row['N']}: PEP={row['opt_value']:.10f}, conjecture={row['conjectured']:.10f}, status={row['attempts'][-1]['status']}\")\nvalues = np.array([row['opt_value'] for row in rows])\nhorizons = np.array([row['N'] for row in rows])\nprint('Inverse values:', 1 / values)\nprint('Inverse differences:', np.diff(1 / values))\nprint('Maximum absolute discrepancy:', max(row['absolute_error'] for row in rows))\nassert np.max(np.abs(values - 1 / horizons)) < 1e-5\nplt.figure(figsize=(6, 4))\nplt.plot(horizons, values, 'o', label='PEP (CLARABEL)')\nplt.plot(horizons, 1 / horizons, '--', label='Conjecture R/(alpha N)')\nplt.xlabel('Horizon N')\nplt.ylabel('f(x_N) - f(x_star)')\nplt.legend()\nplt.grid(alpha=0.3)\nplt.tight_layout()\nplt.show()"),
    md(r"The computed values match the supplied conjecture $R/(\alpha N)$ for the tested normalization. The inverse values grow by approximately one at every step. Parameter scaling and the all-horizon guarantee remain proof obligations."),
    md("## Full-PEP certificate\n\nPending Block 2."),
    md("## Lyapunov partial sums\n\nPending Block 3."),
    md("## Identify the vectors composing the Lyapunov function\n\nPending Block 4."),
    md("## Closed-form Lyapunov function and symbolic identities\n\nPending Block 5.")
])
nb.metadata.kernelspec = {"name": "bppm-owned", "display_name": "BPPM owned kernel", "language": "python"}
dest = root / "bppm_example_lyap.ipynb"
nbf.write(nb, dest)
NotebookClient(nb, timeout=120, kernel_name="bppm-owned", resources={"metadata": {"path": str(root)}}).execute()
nbf.write(nb, dest)
for idx, cell in enumerate(nb.cells):
    if cell.cell_type == "markdown":
        assert not any(x in cell.source for x in ("\\(", "\\)", "\\[", "\\]", "\x0c", "\r"))
    elif cell.cell_type == "code":
        assert cell.execution_count is not None
        assert not any(o.output_type == "error" for o in cell.outputs)
plots = [o for c in nb.cells if c.cell_type == "code" for o in c.outputs if o.output_type in ("display_data", "execute_result") and "image/png" in o.get("data", {})]
assert plots
items = [
    ('title, problem description, and the algorithm update equations in LaTeX', 'verified', '0', 'Assumptions, update, initial radius, and metric inspected in source.'),
    ('proof statement placeholder, to be filled with the final theorem and proof outline in Block 5', 'pending', '1', 'Placeholder present; exact proof belongs to B5.'),
    ('imports', 'verified', '2,3', 'Approved framework origin printed by fresh kernel.'),
    ('function/operator definitions', 'verified', '4,5', 'Both convex functions and Bregman definition visible.'),
    ('make_ctx_{ALGO_NAME} and get_pep_setup', 'verified', '6,7,8', 'Executable setup visible; context and terminal tag validated.'),
    ('numerical evidence, including a plot comparing the PEP values against the discovered or conjectured rate', 'verified', '9,10,11', 'Seven printed values; discrepancy assertion passes; PNG plot output present. Images not inspected under evaluation policy.'),
    ('dense and relaxed proof solves', 'pending', '12', 'B2'),
    ('lambda and S verification (closed-form when available, otherwise numerical with explicit analytic status)', 'pending', '12', 'B2'),
    ('partial-sum Lyapunov construction and rank profile', 'pending', '13', 'B3'),
    ('special-vector identification', 'pending', '14', 'B4'),
    ('coefficient extraction and closed-form V_k', 'pending', '15', 'B4/B5'),
    ('symbolic step, base, and boundary identities', 'pending', '15', 'B5')]
header = f"# Notebook evidence checklist\n\nNotebook: {dest.name}\nLast reviewed block: B1\nSHA-256: {hashlib.sha256(dest.read_bytes()).hexdigest()}\n\nPresentation policy: evaluation-ancillary-v1. Source math delimiters checked; no rendering or image inspection performed or claimed.\n\n| Item | Requirement | Status | Cell indices | Evidence |\n|---|---|---|---|---|\n"
(root / 'supplementary' / 'bppm_example_lyap_checklist.md').write_text(header + '\n'.join(f'| {i} | {a} | {b} | {c} | {d} |' for i, (a,b,c,d) in enumerate(items, 1)), encoding='utf-8')
(root / 'supplementary' / 'b1-execution.json').write_text(json.dumps({'clean_kernel': True, 'kernel_argv': [sys.executable, '-I', '-B', '-m', 'ipykernel_launcher'], 'code_cells': sum(c.cell_type == 'code' for c in nb.cells), 'plot_outputs': len(plots), 'markdown_source_check': 'passed', 'rendered_review': 'omitted_by_evaluation_policy'}, indent=2))
print('Notebook executed and B1 content inspected:', dest)

