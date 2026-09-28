"""Capture and verify a complete scalar-constraint PEP certificate."""
import hashlib
import json
import uuid
from importlib.metadata import version

import cvxpy as cp
import numpy as np
import pepflow as pf


def inventory(ctx, pb):
    entries = [(c, "initial", None, None) for c in pb.init_conditions]
    for owner in ctx.func_to_triplets:
        groups = ctx.get_constraint_data(owner)
        entries.extend((c, "interpolation", str(owner), str(group))
                       for group, constraints in groups.sc_dict.items() for c in constraints)
        entries.extend((c, "interpolation", str(owner), str(group))
                       for group, c in groups.psd_dict.items())
    assert not ctx.oper_to_duplets
    assert all(isinstance(c, pf.ScalarConstraint) for c, *_ in entries)
    assert len({c.name for c, *_ in entries}) == len(entries)
    return entries


def solve_capture(ctx, pb, params, source_hashes):
    entries = inventory(ctx, pb)
    constraints = [c for c, *_ in entries if c.name not in pb.relaxed_constraints]
    solver = pf.CVXPrimalSolver(pb.performance_metric, constraints, ctx)
    problem = solver.build_problem(resolve_parameters=params)
    attempts = []
    try:
        value = problem.solve(solver="CLARABEL")
        attempts.append({"solver": "CLARABEL", "settings": {}, "status": problem.status})
    except cp.error.SolverError as exc:
        attempts.append({"solver": "CLARABEL", "settings": {}, "error": str(exc)})
        value = problem.solve(solver="SCS", eps=1e-7, max_iters=200000)
        attempts.append({"solver": "SCS", "settings": {"eps": 1e-7, "max_iters": 200000}, "status": problem.status})
    assert problem.status == "optimal", attempts
    result = pf.PEPResult(float(value), solver.dual_var_manager, pf.PEPType.PRIMAL, problem.status, ctx)
    named, metadata = {}, {}
    for c, origin, owner, group in entries:
        dropped = c.name in pb.relaxed_constraints
        v = result.get_dual_value(c.name)
        assert dropped or v is not None
        assert v is None or np.isfinite(float(v))
        metadata[c.name] = {"origin": origin, "owner": owner, "group": group,
                            "kind": "scalar", "comparator": c.cmp.value, "shape": [], "relaxed": dropped}
        if dropped:
            named[c.name] = None
        else:
            assert v is not None
            named[c.name] = float(v)
    S = result.get_gram_dual_matrix()
    displays = {}
    for owner in ctx.func_to_triplets:
        group_data = result.get_scalar_constraint_dual_value_in_numpy(owner)
        if not isinstance(group_data, dict):
            group_data = {"convex": group_data}
        displays[str(owner)] = {str(key): {"matrix": np.asarray(m.matrix, dtype=float).tolist(),
                                        "row_names": list(m.row_names), "col_names": list(m.col_names)}
                               for key, m in group_data.items()}
    return {"opt_value": float(value), "tau_sol": named["initial_condition"], "tau_name": "initial_condition",
            "relaxed_constraints": list(pb.relaxed_constraints), "named_dual_values": named,
            "constraint_metadata": metadata, "S_matrix": np.asarray(S.matrix, dtype=float).tolist(),
            "S_row_names": list(S.row_names), "S_col_names": list(S.col_names),
            "basis_vectors": [str(v) for v in ctx.basis_vectors()],
            "basis_scalars": [str(v) for v in ctx.basis_scalars()], "all_lambda_groups": displays,
            "certificate_provenance": {"solve_id": str(uuid.uuid4()), "pep_type": "primal",
                "solver_status": problem.status, "source_hashes": source_hashes,
                "solver": {"api": "CVXPrimalSolver.build_problem + cvxpy.Problem.solve", "effective_name": problem.solver_stats.solver_name,
                           "cvxpy_version": version("cvxpy"), "attempts": attempts}}}


def scalar_from_gram(ctx, matrix):
    basis = ctx.basis_vectors()
    return sum((float(matrix[i, j]) * basis[i] * basis[j]
                for i, j in np.ndindex(matrix.shape)), pf.Scalar.zero())


