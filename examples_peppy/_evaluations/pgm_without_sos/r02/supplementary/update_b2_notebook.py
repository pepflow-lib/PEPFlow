import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent / "helpers"))
import os

# optional notebook-generation dependency
import nbformat as nbf  # ty: ignore[unresolved-import]

# local helper resolved by the notebook runtime path
import runtime  # ty: ignore[unresolved-import]

# optional notebook-generation dependency
from nbclient import NotebookClient  # ty: ignore[unresolved-import]

root = runtime.ROOT
path = root / "pgm_example_lyap.ipynb"
nb = nbf.read(path, as_version=4)
nb.cells = nb.cells[:11]
nb.cells.append(
    nbf.v4.new_markdown_cell(r"""## Dense and relaxed proof solves
At $N=4$, the dense solve and a fresh sparse solve use the same setup and CLARABEL defaults. Their saved data include all function groups and every initial multiplier. The sparse model keeps $(*,j)$ and $(i,i+1)$ interpolation pairs for each function. The following cells reconstruct the contexts without another solve and verify the complete selected sample. The solve route is `CVXPrimalSolver.build_problem`, executed by `supplementary/helpers/certificate.py`; data and source hashes are retained.
""")
)
source = (root / "supplementary/b2_notebook_cells.py").read_text(encoding="utf-8-sig")
for chunk in source.split("# %% ")[1:]:
    heading, code = chunk.split("\n", 1)
    nb.cells.extend(
        [nbf.v4.new_markdown_cell("### " + heading), nbf.v4.new_code_cell(code)]
    )
nb.cells.append(
    nbf.v4.new_markdown_cell(r"""### Initial formula search and status
The fractions suggest $a_i=(i+1)/(2N-i)$ for $f$ and $b_i=i/(2N-i)$ for $g$ on consecutive pairs. Minimizer-pair coefficients are successive flow differences, with final weight $1-a_{N-1}$ or $1-b_{N-1}$.
The candidate residual $S$ has no function-value or constant component at this sample and agrees with the selected numerical $S$. Its arbitrary-horizon positive-semidefinite decomposition is unresolved. All numerical LDL factors, including small pivots, are retained. The certificate identity uses residuals $r_c\leq0$:
$$h(x_N)-h(x_\star)-\mathrm{bound}-\sum_c\lambda_c r_c+S=0.$$
Nonnegative multipliers and $S\geq0$ give the bound at this numerical sample. No all-horizon theorem is asserted.

Numerical certificate: **verified**. Analytic full PEP: **unverified**. Lyapunov proof: **unverified**.
""")
)
for title in [
    "Partial-sum Lyapunov construction and rank profile",
    "Special-vector identification",
    "Coefficient extraction and closed-form V_k",
    "Symbolic step, base, and boundary identities",
]:
    nb.cells.append(nbf.v4.new_markdown_cell("## " + title + "\nPending later blocks."))
os.environ["JUPYTER_PATH"] = str(runtime.RUNTIME / "jupyter")
nbf.write(nb, path)
NotebookClient(
    nb,
    timeout=180,
    kernel_name="pgm-private",
    resources={"metadata": {"path": str(root)}},
).execute()
nbf.write(nb, path)
from pgm_setup import (  # noqa: E402, F401 -- Required by exec of b2_notebook_cells.py. Paths initialized above.
    get_pep_setup,
)

# Reuse the actual executed verification namespace to serialize the checked state.

notebook_dir = root
exec(compile(source, "b2_notebook_cells.py", "exec"))
exec(
    compile(
        (root / "supplementary/save_b2.py").read_text(encoding="utf-8-sig"),
        "save_b2.py",
        "exec",
    )
)
print("B2 notebook executed and state saved.")
