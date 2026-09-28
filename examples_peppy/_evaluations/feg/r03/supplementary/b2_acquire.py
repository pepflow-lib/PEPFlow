import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent / "helpers"))
import fractions
import json

import cvxpy as cp
import numpy as np

# local helper resolved by the notebook runtime path
import runtime  # ty: ignore[unresolved-import]
from feg_setup import get_pep_setup

import pepflow as pf
from pepflow.constraint import ScalarConstraint

ROOT = runtime.ROOT
b1 = json.loads((ROOT / "state/feg_b1.json").read_text())
N = b1["N_verify"]
params = json.loads(b1["params_json"])


def capture(n, dropped):
    ctx, pb, op = get_pep_setup(n, params)
    pb.set_relaxed_constraints(dropped)
    entries = [(c, "initial", None, None) for c in pb.init_conditions]
    groups = op.get_interpolation_constraints_by_group(ctx)
    entries += [
        (c, "interpolation", str(op), group)
        for group, cs in groups.sc_dict.items()
        for c in cs
    ]
    assert not groups.psd_dict
    constraints = [c for c, *_ in entries if c.name not in dropped]
    solver = pf.CVXPrimalSolver(
        perf_metric=pb.performance_metric, constraints=constraints, context=ctx
    )
    problem = solver.build_problem(resolve_parameters=params)
    attempts = []
    try:
        value = problem.solve(solver="CLARABEL")
        attempts.append(dict(solver="CLARABEL", options={}, status=problem.status))
        if problem.status not in ("optimal", "optimal_inaccurate"):
            raise cp.SolverError(problem.status)
    except cp.SolverError as exc:
        attempts.append(dict(solver="CLARABEL", error=str(exc)))
        value = problem.solve(solver="SCS", eps=1e-7, max_iters=200000)
        attempts.append(
            dict(
                solver="SCS",
                options=dict(eps=1e-7, max_iters=200000),
                status=problem.status,
            )
        )
    result = pf.PEPResult(
        opt_value=value,
        dual_var_manager=solver.dual_var_manager,
        pep_type=pf.PEPType.PRIMAL,
        solver_status=problem.status,
        context=ctx,
    )
    meta, vals = {}, {}
    for c, origin, owner, group in entries:
        assert isinstance(c, ScalarConstraint)
        dropped_flag = c.name in dropped
        val = result.get_dual_value(c.name)
        assert dropped_flag or val is not None
        vals[c.name] = None if dropped_flag else float(val)
        meta[c.name] = dict(
            origin=origin,
            owner=owner,
            group=group,
            kind="scalar",
            comparator=c.cmp.value,
            shape=[],
            relaxed=dropped_flag,
        )
    S = result.get_gram_dual_matrix()
    display = result.get_scalar_constraint_dual_value_in_numpy(op)
    assert isinstance(display, dict)
    summary = dict(
        N=n,
        opt_value=float(value),
        solver_status=problem.status,
        attempts=attempts,
        named_dual_values=vals,
        constraint_metadata=meta,
        S_matrix=np.asarray(S.matrix, dtype=float).tolist(),
        S_row_names=list(S.row_names),
        S_col_names=list(S.col_names),
        basis_vectors=[str(v) for v in ctx.basis_vectors()],
        lambda_groups={
            str(k): dict(
                matrix=np.asarray(m.matrix, dtype=float).tolist(),
                row_names=list(m.row_names),
                col_names=list(m.col_names),
            )
            for k, m in display.items()
        },
    )
    return ctx, pb, op, result, entries, summary


if __name__ == "__main__":
    ctx, pb, op, result, entries, dense = capture(N, [])
    (ROOT / "state/feg_dense.json").write_text(json.dumps(dense, indent=2))
    print("DENSE", dense["opt_value"], dense["basis_vectors"], flush=True)
    for name, val in dense["named_dual_values"].items():
        if abs(val) > 1e-6:
            print(
                name,
                round(val, 7),
                str(fractions.Fraction(val).limit_denominator(1000)),
                flush=True,
            )
    print("S eigenvalues", np.linalg.eigvalsh(dense["S_matrix"]), flush=True)
    drops = [
        name
        for name, val in dense["named_dual_values"].items()
        if name != "initial_condition" and abs(val) < 1e-6
    ]
    (ROOT / "state/feg_relaxed_constraints.json").write_text(
        json.dumps(drops, indent=2)
    )
    ctx, pb, op, result, entries, selected = capture(N, drops)
    (ROOT / "supplementary/b2-selected-raw.json").write_text(
        json.dumps(selected, indent=2)
    )
    print("RELAXED", len(drops), selected["opt_value"], flush=True)
    for name, val in selected["named_dual_values"].items():
        if val is not None and abs(val) > 1e-6:
            print(
                name,
                round(val, 7),
                str(fractions.Fraction(val).limit_denominator(1000)),
                flush=True,
            )