def verify_certificate(ctx, pb, params, data, dense_value):
    ctx.set_as_current()
    pm = pf.ExpressionManager(ctx, resolve_parameters=params)
    basis = ctx.basis_vectors()
    assert [str(v) for v in basis] == data["basis_vectors"]
    assert [str(v) for v in ctx.basis_scalars()] == data["basis_scalars"]
    entries = inventory(ctx, pb)
    assert {c.name for c, *_ in entries} == set(data["named_dual_values"]) == set(data["constraint_metadata"])
    weighted = pf.Scalar.zero()
    duals = []
    for c, origin, owner, group in entries:
        meta = data["constraint_metadata"][c.name]
        assert (meta["origin"], meta["owner"], meta["group"], meta["comparator"]) == (origin, owner, group, c.cmp.value)
        v = data["named_dual_values"][c.name]
        if meta["relaxed"]:
            assert v is None and c.name in data["relaxed_constraints"]
            continue
        assert v is not None
        residual = c.lhs - c.rhs
        if c.cmp == pf.Comparator.GE:
            residual = -residual
        weighted += float(v) * (pf.Scalar.zero() + residual)
        if c.cmp != pf.Comparator.EQ:
            duals.append(float(v))
    S = np.asarray(data["S_matrix"], dtype=float)
    S_numeric = scalar_from_gram(ctx, S)
    diff = pb.performance_metric - data["opt_value"] - weighted + S_numeric
    checked = pm.eval_scalar(diff)
    def max_abs(a):
        return float(np.max(np.abs(np.asarray(a, dtype=float)), initial=0.0))
    D = np.asarray(data["numerical_decomposition"]["D"], dtype=float)
    E = np.asarray(data["numerical_decomposition"]["ell_coords"], dtype=float)
    residuals = {"identity_gram_max_abs": max_abs(checked.inner_prod_coords),
                 "identity_func_max_abs": max_abs(checked.func_coords),
                 "identity_offset_abs": max_abs(checked.offset),
                 "S_reconstruction_max_abs": max_abs(E.T @ D @ E - S),
                 "dense_relaxed_gap": abs(data["opt_value"] - dense_value),
                 "minimum_scalar_inequality_dual": min(duals, default=0),
                 "minimum_S_eigenvalue": float(np.linalg.eigvalsh((S + S.T) / 2).min()),
                 "minimum_matrix_inequality_eigenvalue": 0.0}
    tolerances = dict(identity_atol=1e-5, identity_rtol=0, reconstruction_atol=1e-4,
                      reconstruction_rtol=1e-5, dual_tol=1e-6, psd_tol=1e-6, dense_opt_atol=1e-5)
    passed = (data["certificate_provenance"]["solver_status"] == "optimal"
              and np.all(np.isfinite(S)) and np.allclose(S, S.T, atol=1e-6, rtol=0)
              and max(residuals[k] for k in ("identity_gram_max_abs", "identity_func_max_abs", "identity_offset_abs")) <= 1e-5
              and np.allclose(E.T @ D @ E, S, atol=1e-4, rtol=1e-5)
              and residuals["dense_relaxed_gap"] < 1e-5
              and residuals["minimum_scalar_inequality_dual"] >= -1e-6
              and residuals["minimum_S_eigenvalue"] >= -1e-6)
    return {"tolerances": tolerances, "residuals": residuals, "passed": bool(passed)}, checked


CERTIFICATE_KEYS = ('N_verify', 'params_json', 'relaxed_constraints', 'S_matrix', 'S_row_names',
    'S_col_names', 'basis_vectors', 'basis_scalars', 'opt_value', 'tau_sol', 'tau_name',
    'named_dual_values', 'constraint_metadata', 'normalization', 'certificate_provenance',
    'numerical_checks', 'numerical_decomposition')


def certificate_id(data):
    return hashlib.sha256(json.dumps({k: data[k] for k in CERTIFICATE_KEYS}, sort_keys=True,
                                    separators=(',', ':'), allow_nan=False).encode()).hexdigest()
