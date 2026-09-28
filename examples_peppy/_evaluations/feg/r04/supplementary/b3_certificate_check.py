# This saved notebook fragment shares its caller's execution namespace.
# These names are supplied by the notebook cells or serialized proof source.
# ty: ignore[unresolved-reference]
# ruff: noqa: F821

"""Rebuild and verify the selected complete certificate without solving."""

import hashlib
import json
from pathlib import Path

import numpy as np
import sympy as sp

# local helper resolved by the notebook runtime path
from certificate import digest, inventory, verify  # ty: ignore[unresolved-import]
from feg_setup import get_pep_setup

import pepflow as pf

notebook_dir = Path.cwd().resolve()
N_int = certificate["N_verify"]
params_sp: dict[str, pf.NUMERICAL_TYPE] = {"L": sp.S.One, "R": sp.S.One}
assert json.loads(certificate["params_json"]) == {"L": 1, "R": 1}
assert certificate["certificate_id"] == digest(certificate)
assert certificate["closed_form_search"]["completed"]
for relative, expected in certificate["certificate_provenance"][
    "source_hashes"
].items():
    assert (
        hashlib.sha256((notebook_dir / relative).read_bytes()).hexdigest() == expected
    )
assert (
    Path(pf.__file__).resolve()
    == notebook_dir / "supplementary/approved/pepflow/__init__.py"
)
ctx, pb, obj = get_pep_setup(N_int, params_sp)
pb.set_relaxed_constraints(certificate["relaxed_constraints"])
pm = pf.ExpressionManager(ctx, resolve_parameters=params_sp)
records = inventory(ctx, pb, obj)
basis = ctx.basis_vectors()
basis_labels = [str(v) for v in basis]
assert (
    basis_labels
    == certificate["basis_vectors"]
    == certificate["S_row_names"]
    == certificate["S_col_names"]
)
assert [str(v) for v in ctx.basis_scalars()] == certificate["basis_scalars"]
assert set(certificate["named_dual_values"]) == {c.name for c, *_ in records}
weighted_terms, interpolation_terms, extra_terms, extra_duals = {}, {}, {}, {}
for c, origin, owner, group in records:
    assert isinstance(c, pf.ScalarConstraint)
    expected = dict(
        origin=origin,
        owner=owner,
        group=group,
        kind="scalar",
        comparator=c.cmp.value,
        shape=[],
        relaxed=c.name in pb.relaxed_constraints,
    )
    assert certificate["constraint_metadata"][c.name] == expected
    val = certificate["named_dual_values"][c.name]
    if expected["relaxed"]:
        assert val is None
        continue
    assert val is not None and np.isfinite(val) and val >= -1e-6
    assert c.cmp.name == "LE"
    term = float(val) * (c.lhs - c.rhs)
    weighted_terms[c.name] = term
    if origin == "interpolation":
        interpolation_terms[c.name] = term
    elif c.name != certificate["tau_name"]:
        extra_terms[c.name] = term
        extra_duals[c.name] = val
assert not extra_terms
assert (
    certificate["tau_name"]
    == certificate["normalization"]["tau_name"]
    == "initial_condition"
)
assert certificate["tau_sol"] == certificate["named_dual_values"]["initial_condition"]
assert certificate["normalization"]["bound_value"] == certificate["opt_value"]
certificate_checks = verify(certificate, ctx, pb, obj)
assert certificate_checks["passed"]
certificate_checked = True
S_array = np.asarray(certificate["S_matrix"])
S_scalar = sum(
    (float(S_array[i, j]) * basis[i] * basis[j] for i, j in np.ndindex(S_array.shape)),
    pf.Scalar.zero(),
)
tol = certificate_checks["tolerances"]
print("Certificate reconstructed and checked:", certificate_checks["residuals"])
