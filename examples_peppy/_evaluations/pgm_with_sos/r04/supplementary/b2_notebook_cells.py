# This saved notebook fragment shares its caller's execution namespace.
# These names are supplied by the notebook cells or serialized proof source.
# ty: ignore[unresolved-reference]
# ruff: noqa: F821

import hashlib
import json

import numpy as np
import sympy as sp

import pepflow as pf
from pepflow.utils import NUMERICAL_TYPE

b1 = json.loads((notebook_dir / "state/pgm_b1.json").read_text())
dense = json.loads((notebook_dir / "state/pgm_dense.json").read_text())
raw = json.loads((notebook_dir / "state/pgm_selected_raw.json").read_text())
N_int = raw["N"]
N = sp.Integer(N_int)
params_sp: dict[str, NUMERICAL_TYPE] = {"L": sp.Integer(1), "R": sp.Integer(1)}
ctx, pb, obj = get_pep_setup(N_int, params_sp)
pm = pf.ExpressionManager(ctx, resolve_parameters=params_sp)
basis = ctx.basis_vectors()
assert raw["basis_vectors"] == [str(v) for v in basis]
assert raw["basis_scalars"] == [str(v) for v in ctx.basis_scalars()]
for name, digest in raw["source_hashes"].items():
    assert hashlib.sha256((notebook_dir / name).read_bytes()).hexdigest() == digest
print("Dense objective:", dense["opt_value"])
print("Basis:", raw["basis_vectors"])
for owner in ("f", "g"):
    print(
        "Dense active entries",
        owner,
        sum(
            v > 1e-6
            for k, v in dense["named_dual_values"].items()
            if k.startswith(owner + ":")
        ),
    )
print(
    "Dense S rank (tol=1e-4):",
    np.linalg.matrix_rank(np.array(dense["S_matrix"]), tol=1e-4),
)
# Relaxation recipe: retain only optimizer-to-iterate and forward consecutive pairs.
entries = list(pb.init_conditions)
for owner in (f, g):
    entries.extend(owner.get_interpolation_constraints(ctx))


def retained(name):
    if ":" not in name:
        return True
    left, right = name.split(":")[1].split(",")
    return left == "x_star" or (
        right != "x_star" and int(right[2:]) == int(left[2:]) + 1
    )


assert set(raw["relaxed_constraints"]) == {
    c.name for c in entries if not retained(c.name)
}
assert set(raw["named_dual_values"]) == {c.name for c in entries}
print("Relaxed constraints dropped:", len(raw["relaxed_constraints"]))
print("Selected objective:", raw["opt_value"], "status:", raw["status"])
print("Dense/relaxed gap:", abs(dense["opt_value"] - raw["opt_value"]))


# Candidate multipliers inferred from the selected consecutive-pair sample.
def lambda_candidate(owner, left, right, n):
    j = int(right[2:])

    def alpha(t):
        return sp.Rational(t, 2 * n + 1 - t)

    def beta(t):
        return sp.Rational(t, 2 * n - t)

    if owner == "f":
        return (
            alpha(j)
            if left != "x_star"
            else (alpha(j + 1) - alpha(j) if j < n else 1 - alpha(n))
        )
    return beta(j - 1) if left != "x_star" else beta(j) - beta(j - 1)


lambda_errors = []
for owner in ("f", "g"):
    labels = ["x_star"] + [f"x_{i}" for i in range(0 if owner == "f" else 1, N_int + 1)]
    candidate_matrix = np.zeros((len(labels), len(labels)))
    for row, left in enumerate(labels):
        for col, right in enumerate(labels):
            name = f"{owner}:{left},{right}"
            value = raw["named_dual_values"].get(name)
            if value is not None:
                candidate = lambda_candidate(owner, left, right, N_int)
                candidate_matrix[row, col] = float(candidate)
                lambda_errors.append(abs(float(candidate) - value))
                print(name, value, "candidate", candidate)
    print("Candidate lambda", owner)
    pf.pprint_labeled_matrix(candidate_matrix, labels)
assert max(lambda_errors) <= 1e-4


