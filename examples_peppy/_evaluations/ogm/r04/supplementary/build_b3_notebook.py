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

nbpath = attempt / "ogm_example_lyap.ipynb"
nb = nbf.read(nbpath, as_version=4)
nb.cells = nb.cells[:22]
md, code = nbf.v4.new_markdown_cell, nbf.v4.new_code_cell
nb.cells.append(
    md(r"""## Lyapunov partial sums
Let $I_{i,j}=f(x_j)-f(x_i)+\langle g_j,x_i-x_j\rangle+\|g_i-g_j\|^2/(2L)\leq0$. Keep the actual saved nonnegative multipliers. Start at $V_0=0$ and form
$$V_k=\sum_{j=0}^{k}\lambda_{\star,j}I_{\star,j}+\sum_{j=0}^{k-1}\lambda_{j,j+1}I_{j,j+1},\qquad 1\leq k\leq N.$$
For $k\geq1$, the increment is $V_{k+1}-V_k=\lambda_{\star,k+1}I_{\star,k+1}+\lambda_{k,k+1}I_{k,k+1}\leq0$; the first increment also contains $\lambda_{\star,0}I_{\star,0}$. The verified rank-one square is retained as a terminal boundary remainder. Thus the numerical coverage identity is
$$V_N-S=f(x_N)-f(x_\star)-b-\tau(\|x_0-x_\star\|^2-R^2).$$
This construction has interior quadratic rank three at two sampled horizons; numerical rank evidence alone does not prove an arbitrary-horizon formula. We retain the N=4 certificate as the main sample.
""")
)
nb.cells.append(
    code("""import sympy as sp

REPO_ROOT = repo_root
certificate = json.loads((notebook_dir/'state/ogm_b2.json').read_text())
N_int = certificate['N_verify']
params_sp = {key:sp.S(value) for key,value in json.loads(certificate['params_json']).items()}
ctx,pb,obj = get_pep_setup(N_int,params_sp)
pb.set_relaxed_constraints(certificate['relaxed_constraints'])
ctx.set_as_current()
""")
)
for filename in (
    "b3_certificate_check.py",
    "b3_decomposition.py",
    "b3_grouping.py",
    "b3_rank_assess.py",
    "b3_save.py",
):
    nb.cells.append(
        code((attempt / "supplementary" / filename).read_text(encoding="utf-8-sig"))
    )
nb.cells.extend(
    [
        md("## Identify the vectors composing the Lyapunov function\nBlock 4 pending."),
        md("## Closed-form Lyapunov function and exact identities\nBlock 5 pending."),
    ]
)
nbf.write(nb, nbpath)
os.environ["JUPYTER_PATH"] = str(attempt / "supplementary/.runtime/jupyter")
NotebookClient(
    nb,
    timeout=120,
    kernel_name="ogm-own",
    resources={"metadata": {"path": str(attempt)}},
).execute()
nbf.write(nb, nbpath)
for i, c in enumerate(nb.cells):
    if c.cell_type == "markdown":
        assert "\\(" not in c.source and "\\[" not in c.source
        assert not any(ord(ch) < 32 and ch not in "\n\t" for ch in c.source)
    elif i >= 22:
        for out in c.outputs:
            if out.output_type == "stream":
                print("CELL", i, out.text)
print("Saved cells:", len(nb.cells))
