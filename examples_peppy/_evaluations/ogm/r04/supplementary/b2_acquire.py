"""B2 certificate acquisition using only approved PEPFlow solver APIs."""

import hashlib
import json
import sys
import uuid
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent / "helpers"))
# local helper resolved by the notebook runtime path
from runtime import configure  # ty: ignore[unresolved-import]

attempt, approved = configure()
import cvxpy as cp  # noqa: E402 - imports follow runtime or notebook setup
import numpy as np  # noqa: E402 - imports follow runtime or notebook setup
from ogm_setup import (  # noqa: E402 - imports follow runtime or notebook setup
    get_pep_setup,
)

from pepflow.pep_result import (  # noqa: E402 - imports follow runtime or notebook setup
    PEPResult,
)
from pepflow.solver import (  # noqa: E402 - imports follow runtime or notebook setup
    CVXPrimalSolver,
)
from pepflow.utils import (  # noqa: E402 - imports follow runtime or notebook setup
    PEPType,
)

b1 = json.loads((attempt / "state/ogm_b1.json").read_text())
params = json.loads(b1["params_json"])
N = b1["N_verify"]


def acquire(relaxed, filename):
    ctx, pb, obj = get_pep_setup(N, params)
    pb.set_relaxed_constraints(relaxed)
    groups = ctx.get_constraint_data(obj)
    entries = [(c, "initial", None, None) for c in pb.init_conditions]
    entries.extend(
        (c, "interpolation", str(obj), str(group))
        for group, cs in groups.sc_dict.items()
        for c in cs
    )
    assert not groups.psd_dict
    solver = CVXPrimalSolver(
        perf_metric=pb.performance_metric,
        constraints=[c for c, *_ in entries if c.name not in relaxed],
        context=ctx,
    )
    problem = solver.build_problem(resolve_parameters=params)
    options = dict(solver="CLARABEL")
    failure = None
    try:
        value = problem.solve(**options)
    except cp.error.SolverError as exc:
        failure = str(exc)
        options = dict(solver="SCS", eps=1e-7, max_iters=200000)
        value = problem.solve(**options)
    result = PEPResult(
        opt_value=value,
        dual_var_manager=solver.dual_var_manager,
        pep_type=PEPType.PRIMAL,
        solver_status=problem.status,
        context=ctx,
    )
    S = result.get_gram_dual_matrix()
    lamb = result.get_scalar_constraint_dual_value_in_numpy(obj)
    assert not isinstance(lamb, dict)
    metadata, values = {}, {}
    for c, origin, owner, group in entries:
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
        values[c.name] = None if dropped else float(dual)
    source_files = [
        attempt / "ogm_setup.py",
        *[
            Path(p)
            for p in json.loads((approved / "allowlist.json").read_text())[
                "exact_read_files"
            ]
            if Path(p).parent == approved / "pepflow"
        ],
    ]
    state = dict(
        N=N,
        N_verify=N,
        opt_value=float(value),
        tau_sol=values["initial_condition"],
        tau_name="initial_condition",
        S_matrix=np.asarray(S.matrix, dtype=float).tolist(),
        S_row_names=S.row_names,
        S_col_names=S.col_names,
        lambda_matrix=np.asarray(lamb.matrix, dtype=float).tolist(),
        lambda_row_names=lamb.row_names,
        lambda_col_names=lamb.col_names,
        basis_vectors=[str(v) for v in ctx.basis_vectors()],
        basis_scalars=[str(v) for v in ctx.basis_scalars()],
        named_dual_values=values,
        constraint_metadata=metadata,
        relaxed_constraints=relaxed,
        certificate_provenance=dict(
            solve_id=str(uuid.uuid4()),
            pep_type="primal",
            solver_status=problem.status,
            source_hashes={
                str(p): hashlib.sha256(p.read_bytes()).hexdigest() for p in source_files
            },
            solver=dict(
                api="CVXPrimalSolver.build_problem",
                effective_name=problem.solver_stats.solver_name,
                settings=options,
                failure=failure,
            ),
        ),
    )
    (attempt / filename).write_text(json.dumps(state, indent=2, allow_nan=False))
    print(filename, "objective", value, "status", problem.status)
    print("basis", state["basis_vectors"])
    print("S eigenvalues", np.linalg.eigvalsh(np.asarray(S.matrix, dtype=float)))
    print(
        "active:",
        {k: round(v, 9) for k, v in values.items() if v is not None and abs(v) > 1e-6},
    )
    return state


if __name__ == "__main__":
    dense = acquire([], "state/ogm_dense.json")
    relaxed = [
        name
        for name, value in dense["named_dual_values"].items()
        if name != "initial_condition" and value < 1e-6
    ]
    acquire(relaxed, "supplementary/b2-threshold-certificate.json")
