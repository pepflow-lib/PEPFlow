import importlib.util
import os
from pathlib import Path

spec = importlib.util.spec_from_file_location(
    "runtime", Path(__file__).parent / "helpers/runtime.py"
)
assert spec is not None and spec.loader is not None
runtime = importlib.util.module_from_spec(spec)
spec.loader.exec_module(runtime)
import nbformat as nbf  # ty: ignore[unresolved-import]  # optional notebook-generation dependency  # noqa: E402 - imports follow runtime or notebook setup
from nbclient import (  # ty: ignore[unresolved-import]  # optional notebook-generation dependency  # noqa: E402 - imports follow runtime or notebook setup
    NotebookClient,
)

root = runtime.ROOT
path = root / "feg_example_lyap.ipynb"
nb = nbf.read(path, as_version=4)
source = (root / "supplementary/helpers/partial_sums.py").read_text(
    encoding="utf-8-sig"
)
source = source[source.index("KEYS =") :]
start = next(
    i for i, c in enumerate(nb.cells) if c.source.startswith("## Lyapunov partial sums")
)
end = next(
    i for i, c in enumerate(nb.cells) if c.source.startswith("## Identify the vectors")
)
nb.cells[start:end] = [
    nbf.v4.new_markdown_cell(r"""## Lyapunov partial sums
With residuals $\operatorname{Mon}(u,v)=-\langle A(u)-A(v),u-v\rangle\le0$ and $\operatorname{Lip}(u,v)=\|A(u)-A(v)\|^2-L^2\|u-v\|^2\le0$, use $V_0=0$ and
$$V_{k+1}-V_k=\lambda_k^{\rm Lip}\operatorname{Lip}(x_{k+1/2},x_{k+1})+\lambda_k^{\rm Mon}\operatorname{Mon}(x_k,x_{k+1}),$$
where the monotonicity contribution is absent at $k=0$. Nonnegative numerical multipliers make these partial sums nonincreasing. Keep the terminal zero-point monotonicity and the complete positive semidefinite $S$ block for the boundary argument.
The same construction has interior rank 2 at $N=6$ and $N=8$, excluding exactly $V_0,V_N$ in both comparisons. All endpoints remain covered and saved. Ranks use unscaled absolute singular-value tolerance $10^{-4}$; the discarded singular values are far below the threshold."""),
    nbf.v4.new_code_cell(
        source
        + '\nctx_lyap, pb_lyap, A_lyap, pm_lyap, lyap, observation = partial_sums(b2, dense["opt_value"])\n'
    ),
    nbf.v4.new_code_cell("""import contextlib
import io
with contextlib.redirect_stdout(io.StringIO()):
    _, _, _, _, _, observation8 = partial_sums(sample8, dense8["opt_value"])
for obs in [observation, observation8]:
    assert obs["certificate_checked"] and obs["grouping_checked"] and obs["rank_credible"]
    assert len(obs["rank_profile"][1:-1]) >= 3
    assert set(obs["rank_profile"][1:-1]) == {2}
assert observation["recipe_id"] == observation8["recipe_id"]
assert observation["rank_convention"] == observation8["rank_convention"]
print("Confirmed common interior rank: 2; horizons: 6,8; exclusions: (1,1); absolute tolerance: 1e-4.")
print("Full-coordinate coverage residuals:", observation["maximum_coverage_residual"], observation8["maximum_coverage_residual"])
print("Boundary: one terminal monotonicity term and the complete PSD S block; no omitted terms.")
print("Numerical certificate/grouping verified; analytic theorem remains pending.")"""),
]
nbf.write(nb, path)
os.environ["JUPYTER_PATH"] = str(runtime.RUNTIME / "jupyter")
NotebookClient(
    nb,
    timeout=120,
    kernel_name="feg-private",
    resources={"metadata": {"path": str(root)}},
).execute()
nbf.write(nb, path)
print("B3 notebook execution passed.")
