"""Capture and replay a complete scalar-constraint operator certificate."""

import hashlib
import json
import uuid
from importlib.metadata import version

import cvxpy as cp
import numpy as np

import pepflow as pf
from pepflow.lyapunov_utils import ldl_decompose_with_reversed_basis


def inventory(ctx, pb):
    entries = [(c, "initial", None, None) for c in pb.init_conditions]
    for owner in [*ctx.func_to_triplets, *ctx.oper_to_duplets]:
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
    assert len({c.name for c, *_ in entries}) == len(entries)
    return entries


def capture(get_setup, n, params, dropped, source_hashes):
    ctx, pb, obj = get_setup(n, params)
    pb.set_relaxed_constraints(dropped)
    entries = inventory(ctx, pb)
    constraints = [c for c, *_ in entries if c.name not in dropped]
    solver = pf.CVXPrimalSolver(pb.performance_metric, constraints, ctx)
    problem = solver.build_problem(resolve_parameters=params)
    name, options, failure = "CLARABEL", {}, None
    try:
        value = problem.solve(solver=name, **options)
        if problem.status not in ["optimal", "optimal_inaccurate"]:
            raise RuntimeError(problem.status)
    except (cp.error.SolverError, RuntimeError) as exc:
        failure = str(exc)
        name, options = "SCS", {"eps": 1e-7, "max_iters": 200000}
        value = problem.solve(solver=name, **options)
    result = pf.PEPResult(
        opt_value=value,
        dual_var_manager=solver.dual_var_manager,
        pep_type=pf.PEPType.PRIMAL,
        solver_status=problem.status,
        context=ctx,
    )
    metadata, duals = {}, {}
    for c, origin, owner, group in entries:
        assert isinstance(c, pf.ScalarConstraint), (
            "Unexpected matrix constraint requires adaptation"
        )
        relaxed = c.name in dropped
        d = result.get_dual_value(c.name)
        assert relaxed or d is not None
        duals[c.name] = None if relaxed else float(d)
        metadata[c.name] = dict(
            origin=origin,
            owner=owner,
            group=group,
            kind="scalar",
            comparator=c.cmp.value,
            shape=[],
            relaxed=relaxed,
        )
    smat = result.get_gram_dual_matrix()
    basis = ctx.basis_vectors()
    pm = pf.ExpressionManager(ctx, resolve_parameters=params)
    diagonal, ell = ldl_decompose_with_reversed_basis(smat, basis, print_output=False)
    factors = np.asarray([pm.eval_vector(v).coords for v in ell], dtype=float)
    lambdas = result.get_scalar_constraint_dual_value_in_numpy(obj)
    assert isinstance(lambdas, dict)
    state = dict(
        N=n,
        N_verify=n,
        params_json=json.dumps(params),
        opt_value=float(value),
        tau_name="initial_condition",
        tau_sol=float(duals["initial_condition"]),
        relaxed_constraints=dropped,
        S_matrix=np.asarray(smat.matrix).tolist(),
        S_row_names=list(smat.row_names),
        S_col_names=list(smat.col_names),
        basis_vectors=[str(v) for v in basis],
        basis_scalars=[str(v) for v in ctx.basis_scalars()],
        named_dual_values=duals,
        constraint_metadata=metadata,
        numerical_decomposition=dict(
            method="reverse_ldl",
            D=np.asarray(diagonal).tolist(),
            ell_coords=factors.tolist(),
            basis_labels=[str(v) for v in basis],
        ),
        lambda_groups={
            str(k): dict(
                matrix=np.asarray(v.matrix).tolist(),
                row_names=list(v.row_names),
                col_names=list(v.col_names),
            )
            for k, v in lambdas.items()
        },
        normalization=dict(
            tau_name="initial_condition",
            initial_condition="||x_0-x_star||^2 <= R^2",
            performance_metric="||A(x_N)||^2",
            bound_value=float(value),
            bound_formula="4*L**2*R**2/N**2",
        ),
        certificate_provenance=dict(
            solve_id=str(uuid.uuid4()),
            pep_type="primal",
            solver_status=problem.status,
            source_hashes=source_hashes,
            solver=dict(
                api="CVXPrimalSolver.build_problem",
                cvxpy_version=version("cvxpy"),
                effective_name=name,
                settings=options,
                fallback_reason=failure,
            ),
        ),
    )
    return state


