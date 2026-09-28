"""Capture coherent primal PEP certificates using the approved framework."""

import hashlib
import json
import uuid
from pathlib import Path

import cvxpy as cp
import numpy as np
import sympy as sp

import pepflow as pf


def solve_certificate(setup, horizon, dropped=()):
    root = Path(setup.__file__).resolve().parent
    approved = root / "supplementary" / "approved"
    allowlist = json.loads((approved / "allowlist.json").read_text())[
        "exact_read_files"
    ]
    sources = [Path(setup.__file__).resolve(), Path(__file__).resolve()]
    sources.extend(Path(p) for p in allowlist if Path(p).parent == approved / "pepflow")
    hashes = {str(p): hashlib.sha256(p.read_bytes()).hexdigest() for p in sources}
    ctx, pb, obj = setup.get_pep_setup(horizon, {"L": 1, "R": 1})
    entries = [(c, "initial", None, None) for c in pb.init_conditions]
    for owner in ctx.func_to_triplets:
        owner.get_interpolation_constraints(ctx)
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
    pb.set_relaxed_constraints(list(dropped))
    assert pb.performance_metric is not None
    solver = pf.CVXPrimalSolver(
        pb.performance_metric, [c for c, *_ in entries if c.name not in dropped], ctx
    )
    problem = solver.build_problem(resolve_parameters={"L": sp.S(1), "R": sp.S(1)})
    options = {"solver": "CLARABEL"}
    failure = None
    try:
        value = problem.solve(**options)
    except cp.error.SolverError as exc:
        failure = str(exc)
        options = {"solver": "SCS", "eps": 1e-7, "max_iters": 200000}
        value = problem.solve(**options)
    result = pf.PEPResult(
        value, solver.dual_var_manager, pf.PEPType.PRIMAL, problem.status, ctx
    )
    metadata, duals = {}, {}
    for constraint, origin, owner, group in entries:
        assert isinstance(constraint, pf.ScalarConstraint)
        is_dropped = constraint.name in dropped
        dual = result.get_dual_value(constraint.name)
        assert is_dropped or dual is not None
        metadata[constraint.name] = dict(
            origin=origin,
            owner=owner,
            group=group,
            kind="scalar",
            comparator=constraint.cmp.value,
            shape=[],
            relaxed=is_dropped,
        )
        if is_dropped:
            duals[constraint.name] = None
        else:
            assert dual is not None
            duals[constraint.name] = float(dual)
    gram = result.get_gram_dual_matrix()
    state = dict(
        N=horizon,
        N_verify=horizon,
        params_json='{"L": 1, "R": 1}',
        opt_value=float(value),
        tau_sol=float(duals["initial_condition"]),
        tau_name="initial_condition",
        relaxed_constraints=list(dropped),
        S_matrix=np.asarray(gram.matrix, dtype=float).tolist(),
        S_row_names=list(gram.row_names),
        S_col_names=list(gram.col_names),
        basis_vectors=[str(v) for v in ctx.basis_vectors()],
        basis_scalars=[str(v) for v in ctx.basis_scalars()],
        named_dual_values=duals,
        constraint_metadata=metadata,
        certificate_provenance=dict(
            solve_id=str(uuid.uuid4()),
            pep_type="primal",
            solver_status=str(problem.status),
            solver=dict(
                api="CVXPrimalSolver.build_problem",
                effective_name=problem.solver_stats.solver_name,
                settings=options,
                failure=failure,
            ),
            source_hashes=hashes,
        ),
    )
    assert all(
        hashlib.sha256(Path(p).read_bytes()).hexdigest() == digest
        for p, digest in hashes.items()
    )
    return ctx, pb, obj, entries, state


def certificate_digest(state):
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
            {key: state[key] for key in keys},
            sort_keys=True,
            separators=(",", ":"),
            allow_nan=False,
        ).encode()
    ).hexdigest()
