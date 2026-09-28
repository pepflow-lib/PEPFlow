"""B2 certificate acquisition and replay on the approved PEPFlow coordinates."""

import hashlib
import json
import uuid
from fractions import Fraction
from pathlib import Path

import numpy as np
import pgm_setup as setup

# local helper resolved by the notebook runtime path
from runtime import ROOT, solve_selected  # ty: ignore[unresolved-import]

import pepflow as pf
from pepflow.utils import Comparator

TOL = dict(
    identity_atol=1e-5,
    identity_rtol=0.0,
    reconstruction_atol=1e-4,
    reconstruction_rtol=1e-5,
    dual_tol=1e-6,
    psd_tol=1e-6,
    dense_opt_atol=1e-5,
)


def inventory(ctx, pb):
    entries = [(c, "initial", None, None) for c in pb.init_conditions]
    for owner in ctx.func_to_triplets:
        groups = ctx.get_constraint_data(owner)
        entries.extend(
            (c, "interpolation", str(owner), str(group))
            for group, constraints in groups.sc_dict.items()
            for c in constraints
        )
        entries.extend(
            (c, "interpolation", str(owner), str(group))
            for group, c in groups.psd_dict.items()
        )
    return entries


def acquire(n, relaxed=()):
    ctx, pb, obj = setup.get_pep_setup(n, {"L": 1, "R": 1})
    if relaxed:
        pb.set_relaxed_constraints(list(relaxed))
    result, log = solve_selected(ctx, pb, {"L": 1, "R": 1})
    entries = inventory(ctx, pb)
    metadata, duals = {}, {}
    for c, origin, owner, group in entries:
        scalar = isinstance(c, pf.ScalarConstraint)
        dropped = c.name in pb.relaxed_constraints
        value = result.get_dual_value(c.name)
        assert dropped or value is not None
        metadata[c.name] = dict(
            origin=origin,
            owner=owner,
            group=group,
            kind="scalar" if scalar else "psd",
            comparator=c.cmp.value,
            shape=[] if scalar else list(np.asarray(c.lhs - c.rhs).shape),
            relaxed=dropped,
        )
        duals[c.name] = (
            None if dropped else float(value) if scalar else np.asarray(value).tolist()
        )
    sm = result.get_gram_dual_matrix()
    primary = result.get_scalar_constraint_dual_value_in_numpy(obj)
    if isinstance(primary, dict):
        ld = {
            "lambda_groups": {
                str(k): dict(
                    matrix=np.asarray(v.matrix).tolist(),
                    row_names=list(v.row_names),
                    col_names=list(v.col_names),
                )
                for k, v in primary.items()
            }
        }
    else:
        ld = dict(
            lambda_matrix=np.asarray(primary.matrix).tolist(),
            lambda_row_names=list(primary.row_names),
            lambda_col_names=list(primary.col_names),
        )
    allowed = json.loads((ROOT / "supplementary/approved/allowlist.json").read_text())[
        "exact_read_files"
    ]
    paths = [
        Path(p)
        for p in allowed
        if "/pepflow/" in p.replace("\\", "/") and p.endswith(".py")
    ]
    paths += [
        ROOT / "pgm_setup.py",
        ROOT / "supplementary/helpers/runtime.py",
        Path(__file__),
    ]
    hashes = {
        str(p.relative_to(ROOT)): hashlib.sha256(p.read_bytes()).hexdigest()
        for p in paths
    }
    data = dict(
        **ld,
        N=n,
        N_verify=n,
        params_json='{"L": 1, "R": 1}',
        opt_value=float(result.opt_value),
        tau_sol=float(result.get_dual_value("initial_condition")),
        tau_name="initial_condition",
        relaxed_constraints=list(pb.relaxed_constraints),
        S_matrix=np.asarray(sm.matrix, dtype=float).tolist(),
        S_row_names=list(sm.row_names),
        S_col_names=list(sm.col_names),
        basis_vectors=[str(v) for v in ctx.basis_vectors()],
        basis_scalars=[str(v) for v in ctx.basis_scalars()],
        named_dual_values=duals,
        constraint_metadata=metadata,
        normalization=dict(
            tau_name="initial_condition",
            initial_condition="||x_0-x_star||^2 <= R^2",
            performance_metric="h(x_N)-h(x_star)",
            bound_value=float(result.opt_value),
            bound_formula="L*R**2/(4*N)",
        ),
        certificate_provenance=dict(
            solve_id=str(uuid.uuid4()),
            pep_type="primal",
            solver_status=result.solver_status,
            source_hashes=hashes,
            solver=dict(api="CVXPrimalSolver.build_problem", log=log),
        ),
    )
    return data, ctx, pb, result


