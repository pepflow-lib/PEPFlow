import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent / "helpers"))
# local helper resolved by the notebook runtime path
from runtime import NOTEBOOK_DIR, configure  # ty: ignore[unresolved-import]

configure()
import inspect  # noqa: E402 - imports follow runtime or notebook setup

import nbformat as nbf  # ty: ignore[unresolved-import]  # optional notebook-generation dependency  # noqa: E402 - imports follow runtime or notebook setup
from grouping import (  # ty: ignore[unresolved-import]  # local helper resolved by the notebook runtime path  # noqa: E402 - imports follow runtime or notebook setup
    construct,
    replay,
)
from jupyter_client import (  # noqa: E402 - imports follow runtime or notebook setup
    KernelManager,
)
from jupyter_client.kernelspec import (  # noqa: E402 - imports follow runtime or notebook setup
    KernelSpecManager,
)
from nbclient import (  # ty: ignore[unresolved-import]  # optional notebook-generation dependency  # noqa: E402 - imports follow runtime or notebook setup
    NotebookClient,
)

path = NOTEBOOK_DIR / "pgm_example_lyap.ipynb"
nb = nbf.read(path, as_version=4)
nb.cells = nb.cells[:18]
nb.cells[17].source = nb.cells[17].source.split("## Lyapunov partial sums")[0]


def md(s):
    nb.cells.append(nbf.v4.new_markdown_cell(s))


def code(s):
    nb.cells.append(nbf.v4.new_code_cell(s))


md(r"""## Lyapunov partial sums

Write $I^f_{a,b}\leq0$ and $I^g_{a,b}\leq0$ for the normalized interpolation residuals attached to the named directed pairs. Let $Q_i=\sum_{r=1}^3 c_{r,i}\|u_{r,i}\|^2$ be the supplied, verified numerical slack pieces. Starting from $V_0=0$, accumulate all minimizer pairs through $x_k$, all forward pairs through $x_k$, and subtract $Q_1,\ldots,Q_k$.

For $1\leq k<N$,
$$V_{k+1}-V_k=
 \lambda^f_{\star,k+1}I^f_{\star,k+1}
+\lambda^g_{\star,k+1}I^g_{\star,k+1}
+\lambda^f_{k,k+1}I^f_{k,k+1}
+\lambda^g_{k,k+1}I^g_{k,k+1}-Q_{k+1}.$$
At the first step also include $\lambda^f_{\star,0}I^f_{\star,0}$; there is no $g$ forward pair from $x_0$. Every multiplier is nonnegative and every $Q_i$ is nonnegative, so the increments have the nonincreasing sign.

The initial distance constraint stays in the boundary argument. All interpolation terms and all square pieces are accumulated: there are no terminal leftovers. The terminal relation is numerically
$$V_N=h(x_N)-h(x_\star)-B-\tau(\|x_0-x_\star\|^2-R^2),$$
with the full constant-coordinate residual retained. This fixed-sample construction is not yet the analytic theorem.
""")
code(
    """import hashlib
NOTEBOOK_DIR = notebook_dir
REPO_ROOT = repo_root
"""
    + inspect.getsource(replay)
)
code(
    inspect.getsource(construct)
    + """
certificate = b2
ctx, pb, lyap, selected_observation = construct(certificate)
print("Coverage maximum residual:", selected_observation["coverage_residual"])
print("Maximum step identity residual:", max(selected_observation["step_residuals"]))
assert selected_observation["grouping_checked"]
"""
)
md(r"""### Cross-horizon confirmation

Use the same original coordinate ordering, absolute singular-value tolerance $10^{-4}$, and no scaling. Exclude only $V_0$ and $V_N$ in the comparison. The retained indices are $1,\ldots,N-1$, with at least three at each horizon. Endpoint exclusions do not waive reconstruction or boundary proof requirements.

The comparison below replays each horizon's own complete saved certificate and recomputes its partial sums. The selected main sample is $N=6$.
""")
code("""rank_samples = []
for relative in ("supplementary/N4-selected/pgm_b2.json", "state/pgm_b2.json"):
    horizon_certificate = json.loads((notebook_dir / relative).read_text())
    _, _, _, observation = construct(horizon_certificate, verbose=False)
    rank_samples.append(observation)
left = right = 1
retained = [s["rank_profile"][left:s["N"]+1-right] for s in rank_samples]
assert len({s["N"] for s in rank_samples}) >= 2
assert all(len(r) >= 3 for r in retained)
assert len({rank for r in retained for rank in r}) == 1
assert all(s["certificate_checked"] and s["grouping_checked"] and s["rank_credible"]
           for s in rank_samples)
assert all(s["recipe_id"] == rank_samples[0]["recipe_id"] and
           s["rank_convention"] == rank_samples[0]["rank_convention"] for s in rank_samples)
print("Confirming horizons:", [s["N"] for s in rank_samples])
print("Fixed boundary exclusions:", (left, right))
print("Common interior rank:", retained[0][0])
print("Coverage errors:", [s["coverage_residual"] for s in rank_samples])
print("No singular values between 0.5e-4 and 2e-4 at either horizon.")
# Restore the selected context after replaying all samples.
ctx, pb, lyap, selected_observation = construct(certificate, verbose=False)
pm = pf.ExpressionManager(ctx, resolve_parameters={"L": sp.S.One, "R": sp.S.One})
""")
md("""B3 numerical rank and coverage gates are complete. Every partial sum retains its Gram, function-value, and constant coordinates in state. The common rank is discovery evidence; the basis reconstruction and arbitrary-horizon proof remain pending.

## Special vectors (pending)
## Closed-form coefficients and exact identities (pending)
""")
nbf.write(nb, path)
km = KernelManager(
    kernel_name="attempt",
    kernel_spec_manager=KernelSpecManager(
        kernel_dirs=[str(NOTEBOOK_DIR / "supplementary/.runtime/kernels")]
    ),
)
try:
    NotebookClient(
        nb, km=km, timeout=180, resources={"metadata": {"path": str(NOTEBOOK_DIR)}}
    ).execute()
finally:
    if km.has_kernel:
        km.shutdown_kernel(now=True)
nbf.write(nb, path)
print("B3 notebook executed")
