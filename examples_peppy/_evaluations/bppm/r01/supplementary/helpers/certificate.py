"""Capture a coherent primal certificate with explicit solver selection."""

import hashlib
import json
import uuid

import numpy as np
import runtime
import sympy as sp
from bppm_setup import get_pep_setup

import pepflow as pf


def inventory(ctx, pb):
    entries = [(c, "initial", None, None) for c in pb.init_conditions]
    for owner in ctx.func_to_triplets:
        groups = ctx.get_constraint_data(owner)
        entries.extend(
            (c, "interpolation", str(owner), str(group))
            for group, cs in groups.sc_dict.items()
            for c in cs
        )
        entries.extend(
            (c, "interpolation", str(owner), str(group))
            for group, c in groups.psd_dict.items()
        )
    return entries


def solve_capture(N, relaxed=()):
    setup = runtime.ROOT / "bppm_setup.py"
    allowed = json.loads((runtime.APPROVED / "allowlist.json").read_text())
    paths = [
        setup,
        *[
            __import__("pathlib").Path(p)
            for p in allowed["exact_read_files"]
            if "/pepflow/" in p.replace("\\", "/") and p.endswith(".py")
        ],
    ]
    hashes = {
        str(p.relative_to(runtime.ROOT)).replace("\\", "/"): hashlib.sha256(
            p.read_bytes()
        ).hexdigest()
        for p in paths
    }
    params: dict[str, pf.NUMERICAL_TYPE] = {"alpha": sp.S(1), "R": sp.S(1)}
    ctx, pb, obj = get_pep_setup(N, params)
    if relaxed:
        pb.set_relaxed_constraints(list(relaxed))
    entries = inventory(ctx, pb)
    constraints = [c for c, *_ in entries if c.name not in relaxed]
    solver = pf.CVXPrimalSolver(
        perf_metric=pb.performance_metric, constraints=constraints, context=ctx
    )
    problem = solver.build_problem(resolve_parameters=params)
    value = problem.solve(solver="CLARABEL")
    result = pf.PEPResult(
        opt_value=value,
        dual_var_manager=solver.dual_var_manager,
        pep_type=pf.PEPType.PRIMAL,
        solver_status=problem.status,
        context=ctx,
    )
    S = result.get_gram_dual_matrix()
    metadata, values = {}, {}
    for c, origin, owner, group in entries:
        assert isinstance(c, pf.ScalarConstraint), (
            "Unexpected matrix constraint in this two-convex-function setup"
        )
        dropped = c.name in relaxed
        dual = result.get_dual_value(c.name)
        assert dropped or dual is not None
        metadata[c.name] = dict(
            origin=origin,
            owner=owner,
            group=group,
            kind="scalar",
            comparator=c.cmp.value,
            shape=[],
            relaxed=dropped,
        )
        if dropped:
            values[c.name] = None
        else:
            assert dual is not None
            values[c.name] = float(dual)
    data = dict(
        N=N,
        N_verify=N,
        opt_value=float(value),
        tau_sol=values["initial_condition"],
        tau_name="initial_condition",
        named_dual_values=values,
        constraint_metadata=metadata,
        relaxed_constraints=list(relaxed),
        S_matrix=np.asarray(S.matrix, dtype=float).tolist(),
        S_row_names=S.row_names,
        S_col_names=S.col_names,
        basis_vectors=[str(v) for v in ctx.basis_vectors()],
        basis_scalars=[str(v) for v in ctx.basis_scalars()],
        certificate_provenance=dict(
            solve_id=str(uuid.uuid4()),
            pep_type="primal",
            solver_status=problem.status,
            source_hashes=hashes,
            solver=dict(
                api="CVXPrimalSolver.build_problem + cvxpy.Problem.solve",
                effective_name=problem.solver_stats.solver_name,
                settings={},
            ),
        ),
    )
    for rel, expected in hashes.items():
        assert hashlib.sha256((runtime.ROOT / rel).read_bytes()).hexdigest() == expected
    return ctx, pb, result, entries, data
