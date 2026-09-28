import json
import hashlib
from pathlib import Path
import numpy as np
import sympy as sp
import pepflow as pf
from pgm_setup import get_pep_setup, f, g, L
from candidates import aid_pieces, square_sum, multiplier_candidate

N = certificate["N_verify"]
b2 = certificate
from pepflow.parameter import eval_parameter

ctx_b2, pb_b2, obj_b2 = get_pep_setup(N, {"L": 1, "R": 1})
entries = [(c, "initial", None, None) for c in pb_b2.init_conditions]
for owner in ctx_b2.func_to_triplets:
    owner.get_interpolation_constraints(ctx_b2)
    groups = ctx_b2.get_constraint_data(owner)
    entries.extend((c, "interpolation", str(owner), str(group))
                   for group, constraints in groups.sc_dict.items() for c in constraints)
    assert not groups.psd_dict, "Unexpected PSD interpolation extras"
assert len({c.name for c, *_ in entries}) == len(entries)
assert set(b2["named_dual_values"]) == {c.name for c, *_ in entries}
assert [str(v) for v in ctx_b2.basis_vectors()] == b2["basis_vectors"]
assert [str(v) for v in ctx_b2.basis_scalars()] == b2["basis_scalars"]
for filename, expected in b2["certificate_provenance"]["source_hashes"].items():
    assert hashlib.sha256(Path(filename).read_bytes()).hexdigest() == expected
certificate_keys = ("N_verify", "params_json", "relaxed_constraints", "S_matrix", "S_row_names",
    "S_col_names", "basis_vectors", "basis_scalars", "opt_value", "tau_sol", "tau_name",
    "named_dual_values", "constraint_metadata", "normalization", "certificate_provenance",
    "numerical_checks", "numerical_decomposition")
assert hashlib.sha256(json.dumps({k: b2[k] for k in certificate_keys}, sort_keys=True,
    separators=(",", ":"), allow_nan=False).encode()).hexdigest() == b2["certificate_id"]
expected_dropped = []
for c, *_ in entries:
    if c.name == "initial_condition":
        continue
    ri, ci = c.name.split(":")[1].split(",")
    keep = ri == "x_star" or (ci != "x_star" and int(ci[2:]) == int(ri[2:]) + 1)
    if not keep:
        expected_dropped.append(c.name)
assert set(expected_dropped) == set(b2["relaxed_constraints"])
pb_b2.set_relaxed_constraints(expected_dropped)
pm = pf.ExpressionManager(ctx_b2, resolve_parameters={"L": sp.S.One, "R": sp.S.One})
pieces = aid_pieces(ctx_b2, f, g, L, N)
S_candidate = square_sum(pieces)
E = np.array([pm.eval_vector(u).coords for _, _, _, u in pieces], dtype=float)
D = np.diag(np.asarray([eval_parameter(c, {"L": sp.S.One}) for _, _, c, _ in pieces], dtype=float))
S_saved = np.array(b2["S_matrix"])
assert np.allclose(E.T @ D @ E, S_saved, atol=1e-4, rtol=1e-5)
assert np.min(np.diag(D)) >= 0
assert np.allclose(S_saved, S_saved.T, atol=1e-6, rtol=0)
assert np.min(np.linalg.eigvalsh(S_saved)) >= -1e-6
assert all(value is None or value >= -1e-6 for value in b2["named_dual_values"].values())
weighted = pf.Scalar.zero()
weighted_exact = pf.Scalar.zero()
for c, origin, owner, group in entries:
    meta = b2["constraint_metadata"][c.name]
    assert (meta["origin"], meta["owner"], meta["group"], meta["comparator"]) == (
        origin, owner, group, c.cmp.value)
    residual = c.lhs - c.rhs
    if c.cmp == pf.Comparator.GE:
        residual = -residual
    value = b2["named_dual_values"][c.name]
    if value is not None:
        weighted += value * residual
    else:
        assert c.name in expected_dropped
    weighted_exact += multiplier_candidate(c.name, N) * residual
residual_numeric = pm.eval_scalar(pb_b2.performance_metric - b2["opt_value"] - weighted + S_candidate)
def maxabs(values):
    return float(np.max(np.abs(np.asarray(values, dtype=float)), initial=0))

print("Full numerical identity residuals:", maxabs(residual_numeric.inner_prod_coords),
      maxabs(residual_numeric.func_coords), maxabs(residual_numeric.offset))
assert all(maxabs(v) <= 1e-5 for v in (residual_numeric.inner_prod_coords,
    residual_numeric.func_coords, residual_numeric.offset))
print("SOS reconstruction error:", maxabs(E.T @ D @ E - S_saved))
print("Minimum S eigenvalue:", np.min(np.linalg.eigvalsh(S_saved)))
pf.pprint_labeled_matrix(E.T @ D @ E, b2["basis_vectors"], b2["basis_vectors"], precision=4)
pf.pprint_labeled_matrix(np.asarray(residual_numeric.inner_prod_coords, dtype=float),
                        b2["basis_vectors"], b2["basis_vectors"], precision=8)
# Exact-mode fixed-N check; this is separate from the numerical certificate.
exact_manager = pf.ExpressionManager(ctx_b2, resolve_parameters={"L": sp.S.One, "R": sp.S.One})
exact = exact_manager.eval_scalar(pb_b2.performance_metric - sp.Rational(1, 4*N)
    - weighted_exact + S_candidate, sympy_mode=True)
assert all(sp.simplify(v) == 0 for v in np.asarray(exact.inner_prod_coords).flat)
assert all(sp.simplify(v) == 0 for v in np.asarray(exact.func_coords).flat)
assert sp.simplify(exact.offset) == 0
print("Exact candidate fixed-N identity: all coordinates are zero")
for owner in ("f", "g"):
    tags = ["x_star"] + [f"x_{j}" for j in range(0 if owner == "f" else 1, N+1)]
    candidate_matrix = np.array([[sp.S.Zero if ri == ci else multiplier_candidate(
        f"{owner}:{ri},{ci}", N) for ci in tags] for ri in tags], dtype=object)
    pf.pprint_labeled_matrix(candidate_matrix, tags, tags)
candidate_error = max(abs(value - float(multiplier_candidate(name, N)))
    for name, value in b2["named_dual_values"].items() if value is not None)
assert candidate_error < 1e-4
print("Candidate multiplier error:", candidate_error)
print("Numerical certificate verified; arbitrary-horizon analytic proof remains pending.")
# Independently check the original saved S, beyond its candidate reconstruction.
basis = ctx_b2.basis_vectors()
S_scalar = sum((float(S_saved[i,j])*basis[i]*basis[j]
                for i,j in np.ndindex(S_saved.shape)), pf.Scalar.zero())
saved_identity = pm.eval_scalar(pb_b2.performance_metric - b2["opt_value"] - weighted + S_scalar)
assert all(maxabs(v) <= 1e-5 for v in (saved_identity.inner_prod_coords, saved_identity.func_coords, saved_identity.offset))
certificate_checked = True