def verify_certificate(state, get_setup, dense_value):
    params = json.loads(state["params_json"])
    ctx, pb, _ = get_setup(state["N_verify"], params)
    basis = ctx.basis_vectors()
    assert [str(v) for v in basis] == state["basis_vectors"]
    assert [str(v) for v in ctx.basis_scalars()] == state["basis_scalars"]
    assert state["S_row_names"] == state["S_col_names"] == state["basis_vectors"]
    entries = inventory(ctx, pb)
    assert (
        {c.name for c, *_ in entries}
        == set(state["named_dual_values"])
        == set(state["constraint_metadata"])
    )
    pm = pf.ExpressionManager(ctx, resolve_parameters=params)
    weighted = pf.Scalar.zero()
    minimum_duals = []
    for c, origin, owner, group in entries:
        meta = state["constraint_metadata"][c.name]
        assert (
            meta["origin"],
            meta["owner"],
            meta["group"],
            meta["comparator"],
            meta["kind"],
        ) == (origin, owner, group, c.cmp.value, "scalar")
        value = state["named_dual_values"][c.name]
        if meta["relaxed"]:
            assert value is None and c.name in state["relaxed_constraints"]
            continue
        assert value is not None and np.isfinite(value)
        residual = c.lhs - c.rhs
        if c.cmp == pf.Comparator.GE:
            residual = -residual
        weighted += value * residual
        if c.cmp != pf.Comparator.EQ:
            minimum_duals.append(value)
    S = np.asarray(state["S_matrix"], dtype=float)
    D = np.asarray(state["numerical_decomposition"]["D"], dtype=float)
    E = np.asarray(state["numerical_decomposition"]["ell_coords"], dtype=float)
    ell = [
        sum((float(a) * v for a, v in zip(row, basis)), pf.Vector.zero()) for row in E
    ]
    S_numeric = sum(
        (float(D[i, j]) * ell[i] * ell[j] for i, j in np.ndindex(D.shape)),
        pf.Scalar.zero(),
    )
    diff = pb.performance_metric - state["opt_value"] - weighted + S_numeric
    checked = pm.eval_scalar(diff)

    def max_abs(values):
        return float(np.max(np.abs(np.asarray(values, dtype=float)), initial=0.0))

    residuals = dict(
        identity_gram_max_abs=max_abs(checked.inner_prod_coords),
        identity_func_max_abs=max_abs(checked.func_coords),
        identity_offset_abs=max_abs(checked.offset),
        S_reconstruction_max_abs=max_abs(E.T @ D @ E - S),
        dense_relaxed_gap=abs(state["opt_value"] - dense_value),
        conjecture_gap=abs(
            state["opt_value"]
            - 4 * params["L"] ** 2 * params["R"] ** 2 / state["N_verify"] ** 2
        ),
        minimum_scalar_inequality_dual=min(minimum_duals, default=0.0),
        minimum_S_eigenvalue=float(np.linalg.eigvalsh((S + S.T) / 2).min()),
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
        state["certificate_provenance"]["solver_status"] == "optimal"
        and np.all(np.isfinite(S))
        and np.allclose(S, S.T, atol=1e-6, rtol=0)
        and all(
            residuals[k] <= 1e-5
            for k in [
                "identity_gram_max_abs",
                "identity_func_max_abs",
                "identity_offset_abs",
            ]
        )
        and np.allclose(E.T @ D @ E, S, atol=1e-4, rtol=1e-5)
        and residuals["dense_relaxed_gap"] < 1e-5
        and residuals["conjecture_gap"] < 1e-5
        and residuals["minimum_scalar_inequality_dual"] >= -1e-6
        and residuals["minimum_S_eigenvalue"] >= -1e-6
    )
    return (
        dict(tolerances=tolerances, residuals=residuals, passed=bool(passed)),
        ctx,
        pm,
        checked,
    )


def certificate_id(state):
    keys = (
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
    return hashlib.sha256(
        json.dumps(
            {k: state[k] for k in keys},
            sort_keys=True,
            separators=(",", ":"),
            allow_nan=False,
        ).encode()
    ).hexdigest()
