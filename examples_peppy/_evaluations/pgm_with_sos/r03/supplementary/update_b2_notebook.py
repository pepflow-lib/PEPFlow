import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent / "helpers"))
# local helper resolved by the notebook runtime path
from runtime import NOTEBOOK_DIR, configure  # ty: ignore[unresolved-import]

configure()
import inspect  # noqa: E402 - imports follow runtime or notebook setup

import nbformat as nbf  # ty: ignore[unresolved-import]  # optional notebook-generation dependency  # noqa: E402 - imports follow runtime or notebook setup
from certificates import (  # ty: ignore[unresolved-import]  # local helper resolved by the notebook runtime path  # noqa: E402 - imports follow runtime or notebook setup
    aid_terms,
    inventory,
    lambda_candidate,
    maxabs,
    residual,
    verify,
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
nb.cells = nb.cells[:10]
nb.cells[9].source = nb.cells[9].source.split("## Full-PEP")[0]


def md(s):
    nb.cells.append(nbf.v4.new_markdown_cell(s))


def code(s):
    nb.cells.append(nbf.v4.new_code_cell(s))


md(r"""## Full-PEP certificate: dense and sparse solves

At $N=4$, the dense solve includes every smooth-convex interpolation inequality of $f$ and convex interpolation inequality of $g$. Both solves use CLARABEL defaults. The sparse solve retains only pairs $(x_\star,x_j)$ and $(x_i,x_{i+1})$ for both functions, with their applicable index ranges. Small dense entries alone are not set to zero: a fresh solve under this relaxation supplies all selected duals and the slack matrix together.
""")
code("""import sympy as sp
from pepflow.utils import Comparator

b2 = json.loads((notebook_dir / "state/pgm_b2.json").read_text())
dense = json.loads((notebook_dir / "state/pgm_dense.json").read_text())
print("Dense objective:", dense["opt_value"])
print("Selected objective:", b2["opt_value"])
print("Dense-relaxed gap:", abs(dense["opt_value"] - b2["opt_value"]))
assert abs(dense["opt_value"] - b2["opt_value"]) < 1e-5
print("Basis:", b2["basis_vectors"])
for owner in ("f", "g"):
    active = [(name, value) for name, value in dense["named_dual_values"].items()
              if name.startswith(owner + ":") and value is not None and value > 1e-6]
    print("Dense active group", owner, "count", len(active), "range",
          (min(v for _, v in active), max(v for _, v in active)))
    selected = [(name, value) for name, value in b2["named_dual_values"].items()
                if name.startswith(owner + ":") and value is not None]
    print("Selected", owner, selected)
print("Dense S eigenvalues:", np.linalg.eigvalsh(dense["S_matrix"]))
print("Selected solver:", b2["certificate_provenance"]["solver"])
""")
md(r"""### Candidate multipliers and supplied SOS

Rational inspection of the selected multipliers gives forward weights
$$\alpha_i=\frac{i+1}{2N-i}\quad(0\leq i<N),\qquad
\beta_i=\frac{i}{2N-i}\quad(1\leq i<N).$$
The outgoing minimizer weights are the consecutive differences of these flows, with terminal flow one; the code includes both endpoints explicitly. The initial multiplier is $L/(4N)$ (the code below evaluates $L=1$).

The SOS below is the supplied candidate, implemented with exact rational coefficients. The certificate uses it with overall scale **one**. Its coefficients are positive for $1\leq i\leq N$, $N\geq1$, and $L>0$: all denominators are positive and the second family's strictly positive second summand covers $i=1$.

The formulas remain candidates for arbitrary horizons. An exact identity at this selected horizon is a fixed-sample check.
""")
code(
    "\n\n".join(
        inspect.getsource(fn)
        for fn in [inventory, residual, maxabs, aid_terms, lambda_candidate, verify]
    )
)
code("""n = b2["N_verify"]
ctx, pb, _ = get_pep_setup(n, {"L": sp.S.One, "R": sp.S.One})
pb.set_relaxed_constraints(b2["relaxed_constraints"])
assert [str(v) for v in ctx.basis_vectors()] == b2["basis_vectors"]
assert [str(v) for v in ctx.basis_scalars()] == b2["basis_scalars"]
checks, numerical_residual = verify(ctx, pb, b2, dense["opt_value"])
pm = pf.ExpressionManager(ctx, resolve_parameters={"L": sp.S.One, "R": sp.S.One})
for owner, first in (("f", 0), ("g", 1)):
    labels = ["x_star"] + [f"x_{j}" for j in range(first, n+1)]
    candidate_matrix = np.array([[lambda_candidate(f"{owner}:{a},{b}", n)
        if a != b else sp.S.Zero for b in labels] for a in labels], dtype=object)
    print("Candidate lambda", owner)
    pf.pprint_labeled_matrix(pf.MatrixWithNames(candidate_matrix, labels, labels))
fit_errors = [abs(float(lambda_candidate(name, n))-value)
              for name, value in b2["named_dual_values"].items() if value is not None]
assert max(fit_errors) <= 1e-4
print("Candidate multiplier max error:", max(fit_errors))
""")
md(r"""### Slack decomposition and complete certificate checks

Normalize every interpolation inequality as $R\leq0$. The primal dual certificate identity is
$$h(x_N)-h(x_\star)-B-\sum_c d_cR_c+S=0.$$
The sum includes the initial residual $\|x_0-x_\star\|^2-R^2$ and every active interpolation group. The checks cover Gram coefficients, function coefficients, constants, multiplier signs, slack PSD, and the preserved bound. No multiplier is drawn from a different solve.
""")
code("""terms = aid_terms(ctx, n)
aid = sum((c*u**2 for _, _, c, u in terms), pf.Scalar.zero())
D = np.diag([float(pm.eval_scalar(c)) for _, _, c, _ in terms])
E = np.array([pm.eval_vector(u).coords for _, _, _, u in terms], dtype=float)
S_candidate = E.T @ D @ E
assert np.all(np.diag(D) > 0)
assert np.allclose(S_candidate, b2["S_matrix"], atol=1e-4, rtol=1e-5)
ae = pm.eval_scalar(aid)
assert maxabs(ae.func_coords) == 0 and maxabs(ae.offset) == 0
print("Direct S reconstruction error:", maxabs(S_candidate - np.array(b2["S_matrix"])))
pf.pprint_labeled_matrix(pf.MatrixWithNames(
    S_candidate, b2["basis_vectors"], b2["basis_vectors"]))
weighted = pf.Scalar.zero()
exact_weighted = pf.Scalar.zero()
for c, *_ in inventory(ctx, pb):
    value = b2["named_dual_values"][c.name]
    if value is not None:
        weighted += value * residual(c)
    else:
        assert lambda_candidate(c.name, n) == 0
    exact_weighted += lambda_candidate(c.name, n) * residual(c)
aid_residual = pm.eval_scalar(pb.performance_metric - b2["opt_value"] - weighted + aid)
print("Saved S complete numerical residuals:", checks)
print("Using direct SOS: Gram, function, offset:",
      maxabs(aid_residual.inner_prod_coords), maxabs(aid_residual.func_coords),
      maxabs(aid_residual.offset))
assert max(maxabs(aid_residual.inner_prod_coords),
           maxabs(aid_residual.func_coords), maxabs(aid_residual.offset)) <= 1e-5
pf.pprint_labeled_matrix(pf.MatrixWithNames(
    np.asarray(aid_residual.inner_prod_coords, dtype=float),
    b2["basis_vectors"], b2["basis_vectors"]))
exact_residual = pm.eval_scalar(
    pb.performance_metric - sp.Rational(1, 4*n) - exact_weighted + aid, sympy_mode=True)
assert all(sp.simplify(v) == 0 for v in [
    *exact_residual.inner_prod_coords.flat, *exact_residual.func_coords.flat,
    exact_residual.offset])
print("Exact candidate identity at N =", n, ": all coordinates zero")
print("Numerical certificate verified; analytic full-PEP and Lyapunov proof remain pending.")
""")
md(r"""### Initial formula search and B2 conclusion

The dense certificate was inspected across both interpolation families. The consecutive/minimizer sparse recipe preserved its bound. Rational approximations and flow differences supplied multiplier candidates, compared against every active selected multiplier. The supplied three-family SOS matches the same selected slack; its exact candidate identity also vanishes in every coordinate at $N=4$.

This completes the initial formula search and numerical certificate gate. The all-horizon analytic identity and Lyapunov proof are unresolved.

## Lyapunov partial sums (pending)
## Special vectors (pending)
## Closed-form coefficients and exact identities (pending)
""")
nbf.write(nb, path)
kdir = NOTEBOOK_DIR / "supplementary/.runtime/kernels"
km = KernelManager(
    kernel_name="attempt",
    kernel_spec_manager=KernelSpecManager(kernel_dirs=[str(kdir)]),
)
try:
    NotebookClient(
        nb, km=km, timeout=180, resources={"metadata": {"path": str(NOTEBOOK_DIR)}}
    ).execute()
finally:
    if km.has_kernel:
        km.shutdown_kernel(now=True)
nbf.write(nb, path)
print("B2 notebook executed", path)
