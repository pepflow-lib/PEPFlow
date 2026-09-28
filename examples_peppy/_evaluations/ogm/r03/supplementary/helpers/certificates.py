"""Capture and revalidate complete primal certificates without hidden solves."""
import hashlib
import json
import uuid

import cvxpy as cp
import numpy as np
import pepflow as pf
import sympy as sp

from ogm_setup import get_pep_setup


def solve_certificate(n, relaxed=()):
    ctx, pb, obj = get_pep_setup(n, {"L": 1, "R": 1})
    all_constraints = [*pb.init_conditions, *obj.get_interpolation_constraints(ctx)]
    pb.set_relaxed_constraints(list(relaxed))
    assert pb.performance_metric is not None
    solver = pf.CVXPrimalSolver(pb.performance_metric, [c for c in all_constraints if c.name not in relaxed], ctx)
    problem = solver.build_problem(resolve_parameters={"L": sp.Integer(1), "R": sp.Integer(1)})
    attempts = []
    try:
        value = problem.solve(solver="CLARABEL")
        attempts.append({"solver": "CLARABEL", "settings": {}, "status": problem.status})
    except cp.SolverError as error:
        attempts.append({"solver": "CLARABEL", "settings": {}, "error": str(error)})
        value = None
    if problem.status != "optimal":
        value = problem.solve(solver="SCS", eps=1e-7, max_iters=200000)
        attempts.append({"solver": "SCS", "settings": {"eps": 1e-7, "max_iters": 200000}, "status": problem.status})
    assert problem.status == "optimal" and value is not None, attempts
    result = pf.PEPResult(value, solver.dual_var_manager, pf.PEPType.PRIMAL, problem.status, ctx)
    groups = ctx.get_constraint_data(obj)
    group_names = {c.name: str(group) for group, constraints in groups.sc_dict.items() for c in constraints}
    meta, duals = {}, {}
    for c in all_constraints:
        initial = c in pb.init_conditions
        assert isinstance(c, pf.ScalarConstraint)
        meta[c.name] = dict(origin="initial" if initial else "interpolation", owner=None if initial else str(obj), group=group_names.get(c.name), kind="scalar", comparator=c.cmp.value, shape=[], relaxed=c.name in relaxed)
        dual = result.get_dual_value(c.name)
        if c.name in relaxed:
            duals[c.name] = None
        else:
            assert dual is not None
            duals[c.name] = float(dual)
    matrix = result.get_gram_dual_matrix()
    lamb = result.get_scalar_constraint_dual_value_in_numpy(obj)
    assert not isinstance(lamb, dict)
    data = dict(N=n, N_verify=n, opt_value=float(value), tau_sol=duals["initial_condition"], tau_name="initial_condition",
                relaxed_constraints=list(relaxed), S_matrix=np.asarray(matrix.matrix, dtype=float).tolist(), S_row_names=matrix.row_names, S_col_names=matrix.col_names,
                basis_vectors=[str(v) for v in ctx.basis_vectors()], basis_scalars=[str(v) for v in ctx.basis_scalars()],
                named_dual_values=duals, constraint_metadata=meta, solver_attempts=attempts,
                lambda_matrix=np.asarray(lamb.matrix, dtype=float).tolist(), lambda_row_names=lamb.row_names, lambda_col_names=lamb.col_names,
                certificate_provenance=dict(solve_id=str(uuid.uuid4()), pep_type="primal", solver_status=problem.status, solver=dict(api="CVXPrimalSolver.build_problem", cvxpy_version=cp.__version__, effective_name=problem.solver_stats.solver_name, settings={})))
    return data


def revalidate(data):
    ctx, pb, obj = get_pep_setup(data["N"], {"L": 1, "R": 1})
    all_constraints = [*pb.init_conditions, *obj.get_interpolation_constraints(ctx)]
    assert [str(v) for v in ctx.basis_vectors()] == data["basis_vectors"]
    assert [str(v) for v in ctx.basis_scalars()] == data["basis_scalars"]
    assert {c.name for c in all_constraints} == set(data["named_dual_values"]) == set(data["constraint_metadata"])
    pm = pf.ExpressionManager(ctx, resolve_parameters={"L": sp.Integer(1), "R": sp.Integer(1)})
    weighted = pf.Scalar.zero()
    for c in all_constraints:
        assert c.cmp.value == data["constraint_metadata"][c.name]["comparator"]
        value = data["named_dual_values"][c.name]
        if c.name in data["relaxed_constraints"]:
            assert value is None
            continue
        assert value is not None and np.isfinite(value)
        residual = c.lhs - c.rhs
        if c.cmp == pf.Comparator.GE:
            residual = -residual
        weighted += value * residual
    basis = ctx.basis_vectors()
    matrix = np.asarray(data["S_matrix"], dtype=float)
    scalar = sum((float(matrix[i, j]) * basis[i] * basis[j] for i, j in np.ndindex(matrix.shape)), pf.Scalar.zero())
    assert pb.performance_metric is not None
    checked = pm.eval_scalar(pb.performance_metric - data["opt_value"] - weighted + scalar)
    residuals = dict(identity_gram_max_abs=float(np.max(np.abs(checked.inner_prod_coords), initial=0)), identity_func_max_abs=float(np.max(np.abs(checked.func_coords), initial=0)), identity_offset_abs=float(abs(checked.offset)), minimum_S_eigenvalue=float(np.linalg.eigvalsh(matrix).min()), minimum_scalar_inequality_dual=min(v for v in data["named_dual_values"].values() if v is not None), minimum_matrix_inequality_eigenvalue=0.)
    assert all(residuals[key] <= 1e-5 for key in ("identity_gram_max_abs", "identity_func_max_abs", "identity_offset_abs")), residuals
    assert residuals["minimum_S_eigenvalue"] >= -1e-6 and residuals["minimum_scalar_inequality_dual"] >= -1e-6, residuals
    return ctx, pb, obj, pm, checked, residuals


def certificate_digest(data):
    keys = ('N_verify', 'params_json', 'relaxed_constraints', 'S_matrix', 'S_row_names', 'S_col_names', 'basis_vectors', 'basis_scalars', 'opt_value', 'tau_sol', 'tau_name', 'named_dual_values', 'constraint_metadata', 'normalization', 'certificate_provenance', 'numerical_checks', 'numerical_decomposition')
    return hashlib.sha256(json.dumps({key: data[key] for key in keys}, sort_keys=True, separators=(',', ':'), allow_nan=False).encode()).hexdigest()
