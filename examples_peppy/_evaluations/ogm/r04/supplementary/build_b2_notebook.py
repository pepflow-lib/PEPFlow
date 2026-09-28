import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent / "helpers"))
# local helper resolved by the notebook runtime path
from runtime import configure  # ty: ignore[unresolved-import]

attempt, approved = configure()
import nbformat as nbf  # ty: ignore[unresolved-import]  # optional notebook-generation dependency  # noqa: E402 - imports follow runtime or notebook setup
from nbclient import (  # ty: ignore[unresolved-import]  # optional notebook-generation dependency  # noqa: E402 - imports follow runtime or notebook setup
    NotebookClient,
)

path = attempt / "ogm_example_lyap.ipynb"
nb = nbf.read(path, as_version=4)
nb.cells = nb.cells[:9]
md = nbf.v4.new_markdown_cell
code = nbf.v4.new_code_cell
nb.cells.append(
    md("""## Full-PEP certificate
The dense and relaxed solves were acquired directly using the approved `CVXPrimalSolver`, with CLARABEL defaults. Each saved certificate contains all multipliers and the Gram dual from one solve. We replay their mathematical checks below without rerunning an unchanged solve. Thresholding at $10^{-6}$ retained a small backward terminal multiplier; removing that extra edge and retaining the optimizer row and consecutive forward edges preserved the optimum.
""")
)
sections = (
    (attempt / "supplementary/b2_notebook_cells.py").read_text().split("# %%")[1:]
)
headings = [
    "### Dense solve and sparse relaxation",
    "### Complete selected multiplier inventory",
    "### Candidate formulas and direct S decomposition",
    "### Full numerical certificate identity",
    "### B2 state and initial search record",
]
for heading, source in zip(headings, sections):
    nb.cells.append(md(heading))
    if "Candidate formulas" in heading:
        nb.cells.append(
            md(r"""Write $g_i=\nabla f(x_i)$. The numerical candidates are
$$\lambda_{\star,i}=\frac{2\theta_i}{\theta_N^2}\ (i<N),\quad
\lambda_{\star,N}=\frac1{\theta_N},\quad
\lambda_{i,i+1}=\frac{2\theta_i^2}{\theta_N^2}\ (i<N),$$
with other interpolation multipliers zero, and
$$S=\frac{L}{2\theta_N^2}\left\|z_N-x_\star-\frac{\theta_N}{L}g_N\right\|^2.$$
These are candidate formulas, not yet an arbitrary-horizon analytic identity. The selected numerical factor uses the actual initial-condition dual as its coefficient and is checked against the same solve's full Gram matrix. Here `z_0` and `x_0` denote the same vector; the framework prints its most recent tag.
""")
        )
    if "Full numerical" in heading:
        nb.cells.append(
            md(r"""Normalize each inequality residual to $R_c\leq0$. Check all scalar coordinates of
$$f(x_N)-f(x_\star)-b-\sum_c d_c R_c+S_{\rm numeric}=0.$$
Every active scalar constraint is included, including the initial radius and its constant. There are no matrix-extra constraints in this setup. Nonnegative multipliers and the positive Gram remainder give an upper bound at the sampled horizon. The checks below are numerical; the all-horizon proof remains pending.
""")
        )
    nb.cells.append(code(source.strip()))
nb.cells.extend(
    [
        md("## Lyapunov partial sums (Block 3 pending)"),
        md("## Identify the vectors composing the Lyapunov function\nBlock 4 pending."),
        md("## Closed-form Lyapunov function and exact identities\nBlock 5 pending."),
    ]
)
nbf.write(nb, path)
os.environ["JUPYTER_PATH"] = str(attempt / "supplementary/.runtime/jupyter")
NotebookClient(
    nb,
    timeout=120,
    kernel_name="ogm-own",
    resources={"metadata": {"path": str(attempt)}},
).execute()
nbf.write(nb, path)
for i, c in enumerate(nb.cells):
    if c.cell_type == "markdown":
        assert "\\(" not in c.source and "\\[" not in c.source
        assert not any(ord(ch) < 32 and ch not in "\n\t" for ch in c.source)
    else:
        for o in c.outputs:
            if o.output_type == "stream":
                print("CELL", i, o.text)
print("Saved", len(nb.cells), "cells")
