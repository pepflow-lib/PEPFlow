"""Revalidate and group one saved certificate without solving."""

import hashlib
import json
import sys
from pathlib import Path

import numpy as np
import sympy as sp

# local helper resolved by the notebook runtime path
from certificate_tools import check_saved, entries_for  # ty: ignore[unresolved-import]
from feg_setup import get_pep_setup

import pepflow as pf

notebook_dir = Path.cwd()
REPO_ROOT = notebook_dir / "supplementary/approved"
certificate_path = Path(sys.argv[1]) if len(sys.argv) > 1 else Path("state/feg_b2.json")
certificate = json.loads(certificate_path.read_text())
N_int = certificate["N_verify"]
params_sp: dict[str, pf.NUMERICAL_TYPE] = {"L": sp.S(1), "R": sp.S(1)}
ctx, pb, obj = get_pep_setup(N_int, params_sp)
pb.set_relaxed_constraints(certificate["relaxed_constraints"])
pm = pf.ExpressionManager(ctx, resolve_parameters=params_sp)

# BEGIN CERTIFICATE CHECK
certificate_checked = False
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
payload = {key: certificate[key] for key in certificate_keys}
assert (
    hashlib.sha256(
        json.dumps(
            payload, sort_keys=True, separators=(",", ":"), allow_nan=False
        ).encode()
    ).hexdigest()
    == certificate["certificate_id"]
)
assert certificate["certificate_provenance"]["pep_type"] == "primal"
assert certificate["closed_form_search"]["completed"]
assert Path(pf.__file__).resolve() == REPO_ROOT / "pepflow/__init__.py"
for relative, expected in certificate["certificate_provenance"][
    "source_hashes"
].items():
    source = (notebook_dir / relative).resolve()
    assert source.is_relative_to(notebook_dir)
    assert hashlib.sha256(source.read_bytes()).hexdigest() == expected
assert json.loads(certificate["params_json"]) == {"L": 1, "R": 1}
assert certificate["N"] == N_int
basis = list(ctx.basis_vectors())
labels = [str(v) for v in basis]
assert (
    labels
    == certificate["basis_vectors"]
    == certificate["S_row_names"]
    == certificate["S_col_names"]
)
assert [str(v) for v in ctx.basis_scalars()] == certificate["basis_scalars"]
records = entries_for(ctx, pb)
assert set(certificate["constraint_metadata"]) == {c.name for c, *_ in records}
weighted_terms = {}
for constraint, origin, owner, group in records:
    name = constraint.name
    meta = dict(
        origin=origin,
        owner=owner,
        group=group,
        kind="scalar",
        comparator=constraint.cmp.value,
        shape=[],
        relaxed=name in pb.relaxed_constraints,
    )
    assert meta == certificate["constraint_metadata"][name]
    value = certificate["named_dual_values"][name]
    if meta["relaxed"]:
        assert value is None
        continue
    assert value is not None and np.isfinite(value)
    residual = constraint.lhs - constraint.rhs
    if constraint.cmp.name in ("GE", "SEQ"):
        residual = -residual
    weighted_terms[name] = float(value) * residual
tau_name = certificate["tau_name"]
assert tau_name == certificate["normalization"]["tau_name"] == "initial_condition"
assert abs(certificate["named_dual_values"][tau_name] - certificate["tau_sol"]) <= 1e-6
assert certificate["normalization"]["bound_value"] == certificate["opt_value"]
assert abs(certificate["opt_value"] - 4 / N_int**2) <= 1e-5
checks, identity_residual = check_saved(
    ctx, pb, certificate, params_sp, certificate["opt_value"]
)
assert checks["passed"]
S_array = np.asarray(certificate["S_matrix"], float)
assert np.all(np.isfinite(S_array)) and np.allclose(
    S_array, S_array.T, atol=1e-6, rtol=0
)
assert np.linalg.eigvalsh(S_array).min() >= -1e-6
D = np.asarray(certificate["numerical_decomposition"]["D"], float)
E = np.asarray(certificate["numerical_decomposition"]["ell_coords"], float)
assert certificate["numerical_decomposition"]["basis_labels"] == labels
assert D.shape == (len(E), len(E)) and E.shape[1] == len(basis)
assert np.all(np.isfinite(D)) and np.all(np.isfinite(E))
assert np.allclose(E.T @ D @ E, S_array, atol=1e-4, rtol=1e-5)
certificate_checked = True
# END CERTIFICATE CHECK

# BEGIN DECOMPOSITION
# The failed analytic S guess is not used. Retain the complete numerical LDL
# together as one PSD boundary block, including all small factor contributions.
ell = [sum((float(c) * v for c, v in zip(row, basis)), pf.Vector.zero()) for row in E]
S_scalar = sum(
    (float(D[i, j]) * ell[i] * ell[j] for i, j in np.ndindex(D.shape)), pf.Scalar.zero()
)
S_piece_terms = {"complete_S": S_scalar}
decomposition_residual = (
    np.asarray(pm.eval_scalar(S_scalar).inner_prod_coords, float) - S_array
)
assert np.max(np.abs(decomposition_residual)) <= 1e-5
S_assignment = {"complete_S": "boundary"}
# END DECOMPOSITION

