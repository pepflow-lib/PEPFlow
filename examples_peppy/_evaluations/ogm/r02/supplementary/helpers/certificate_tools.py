"""Attempt-owned solver capture and numerical certificate utilities."""

import hashlib
import json
import uuid
from importlib.metadata import version
from pathlib import Path

import cvxpy as cp
import numpy as np
import pepflow as pf
import sympy as sp

from ogm_setup import get_pep_setup

ROOT = Path(__file__).resolve().parents[2]
PARAMS: dict[str, pf.NUMERICAL_TYPE] = {"L": sp.Integer(1), "R": sp.Integer(1)}


def source_hashes():
    allowlist = json.loads((ROOT / "supplementary/approved/allowlist.json").read_text())
    paths = [Path(p) for p in allowlist["exact_read_files"] if Path(p).parent.name == "pepflow"]
    paths += [ROOT / "ogm_setup.py", Path(__file__).resolve()]
    return {str(p.relative_to(ROOT)).replace("\\", "/"): hashlib.sha256(p.read_bytes()).hexdigest() for p in paths}


def inventory(ctx, pb):
    entries = [(c, "initial", None, None) for c in pb.init_conditions]
    for owner in ctx.func_to_triplets:
        groups = ctx.get_constraint_data(owner)
        entries.extend((c, "interpolation", str(owner), str(group))
                       for group, constraints in groups.sc_dict.items() for c in constraints)
        entries.extend((c, "interpolation", str(owner), str(group)) for group, c in groups.psd_dict.items())
    assert not ctx.oper_to_duplets
    assert len({c.name for c, *_ in entries}) == len(entries)
    return entries


def acquire(N, relaxed=()):
    hashes = source_hashes()
    ctx, pb, obj = get_pep_setup(N, PARAMS)
    pb.set_relaxed_constraints(list(relaxed))
    entries = inventory(ctx, pb)
    constraints = [c for c, *_ in entries if c.name not in relaxed]
    solver = pf.CVXPrimalSolver(pb.performance_metric, constraints, ctx)
    problem = solver.build_problem(resolve_parameters=PARAMS)
    options = {"solver": "CLARABEL"}
    failure = None
    try:
        value = problem.solve(**options)
        if problem.status not in (cp.OPTIMAL, cp.OPTIMAL_INACCURATE):
            raise RuntimeError(str(problem.status))
    except (cp.SolverError, RuntimeError) as exc:
        failure = repr(exc)
        options = {"solver": "SCS", "eps": 1e-7, "max_iters": 200000}
        value = problem.solve(**options)
    if value is None:
        raise RuntimeError("No bound returned")
    result = pf.PEPResult(opt_value=value, dual_var_manager=solver.dual_var_manager,
                          pep_type=pf.PEPType.PRIMAL, solver_status=problem.status, context=ctx)
    S = result.get_gram_dual_matrix()
    matrix = result.get_scalar_constraint_dual_value_in_numpy(obj)
    assert not isinstance(matrix, dict)
    metadata, duals = {}, {}
    for c, origin, owner, group in entries:
        assert isinstance(c, pf.ScalarConstraint), "This case has only scalar non-Gram constraints"
        dropped = c.name in relaxed
        dual = result.get_dual_value(c.name)
        assert dropped or dual is not None
        metadata[c.name] = dict(origin=origin, owner=owner, group=group, kind="scalar",
                                comparator=c.cmp.value, shape=[], relaxed=dropped)
        if dropped:
            duals[c.name] = None
        else:
            assert dual is not None
            duals[c.name] = float(dual)
    data = dict(N=N, N_verify=N, params_json='{"L": 1, "R": 1}',
                opt_value=float(value), tau_name="initial_condition", tau_sol=float(duals["initial_condition"]),
                relaxed_constraints=list(relaxed), S_matrix=np.asarray(S.matrix, dtype=float).tolist(),
                S_row_names=list(S.row_names), S_col_names=list(S.col_names),
                basis_vectors=[str(v) for v in ctx.basis_vectors()],
                basis_scalars=[str(v) for v in ctx.basis_scalars()],
                lambda_matrix=np.asarray(matrix.matrix, dtype=float).tolist(),
                lambda_row_names=list(matrix.row_names), lambda_col_names=list(matrix.col_names),
                named_dual_values=duals, constraint_metadata=metadata,
                normalization=dict(tau_name="initial_condition", initial_condition="||x_0-x_star||^2 <= R^2",
                                   performance_metric="f(x_N)-f(x_star)", bound_value=float(value),
                                   bound_formula="L*R**2/(2*theta_N**2)"),
                certificate_provenance=dict(solve_id=str(uuid.uuid4()), pep_type="primal",
                    solver_status=str(problem.status), source_hashes=hashes,
                    solver=dict(api="CVXPrimalSolver.build_problem", cvxpy_version=version("cvxpy"),
                                effective_name=problem.solver_stats.solver_name, settings=options, fallback_reason=failure)))
    assert source_hashes() == hashes
    return ctx, pb, obj, data


def summary(data):
    S = np.asarray(data["S_matrix"])
    return {"N": data["N"], "opt_value": data["opt_value"], "status": data["certificate_provenance"]["solver_status"],
            "basis_vectors": data["basis_vectors"], "S_eigenvalues": np.linalg.eigvalsh(S).tolist(),
            "active_duals": {name: v for name, v in data["named_dual_values"].items() if v is not None and abs(v) > 1e-6}}
