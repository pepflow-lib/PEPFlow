"""Explicit one-thread solver selection, inventory and serialization."""

import json
from pathlib import Path

import numpy as np

import pepflow as pf

SOLVER_SETTINGS = dict(
    solver="CLARABEL",
    max_threads=1,
    tol_gap_abs=1e-10,
    tol_gap_rel=1e-10,
    tol_feas=1e-10,
    max_iter=300,
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
    assert len({c.name for c, *_ in entries}) == len(entries)
    return entries


def solve(ctx, pb, params, settings=None):
    constraints = [
        c for c, *_ in inventory(ctx, pb) if c.name not in pb.relaxed_constraints
    ]
    solver = pf.CVXPrimalSolver(
        perf_metric=pb.performance_metric, constraints=constraints, context=ctx
    )
    problem = solver.build_problem(resolve_parameters=params)
    effective_settings = SOLVER_SETTINGS if settings is None else settings
    value = problem.solve(**effective_settings)
    result = pf.PEPResult(
        opt_value=value,
        dual_var_manager=solver.dual_var_manager,
        pep_type=pf.PEPType.PRIMAL,
        solver_status=problem.status,
        context=ctx,
    )
    return result, problem


def capture(ctx, pb, result):
    metadata, values = {}, {}
    for c, origin, owner, group in inventory(ctx, pb):
        dropped = c.name in pb.relaxed_constraints
        val = result.get_dual_value(c.name)
        assert dropped or val is not None, c.name
        assert isinstance(c, pf.ScalarConstraint)
        metadata[c.name] = dict(
            origin=origin,
            owner=owner,
            group=group,
            kind="scalar",
            comparator=c.cmp.value,
            shape=[],
            relaxed=dropped,
        )
        values[c.name] = None if dropped else float(val)
    S = result.get_gram_dual_matrix()
    return dict(
        opt_value=float(result.opt_value),
        solver_status=str(result.solver_status),
        tau_sol=float(result.get_dual_value("initial_condition")),
        tau_name="initial_condition",
        named_dual_values=values,
        constraint_metadata=metadata,
        S_matrix=np.asarray(S.matrix).tolist(),
        S_row_names=list(S.row_names),
        S_col_names=list(S.col_names),
        basis_vectors=[str(v) for v in ctx.basis_vectors()],
        basis_scalars=[str(v) for v in ctx.basis_scalars()],
        relaxed_constraints=list(pb.relaxed_constraints),
    )


def dump(path, data):
    Path(path).parent.mkdir(parents=True, exist_ok=True)
    Path(path).write_text(json.dumps(data, indent=2, allow_nan=False), encoding="utf-8")
