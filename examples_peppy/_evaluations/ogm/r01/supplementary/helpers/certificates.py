"""B2 certificate acquisition using the approved primal solver API."""

import hashlib
import json
import uuid
from importlib.metadata import version

import cvxpy as cp
import numpy as np
import sympy as sp
from ogm_setup import get_pep_setup
from runtime import APPROVED, ROOT

from pepflow.constraint import ScalarConstraint
from pepflow.pep_result import PEPResult
from pepflow.solver import CVXPrimalSolver
from pepflow.utils import PEPType


def acquire(N, dropped=()):
    allowlist = json.loads((APPROVED / "allowlist.json").read_text())
    source_paths = [ROOT / "ogm_setup.py"] + [
        __import__("pathlib").Path(p)
        for p in allowlist["exact_read_files"]
        if str(p).endswith(".py")
        and str(p).replace("\\", "/").split("/")[-2] == "pepflow"
    ]
    hashes = {
        str(p.relative_to(ROOT)).replace("\\", "/"): hashlib.sha256(
            p.read_bytes()
        ).hexdigest()
        for p in source_paths
    }
    ctx, pb, obj = get_pep_setup(N, {"L": 1, "R": 1})
    interpolation = obj.get_interpolation_constraints(ctx)
    pb.set_relaxed_constraints(list(dropped))
    entries = [(c, "initial", None, None) for c in pb.init_conditions]
    groups = ctx.get_constraint_data(obj)
    entries.extend(
        (c, "interpolation", str(obj), str(group))
        for group, cs in groups.sc_dict.items()
        for c in cs
    )
    assert not groups.psd_dict
    assert len(entries) == len(interpolation) + len(pb.init_conditions)
    solver = CVXPrimalSolver(
        perf_metric=pb.performance_metric,
        constraints=[c for c, *_ in entries if c.name not in dropped],
        context=ctx,
    )
    problem = solver.build_problem(
        resolve_parameters={"L": sp.Integer(1), "R": sp.Integer(1)}
    )
    options = {"solver": "CLARABEL"}
    try:
        value = problem.solve(**options)
    except cp.SolverError:
        options = {"solver": "SCS", "eps": 1e-7, "max_iters": 200000}
        value = problem.solve(**options)
    result = PEPResult(
        opt_value=value,
        dual_var_manager=solver.dual_var_manager,
        pep_type=PEPType.PRIMAL,
        solver_status=problem.status,
        context=ctx,
    )
    assert problem.status == "optimal"
    S = result.get_gram_dual_matrix()
    lam = result.get_scalar_constraint_dual_value_in_numpy(obj)
    assert not isinstance(lam, dict)
    metadata, duals = {}, {}
    for con, origin, owner, group in entries:
        assert isinstance(con, ScalarConstraint)
        v = result.get_dual_value(con.name)
        is_dropped = con.name in dropped
        assert is_dropped or v is not None
        metadata[con.name] = dict(
            origin=origin,
            owner=owner,
            group=group,
            kind="scalar",
            comparator=con.cmp.value,
            shape=[],
            relaxed=is_dropped,
        )
        if is_dropped:
            duals[con.name] = None
        else:
            assert v is not None
            duals[con.name] = float(v)
    tau = result.get_dual_value("initial_condition")
    assert tau is not None
    state = dict(
        N=N,
        N_verify=N,
        opt_value=float(value),
        tau_sol=float(tau),
        tau_name="initial_condition",
        relaxed_constraints=list(dropped),
        S_matrix=np.asarray(S.matrix).tolist(),
        S_row_names=list(S.row_names),
        S_col_names=list(S.col_names),
        basis_vectors=[str(v) for v in ctx.basis_vectors()],
        basis_scalars=[str(v) for v in ctx.basis_scalars()],
        lambda_matrix=np.asarray(lam.matrix).tolist(),
        lambda_row_names=list(lam.row_names),
        lambda_col_names=list(lam.col_names),
        named_dual_values=duals,
        constraint_metadata=metadata,
        certificate_provenance=dict(
            solve_id=str(uuid.uuid4()),
            pep_type="primal",
            solver_status=problem.status,
            source_hashes=hashes,
            solver=dict(
                api="CVXPrimalSolver.build_problem",
                cvxpy_version=version("cvxpy"),
                effective_name=problem.solver_stats.solver_name,
                settings=options,
            ),
        ),
    )
    assert all(
        hashlib.sha256((ROOT / p).read_bytes()).hexdigest() == h
        for p, h in hashes.items()
    )
    return state, ctx, pb, result, entries
