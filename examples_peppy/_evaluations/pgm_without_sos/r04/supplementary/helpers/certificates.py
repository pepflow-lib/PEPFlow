"""Capture complete primal certificates using the approved framework."""
import hashlib
import uuid
import numpy as np
import cvxpy as cp
import sympy as sp
import pepflow as pf
from pepflow.constraint import ScalarConstraint
from pgm_setup import get_pep_setup


def entries_for(ctx, pb):
    entries = [(c, 'initial', None, None) for c in pb.init_conditions]
    for owner in ctx.func_to_triplets:
        groups = ctx.get_constraint_data(owner)
        entries.extend((c, 'interpolation', str(owner), str(group))
                       for group, constraints in groups.sc_dict.items() for c in constraints)
        entries.extend((c, 'interpolation', str(owner), str(group))
                       for group, c in groups.psd_dict.items())
    return entries


def acquire(N, dropped=()):
    params: dict[str, pf.NUMERICAL_TYPE] = {'L': sp.S.One, 'R': sp.S.One}
    ctx, pb, obj = get_pep_setup(N, params)
    pb.set_relaxed_constraints(list(dropped))
    entries = entries_for(ctx, pb)
    assert len({c.name for c, *_ in entries}) == len(entries)
    constraints = [c for c, *_ in entries if c.name not in dropped]
    assert pb.performance_metric is not None
    solver = pf.CVXPrimalSolver(pb.performance_metric, constraints, ctx)
    problem = solver.build_problem(resolve_parameters=params)
    settings = {'solver': 'CLARABEL'}
    failure = None
    try:
        value = problem.solve(**settings)
    except cp.error.SolverError as exc:
        failure = str(exc)
        settings = {'solver': 'SCS', 'eps': 1e-7, 'max_iters': 200000}
        value = problem.solve(**settings)
    result = pf.PEPResult(opt_value=value, dual_var_manager=solver.dual_var_manager,
                          pep_type=pf.PEPType.PRIMAL, solver_status=problem.status, context=ctx)
    named, metadata = {}, {}
    for c, origin, owner, group in entries:
        assert isinstance(c, ScalarConstraint), 'Unexpected matrix constraint family'
        dropped_now = c.name in dropped
        dual = result.get_dual_value(c.name)
        assert dropped_now or dual is not None
        if dropped_now:
            named[c.name] = None
        else:
            assert dual is not None
            named[c.name] = float(dual)
        metadata[c.name] = dict(origin=origin, owner=owner, group=group, kind='scalar',
                                comparator=c.cmp.value, shape=[], relaxed=dropped_now)
    S = result.get_gram_dual_matrix()
    primary = result.get_scalar_constraint_dual_value_in_numpy(obj)
    assert isinstance(primary, pf.MatrixWithNames)
    data = dict(N=N, N_verify=N, params_json='{"L": 1, "R": 1}',
                opt_value=float(value), tau_sol=named['initial_condition'], tau_name='initial_condition',
                solver_status=problem.status, solver_options=settings, fallback_reason=failure,
                named_dual_values=named, constraint_metadata=metadata,
                S_matrix=np.asarray(S.matrix, float).tolist(), S_row_names=list(S.row_names),
                S_col_names=list(S.col_names), basis_vectors=[str(v) for v in ctx.basis_vectors()],
                basis_scalars=[str(v) for v in ctx.basis_scalars()], relaxed_constraints=list(dropped),
                lambda_matrix=np.asarray(primary.matrix, float).tolist(),
                lambda_row_names=list(primary.row_names), lambda_col_names=list(primary.col_names),
                certificate_provenance=dict(solve_id=str(uuid.uuid4()), pep_type='primal',
                    solver_status=problem.status, solver=dict(api='CVXPrimalSolver.build_problem',
                    effective_name=problem.solver_stats.solver_name, settings=settings)))
    return ctx, pb, result, data


def file_hash(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

