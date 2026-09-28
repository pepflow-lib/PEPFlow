import json
from pathlib import Path

# optional notebook-generation dependency
import nbformat as nbf  # ty: ignore[unresolved-import]

root = Path(__file__).resolve().parents[1]
path = root / "pgm_example_lyap.ipynb"
nb = nbf.read(path, as_version=4)
state = json.loads((root / "state/pgm_b2.json").read_text())
cells = [
    nbf.v4.new_markdown_cell(r"""## Dense and relaxed proof solves
The dense solve and one sparse solve both use CLARABEL defaults at $N=4$, $L=R=1$. Every initial and interpolation dual, together with $S$, is captured from the same selected sparse solve. The relaxation retains only pairs $(x_\star,x_j)$ and forward adjacent pairs $(x_i,x_{i+1})$ separately for $f$ and $g$. No fixed-S constraint is imposed. The actual solves and full inventories are preserved in the state files; this notebook replays their checks without solving again."""),
    nbf.v4.new_code_cell("""import numpy as np
import sympy as sp
import pgm_setup as setup
from pepflow.utils import Comparator
from pepflow.parameter import eval_parameter

dense = json.loads((notebook_dir / "state/pgm_dense.json").read_text())
b2 = json.loads((notebook_dir / "state/pgm_b2.json").read_text())
print("Dense bound:", dense["opt_value"], "selected bound:", b2["opt_value"])
print("Dense/selected difference:", abs(dense["opt_value"]-b2["opt_value"]))
print("Selected basis:", b2["basis_vectors"])
print("Dense Gram rank (absolute tolerance 1e-4):", np.linalg.matrix_rank(np.asarray(dense["S_matrix"]), tol=1e-4))
for owner in ("f", "g"):
    dense_active = [(name, value) for name, value in dense["named_dual_values"].items() if name.startswith(owner+":") and abs(value)>1e-6]
    print(owner, "dense active entries:", len(dense_active), "range:", min(v for _,v in dense_active), max(v for _,v in dense_active))
    print(owner, "selected active entries:")
    for name, value in b2["named_dual_values"].items():
        if name.startswith(owner+":") and value is not None:
            print(" ", name, value)
assert abs(dense["opt_value"]-b2["opt_value"]) < 1e-5"""),
    nbf.v4.new_markdown_cell(r"""## Lambda and S verification
Write $R_{ij}^f=f_j-f_i+\langle a_j,x_i-x_j\rangle+\|a_i-a_j\|^2/(2L)\leq0$ and $R_{ij}^g=g_j-g_i+\langle s_j,x_i-x_j\rangle\leq0$. For forward adjacent pairs, the candidate weights are
$$\lambda^f_{i,i+1}=\frac{i+1}{2N-i},\quad 0\leq i<N,\qquad \lambda^g_{i,i+1}=\frac{i}{2N-i},\quad 1\leq i<N.$$
The star weights equal successive increments of these weights, with the endpoint corrections displayed by the executable definitions below. These are inferred candidates, not yet an arbitrary-horizon certificate proof. The normalization multiplier is $L/(4N)$ for the squared-radius constraint.
The supplied three-family SOS is reproduced below in exact rational arithmetic. Its normalization factor relative to this certificate is 1. Its coefficients are nonnegative for $1\leq i\leq N$, $N\geq1$, $L>0$: every denominator is positive and every numerator is nonnegative. The first and third coefficients are strictly positive; the second also has a positive second summand."""),
    nbf.v4.new_code_cell(state["lamb_code"] + "\n" + state["S_code"]),
    nbf.v4.new_code_cell(
        """TOL = b2["numerical_checks"]["tolerances"]
"""
        + state["certificate_check_source"]
    ),
    nbf.v4.new_code_cell("""checks, ctx, pb, numerical_residual = verify(b2, dense["opt_value"], b2["numerical_decomposition"])
assert checks["passed"]
print("Complete numerical certificate:", checks)
pf.pprint_labeled_matrix(np.asarray(numerical_residual.inner_prod_coords, dtype=float), b2["basis_vectors"], precision=9)
print("Function residual:", numerical_residual.func_coords)
print("Offset residual:", numerical_residual.offset)
print("Numerical certificate verified; analytic full-PEP and Lyapunov proof statuses remain false.")"""),
    nbf.v4.new_code_cell("""N = b2["N"]
pm = pf.ExpressionManager(ctx, resolve_parameters={"L": sp.S.One, "R": sp.S.One})
weighted_exact = pf.Scalar.zero()
fit_errors = []
for constraint, origin, owner, group in inventory(ctx, pb):
    if origin == "initial":
        coefficient = sp.Rational(1, 4*N)
    else:
        left, right = constraint.name.split(":")[1].split(",")
        coefficient = lambda_candidate(owner, left, right, N)
        fit_errors.append(abs(float(coefficient)-(b2["named_dual_values"][constraint.name] or 0.0)))
    weighted_exact += coefficient * residual_of(constraint)
for owner, labels in (("f", ["x_star"]+[f"x_{i}" for i in range(N+1)]), ("g", ["x_star"]+[f"x_{i}" for i in range(1,N+1)])):
    matrix = np.array([[sp.S.Zero if left == right or right == "x_star" else lambda_candidate(owner,left,right,N) for right in labels] for left in labels], dtype=object)
    print(owner, "candidate weights:")
    pf.pprint_labeled_matrix(matrix, labels)
print("Maximum candidate multiplier discrepancy:", max(fit_errors))
assert max(fit_errors) <= 1e-4
pieces = sos_pieces(ctx, N)
D = np.diag([float(sp.N(eval_parameter(coefficient, {"L": sp.S.One}))) for _,_,coefficient,_ in pieces])
E = np.asarray([pm.eval_vector(vector).coords for _,_,_,vector in pieces], dtype=float)
S_candidate_matrix = E.T @ D @ E
S_saved = np.asarray(b2["S_matrix"])
assert np.allclose(S_candidate_matrix, S_saved, atol=1e-4, rtol=1e-5)
print("SOS reconstruction residual:", np.max(abs(S_candidate_matrix-S_saved)))
pf.pprint_labeled_matrix(S_candidate_matrix, b2["basis_vectors"], precision=6)
exact_residual = pm.eval_scalar(pb.performance_metric-sp.Rational(1,4*N)-weighted_exact+sos_scalar(ctx,N), sympy_mode=True)
assert all(sp.simplify(value)==0 for arr in (exact_residual.inner_prod_coords,exact_residual.func_coords,np.asarray(exact_residual.offset)) for value in np.asarray(arr).flat)
print("Exact candidate identity at N=4: all Gram, function and offset coordinates vanish.")
pf.pprint_labeled_matrix(exact_residual.inner_prod_coords, b2["basis_vectors"])
print("This finite-horizon exact check does not prove the all-horizon formula.")"""),
    nbf.v4.new_markdown_cell("""### Initial closed-form search and B2 conclusion
Inspecting rational approximations of the sparse weights led to the adjacent formulas and star increments above. The supplied SOS matches the same selected certificate numerically. Exact coordinate arithmetic also confirms the candidate identity at the selected horizon. The first exact-check attempt used the framework's numerical evaluation mode, leaving roundoff residuals; explicitly selecting `sympy_mode=True` removes them without rounding or tolerance changes.
The complete numerical certificate is verified. The arbitrary-horizon global identity and the Lyapunov proof remain unresolved. These candidate formulas and the same coherent numerical certificate are passed to the next block."""),
]
end = next(
    i
    for i, c in enumerate(nb.cells)
    if c.cell_type == "markdown" and c.source.startswith("## Partial-sum Lyapunov")
)
nb.cells[9:end] = cells
nbf.write(nb, path)
print("B2 notebook sections updated")
