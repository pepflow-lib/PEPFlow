"""Capture whole primal certificates through the approved framework."""
import hashlib
import json
from pathlib import Path
import uuid

import cvxpy as cp
import numpy as np
import pepflow as pf
import sympy as sp
from pepflow.solver import CVXPrimalSolver

from dual_feg_setup import get_pep_setup


def acquire(n, dropped=()):
    ctx, pb, obj = get_pep_setup(n, {'L': 1, 'R': 1})
    pb.set_relaxed_constraints(list(dropped))
    groups = ctx.get_constraint_data(obj)
    entries = [(c, 'initial', None, None) for c in pb.init_conditions]
    entries.extend((c, 'interpolation', str(obj), str(group))
                   for group, constraints in groups.sc_dict.items() for c in constraints)
    assert not groups.psd_dict
    solver = CVXPrimalSolver(perf_metric=pb.performance_metric,
                            constraints=[c for c, *_ in entries if c.name not in dropped], context=ctx)
    problem = solver.build_problem(resolve_parameters={'L': sp.S.One, 'R': sp.S.One})
    options = {'solver': 'CLARABEL'}
    failures = []
    try:
        val = problem.solve(**options)
    except cp.error.SolverError as exc:
        failures.append(str(exc))
        options = {'solver': 'SCS', 'eps': 1e-7, 'max_iters': 200000}
        val = problem.solve(**options)
    result = pf.PEPResult(opt_value=val, dual_var_manager=solver.dual_var_manager,
                          pep_type=pf.PEPType.PRIMAL, solver_status=problem.status, context=ctx)
    metadata, duals = {}, {}
    for c, origin, owner, group in entries:
        value = result.get_dual_value(c.name)
        is_dropped = c.name in dropped
        assert is_dropped or value is not None
        metadata[c.name] = dict(origin=origin, owner=owner, group=group, kind='scalar',
                               comparator=c.cmp.value, shape=[], relaxed=is_dropped)
        if is_dropped:
            duals[c.name] = None
        else:
            assert value is not None
            duals[c.name] = float(value)
    S = result.get_gram_dual_matrix()
    lam = result.get_scalar_constraint_dual_value_in_numpy(obj)
    assert isinstance(lam, dict)
    display = {str(group): {'matrix': np.asarray(m.matrix, dtype=float).tolist(),
                          'row_names': m.row_names, 'col_names': m.col_names} for group, m in lam.items()}
    state = dict(N=n, N_verify=n, opt_value=float(val), tau_sol=duals['initial_condition'],
                 tau_name='initial_condition', relaxed_constraints=list(dropped),
                 S_matrix=S.matrix.tolist(), S_row_names=S.row_names, S_col_names=S.col_names,
                 basis_vectors=[str(v) for v in ctx.basis_vectors()], basis_scalars=[str(v) for v in ctx.basis_scalars()],
                 named_dual_values=duals, constraint_metadata=metadata, lambda_groups=display,
                 certificate_provenance={'solve_id': str(uuid.uuid4()), 'pep_type': 'primal',
                                         'solver_status': problem.status,
                                         'solver': {'api': 'CVXPrimalSolver.build_problem', 'effective_name': problem.solver_stats.solver_name,
                                                    'settings': options, 'failures': failures}})
    return ctx, pb, result, entries, state


def source_hashes(root):
    approved = root / 'supplementary' / 'approved'
    allowed = json.loads((approved / 'allowlist.json').read_text())['exact_read_files']
    sources = [Path(p) for p in allowed if Path(p).parent == approved / 'pepflow']
    sources += [root / 'dual_feg_setup.py', root / 'supplementary' / 'helpers' / 'certificate_tools.py']
    return {str(p.relative_to(root)): hashlib.sha256(p.read_bytes()).hexdigest() for p in sources}
