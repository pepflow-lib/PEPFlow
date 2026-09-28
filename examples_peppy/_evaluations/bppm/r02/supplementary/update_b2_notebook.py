from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).resolve().parent / "helpers"))
from runtime import ATTEMPT
from certificates import entries_for, candidate_weights, max_abs, verify_certificate
import inspect
import nbformat as nbf

path = ATTEMPT / "bppm_example_lyap.ipynb"
nb = nbf.read(path, as_version=4)
start = next(i for i,c in enumerate(nb.cells) if c.cell_type == "markdown" and c.source.startswith("## Dense and relaxed"))
end = next(i for i,c in enumerate(nb.cells) if c.cell_type == "markdown" and c.source.startswith("## Partial-sum"))
new = [
nbf.v4.new_markdown_cell('''## Dense and relaxed proof solves
The complete dense solve at $N=4$ contains both convex interpolation families. Its near-zero Gram dual suggests a certificate using only scalar interpolation inequalities. We keep $f$ inequalities from the optimum to every iterate and from each preceding iterate to its successor, both directions of adjacent $h$ inequalities, and the terminal $h$ inequality from the optimum. A fresh solve enforces this support; it does not combine dual components from different solves.'''),
nbf.v4.new_code_cell('''import numpy as np
import sympy as sp
from pepflow.utils import Comparator
b2 = json.loads((notebook_dir / "state/bppm_b2.json").read_text())
dense = json.loads((notebook_dir / "state/bppm_dense.json").read_text())
print("Dense optimum:", dense["opt_value"])
print("Selected optimum:", b2["opt_value"])
print("Gap:", abs(dense["opt_value"] - b2["opt_value"]))
print("Basis vectors:", b2["basis_vectors"])
for owner, duals in dense["all_owner_duals"].items():
    print("Dense active", owner, {name: round(value, 7) for name, value in duals.items() if abs(value) > 1e-6})
print("Dense S eigenvalues:", np.linalg.eigvalsh(np.asarray(dense["S_matrix"])))
print("Dropped constraints:", len(b2["relaxed_constraints"]))
for name, value in b2["named_dual_values"].items():
    if value is not None:
        print(name, value)
assert abs(dense["opt_value"] - b2["opt_value"]) < 1e-5'''),
nbf.v4.new_markdown_cell(r'''## Lambda and S verification
### Initial formula search
Write $C^q_{i,j}=q(x_j)-q(x_i)+\langle\nabla q(x_j),x_i-x_j\rangle\le0$. The sparse numerical dual suggests
$$\lambda^f_{\star,k}=\frac1N,\qquad
\lambda^f_{k-1,k}=\frac{k-1}{N},$$
$$\lambda^h_{k,k-1}=\frac{k}{\alpha N},\qquad
\lambda^h_{k-1,k}=\frac{k-1}{\alpha N},\qquad
\lambda^h_{\star,N}=\frac1{\alpha N},\qquad
\tau=\frac1{\alpha N},\quad S=0.$$
Here $1\le k\le N$; zero-weight terms are omitted. We compared every retained multiplier with these formulas. No external target references were consulted. These remain candidate formulas until their all-horizon identity and domain conditions are established. The following exact check is at the selected finite horizon only.'''),
nbf.v4.new_code_cell(inspect.getsource(candidate_weights) + '''
weights = candidate_weights(b2["N"], sp.Integer(1))
maximum_lambda_error = max(abs(float(weights.get(name, 0)) - float(value or 0)) for name, value in b2["named_dual_values"].items())
assert maximum_lambda_error < 1e-4
print("Candidate lambda discrepancy:", maximum_lambda_error)
for owner, groups in b2["all_owner_lambda_groups"].items():
    for group in groups.values():
        rows, cols = group["row_names"], group["col_names"]
        matrix = np.array([[weights.get(f"{owner}:{r},{c}", 0) for c in cols] for r in rows], dtype=object)
        print("Candidate lambda for", owner)
        pf.pprint_labeled_matrix(pf.MatrixWithNames(matrix, rows, cols))'''),
nbf.v4.new_markdown_cell(r'''### Selected numerical S decomposition
The saved certificate retains every eigenvalue: $S=E^\top D E$, with $D$ diagonal and $E$ containing the orthonormal eigenvectors as rows. No small numerical term is dropped. The exact candidate $S=0$ matches to the fixed reconstruction tolerance but does not replace the selected numerical certificate.'''),
nbf.v4.new_code_cell('''S_array = np.asarray(b2["S_matrix"])
D = np.asarray(b2["numerical_decomposition"]["D"])
E = np.asarray(b2["numerical_decomposition"]["ell_coords"])
assert np.allclose(E.T @ D @ E, S_array, atol=1e-4, rtol=1e-5)
assert np.allclose(S_array, 0, atol=1e-4, rtol=0)
print("All numerical diagonal coefficients:", np.diag(D))
print("S reconstruction discrepancy:", np.max(np.abs(E.T @ D @ E - S_array)))
pf.pprint_labeled_matrix(pf.MatrixWithNames(np.zeros_like(S_array), b2["S_row_names"], b2["S_col_names"]))'''),
nbf.v4.new_markdown_cell(r'''### Complete numerical certificate identity
All scalar interpolation families and the initial constraint use residuals $C\le0$. The checked identity is
$$\mathrm{metric}-\mathrm{bound}-\sum_c d_c C_c+S=0.$$
We verify every Gram entry, every function-value coordinate, the constant, multiplier signs, and PSD signs. The scalar-only inventory is explicitly checked; there are no extra matrix constraints in this model.'''),
nbf.v4.new_code_cell('\n\n'.join(inspect.getsource(f) for f in (entries_for, max_abs, verify_certificate)) + '''
ctx, pb = ctx_b1, pb_b1
pb.set_relaxed_constraints(b2["relaxed_constraints"])
checks, residual = verify_certificate(ctx, pb, b2)
print("Numerical certificate checks:", checks)
pf.pprint_labeled_matrix(pf.MatrixWithNames(np.asarray(residual.inner_prod_coords, dtype=float), b2["basis_vectors"], b2["basis_vectors"]))
print("Function residual:", residual.func_coords)
print("Constant residual:", residual.offset)
pm = pf.ExpressionManager(ctx, resolve_parameters={"alpha": sp.Integer(1), "R": sp.Integer(1)})
exact_candidate = pb.performance_metric - sp.Rational(1, b2["N"])
for constraint, *_ in entries_for(ctx, pb):
    exact_candidate -= weights.get(constraint.name, 0) * (pf.Scalar.zero() + constraint.lhs - constraint.rhs)
exact_coordinates = pm.eval_scalar(exact_candidate)
for array in (exact_coordinates.inner_prod_coords, exact_coordinates.func_coords, np.asarray([exact_coordinates.offset])):
    assert all(sp.simplify(v) == 0 for v in np.asarray(array, dtype=object).flat)
print("Fixed-N exact candidate identity: all coordinates zero.")
print("Numerical certificate verified: True; analytic full-PEP verified: False; Lyapunov proof verified: False.")'''),
nbf.v4.new_markdown_cell('''### Block 2 conclusion
The complete numerical certificate and its decomposition are verified. The initial formula search produced candidates for all multiplier groups and $S$, confirmed numerically and by a fixed-$N$ exact identity. The all-horizon analytic argument remains unresolved and is carried forward explicitly. Later blocks will construct and verify the Lyapunov sequence.''')]
nb.cells[start:end] = new
nbf.write(nb, path)
print("Updated B2 notebook sections.")

