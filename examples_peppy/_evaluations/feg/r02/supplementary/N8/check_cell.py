# This saved notebook fragment shares its caller's execution namespace.
# These names are supplied by the notebook cells or serialized proof source.
# ty: ignore[unresolved-reference]
# ruff: noqa: F821

import json

import numpy as np
import sympy as sp

import pepflow as pf
from pepflow.lyapunov_utils import ldl_decompose_with_reversed_basis

b1 = json.loads((notebook_dir / "state/feg_b1.json").read_text())
dense = json.loads((notebook_dir / "supplementary/N8/feg_dense.json").read_text())
selected = json.loads((notebook_dir / "supplementary/N8/selected-raw.json").read_text())
N = selected["N"]
ctx, pb, op = get_pep_setup(N, {})
ctx.set_as_current()
pm = pf.ExpressionManager(
    ctx, resolve_parameters={"L": sp.Integer(1), "R": sp.Integer(1)}
)
basis = ctx.basis_vectors()
assert [str(v) for v in basis] == selected["basis_vectors"]
assert [str(v) for v in ctx.basis_scalars()] == selected["basis_scalars"]
entries = [(c, "initial", None, None) for c in pb.init_conditions]
for owner in [*ctx.func_to_triplets, *ctx.oper_to_duplets]:
    groups = ctx.get_constraint_data(owner)
    entries.extend(
        (c, "interpolation", str(owner), str(group))
        for group, cs in groups.sc_dict.items()
        for c in cs
    )
    entries.extend(
        (c, "interpolation", str(owner), str(group))
        for group, c in groups.psd_dict.items()
    )
assert (
    {c.name for c, *_ in entries}
    == set(selected["named_dual_values"])
    == set(selected["constraint_metadata"])
)
S_array = np.asarray(selected["S_matrix"], dtype=float)
S_labeled = pf.MatrixWithNames(
    S_array, selected["S_row_names"], selected["S_col_names"]
)
D, ell = ldl_decompose_with_reversed_basis(S_labeled, basis, print_output=False)
E = np.asarray([pm.eval_vector(v).coords for v in ell], dtype=float)
S_numeric = sum(
    (float(D[i, j]) * ell[i] * ell[j] for i, j in np.ndindex(D.shape)), pf.Scalar.zero()
)
weighted = pf.Scalar.zero()
inequality_duals = []
for c, origin, owner_name, group in entries:
    meta = selected["constraint_metadata"][c.name]
    assert (
        meta["origin"] == origin
        and meta["owner"] == owner_name
        and meta["group"] == group
    )
    assert meta["comparator"] == c.cmp.value
    assert (
        isinstance(c, pf.ScalarConstraint)
        and meta["kind"] == "scalar"
        and meta["shape"] == []
    )
    value = selected["named_dual_values"][c.name]
    if meta["relaxed"]:
        assert value is None and c.name in selected["relaxed_constraints"]
        continue
    assert value is not None and np.isfinite(value)
    residual = c.lhs - c.rhs
    if c.cmp in (pf.Comparator.GE, pf.Comparator.SEQ):
        residual = -residual
    weighted += float(value) * residual
    if c.cmp != pf.Comparator.EQ:
        inequality_duals.append(value)
diff = pb.performance_metric - selected["opt_value"] - weighted + S_numeric
checked = pm.eval_scalar(diff)


def max_abs(a):
    return float(np.max(np.abs(np.asarray(a, dtype=float)), initial=0))


residuals = dict(
    identity_gram_max_abs=max_abs(checked.inner_prod_coords),
    identity_func_max_abs=max_abs(checked.func_coords),
    identity_offset_abs=max_abs(checked.offset),
    S_reconstruction_max_abs=max_abs(E.T @ D @ E - S_array),
    dense_relaxed_gap=abs(dense["opt_value"] - selected["opt_value"]),
    minimum_scalar_inequality_dual=min(inequality_duals),
    minimum_S_eigenvalue=float(np.linalg.eigvalsh(S_array).min()),
    minimum_matrix_inequality_eigenvalue=0.0,
)
assert selected["solver_status"] == "optimal"
assert all(
    residuals[k] <= 1e-5
    for k in (
        "identity_gram_max_abs",
        "identity_func_max_abs",
        "identity_offset_abs",
        "dense_relaxed_gap",
    )
)
assert np.allclose(E.T @ D @ E, S_array, atol=1e-4, rtol=1e-5)
assert np.allclose(S_array, S_array.T, atol=1e-6, rtol=0)
assert residuals["minimum_S_eigenvalue"] >= -1e-6 and min(inequality_duals) >= -1e-6
assert abs(selected["opt_value"] - 4 / N**2) < 1e-5
print(
    "Dense/selected:",
    dense["opt_value"],
    selected["opt_value"],
    "removed:",
    len(selected["relaxed_constraints"]),
)
print("Basis:", selected["basis_vectors"])
print("LDL diagonal:", np.diag(D))
print("Full certificate checks:", residuals)
pf.pprint_labeled_matrix(
    pf.MatrixWithNames(
        E.T @ D @ E, selected["basis_vectors"], selected["basis_vectors"]
    )
)
pf.pprint_labeled_matrix(
    pf.MatrixWithNames(
        np.asarray(checked.inner_prod_coords),
        selected["basis_vectors"],
        selected["basis_vectors"],
    )
)
