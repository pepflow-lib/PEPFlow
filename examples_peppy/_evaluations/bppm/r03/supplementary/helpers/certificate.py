"""Capture and validate complete scalar-constraint certificates in this attempt."""

import hashlib
import json
import uuid

import numpy as np
from runtime import APPROVED, ROOT, solve_builder

import pepflow as pf
from pepflow.utils import Comparator


def inventory(ctx, pb):
    rows = [(c, "initial", None, None) for c in pb.init_conditions]
    for owner in ctx.func_to_triplets:
        groups = ctx.get_constraint_data(owner)
        rows.extend(
            (c, "interpolation", str(owner), str(group))
            for group, constraints in groups.sc_dict.items()
            for c in constraints
        )
        rows.extend(
            (c, "interpolation", str(owner), str(group))
            for group, c in groups.psd_dict.items()
        )
    return rows


def max_abs(value):
    return float(np.max(np.abs(np.asarray(value, dtype=float)), initial=0.0))


def capture(ctx, pb, obj, params, dense_opt=None):
    paths = [
        ROOT / "bppm_setup.py",
        ROOT / "supplementary/helpers/runtime.py",
        ROOT / "supplementary/helpers/certificate.py",
    ]
    allowed = json.loads((APPROVED / "allowlist.json").read_text())["exact_read_files"]
    paths += [
        __import__("pathlib").Path(p)
        for p in allowed
        if "/pepflow/" in p.replace("\\", "/") and p.endswith(".py")
    ]
    hashes = {
        str(p.relative_to(ROOT)): hashlib.sha256(p.read_bytes()).hexdigest()
        for p in paths
    }
    result, info = solve_builder(ctx, pb, params)
    rows = inventory(ctx, pb)
    values, metadata = {}, {}
    for c, origin, owner, group in rows:
        assert isinstance(c, pf.ScalarConstraint), (
            "This capture handles scalar-only inventory."
        )
        dropped = c.name in pb.relaxed_constraints
        value = result.get_dual_value(c.name)
        assert dropped or value is not None
        values[c.name] = None if dropped else float(value)
        metadata[c.name] = dict(
            origin=origin,
            owner=owner,
            group=group,
            kind="scalar",
            comparator=c.cmp.value,
            shape=[],
            relaxed=dropped,
        )
    S = result.get_gram_dual_matrix()
    array = np.asarray(S.matrix, dtype=float)
    eigenvalues, eigenvectors = np.linalg.eigh((array + array.T) / 2)
    decomposition = dict(
        method="direct",
        D=np.diag(eigenvalues).tolist(),
        ell_coords=eigenvectors.T.tolist(),
        basis_labels=[str(v) for v in ctx.basis_vectors()],
    )
    lamb = result.get_scalar_constraint_dual_value_in_numpy(obj)
    assert isinstance(lamb, pf.MatrixWithNames)
    data = dict(
        N=int(ctx.name.split("_")[-1]),
        opt_value=float(result.opt_value),
        tau_sol=values["initial_condition"],
        tau_name="initial_condition",
        named_dual_values=values,
        constraint_metadata=metadata,
        S_matrix=array.tolist(),
        S_row_names=list(S.row_names),
        S_col_names=list(S.col_names),
        basis_vectors=[str(v) for v in ctx.basis_vectors()],
        basis_scalars=[str(v) for v in ctx.basis_scalars()],
        lambda_matrix=np.asarray(lamb.matrix, dtype=float).tolist(),
        lambda_row_names=list(lamb.row_names),
        lambda_col_names=list(lamb.col_names),
        relaxed_constraints=list(pb.relaxed_constraints),
        numerical_decomposition=decomposition,
        certificate_provenance=dict(
            solve_id=str(uuid.uuid4()),
            pep_type="primal",
            solver_status=result.solver_status,
            source_hashes=hashes,
            solver=info,
        ),
    )
    data["numerical_checks"] = verify(
        ctx, pb, params, data, data["opt_value"] if dense_opt is None else dense_opt
    )
    for relative, digest in hashes.items():
        assert hashlib.sha256((ROOT / relative).read_bytes()).hexdigest() == digest
    return data


def verify(ctx, pb, params, data, dense_opt):
    ctx.set_as_current()
    assert data["basis_vectors"] == [str(v) for v in ctx.basis_vectors()]
    assert data["basis_scalars"] == [str(v) for v in ctx.basis_scalars()]
    rows = inventory(ctx, pb)
    assert set(data["named_dual_values"]) == {c.name for c, *_ in rows}
    pm = pf.ExpressionManager(ctx, resolve_parameters=params)
    weighted = pf.Scalar.zero()
    duals = []
    for c, *_ in rows:
        value = data["named_dual_values"][c.name]
        if c.name in data["relaxed_constraints"]:
            assert value is None
            continue
        assert value is not None and np.isfinite(value)
        residual = c.lhs - c.rhs
        if c.cmp in (Comparator.GE, Comparator.SEQ):
            residual = -residual
        weighted += value * residual
        if c.cmp != Comparator.EQ:
            duals.append(value)
    basis = ctx.basis_vectors()
    S = np.array(data["S_matrix"])
    S_numeric = sum(
        (float(S[i, j]) * basis[i] * basis[j] for i, j in np.ndindex(S.shape)),
        pf.Scalar.zero(),
    )
    checked = pm.eval_scalar(
        pb.performance_metric - data["opt_value"] - weighted + S_numeric
    )
    E = np.array(data["numerical_decomposition"]["ell_coords"])
    D = np.array(data["numerical_decomposition"]["D"])
    residuals = dict(
        identity_gram_max_abs=max_abs(checked.inner_prod_coords),
        identity_func_max_abs=max_abs(checked.func_coords),
        identity_offset_abs=max_abs(checked.offset),
        S_reconstruction_max_abs=max_abs(E.T @ D @ E - S),
        dense_relaxed_gap=abs(dense_opt - data["opt_value"]),
        minimum_scalar_inequality_dual=min(duals, default=0.0),
        minimum_S_eigenvalue=float(np.linalg.eigvalsh((S + S.T) / 2).min()),
        minimum_matrix_inequality_eigenvalue=0.0,
    )
    tol = json.loads((APPROVED / "settings.json").read_text())["tolerances"]
    passed = (
        data["certificate_provenance"]["solver_status"] == "optimal"
        and all(
            residuals[key] <= tol["identity_atol"]
            for key in (
                "identity_gram_max_abs",
                "identity_func_max_abs",
                "identity_offset_abs",
            )
        )
        and np.allclose(
            E.T @ D @ E,
            S,
            atol=tol["reconstruction_atol"],
            rtol=tol["reconstruction_rtol"],
        )
        and np.allclose(S, S.T, atol=tol["psd_tol"], rtol=0)
        and residuals["dense_relaxed_gap"] < tol["dense_opt_atol"]
        and min(duals, default=0.0) >= -tol["dual_tol"]
        and residuals["minimum_S_eigenvalue"] >= -tol["psd_tol"]
    )
    assert passed, residuals
    return dict(passed=bool(passed), tolerances=tol, residuals=residuals)
