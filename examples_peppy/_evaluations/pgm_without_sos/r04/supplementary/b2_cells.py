# This saved notebook fragment shares its caller's execution namespace.
# These names are supplied by the notebook cells or serialized proof source.
# ty: ignore[unresolved-reference]
# ruff: noqa: F821

import hashlib
import json
from fractions import Fraction

import sympy as sp

# local helper resolved by the notebook runtime path
from certificates import entries_for  # ty: ignore[unresolved-import]
from pgm_setup import get_pep_setup as saved_get_pep_setup

from pepflow.lyapunov_utils import ldl_decompose_with_reversed_basis

b1 = json.loads((notebook_dir / "state/pgm_b1.json").read_text())
dense = json.loads((notebook_dir / "state/pgm_dense.json").read_text())
sample = json.loads((notebook_dir / "supplementary/b2-selected-raw.json").read_text())
N = sample["N_verify"]
params: dict[str, pf.NUMERICAL_TYPE] = {"L": sp.S.One, "R": sp.S.One}
ctx, pb, obj = saved_get_pep_setup(N, params)
pb.set_relaxed_constraints(sample["relaxed_constraints"])
ctx.set_as_current()
entries = entries_for(ctx, pb)
pm = pf.ExpressionManager(ctx, resolve_parameters=params)
basis = ctx.basis_vectors()
assert [str(v) for v in basis] == sample["basis_vectors"]
assert [str(v) for v in ctx.basis_scalars()] == sample["basis_scalars"]
assert (
    {c.name for c, *_ in entries}
    == set(sample["named_dual_values"])
    == set(sample["constraint_metadata"])
)
for relative, digest in sample["certificate_provenance"]["source_hashes"].items():
    assert hashlib.sha256((notebook_dir / relative).read_bytes()).hexdigest() == digest
print("Dense/relaxed objectives:", dense["opt_value"], sample["opt_value"])
print("Basis:", sample["basis_vectors"])
for owner in ("f", "g"):
    values = [
        (name, value)
        for name, value in dense["named_dual_values"].items()
        if name.startswith(owner + ":") and value is not None and abs(value) > 1e-6
    ]
    print(
        "Dense active",
        owner,
        len(values),
        "largest:",
        sorted(values, key=lambda pair: -pair[1])[:5],
    )
print("Relaxation: retain x_star -> x_j and x_i -> x_(i+1), for both owners.")
print("Dropped constraints:", len(sample["relaxed_constraints"]))
for name, value in sample["named_dual_values"].items():
    if value is not None and abs(value) > 1e-6:
        print(name, value, Fraction(value).limit_denominator(1000))


# CELL
# Initial formula search inferred from the two groups' rational sequences.
def candidate_lambda(owner, ri, ci, horizon):
    def cumulative(i):
        if owner == "f":
            if i < 0:
                return sp.S.Zero
            if i == horizon:
                return sp.S.One
            return sp.Rational(i + 1, 2 * horizon - i)
        if i <= 0:
            return sp.S.Zero
        if i == horizon:
            return sp.S.One
        return sp.Rational(i, 2 * horizon - i)

    if ci == "x_star":
        return sp.S.Zero
    j = int(ci[2:])
    if ri == "x_star":
        return cumulative(j) - cumulative(j - 1)
    i = int(ri[2:])
    return cumulative(i) if j == i + 1 else sp.S.Zero


candidate_errors = []
weighted_guess = pf.Scalar.zero()
for c, origin, owner, group in entries:
    if origin != "interpolation":
        continue
    ri, ci = c.name.split(":")[1].split(",")
    guess = candidate_lambda(owner, ri, ci, N)
    actual = sample["named_dual_values"][c.name]
    actual = 0.0 if actual is None else actual
    candidate_errors.append(abs(float(guess) - actual))
    weighted_guess += guess * (c.lhs - c.rhs)
print("Maximum lambda candidate error:", max(candidate_errors))
assert max(candidate_errors) <= 1e-4
for owner in ("f", "g"):
    tags = ["x_star"] + [f"x_{j}" for j in range(0 if owner == "f" else 1, N + 1)]
    candidate_matrix = np.array(
        [[float(candidate_lambda(owner, ri, ci, N)) for ci in tags] for ri in tags]
    )
    print("Candidate lambda:", owner)
    pf.pprint_labeled_matrix(candidate_matrix, tags, precision=5)
