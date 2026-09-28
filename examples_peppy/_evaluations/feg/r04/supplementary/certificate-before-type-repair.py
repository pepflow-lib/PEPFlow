"""Attempt-owned numerical certificate acquisition and reconstruction."""

import hashlib
import json
import uuid
from importlib.metadata import version
from pathlib import Path

import numpy as np
import sympy as sp
from feg_setup import get_pep_setup

import pepflow as pf
from pepflow.lyapunov_utils import ldl_decompose_with_reversed_basis
from pepflow.utils import Comparator

ROOT = Path(__file__).resolve().parents[2]
PARAMS = {"L": sp.S.One, "R": sp.S.One}
KEYS = (
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


def inventory(ctx, pb, op):
    entries = [(c, "initial", None, None) for c in pb.init_conditions]
    groups = ctx.get_constraint_data(op)
    entries += [
        (c, "interpolation", str(op), str(group))
        for group, cs in groups.sc_dict.items()
        for c in cs
    ]
    assert (
        not groups.psd_dict
        and len(ctx.oper_to_duplets) == 1
        and not ctx.func_to_triplets
    )
    return entries


def source_hashes():
    files = json.loads((ROOT / "supplementary/approved/allowlist.json").read_text())[
        "exact_read_files"
    ]
    paths = [
        Path(p)
        for p in files
        if Path(p).parent == ROOT / "supplementary/approved/pepflow"
    ]
    paths += [ROOT / "feg_setup.py", Path(__file__).resolve()]
    return {
        str(p.relative_to(ROOT)).replace("\\", "/"): hashlib.sha256(
            p.read_bytes()
        ).hexdigest()
        for p in paths
    }


def acquire(n, relaxed=(), dense_value=None):
    hashes = source_hashes()
    ctx, pb, op = get_pep_setup(n, PARAMS)
    pb.set_relaxed_constraints(list(relaxed))
    entries = inventory(ctx, pb, op)
    constraints = [c for c, *_ in entries if c.name not in relaxed]
    solver = pf.CVXPrimalSolver(
        perf_metric=pb.performance_metric, constraints=constraints, context=ctx
    )
    problem = solver.build_problem(resolve_parameters=PARAMS)
    value = problem.solve(solver="CLARABEL")
    result = pf.PEPResult(
        opt_value=value,
        dual_var_manager=solver.dual_var_manager,
        pep_type=pf.PEPType.PRIMAL,
        solver_status=problem.status,
        context=ctx,
    )
    if problem.status != "optimal":
        raise RuntimeError(f"Solver status {problem.status}")
    S = result.get_gram_dual_matrix()
    named, meta = {}, {}
    for c, origin, owner, group in entries:
        assert isinstance(c, pf.ScalarConstraint)
        dropped = c.name in relaxed
        val = result.get_dual_value(c.name)
        assert dropped or val is not None
        named[c.name] = None if dropped else float(val)
        meta[c.name] = dict(
            origin=origin,
            owner=owner,
            group=group,
            kind="scalar",
            comparator=c.cmp.value,
            shape=[],
            relaxed=dropped,
        )
    lamb = result.get_scalar_constraint_dual_value_in_numpy(op)
    assert isinstance(lamb, dict)
    displays = {
        g: dict(
            matrix=np.nan_to_num(v.matrix).tolist(),
            row_names=list(v.row_names),
            col_names=list(v.col_names),
        )
        for g, v in lamb.items()
    }
    basis = ctx.basis_vectors()
    pm = pf.ExpressionManager(ctx, resolve_parameters=PARAMS)
    D, ell = ldl_decompose_with_reversed_basis(S, basis, print_output=False)
    E = np.array([pm.eval_vector(v).coords for v in ell], dtype=float)
    b1 = json.loads((ROOT / "state/feg_b1.json").read_text())
    data = dict(**b1)
    data.update(
        N=n,
        N_verify=n,
        opt_value=float(value),
        tau_sol=float(named["initial_condition"]),
        tau_name="initial_condition",
        relaxed_constraints=list(relaxed),
        S_matrix=np.asarray(S.matrix, dtype=float).tolist(),
        S_row_names=list(S.row_names),
        S_col_names=list(S.col_names),
        basis_vectors=[str(v) for v in basis],
        basis_scalars=[str(v) for v in ctx.basis_scalars()],
        named_dual_values=named,
        constraint_metadata=meta,
        lambda_groups=displays,
        normalization=dict(
            tau_name="initial_condition",
            initial_condition=b1["initial_condition"],
            performance_metric=b1["performance_metric"],
            bound_value=float(value),
            bound_formula=b1["conjectured_rate"],
        ),
        certificate_provenance=dict(
            solve_id=str(uuid.uuid4()),
            pep_type="primal",
            solver_status=problem.status,
            source_hashes=hashes,
            solver=dict(
                api="CVXPrimalSolver.build_problem",
                cvxpy_version=version("cvxpy"),
                effective_name="CLARABEL",
                settings={},
            ),
        ),
        numerical_decomposition=dict(
            method="reverse_ldl",
            D=np.asarray(D).tolist(),
            ell_coords=E.tolist(),
            basis_labels=[str(v) for v in basis],
        ),
    )
    data["numerical_checks"] = verify(
        data, ctx, pb, op, float(value) if dense_value is None else dense_value
    )
    data["numerical_certificate_verified"] = data["numerical_checks"]["passed"]
    data["certificate_id"] = digest(data)
    assert hashes == source_hashes()
    return data


def digest(data):
    return hashlib.sha256(
        json.dumps(
            {key: data[key] for key in KEYS},
            sort_keys=True,
            separators=(",", ":"),
            allow_nan=False,
        ).encode()
    ).hexdigest()


def verify(data, ctx=None, pb=None, op=None, dense_value=None):
    if ctx is None:
        ctx, pb, op = get_pep_setup(data["N_verify"], PARAMS)
    assert pb is not None and op is not None
    ctx.set_as_current()
    entries = inventory(ctx, pb, op)
    assert set(data["constraint_metadata"]) == {c.name for c, *_ in entries}
    assert set(data["named_dual_values"]) == set(data["constraint_metadata"])
    assert data["basis_vectors"] == [str(v) for v in ctx.basis_vectors()]
    pm = pf.ExpressionManager(ctx, resolve_parameters=PARAMS)
    weighted = pf.Scalar.zero()
    ineq = []
    for c, *_ in entries:
        val = data["named_dual_values"][c.name]
        if data["constraint_metadata"][c.name]["relaxed"]:
            assert val is None
            continue
        assert val is not None and np.isfinite(val)
        residual = c.lhs - c.rhs
        if c.cmp in (Comparator.GE, Comparator.SEQ):
            residual = -residual
        weighted += float(val) * (pf.Scalar.zero() + residual)
        if c.cmp != Comparator.EQ:
            ineq.append(float(val))
    E = np.asarray(data["numerical_decomposition"]["ell_coords"])
    D = np.asarray(data["numerical_decomposition"]["D"])
    S = np.asarray(data["S_matrix"])
    basis = ctx.basis_vectors()
    ell = [
        sum((float(a) * v for a, v in zip(row, basis)), pf.Vector.zero()) for row in E
    ]
    square = sum(
        (float(D[i, j]) * ell[i] * ell[j] for i, j in np.ndindex(D.shape)),
        pf.Scalar.zero(),
    )
    checked = pm.eval_scalar(
        pb.performance_metric - float(data["opt_value"]) - weighted + square
    )

    def maxabs(x):
        return float(np.max(np.abs(np.asarray(x, dtype=float)), initial=0))

    tol = dict(
        identity_atol=1e-5,
        identity_rtol=0.0,
        reconstruction_atol=1e-4,
        reconstruction_rtol=1e-5,
        dual_tol=1e-6,
        psd_tol=1e-6,
        dense_opt_atol=1e-5,
    )
    res = dict(
        identity_gram_max_abs=maxabs(checked.inner_prod_coords),
        identity_func_max_abs=maxabs(checked.func_coords),
        identity_offset_abs=maxabs(checked.offset),
        S_reconstruction_max_abs=maxabs(E.T @ D @ E - S),
        dense_relaxed_gap=abs(
            data["opt_value"]
            - (data["opt_value"] if dense_value is None else dense_value)
        ),
        minimum_scalar_inequality_dual=min(ineq, default=0),
        minimum_S_eigenvalue=float(np.linalg.eigvalsh((S + S.T) / 2).min()),
        minimum_matrix_inequality_eigenvalue=0.0,
    )
    passed = (
        data["certificate_provenance"]["solver_status"] == "optimal"
        and all(
            res[k] <= tol["identity_atol"]
            for k in (
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
        and res["dense_relaxed_gap"] < tol["dense_opt_atol"]
        and res["minimum_scalar_inequality_dual"] >= -tol["dual_tol"]
        and res["minimum_S_eigenvalue"] >= -tol["psd_tol"]
        and np.allclose(S, S.T, atol=tol["psd_tol"], rtol=0)
    )
    return dict(tolerances=tol, residuals=res, passed=bool(passed))
