# This saved notebook fragment shares its caller's execution namespace.
# These names are supplied by the notebook cells or serialized proof source.
# ty: ignore[unresolved-reference]
# ruff: noqa: F821

# Visible/replayable selected-certificate and partial-sum checks; no solves.
import hashlib
import json
from pathlib import Path

import numpy as np
import sympy as sp

import pepflow as pf

# Caller supplies notebook_dir, certificate and get_pep_setup.
N_int = certificate["N_verify"]
params_sp = {
    name: sp.S(value) for name, value in json.loads(certificate["params_json"]).items()
}
ctx, pb, obj = get_pep_setup(N_int, params_sp)
ctx.set_as_current()
pb.set_relaxed_constraints(certificate["relaxed_constraints"])
certificate_keys = (
    "N_verify",
    "params_json",
    "relaxed_constraints",
    "S_matrix",
    "S_row_names",
    "S_col_names",
    "basis_vectors",
    "basis_scalars",
    "opt_value",
    "tau_sol",
    "tau_name",
    "named_dual_values",
    "constraint_metadata",
    "normalization",
    "certificate_provenance",
    "numerical_checks",
    "numerical_decomposition",
)
digest = hashlib.sha256(
    json.dumps(
        {key: certificate[key] for key in certificate_keys},
        sort_keys=True,
        separators=(",", ":"),
        allow_nan=False,
    ).encode()
).hexdigest()
assert digest == certificate["certificate_id"]
for path, expected in certificate["certificate_provenance"]["source_hashes"].items():
    source_path = Path(path).resolve()
    assert source_path.is_relative_to(notebook_dir)
    assert hashlib.sha256(source_path.read_bytes()).hexdigest() == expected
assert (
    Path(pf.__file__)
    .resolve()
    .is_relative_to(notebook_dir / "supplementary" / "approved")
)
assert certificate["certificate_provenance"]["pep_type"] == "primal"
assert certificate["certificate_provenance"]["solver_status"] == "optimal"
assert certificate["closed_form_search"]["completed"]
assert certificate["normalization"]["tau_name"] == "initial_condition"
assert certificate["normalization"]["initial_condition"] == "||x_0-x_star||^2 <= R^2"
assert certificate["normalization"]["performance_metric"] == "h(x_N)-h(x_star)"
assert certificate["normalization"]["bound_formula"] == "L*R**2/(4*N)"
assert certificate["normalization"]["bound_value"] == certificate["opt_value"]
records = [(c, "initial", None, None) for c in pb.init_conditions]
assert not ctx.oper_to_duplets
for owner in ctx.func_to_triplets:
    owner.get_interpolation_constraints(ctx)
    data = ctx.get_constraint_data(owner)
    assert not data.psd_dict
    records.extend(
        (c, "interpolation", str(owner), str(group))
        for group, family in data.sc_dict.items()
        for c in family
    )
assert len({c.name for c, *_ in records}) == len(records)
assert (
    {c.name for c, *_ in records}
    == set(certificate["named_dual_values"])
    == set(certificate["constraint_metadata"])
)
basis = ctx.basis_vectors()
basis_labels = [str(v) for v in basis]
assert (
    basis_labels
    == certificate["basis_vectors"]
    == certificate["S_row_names"]
    == certificate["S_col_names"]
)
assert [str(v) for v in ctx.basis_scalars()] == certificate["basis_scalars"]
pm = pf.ExpressionManager(ctx, resolve_parameters=params_sp)
tol = certificate["numerical_checks"]["tolerances"]
S_array = np.asarray(certificate["S_matrix"], dtype=float)
assert S_array.shape == (len(basis), len(basis))
assert np.all(np.isfinite(S_array))
assert np.allclose(S_array, S_array.T, atol=tol["psd_tol"], rtol=0)
assert np.linalg.eigvalsh(S_array).min() >= -tol["psd_tol"]
weighted_terms, group_terms, extra_duals = {}, {}, {}
for c, origin, owner, group in records:
    assert isinstance(c, pf.ScalarConstraint)
    dropped = c.name in certificate["relaxed_constraints"]
    meta = dict(
        origin=origin,
        owner=owner,
        group=group,
        kind="scalar",
        comparator=c.cmp.value,
        shape=[],
        relaxed=dropped,
    )
    assert meta == certificate["constraint_metadata"][c.name]
    value = certificate["named_dual_values"][c.name]
    if dropped:
        assert value is None
        continue
    assert value is not None and np.isfinite(value)
    if c.cmp != pf.Comparator.EQ:
        assert value >= -tol["dual_tol"]
    residual = (
        c.rhs - c.lhs
        if c.cmp in (pf.Comparator.GE, pf.Comparator.SEQ)
        else c.lhs - c.rhs
    )
    weighted_terms[c.name] = value * residual
    if origin == "interpolation":
        group_terms[c.name] = weighted_terms[c.name]
    elif c.name != certificate["tau_name"]:
        group_terms[c.name] = weighted_terms[c.name]
        extra_duals[c.name] = value
assert set(certificate["relaxed_constraints"]).issubset(
    certificate["constraint_metadata"]
)
assert certificate["named_dual_values"]["initial_condition"] == certificate["tau_sol"]
S_scalar = sum(
    (float(S_array[i, j]) * basis[i] * basis[j] for i, j in np.ndindex(S_array.shape)),
    pf.Scalar.zero(),
)


def scalar_residual(expression):
    evaluated = pm.eval_scalar(expression)
    return [
        float(np.max(np.abs(np.asarray(values, dtype=float)), initial=0.0))
        for values in (
            evaluated.inner_prod_coords,
            evaluated.func_coords,
            evaluated.offset,
        )
    ]


