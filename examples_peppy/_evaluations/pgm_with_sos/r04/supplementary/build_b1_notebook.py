import hashlib
import json
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parent / "helpers"))
import runtime
import nbformat as nbf
from nbclient import NotebookClient

root = runtime.ROOT
results = json.loads((root / "supplementary/_sweep_tmp.json").read_text())
state = dict(algo_name="pgm", problem_type="composite", obj_tag="f", params_json='{"L":1,"R":1}',
             performance_metric="h(x_N)-h(x_star)", initial_condition="||x_0-x_star||^2 <= R^2",
             conjectured_rate="L*R**2/(4*N)", setup_file="pgm_setup.py", sweep_results=results, N_verify=4,
             supplied_assistance="Fixed PGM SOS aid in approved/input.md; unverified in B1",
             numerical_certificate_verified=False, analytic_full_pep_verified=False, lyapunov_proof_verified=False)
(root / "state").mkdir(exist_ok=True)
(root / "state/pgm_b1.json").write_text(json.dumps(state, indent=2))
setup = (root / "pgm_setup.py").read_text()
nb = nbf.v4.new_notebook()
nb.cells = [
    nbf.v4.new_markdown_cell(r'''# Proximal gradient: numerical discovery and Lyapunov analysis
Let $f$ be convex and $L$-smooth, $g$ closed, proper and convex, and $h=f+g$ on a finite-dimensional real Euclidean space. Assume $L>0$, $R\geq0$, $N\geq1$, and $x_\star\in\arg\min h$ with $\|x_0-x_\star\|^2\leq R^2$. Proximal steps are well-defined.
$$x_{k+1}=\operatorname{prox}_{g/L}\left(x_k-\frac{1}{L}\nabla f(x_k)\right),\qquad k=0,\ldots,N-1.$$
The metric is $h(x_N)-h(x_\star)$. The equivalent proximal relation is $s_{k+1}=L(x_k-x_{k+1})-\nabla f(x_k)\in\partial g(x_{k+1})$.
The fixed PGM SOS expression in the supplied input is authorized assistance, awaiting certificate verification.'''),
    nbf.v4.new_markdown_cell("## Proof statement\nPending Blocks 2–5. Numerical evidence alone is not an arbitrary-horizon theorem."),
    nbf.v4.new_code_cell('from pathlib import Path\nimport sys\nnotebook_dir = Path.cwd()\nrepo_root = notebook_dir / "supplementary" / "approved"\nsys.path[:0] = [str(repo_root), str(notebook_dir / "supplementary" / "helpers")]'),
    nbf.v4.new_code_cell('import json\nimport matplotlib.pyplot as plt\nimport pepflow as pf'),
    nbf.v4.new_code_cell(setup[setup.index('L = pf.Parameter'):setup.index('\ndef make_ctx_pgm')]),
    nbf.v4.new_code_cell(setup[setup.index('def make_ctx_pgm'):]),
    nbf.v4.new_markdown_cell("## Numerical evidence\nThe single saved sweep used CLARABEL defaults at $L=R=1$. Horizons 6 and 7 returned `optimal_inaccurate`; these are recorded rather than treated as exact proof."),
    nbf.v4.new_code_cell('sweep = json.loads((notebook_dir / "state/pgm_b1.json").read_text())["sweep_results"]\nfor row in sweep:\n    print(f"N={row[\'N\']}: {row[\'opt_value\']:.10f} ({row[\'status\']})")\nns = [r["N"] for r in sweep]\nvalues = [r["opt_value"] for r in sweep]\ncandidate = [1 / (4 * n) for n in ns]\nprint("Maximum absolute candidate residual:", max(abs(a-b) for a,b in zip(values,candidate)))\nplt.plot(ns, values, "o", label="PEP sweep")\nplt.plot(ns, candidate, "-", label="candidate 1/(4N)")\nplt.xlabel("N")\nplt.ylabel("objective gap, L=R=1")\nplt.legend()\nplt.grid(True)\nplt.show()'),
    nbf.v4.new_markdown_cell(r'The observed reciprocals are $4,8,12,16,20,24,28$, suggesting $h(x_N)-h(x_\star)\leq LR^2/(4N)$. Scaling the objective by $L$ and positions by $R$ gives the displayed dimensional factor; $R=0$ is the stationary case. This is a conjecture pending proof.'),
    nbf.v4.new_markdown_cell("## Dense and relaxed proof solves\nPending Block 2."),
    nbf.v4.new_markdown_cell("## Lambda and S verification\nPending Block 2."),
    nbf.v4.new_markdown_cell("## Partial-sum Lyapunov construction and rank profile\nPending Block 3."),
    nbf.v4.new_markdown_cell("## Identify the vectors composing the Lyapunov function\nPending Block 4."),
    nbf.v4.new_markdown_cell("## Coefficient extraction and closed-form Lyapunov function\nPending Blocks 4–5."),
    nbf.v4.new_markdown_cell("## Symbolic step, base, and boundary identities\nPending Block 5.")]
nb.metadata.kernelspec = {"display_name":"Attempt Python", "language":"python", "name":"attempt-python"}
kernels = runtime.RUNTIME / "jupyter/kernels/attempt-python"
kernels.mkdir(parents=True, exist_ok=True)
(kernels / "kernel.json").write_text(json.dumps({"argv":[sys.executable,"-I","-B","-m","ipykernel_launcher","-f","{connection_file}"],"display_name":"Attempt Python","language":"python"}))
import os
os.environ["JUPYTER_PATH"] = str(runtime.RUNTIME / "jupyter")
path = root / "pgm_example_lyap.ipynb"
nbf.write(nb, path)
NotebookClient(nb, timeout=120, kernel_name="attempt-python", resources={"metadata":{"path":str(root)}}).execute()
nbf.write(nb, path)
for i,c in enumerate(nb.cells):
    if c.cell_type == "markdown":
        assert '\\(' not in c.source and '\\[' not in c.source
        assert not any(ord(v)<32 and v not in '\n\t' for v in c.source)
    for output in c.get("outputs", []):
        if output.output_type == "stream":
            print(output.text)
assert any("image/png" in o.get("data", {}) for o in nb.cells[7].outputs)
items = ["title, problem description, and the algorithm update equations in LaTeX", "proof statement placeholder, to be filled with the final theorem and proof outline in Block 5", "imports", "function/operator definitions", "make_ctx_pgm and get_pep_setup", "numerical evidence, including a plot comparing the PEP values against the discovered or conjectured rate", "dense and relaxed proof solves", "lambda and S verification (closed-form when available, otherwise numerical with explicit analytic status)", "partial-sum Lyapunov construction and rank profile", "special-vector identification", "coefficient extraction and closed-form V_k", "symbolic step, base, and boundary identities"]
indices = [0,1,3,4,5,7,9,10,11,12,13,14]
lines = [f"Notebook: {path.name}\nLast reviewed block: B1\nSHA-256: {hashlib.sha256(path.read_bytes()).hexdigest()}\nPresentation policy: evaluation-ancillary-v1; rendering omitted; executed plot MIME output and Markdown delimiters checked.\n", "| Item | Status | Cell index | Evidence |", "|---|---|---|---|"]
for i,(item,idx) in enumerate(zip(items,indices),1):
    done = i in [1,3,4,5,6]
    lines.append(f"| {i}. {item} | {'verified' if done else 'pending'} | {idx} | {'Saved source inspected; clean kernel execution passed' if done else 'Later block obligation'} |")
(root / "supplementary/pgm_example_lyap_checklist.md").write_text('\n'.join(lines))
print("B1 notebook execution and source inspection passed")