# Supplied SOS aid, implemented in exact rational arithmetic.
def supplied_sos(ctx, n, smoothness):
    n = sp.Integer(n)
    smoothness = sp.sympify(smoothness)
    star = ctx["x_star"]
    astar = f.grad(star)
    pieces, coefficients, vectors = [], [], []
    for i in range(1, int(n) + 1):
        xp, x = ctx[f"x_{i - 1}"], ctx[f"x_{i}"]
        ap, a, s = f.grad(xp), f.grad(x), g.grad(x)
        c1 = n / ((2 * n + 1 - i) * (2 * n - i) * smoothness)
        u1 = i / (2 * n) * a + (2 * n - i) / (2 * n) * ap - astar
        c2 = (
            (i - 1) / (2 * n - i) * (2 * n + 2) / (2 * n + 1)
            + 2 * n / ((2 * n - i) ** 2 * (2 * n + 1))
        ) / (2 * smoothness)
        u2 = ap + s - smoothness / (2 * n + 1 - i) * (xp - star)
        c3 = i / (2 * n + 1 - i) * (2 * n) / (2 * n + 1) / (2 * smoothness)
        u3 = (
            (2 * n + 1) / (2 * n) * (a + s)
            - (ap + s) / (2 * n)
            - smoothness / (2 * n - i) * (x - star)
        )
        coefficients.extend([c1, c2, c3])
        vectors.extend([u1, u2, u3])
        pieces.append(c1 * u1**2 + c2 * u2**2 + c3 * u3**2)
    return pieces, coefficients, vectors


pieces, coefficients, vectors = supplied_sos(ctx, N_int, 1)
S_candidate = sum(pieces, pf.Scalar.zero())
S_eval = pm.eval_scalar(S_candidate)
S_array = np.array(raw["S_matrix"])
D = np.diag(np.array(coefficients, dtype=float))
E = np.array([pm.eval_vector(v).coords for v in vectors], dtype=float)
S_reconstructed = E.T @ D @ E
assert np.all(np.array(coefficients, dtype=float) >= 0)
assert np.allclose(S_reconstructed, S_array, atol=1e-4, rtol=1e-5)
assert np.max(np.abs(np.array(S_eval.func_coords, dtype=float)), initial=0) == 0
assert float(S_eval.offset) == 0
print("Supplied aid normalization factor: 1")
print("SOS reconstruction residual:", np.max(np.abs(S_reconstructed - S_array)))
pf.pprint_labeled_matrix(S_reconstructed, raw["basis_vectors"])

# Complete numerical identity including initial constraint and both functions.
weighted = pf.Scalar.zero()
inequality_duals = []
for c in entries:
    value = raw["named_dual_values"][c.name]
    if raw["constraint_metadata"][c.name]["relaxed"]:
        assert value is None
        continue
    assert value is not None
    assert c.cmp.value == "LE"
    weighted += value * (c.lhs - c.rhs)
    inequality_duals.append(value)
diff = pm.eval_scalar(pb.performance_metric - raw["opt_value"] - weighted + S_candidate)


def maxabs(x):
    return float(np.max(np.abs(np.asarray(x, dtype=float)), initial=0))


residuals = dict(
    identity_gram_max_abs=maxabs(diff.inner_prod_coords),
    identity_func_max_abs=maxabs(diff.func_coords),
    identity_offset_abs=maxabs(diff.offset),
    S_reconstruction_max_abs=maxabs(S_reconstructed - S_array),
    dense_relaxed_gap=abs(dense["opt_value"] - raw["opt_value"]),
    minimum_scalar_inequality_dual=min(inequality_duals),
    minimum_S_eigenvalue=float(np.linalg.eigvalsh(S_array).min()),
    minimum_matrix_inequality_eigenvalue=0.0,
)
assert raw["status"] == "optimal"
assert all(
    residuals[k] <= 1e-5
    for k in ("identity_gram_max_abs", "identity_func_max_abs", "identity_offset_abs")
)
assert residuals["dense_relaxed_gap"] < 1e-5
assert residuals["minimum_scalar_inequality_dual"] >= -1e-6
assert residuals["minimum_S_eigenvalue"] >= -1e-6
assert np.allclose(S_array, S_array.T, atol=1e-6, rtol=0)
print("Complete numerical certificate checks:", residuals)
pf.pprint_labeled_matrix(
    np.asarray(diff.inner_prod_coords, dtype=float), raw["basis_vectors"]
)
# Independent candidate identity at this sample only; no all-horizon proof claim.
exact_weighted = sp.Rational(1, 4 * N_int) * (
    pb.init_conditions[0].lhs - pb.init_conditions[0].rhs
)
for c in entries[1:]:
    if not raw["constraint_metadata"][c.name]["relaxed"]:
        owner, pair = c.name.split(":")
        left, right = pair.split(",")
        exact_weighted += lambda_candidate(owner, left, right, N_int) * (c.lhs - c.rhs)
candidate_diff = pm.eval_scalar(
    pb.performance_metric - sp.Rational(1, 4 * N_int) - exact_weighted + S_candidate
)
print("Candidate fixed-sample Gram residual:", maxabs(candidate_diff.inner_prod_coords))
print("Candidate fixed-sample function residual:", maxabs(candidate_diff.func_coords))
print("Candidate fixed-sample offset:", candidate_diff.offset)
