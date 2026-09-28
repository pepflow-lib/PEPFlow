"""Show the first partial-sum observation before the B2 confirmation revisit."""
import inspect
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT / "supplementary"), str(ROOT / "supplementary/helpers")]
import run_b1  # noqa: E402,F401
import nbformat as nbf  # noqa: E402
from certificate import certificate_id  # noqa: E402
from grouping import replay_certificate, full_psd_piece, build_partial_sums  # noqa: E402
from execute_notebook import execute  # noqa: E402

nb = nbf.read(ROOT / "dual_feg_example_lyap.ipynb", as_version=4)
md, code = nbf.v4.new_markdown_cell, nbf.v4.new_code_cell
cells = [md(r"""## Lyapunov partial sums and ranks
Write $y_k=x_{k+1/2}$ and use residuals
$$M_k=-\langle x_N-y_k,A(x_N)-A(y_k)\rangle\leq0,$$
$$Q_k=\|A(x_k)-A(y_k)\|^2-L^2\|x_k-y_k\|^2\leq0.$$
For $k<N-1$, group the selected numerical multipliers as
$$V_{k+1}-V_k=\lambda^M_kM_k+\lambda^Q_kQ_k,$$
with $V_0=0$. The final increment uses the selected Lipschitz residual between $x_{N-1}$ and $x_N$. All weights are nonnegative, so this convention gives $V_{k+1}\leq V_k$.

The star monotonicity term and the full PSD remainder are retained as the one interpolation and one PSD boundary terms. The candidate single square approximates the saved remainder at the reconstruction tolerance, but its error exceeds the stricter coverage tolerance. Therefore the construction retains the full numerical $S$ as one PSD boundary block, without truncating any term.

At the initial horizon the three interior ranks agree. Confirmation at another horizon is still pending; no rank-constancy claim across horizons is made yet."""),
code("import hashlib\n\n" + inspect.getsource(certificate_id) + "\n" + inspect.getsource(replay_certificate)),
code(inspect.getsource(full_psd_piece)),
code(inspect.getsource(build_partial_sums)),
code('certificate = json.loads((notebook_dir / "state/dual_feg_b2.json").read_text())\nreplay_checks, _, _ = replay_certificate(certificate, get_pep_setup, notebook_dir, dense["opt_value"])\nctx, pb, _ = get_pep_setup(certificate["N_verify"], json.loads(certificate["params_json"]))\npm = pf.ExpressionManager(ctx, resolve_parameters=json.loads(certificate["params_json"]))\nS_scalar, S_piece_terms = full_psd_piece(certificate, ctx, pm)\nlyap, observation = build_partial_sums(certificate, ctx, pb, pm, S_scalar, S_piece_terms)\nprint("Full-coordinate coverage and increments:", observation["coverage_residuals"])\nprint("Singular values avoid the diagnostic band [0.5e-4, 2e-4]:", observation["rank_credible"])\nprint("Cross-horizon status: pending a coherent N=6 certificate")')]
start = next(i for i, c in enumerate(nb.cells) if c.source.startswith("## Lyapunov partial sums"))
end = next(i for i, c in enumerate(nb.cells) if c.source.startswith("## Identify the vectors"))
nb.cells[start:end] = cells
nbf.write(nb, ROOT / "dual_feg_example_lyap.ipynb")
execute("B3-initial")
