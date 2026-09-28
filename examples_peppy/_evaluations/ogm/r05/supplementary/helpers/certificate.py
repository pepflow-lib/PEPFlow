"""Capture and replay complete scalar OGM certificates using the approved API."""

import hashlib
import json
import uuid

import numpy as np
from runtime import NOTEBOOK_DIR, REPO_ROOT, solve_pep

import pepflow as pf
from pepflow.lyapunov_utils import ldl_decompose_with_reversed_basis

CERTIFICATE_KEYS = (
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


def digest_state(data):
    return hashlib.sha256(
        json.dumps(
            {key: data[key] for key in CERTIFICATE_KEYS},
            sort_keys=True,
            separators=(",", ":"),
            allow_nan=False,
        ).encode()
    ).hexdigest()


def source_hashes():
    allowlist = json.loads((REPO_ROOT / "allowlist.json").read_text())
    files = [
        NOTEBOOK_DIR / "ogm_setup.py",
        NOTEBOOK_DIR / "supplementary/helpers/runtime.py",
        NOTEBOOK_DIR / "supplementary/helpers/certificate.py",
    ]
    files += [
        REPO_ROOT / "pepflow" / __import__("pathlib").Path(p).name
        for p in allowlist["exact_read_files"]
        if __import__("pathlib").Path(p).parent == REPO_ROOT / "pepflow"
    ]
    return {
        str(p.relative_to(NOTEBOOK_DIR)): hashlib.sha256(p.read_bytes()).hexdigest()
        for p in files
    }


def inventory(ctx, pb):
    entries = [(c, "initial", None, None) for c in pb.init_conditions]
    assert not ctx.oper_to_duplets, "This OGM case has no operators"
    for owner in ctx.func_to_triplets:
        groups = ctx.get_constraint_data(owner)
        assert not groups.psd_dict, "This OGM case has only scalar interpolation"
        entries += [
            (c, "interpolation", str(owner), str(group))
            for group, cs in groups.sc_dict.items()
            for c in cs
        ]
    assert len({c.name for c, *_ in entries}) == len(entries)
    return entries


def scalar_coordinates(pm, scalar):
    value = pm.eval_scalar(pf.Scalar.zero() + scalar)
    return {
        "gram": np.asarray(value.inner_prod_coords, dtype=float).tolist(),
        "func": np.asarray(value.func_coords, dtype=float).tolist(),
        "offset": float(value.offset),
    }


def verify_certificate(ctx, pb, data, dense_value):
    """Check all coordinates and cone signs without another solve."""
    pm = pf.ExpressionManager(ctx, resolve_parameters=json.loads(data["params_json"]))
    basis = ctx.basis_vectors()
    assert [str(v) for v in basis] == data["basis_vectors"]
    assert [str(v) for v in ctx.basis_scalars()] == data["basis_scalars"]
    entries = inventory(ctx, pb)
    assert (
        {c.name for c, *_ in entries}
        == set(data["named_dual_values"])
        == set(data["constraint_metadata"])
    )
    assert set(pb.relaxed_constraints) == set(data["relaxed_constraints"])
    weighted = pf.Scalar.zero()
    duals = []
    for c, origin, owner, group in entries:
        meta = data["constraint_metadata"][c.name]
        assert meta == dict(
            origin=origin,
            owner=owner,
            group=group,
            kind="scalar",
            comparator=c.cmp.value,
            shape=[],
            relaxed=c.name in pb.relaxed_constraints,
        )
        value = data["named_dual_values"][c.name]
        if meta["relaxed"]:
            assert value is None
            continue
        assert value is not None and np.isfinite(value)
        residual = c.lhs - c.rhs
        if c.cmp in (pf.Comparator.GE, pf.Comparator.SEQ):
            residual = -residual
        weighted += value * (pf.Scalar.zero() + residual)
        if c.cmp != pf.Comparator.EQ:
            duals.append(value)
    S = np.asarray(data["S_matrix"], dtype=float)
    D = np.asarray(data["numerical_decomposition"]["D"], dtype=float)
    E = np.asarray(data["numerical_decomposition"]["ell_coords"], dtype=float)
    S_numeric = sum(
        (float(S[i, j]) * basis[i] * basis[j] for i, j in np.ndindex(S.shape)),
        pf.Scalar.zero(),
    )
    residual = scalar_coordinates(
        pm, pb.performance_metric - data["opt_value"] - weighted + S_numeric
    )

    def max_abs(a):
        return float(np.max(np.abs(a), initial=0))

    checks = dict(
        identity_gram_max_abs=max_abs(residual["gram"]),
        identity_func_max_abs=max_abs(residual["func"]),
        identity_offset_abs=abs(residual["offset"]),
        S_reconstruction_max_abs=max_abs(E.T @ D @ E - S),
        dense_relaxed_gap=abs(dense_value - data["opt_value"]),
        minimum_scalar_inequality_dual=min(duals, default=0),
        minimum_S_eigenvalue=float(np.linalg.eigvalsh(S).min()),
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
    passed = (
        data["certificate_provenance"]["solver_status"] == "optimal"
        and np.all(np.isfinite(S))
        and np.allclose(S, S.T, atol=1e-6, rtol=0)
        and all(
            checks[k] <= 1e-5
            for k in (
                "identity_gram_max_abs",
                "identity_func_max_abs",
                "identity_offset_abs",
            )
        )
        and np.allclose(E.T @ D @ E, S, atol=1e-4, rtol=1e-5)
        and checks["dense_relaxed_gap"] < 1e-5
        and checks["minimum_scalar_inequality_dual"] >= -1e-6
        and checks["minimum_S_eigenvalue"] >= -1e-6
    )
    return {
        "tolerances": tolerances,
        "residuals": checks,
        "passed": bool(passed),
    }, residual


def capture(N, relaxed=(), dense_value=None):
    from ogm_setup import get_pep_setup

    hashes_before = source_hashes()
    b1 = json.loads((NOTEBOOK_DIR / "state/ogm_b1.json").read_text())
    ctx, pb, obj = get_pep_setup(N, json.loads(b1["params_json"]))
    if relaxed:
        pb.set_relaxed_constraints(list(relaxed))
    result, calls = solve_pep(ctx, pb, obj, json.loads(b1["params_json"]))
    pm = pf.ExpressionManager(ctx, resolve_parameters=json.loads(b1["params_json"]))
    entries = inventory(ctx, pb)
    metadata, values, coordinates = {}, {}, {}
    for c, origin, owner, group in entries:
        assert isinstance(c, pf.ScalarConstraint)
        dropped = c.name in pb.relaxed_constraints
        value = result.get_dual_value(c.name)
        assert dropped or value is not None
        metadata[c.name] = dict(
            origin=origin,
            owner=owner,
            group=group,
            kind="scalar",
            comparator=c.cmp.value,
            shape=[],
            relaxed=dropped,
        )
        values[c.name] = None if dropped else float(value)
        residual = c.lhs - c.rhs
        if c.cmp in (pf.Comparator.GE, pf.Comparator.SEQ):
            residual = -residual
        coordinates[c.name] = scalar_coordinates(pm, residual)
    S_sol = result.get_gram_dual_matrix()
    basis = ctx.basis_vectors()
    D, ell = ldl_decompose_with_reversed_basis(S_sol, basis, print_output=False)
    E = np.asarray([pm.eval_vector(v).coords for v in ell], dtype=float)
    lamb = result.get_scalar_constraint_dual_value_in_numpy(obj)
    assert isinstance(lamb, pf.MatrixWithNames)
    data = {
        **b1,
        "N": int(N),
        "N_verify": int(N),
        "opt_value": float(result.opt_value),
        "tau_name": "initial_condition",
        "tau_sol": values["initial_condition"],
        "relaxed_constraints": list(relaxed),
        "named_dual_values": values,
        "constraint_metadata": metadata,
        "constraint_coordinates": coordinates,
        "lambda_matrix": np.asarray(lamb.matrix, dtype=float).tolist(),
        "lambda_row_names": list(lamb.row_names),
        "lambda_col_names": list(lamb.col_names),
        "S_matrix": np.asarray(S_sol.matrix, dtype=float).tolist(),
        "S_row_names": list(S_sol.row_names),
        "S_col_names": list(S_sol.col_names),
        "basis_vectors": [str(v) for v in basis],
        "basis_scalars": [str(v) for v in ctx.basis_scalars()],
        "numerical_decomposition": {
            "method": "reverse_ldl",
            "D": np.asarray(D, dtype=float).tolist(),
            "ell_coords": E.tolist(),
            "basis_labels": [str(v) for v in basis],
        },
        "certificate_provenance": {
            "solve_id": str(uuid.uuid4()),
            "pep_type": "primal",
            "solver_status": str(result.solver_status),
            "source_hashes": hashes_before,
            "solver": {"api": "CVXPrimalSolver.build_problem", "calls": calls},
        },
        "normalization": {
            "tau_name": "initial_condition",
            "initial_condition": b1["initial_condition"],
            "performance_metric": b1["performance_metric"],
            "bound_value": float(result.opt_value),
            "bound_formula": b1["conjectured_rate"],
        },
    }
    if dense_value is None:
        dense_value = data["opt_value"]
    checks, residual = verify_certificate(ctx, pb, data, dense_value)
    data.update(
        numerical_checks=checks,
        identity_residual_coordinates=residual,
        numerical_certificate_verified=checks["passed"],
        proof_valid=checks["passed"],
        S_decomp_type="ldl",
        lamb_code=None,
        S_code=None,
    )
    assert hashes_before == source_hashes()
    data["certificate_id"] = digest_state(data)
    return data
