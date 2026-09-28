"""Create B1 state and the main evolving notebook from the saved sweep."""

import json
from pathlib import Path

# optional notebook-generation dependency
import nbformat  # ty: ignore[unresolved-import]

ROOT = Path(__file__).resolve().parents[1]
rows = json.loads((ROOT / "supplementary/b1_sweep.json").read_text())
for row in rows:
    row["candidate"] = 1 / (2 * row["theta_N"] ** 2)
    row["absolute_error"] = abs(row["opt_value"] - row["candidate"])
    row["scaled_value"] = row["opt_value"] * row["theta_N"] ** 2
assert max(row["absolute_error"] for row in rows) < 1e-5
state = {
    "algo_name": "ogm",
    "problem_type": "smooth_convex",
    "obj_tag": "f",
    "params_json": '{"L": 1, "R": 1}',
    "performance_metric": "f(x_N) - f(x_star)",
    "initial_condition": "||x_0-x_star||^2 <= R^2; z_0=x_0; grad f(x_star)=0",
    "conjectured_rate": "L*R**2/(2*theta_N**2)",
    "setup_file": "ogm_setup.py",
    "notebook_file": "ogm_example_lyap.ipynb",
    "sweep_results": rows,
    "N_verify": 4,
    "rate_status": "numerical_conjecture_only",
    "theta_definition": "theta_-1=0; theta_k=(1+sqrt(1+4*theta_(k-1)^2))/2 for k<N; theta_N=(1+sqrt(1+8*theta_(N-1)^2))/2",
    "numerical_certificate_verified": False,
    "analytic_full_pep_verified": False,
    "lyapunov_proof_verified": False,
    "attempt_id": "ogm_r05",
    "access_control": "instruction_only",
    "presentation_policy": "evaluation-ancillary-v1",
}
(ROOT / "state").mkdir(exist_ok=True)
(ROOT / "state/ogm_b1.json").write_text(json.dumps(state, indent=2), encoding="utf-8")
nb = nbformat.v4.new_notebook()
md = nbformat.v4.new_markdown_cell
code = nbformat.v4.new_code_cell
setup = (ROOT / "ogm_setup.py").read_text()
definitions = setup[setup.index("L = pf.Parameter") : setup.index("def make_ctx_ogm")]
builder = setup[setup.index("def make_ctx_ogm") :]
nb.cells = [
    md(r"""# OGM: numerical discovery and Lyapunov workflow

Let $f$ be convex and $L$-smooth on a finite-dimensional real Euclidean space, with $L>0$, $R\geq0$, $N\geq1$, $\nabla f(x_\star)=0$ and $\|x_0-x_\star\|^2\leq R^2$. Set $z_0=x_0$. The target is $f(x_N)-f(x_\star)$.

With $\theta_{-1}=0$, define
$$\theta_k=\frac{1+\sqrt{1+4\theta_{k-1}^2}}2\quad(0\leq k<N),\qquad
\theta_N=\frac{1+\sqrt{1+8\theta_{N-1}^2}}2.$$
For $k=0,\ldots,N-1$, perform
$$y_{k+1}=x_k-\frac1L\nabla f(x_k),\qquad
z_{k+1}=z_k-\frac{2\theta_k}{L}\nabla f(x_k),$$
$$x_{k+1}=\left(1-\frac1{\theta_{k+1}}\right)y_{k+1}
+\frac1{\theta_{k+1}}z_{k+1}.$$
The terminal coefficient uses the factor $8$, including when $N=1$."""),
    md(
        "## Proof statement\nPending: the candidate bound below is numerical evidence, not yet a theorem. Blocks 2–5 will provide the certificate, Lyapunov construction and exact identities."
    ),
    code(
        "import sys\nfrom pathlib import Path\n\nnotebook_dir = Path.cwd().resolve()\nrepo_root = notebook_dir / 'supplementary' / 'approved'\nfor path in (notebook_dir, notebook_dir / 'supplementary' / 'helpers', repo_root):\n    sys.path.insert(0, str(path))"
    ),
    code(
        "import json\nimport math\nimport matplotlib.pyplot as plt\nimport pepflow as pf\nfrom runtime import configure\n\nconfigure()\nassert Path(pf.__file__).resolve().is_relative_to(repo_root)\nprint('Approved framework:', pf.__file__)"
    ),
    md(
        "## Function and algorithm definitions\nThe finite-horizon solver uses floating-point evaluations of the supplied theta recurrence. The initial condition uses $R^2$, with $R$ denoting the radius."
    ),
    code(definitions),
    code(builder),
    code(
        "ctx, pb, obj = get_pep_setup(4, {'L': 1, 'R': 1})\nprint('Setup constructed for N=4; terminal theta =', theta_sequence(4)[-1])"
    ),
    md(
        "## Numerical evidence\nA single sweep at $L=R=1$, using CLARABEL defaults, produced the following results. All solves returned `optimal`. Scaling the objective by $\\theta_N^2$ gives approximately $1/2$ at every sampled horizon."
    ),
    code(
        "state_b1 = json.loads((notebook_dir / 'state/ogm_b1.json').read_text())\nrows = state_b1['sweep_results']\nfor row in rows:\n    print(f\"N={row['N']}: PEP={row['opt_value']:.10f}, candidate={row['candidate']:.10f}, scaled={row['scaled_value']:.10f}\")\nerror = max(row['absolute_error'] for row in rows)\nprint('Maximum absolute discrepancy:', error)\nassert error < 1e-5\nplt.figure(figsize=(6, 3.5))\nplt.plot([r['N'] for r in rows], [r['opt_value'] for r in rows], 'o', label='PEP optimum')\nplt.plot([r['N'] for r in rows], [r['candidate'] for r in rows], '-', label=r'$1/(2\\theta_N^2)$ candidate')\nplt.xlabel('Horizon N')\nplt.ylabel('Function gap, L=R=1')\nplt.legend()\nplt.grid(alpha=0.25)\nplt.tight_layout()\nplt.show()"
    ),
    md(r"""## B1 conclusion
The observed candidate is
$$f(x_N)-f(x_\star)\leq\frac{LR^2}{2\theta_N^2}.$$
The $LR^2$ factor follows from rescaling the smoothness and distance units. The horizon dependence is conjectured from the numerical sweep. No full certificate or arbitrary-horizon proof has yet been established.

## Full-PEP certificate
Pending Block 2.

## Lyapunov partial sums and rank profile
Pending Block 3.

## Identify the vectors composing the Lyapunov function
Pending Block 4.

## Closed-form Lyapunov function and exact proof
Pending Block 5."""),
]
nb.metadata["kernelspec"] = {
    "name": "ogm-isolated",
    "display_name": "OGM isolated",
    "language": "python",
}
nbformat.write(nb, ROOT / "ogm_example_lyap.ipynb")
print(
    json.dumps(
        {
            "max_absolute_error": max(r["absolute_error"] for r in rows),
            "state": "state/ogm_b1.json",
        }
    )
)
