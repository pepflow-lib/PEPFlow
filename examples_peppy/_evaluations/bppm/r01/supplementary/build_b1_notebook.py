import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent / "helpers"))
import json
import os

# optional notebook-generation dependency
import nbformat as nbf  # ty: ignore[unresolved-import]
import runtime

# optional notebook-generation dependency
from nbclient import NotebookClient  # ty: ignore[unresolved-import]

root = runtime.ROOT
source = (root / "bppm_setup.py").read_text(encoding="utf-8-sig")
nb = nbf.v4.new_notebook()
md, code = nbf.v4.new_markdown_cell, nbf.v4.new_code_cell
nb.cells = [
    md(r"""# Bregman proximal point minimization

Let $f$ and $h$ be closed, proper, convex functions on a finite-dimensional real Euclidean space, with the differentiability and well-definedness assumed in the input. Let $x_\star$ minimize $f$, $\alpha>0$, $R\ge0$, and $N\ge1$.

$$D_h(u,v)=h(u)-h(v)-\langle\nabla h(v),u-v\rangle,$$
$$D_h(x_\star,x_0)\le R,\qquad x_{k+1}\in\arg\min_x\{\alpha f(x)+D_h(x,x_k)\},\quad 0\le k<N.$$
The update satisfies $\nabla h(x_{k+1})=\nabla h(x_k)-\alpha\nabla f(x_{k+1})$. We study $f(x_N)-f(x_\star)$.

Convex interpolation supplies the finite PEP relaxation; no smoothness or strong convexity is imposed."""),
    md(
        "## Proof statement\nPending Block 5. The supplied conjecture is $R/(\\alpha N)$."
    ),
    code("""import sys
from pathlib import Path
notebook_dir = Path.cwd().resolve()
repo_root = notebook_dir / "supplementary" / "approved"
sys.path[:0] = [str(repo_root), str(notebook_dir), str(notebook_dir / "supplementary" / "helpers")]
import runtime
import json
import pepflow as pf
import matplotlib.pyplot as plt
print("Framework:", pf.__file__)
"""),
    md("## Function and parameter definitions"),
    code(source[source.index("alpha: Any =") : source.index("\ndef make_ctx")]),
    md("## Algorithm and PEP setup"),
    code(source[source.index("def make_ctx") :]),
    md("## Numerical evidence"),
    code("""sweep = json.loads((notebook_dir / "supplementary" / "b1-sweep.json").read_text())
for row in sweep:
    print(f"N={row['N']}: PEP={row['opt_value']:.10f}, candidate={row['candidate']:.10f}, status={row['status']}")
errors = [abs(row["error"]) for row in sweep]
assert max(errors) < 1e-5
print("Maximum discrepancy:", max(errors))
print("Inverse-rate increments:", [1/sweep[j+1]["opt_value"] - 1/sweep[j]["opt_value"] for j in range(6)])
plt.figure(figsize=(7, 4))
plt.plot([row["N"] for row in sweep], [row["opt_value"] for row in sweep], "o", label="PEP, alpha=R=1")
plt.plot([row["N"] for row in sweep], [row["candidate"] for row in sweep], "-", label="Conjecture 1/N")
plt.xlabel("N")
plt.ylabel("Final objective gap")
plt.legend()
plt.grid(alpha=0.3)
plt.show()
"""),
    md(
        r"""All seven CLARABEL solves used default options and returned optimal status. The values support the supplied conjecture $R/(\alpha N)$ at $\alpha=R=1$; this is numerical evidence, not an arbitrary-horizon proof. The original sweep is cached and is not repeated when executing this notebook."""
    ),
    md("## Full-PEP certificate\nPending Block 2."),
    md("## Lyapunov partial sums and rank profile\nPending Block 3."),
    md("## Special vectors and coefficients\nPending Block 4."),
    md("## Exact step, base, and boundary identities\nPending Block 5."),
]
imports_source = nb.cells[2].source
bootstrap, imports = imports_source.split("import runtime", 1)
nb.cells[2].source = bootstrap
nb.cells.insert(
    3,
    code(
        "from typing import Any\nimport runtime"
        + imports
        + "\nassert runtime.ROOT == notebook_dir\n"
    ),
)
nb.metadata.kernelspec = {
    "name": "bppm-owned",
    "display_name": "BPPM isolated Python",
    "language": "python",
}
kernels = runtime.RUNTIME / "jupyter" / "kernels" / "bppm-owned"
kernels.mkdir(parents=True, exist_ok=True)
(kernels / "kernel.json").write_text(
    json.dumps(
        {
            "argv": [
                sys.executable,
                "-I",
                "-B",
                "-m",
                "ipykernel_launcher",
                "-f",
                "{connection_file}",
            ],
            "display_name": "BPPM isolated Python",
            "language": "python",
        }
    )
)
os.environ["JUPYTER_PATH"] = str(runtime.RUNTIME / "jupyter")
path = root / "bppm_example_lyap.ipynb"
nbf.write(nb, path)
NotebookClient(
    nb,
    timeout=120,
    kernel_name="bppm-owned",
    resources={"metadata": {"path": str(root)}},
).execute()
nbf.write(nb, path)
results = json.loads((root / "supplementary" / "b1-sweep.json").read_text())
state = {
    "algo_name": "bppm",
    "problem_type": "convex_bregman",
    "obj_tag": "f",
    "params_json": json.dumps({"alpha": 1, "R": 1}),
    "performance_metric": "f(x_N)-f(x_star)",
    "initial_condition": "D_h(x_star,x_0)<=R",
    "conjectured_rate": "R/(alpha*N)",
    "setup_file": "bppm_setup.py",
    "sweep_results": results,
    "N_verify": 4,
    "notebook": "bppm_example_lyap.ipynb",
    "presentation_policy": "evaluation-ancillary-v1",
}
(root / "state").mkdir(exist_ok=True)
(root / "state" / "bppm_b1.json").write_text(json.dumps(state, indent=2))
print("Notebook fresh-kernel execution passed.")
for j, cell in enumerate(nb.cells):
    if cell.cell_type == "code":
        print(j, cell.id, [o.output_type for o in cell.outputs])