assert pb.performance_metric is not None
certificate_residuals = scalar_residual(
    pb.performance_metric
    - certificate["opt_value"]
    - sum(weighted_terms.values(), pf.Scalar.zero())
    + S_scalar
)
assert max(certificate_residuals) <= tol["identity_atol"]
certificate_checked = True
# Decomposition: align supplied square factors to the same saved PSD slack.
D = np.asarray(certificate["numerical_decomposition"]["D"], dtype=float)
E = np.asarray(certificate["numerical_decomposition"]["ell_coords"], dtype=float)
assert E.shape == (3 * N_int, len(basis)) and D.shape == (3 * N_int, 3 * N_int)
assert np.allclose(D, np.diag(np.diag(D)), atol=0, rtol=0)
assert np.min(np.diag(D)) >= 0
assert certificate["numerical_decomposition"]["basis_labels"] == basis_labels
assert np.allclose(
    E.T @ D @ E,
    S_array,
    atol=tol["reconstruction_atol"],
    rtol=tol["reconstruction_rtol"],
)
A_supplied = np.sqrt(D) @ E
polar_U, polar_singular, polar_Vt = np.linalg.svd(A_supplied, full_matrices=False)
slack_eigenvalues, slack_vectors = np.linalg.eigh(S_array)
slack_sqrt = (
    slack_vectors
    @ np.diag(
        np.sqrt(np.where(slack_eigenvalues > tol["psd_tol"], slack_eigenvalues, 0))
    )
    @ slack_vectors.T
)
E = polar_U @ polar_Vt @ slack_sqrt
D = np.eye(3 * N_int)
polar_reconstruction = float(np.max(np.abs(E.T @ E - S_array)))
assert polar_reconstruction <= tol["identity_atol"]
decomposition_trial = dict(
    method="polar_aligned_supplied_squares",
    eigenvalue_cutoff=tol["psd_tol"],
    discarded_slack_eigenvalues=slack_eigenvalues[
        slack_eigenvalues <= tol["psd_tol"]
    ].tolist(),
    reconstruction_max_abs=polar_reconstruction,
    D=D.tolist(),
    ell_coords=E.tolist(),
)
ell = [sum((float(c) * v for c, v in zip(row, basis)), pf.Vector.zero()) for row in E]
S_piece_terms = {
    f"S_{i + 1}": sum(
        (float(D[j, j]) * ell[j] ** 2 for j in range(3 * i, 3 * i + 3)),
        pf.Scalar.zero(),
    )
    for i in range(N_int)
}
piece_residuals = scalar_residual(
    sum(S_piece_terms.values(), pf.Scalar.zero()) - S_scalar
)
assert max(piece_residuals) <= tol["identity_atol"]
for piece in S_piece_terms.values():
    evaluated = pm.eval_scalar(piece)
    assert (
        np.max(np.abs(evaluated.func_coords), initial=0.0) == 0
        and evaluated.offset == 0
    )
    assert (
        np.linalg.eigvalsh(np.asarray(evaluated.inner_prod_coords, dtype=float)).min()
        >= -tol["psd_tol"]
    )
# Grouping convention: each increment is a sum of nonpositive residuals minus PSD pieces.
term_assignment = {}
for name in group_terms:
    left, right = name.split(":")[1].split(",")
    assert right != "x_star"
    j = int(right.split("_")[1])
    term_assignment[name] = j - 1
S_assignment = {f"S_{i + 1}": i for i in range(N_int)}
lyap = [pf.Scalar.zero()]
partial_sum = sum(
    (group_terms[name] for name, step in term_assignment.items() if step == -1),
    pf.Scalar.zero(),
)
for k in range(N_int):
    partial_sum += sum(
        (group_terms[name] for name, step in term_assignment.items() if step == k),
        pf.Scalar.zero(),
    )
    partial_sum -= S_piece_terms[f"S_{k + 1}"]
    lyap.append(partial_sum)
rank_tolerance, rank_left, rank_right = 1e-4, 1, 1
ranks, singular_values = [], []
for k, value in enumerate(lyap):
    matrix = np.asarray(pm.eval_scalar(value).inner_prod_coords, dtype=float)
    singular = np.linalg.svd(matrix, compute_uv=False)
    singular_values.append(singular.tolist())
    rank = int(np.sum(singular > rank_tolerance))
    ranks.append(rank)
    print(f"rank V_{k}: {rank}")
    if k == 0:
        print()
retained_ranks = ranks[rank_left : N_int + 1 - rank_right]
print(
    "Interior rank is constant at this N:",
    len(retained_ranks) >= 3 and len(set(retained_ranks)) == 1,
    "boundary exclusions:",
    (rank_left, rank_right),
)
coverage_residuals = scalar_residual(
    lyap[-1] - (sum(group_terms.values(), pf.Scalar.zero()) - S_scalar)
)
assert max(coverage_residuals) <= tol["identity_atol"]
increment_residuals = []
for k in range(N_int):
    steps = {-1, 0} if k == 0 else {k}
    increment = (
        sum(
            (
                group_terms[name]
                for name, step in term_assignment.items()
                if step in steps
            ),
            pf.Scalar.zero(),
        )
        - S_piece_terms[f"S_{k + 1}"]
    )
    residual = scalar_residual(lyap[k + 1] - lyap[k] - increment)
    increment_residuals.append(residual)
    assert max(residual) <= tol["identity_atol"]
grouping_checked = True
rank_credible = all(
    not any(rank_tolerance / 2 < v < rank_tolerance * 2 for v in values)
    for values in singular_values
)
print("Coverage residuals:", coverage_residuals, "rank credible:", rank_credible)