assert pb.performance_metric is not None
S_guess = (
    sp.Rational(1, 4 * N) * (ctx["x_0"] - ctx["x_star"]) ** 2
    - pb.performance_metric
    + weighted_guess
)
S_array = np.asarray(sample["S_matrix"], dtype=float)
S_guess_eval = pm.eval_scalar(S_guess)
S_candidate_error = float(
    np.max(np.abs(np.asarray(S_guess_eval.inner_prod_coords, float) - S_array))
)
print("S candidate coordinate discrepancy:", S_candidate_error)
assert np.allclose(S_guess_eval.inner_prod_coords, S_array, atol=1e-4, rtol=1e-5)
assert np.allclose(S_guess_eval.func_coords, 0, atol=1e-4, rtol=0)
assert abs(float(S_guess_eval.offset)) <= 1e-4
print("S eigenvalues:", np.linalg.eigvalsh(S_array))
# The candidate S is a residual formula, not yet a proof of all-horizon positivity.
# No pre-existing decomposition is permitted. Apply approved reverse LDL to this sample.
S_named = pf.MatrixWithNames(S_array, sample["S_row_names"], sample["S_col_names"])
D, ell = ldl_decompose_with_reversed_basis(S_named, basis, print_output=False)
D = np.asarray(D, dtype=float)
E = np.asarray([pm.eval_vector(v).coords for v in ell], dtype=float)
S_numeric = sum(
    (float(D[i, j]) * ell[i] * ell[j] for i, j in np.ndindex(D.shape)), pf.Scalar.zero()
)
print("Reverse-LDL diagonal:", np.diag(D))
print("Significant factors (full factors retained in state):")
for i, coefficient in enumerate(np.diag(D)):
    if abs(coefficient) > 1e-6:
        print(i, coefficient, str(ell[i]))
pf.pprint_labeled_matrix(D, [f"ell_{i}" for i in range(len(D))], precision=5)
# CELL
# Complete numerical identity: metric - bound - sum(dual * residual) + S = 0.
weighted_constraints = pf.Scalar.zero()
scalar_duals = []
for c, origin, owner, group in entries:
    meta = sample["constraint_metadata"][c.name]
    value = sample["named_dual_values"][c.name]
    assert (
        meta["origin"] == origin and meta["owner"] == owner and meta["group"] == group
    )
    assert meta["comparator"] == c.cmp.value
    if meta["relaxed"]:
        assert value is None and c.name in pb.relaxed_constraints
        continue
    assert value is not None and np.isfinite(value)
    residual = c.lhs - c.rhs
    if c.cmp in (pf.Comparator.GE, pf.Comparator.SEQ):
        residual = -residual
    weighted_constraints += float(value) * residual
    if c.cmp != pf.Comparator.EQ:
        scalar_duals.append(float(value))
checked = pm.eval_scalar(
    pb.performance_metric - sample["opt_value"] - weighted_constraints + S_numeric
)


def max_abs(values):
    return float(np.max(np.abs(np.asarray(values, dtype=float)), initial=0))


residuals = dict(
    identity_gram_max_abs=max_abs(checked.inner_prod_coords),
    identity_func_max_abs=max_abs(checked.func_coords),
    identity_offset_abs=max_abs(checked.offset),
    S_reconstruction_max_abs=max_abs(E.T @ D @ E - S_array),
    dense_relaxed_gap=abs(dense["opt_value"] - sample["opt_value"]),
    minimum_scalar_inequality_dual=min(scalar_duals),
    minimum_S_eigenvalue=float(np.linalg.eigvalsh(S_array).min()),
    minimum_matrix_inequality_eigenvalue=0.0,
)
tolerances = dict(
    identity_atol=1e-5,
    identity_rtol=0.0,
    reconstruction_atol=1e-4,
    reconstruction_rtol=1e-5,
    dual_tol=1e-6,
    psd_tol=1e-6,
    dense_opt_atol=1e-5,
)
assert sample["solver_status"] == "optimal"
assert all(
    residuals[key] <= 1e-5
    for key in ("identity_gram_max_abs", "identity_func_max_abs", "identity_offset_abs")
)
assert np.all(np.isfinite(S_array)) and np.allclose(
    S_array, S_array.T, atol=1e-6, rtol=0
)
assert np.allclose(E.T @ D @ E, S_array, atol=1e-4, rtol=1e-5)
assert residuals["dense_relaxed_gap"] < 1e-5
assert residuals["minimum_scalar_inequality_dual"] >= -1e-6
assert residuals["minimum_S_eigenvalue"] >= -1e-6
assert abs(sample["opt_value"] - 1 / (4 * N)) < 1e-5
print("Complete numerical certificate checks:", residuals)
pf.pprint_labeled_matrix(
    np.asarray(checked.inner_prod_coords, float), sample["basis_vectors"], precision=8
)
print("Function residuals:", checked.func_coords, "constant residual:", checked.offset)
print(
    "Numerical certificate verified; analytic full-PEP and Lyapunov proof remain unverified."
)