def residual_of(c):
    residual = c.lhs - c.rhs
    return -residual if c.cmp in (Comparator.GE, Comparator.SEQ) else residual


def verify(data, dense_value, decomposition=None):
    ctx, pb, _ = setup.get_pep_setup(data["N"], json.loads(data["params_json"]))
    if data["relaxed_constraints"]:
        pb.set_relaxed_constraints(data["relaxed_constraints"])
    for func in ctx.func_to_triplets:
        func.get_interpolation_constraints(ctx)
    entries = inventory(ctx, pb)
    assert set(data["constraint_metadata"]) == {c.name for c, *_ in entries}
    assert data["basis_vectors"] == [str(v) for v in ctx.basis_vectors()]
    assert data["basis_scalars"] == [str(v) for v in ctx.basis_scalars()]
    pm = pf.ExpressionManager(ctx, resolve_parameters={"L": 1, "R": 1})
    weighted = pf.Scalar.zero()
    vals = []
    for c, *_ in entries:
        value = data["named_dual_values"][c.name]
        if c.name in pb.relaxed_constraints:
            assert value is None
            continue
        assert isinstance(c, pf.ScalarConstraint), (
            "This PGM sample has only scalar constraints"
        )
        weighted += float(value) * (pf.Scalar.zero() + residual_of(c))
        if c.cmp != Comparator.EQ:
            vals.append(float(value))
    basis = ctx.basis_vectors()
    S = np.asarray(data["S_matrix"], dtype=float)
    S_scalar = sum(
        (float(S[i, j]) * basis[i] * basis[j] for i, j in np.ndindex(S.shape)),
        pf.Scalar.zero(),
    )
    checked = pm.eval_scalar(
        pb.performance_metric - data["opt_value"] - weighted + S_scalar
    )
    ma = lambda v: float(np.max(np.abs(np.asarray(v, dtype=float)), initial=0.0))  # noqa: E731 - retain the archived notebook helper
    reconstruction = (
        S
        if decomposition is None
        else np.asarray(decomposition["ell_coords"]).T
        @ np.asarray(decomposition["D"])
        @ np.asarray(decomposition["ell_coords"])
    )
    residuals = dict(
        identity_gram_max_abs=ma(checked.inner_prod_coords),
        identity_func_max_abs=ma(checked.func_coords),
        identity_offset_abs=ma(checked.offset),
        S_reconstruction_max_abs=ma(reconstruction - S),
        dense_relaxed_gap=abs(data["opt_value"] - dense_value),
        minimum_scalar_inequality_dual=min(vals, default=0.0),
        minimum_S_eigenvalue=float(np.linalg.eigvalsh((S + S.T) / 2).min()),
        minimum_matrix_inequality_eigenvalue=0.0,
        candidate_rate_gap=abs(data["opt_value"] - 1 / (4 * data["N"])),
    )
    passed = (
        data["certificate_provenance"]["solver_status"] == "optimal"
        and np.all(np.isfinite(S))
        and np.allclose(S, S.T, atol=1e-6, rtol=0)
    )
    passed = passed and all(
        residuals[k] <= 1e-5
        for k in (
            "identity_gram_max_abs",
            "identity_func_max_abs",
            "identity_offset_abs",
            "dense_relaxed_gap",
            "candidate_rate_gap",
        )
    )
    passed = (
        passed
        and np.allclose(reconstruction, S, atol=1e-4, rtol=1e-5)
        and residuals["minimum_scalar_inequality_dual"] >= -1e-6
        and residuals["minimum_S_eigenvalue"] >= -1e-6
    )
    return (
        dict(tolerances=TOL, residuals=residuals, passed=bool(passed)),
        ctx,
        pb,
        checked,
    )


def summarize(data):
    print(
        "N",
        data["N"],
        "value",
        data["opt_value"],
        "status",
        data["certificate_provenance"]["solver_status"],
    )
    for name, value in data["named_dual_values"].items():
        if value is not None and abs(value) > 1e-6:
            print(name, round(value, 9), str(Fraction(value).limit_denominator(10000)))
    print("S eigenvalues", np.linalg.eigvalsh(data["S_matrix"]))