# BEGIN GROUPING
grouping_checked = False
rank_tolerance = 1e-4
rank_left, rank_right = 1, 1
group_terms = {name: term for name, term in weighted_terms.items() if name != tau_name}
term_assignment = {}
for name in group_terms:
    if name == f"A monotone:x_{N_int},x_star":
        term_assignment[name] = "boundary"
    elif name.startswith("A monotone:"):
        first, second = name.split(":")[1].split(",")
        k = int(first.split("_")[1])
        assert second == f"x_{k + 1}"
        term_assignment[name] = k
    elif name == "A Lipschitz:x_0,x_1":
        term_assignment[name] = 0
    elif name.startswith("A Lipschitz:"):
        first, second = name.split(":")[1].split(",")
        k = int(first.split("_")[1])
        assert second == f"x_{2 * k - 1}/2"
        term_assignment[name] = k - 1
    else:
        raise ValueError(f"Unassigned contribution: {name}")
assert set(term_assignment) == set(group_terms)
lyap = [pf.Scalar.zero()]
partial_sum = pf.Scalar.zero()
for step in range(N_int):
    partial_sum += sum(
        (
            group_terms[name]
            for name, target in term_assignment.items()
            if target == step
        ),
        pf.Scalar.zero(),
    )
    partial_sum -= sum(
        (
            S_piece_terms[name]
            for name, target in S_assignment.items()
            if target == step
        ),
        pf.Scalar.zero(),
    )
    lyap.append(partial_sum)
ranks, singular_values = [], []
for k, Vk in enumerate(lyap):
    matrix = np.asarray(pm.eval_scalar(Vk).inner_prod_coords, float)
    singular = np.linalg.svd(matrix, compute_uv=False)
    rank = int(np.sum(singular > rank_tolerance))
    ranks.append(rank)
    singular_values.append(singular.tolist())
    print(f"rank V_{k}: {rank}")
    if k == 0:
        print()
print(
    "Interior rank is constant at this N:",
    len(set(ranks[rank_left : N_int + 1 - rank_right])) == 1,
    "boundary exclusions:",
    (rank_left, rank_right),
)
boundary_names = [name for name, step in term_assignment.items() if step == "boundary"]
boundary_S = [name for name, step in S_assignment.items() if step == "boundary"]
assert len(boundary_names) <= 1 and len(boundary_S) <= 1
leftover = (
    sum((group_terms[name] for name in boundary_names), pf.Scalar.zero()) - S_scalar
)
coverage_diff = (
    lyap[N_int] + leftover - (sum(group_terms.values(), pf.Scalar.zero()) - S_scalar)
)
coverage_residual = pm.eval_scalar(coverage_diff)
for coords in (
    coverage_residual.inner_prod_coords,
    coverage_residual.func_coords,
    coverage_residual.offset,
):
    assert np.max(np.abs(np.asarray(coords, float)), initial=0) <= 1e-5
for piece in S_piece_terms.values():
    evaluated = pm.eval_scalar(piece)
    assert (
        np.max(np.abs(evaluated.func_coords), initial=0) <= 1e-5
        and abs(evaluated.offset) <= 1e-5
    )
    assert (
        np.linalg.eigvalsh(np.asarray(evaluated.inner_prod_coords, float)).min()
        >= -1e-6
    )
for k in range(N_int):
    increment = sum(
        (group_terms[name] for name, step in term_assignment.items() if step == k),
        pf.Scalar.zero(),
    )
    change = pm.eval_scalar(lyap[k + 1] - lyap[k] - increment)
    for coords in (change.inner_prod_coords, change.func_coords, change.offset):
        assert np.max(np.abs(np.asarray(coords, float)), initial=0) <= 1e-5
    # All included terms are nonnegative multiples of residuals <= 0,
    # hence the chosen convention gives V_{k+1} <= V_k numerically.
    assert all(
        certificate["named_dual_values"][name] >= -1e-6
        for name, step in term_assignment.items()
        if step == k
    )
grouping_checked = True
# END GROUPING

observation = dict(
    N=N_int,
    certificate_id=certificate["certificate_id"],
    certificate_path=str(certificate_path),
    recipe_id="adjacent_full_plus_lip_complete_S_boundary",
    rank_profile=ranks,
    singular_values=singular_values,
    rank_convention={
        "tolerance": 1e-4,
        "scaling": "absolute, unscaled original basis",
        "coordinate_order": "setup basis order",
    },
    rank_credible=all(
        not any(0.5e-4 <= s <= 2e-4 for s in singular_values[k])
        for k in range(1, N_int)
    ),
    certificate_checked=certificate_checked,
    grouping_checked=grouping_checked,
    term_assignment=term_assignment,
    S_assignment=S_assignment,
    certificate_residuals=checks["residuals"],
)
(notebook_dir / f"supplementary/b3-observation-N{N_int}.json").write_text(
    json.dumps(observation, indent=2)
)
print(
    "Observation",
    json.dumps(
        {
            key: value
            for key, value in observation.items()
            if key not in ("singular_values", "term_assignment")
        }
    ),
)
