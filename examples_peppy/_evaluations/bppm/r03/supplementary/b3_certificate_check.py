# This saved notebook fragment shares its caller's execution namespace.
# These names are supplied by the notebook cells or serialized proof source.
# ty: ignore[unresolved-reference]
# ruff: noqa: F821

import hashlib
import json

# local helper resolved by the notebook runtime path
import certificate as certificate_api  # ty: ignore[unresolved-import]
import numpy as np

import pepflow as pf

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
digest = hashlib.sha256(
    json.dumps(
        {key: certificate[key] for key in certificate_keys},
        sort_keys=True,
        separators=(",", ":"),
        allow_nan=False,
    ).encode()
).hexdigest()
assert digest == certificate["certificate_id"]
assert certificate["certificate_provenance"]["pep_type"] == "primal"
for relative, expected in certificate["certificate_provenance"][
    "source_hashes"
].items():
    source_path = (notebook_dir / relative).resolve()
    assert source_path.is_relative_to(notebook_dir)
    assert hashlib.sha256(source_path.read_bytes()).hexdigest() == expected
assert (
    __import__("pathlib").Path(pf.__file__).resolve()
    == REPO_ROOT / "pepflow/__init__.py"
)
assert N_int == certificate["N_verify"]
assert params_sp == json.loads(certificate["params_json"])
assert set(pb.relaxed_constraints) == set(certificate["relaxed_constraints"])
assert pb.ctx is ctx
basis = ctx.basis_vectors()
basis_labels = [str(v) for v in basis]
assert certificate["S_row_names"] == certificate["S_col_names"] == basis_labels
assert (
    certificate["normalization"]["tau_name"]
    == certificate["tau_name"]
    == "initial_condition"
)
assert certificate["normalization"]["initial_condition"] == "D_h(x_star,x_0)<=R"
assert certificate["normalization"]["performance_metric"] == "f(x_N)-f(x_star)"
assert certificate["normalization"]["bound_value"] == certificate["opt_value"]
assert certificate["named_dual_values"]["initial_condition"] == certificate["tau_sol"]
rows = certificate_api.inventory(ctx, pb)
assert len(rows) == len({c.name for c, *_ in rows})
assert set(certificate["constraint_metadata"]) == {c.name for c, *_ in rows}
weighted_terms = {}
extra_duals = {}
for c, origin, owner, group in rows:
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
    assert expected == certificate["constraint_metadata"][c.name]
    value = certificate["named_dual_values"][c.name]
    if value is not None:
        assert c.cmp.value == "LE"
        weighted_terms[c.name] = value * (c.lhs - c.rhs)
        if origin != "interpolation" and c.name != "initial_condition":
            extra_duals[c.name] = value
checks = certificate_api.verify(
    ctx, pb, params_sp, certificate, certificate["opt_value"]
)
assert certificate["closed_form_search"]["completed"]
assert (
    abs(certificate["opt_value"] - params_sp["R"] / (params_sp["alpha"] * N_int))
    <= 1e-5
)
pm = pf.ExpressionManager(ctx, resolve_parameters=params_sp)
S_array = np.asarray(certificate["S_matrix"], dtype=float)
S_scalar = sum(
    (float(S_array[i, j]) * basis[i] * basis[j] for i, j in np.ndindex(S_array.shape)),
    pf.Scalar.zero(),
)
tol = certificate["numerical_checks"]["tolerances"]
certificate_checked = True
