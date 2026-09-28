"""Generic certificate capture using the approved solver and explicit solver policy."""
import hashlib
import json
import uuid
from importlib.metadata import version

import cvxpy as cp
import numpy as np
import pepflow as pf
import sympy as sp
from pepflow.pep_result import PEPResult
from pepflow.solver import CVXPrimalSolver
from pepflow.utils import PEPType
from feg_setup import get_pep_setup
import runtime


def acquire(n, dropped=()):
    ctx, pb, obj = get_pep_setup(n, {"L": 1, "R": 1})
    assert isinstance(ctx, pf.PEPContext)
    groups = ctx.get_constraint_data(obj)
    entries = [(c, 'initial', None, None) for c in pb.init_conditions]
    entries += [(c, 'interpolation', str(obj), group) for group, cs in groups.sc_dict.items() for c in cs]
    assert not groups.psd_dict and not ctx.func_to_triplets
    assert len(ctx.oper_to_duplets) == 1
    pb.set_relaxed_constraints(list(dropped))
    solver = CVXPrimalSolver(perf_metric=pb.performance_metric,
                            constraints=[c for c, *_ in entries if c.name not in dropped], context=ctx)
    problem = solver.build_problem(resolve_parameters={"L": sp.S(1), "R": sp.S(1)})
    options = {"solver": "CLARABEL"}
    failure = None
    try:
        value = problem.solve(**options)
    except cp.error.SolverError as error:
        failure = str(error)
        options = {"solver": "SCS", "eps": 1e-7, "max_iters": 200000}
        value = problem.solve(**options)
    result = PEPResult(opt_value=value, dual_var_manager=solver.dual_var_manager,
                       pep_type=PEPType.PRIMAL, solver_status=problem.status, context=ctx)
    metadata = {c.name: dict(origin=origin, owner=owner, group=group, kind='scalar',
                             comparator=c.cmp.value, shape=[], relaxed=c.name in dropped)
                for c, origin, owner, group in entries}
    duals = {}
    for c, *_ in entries:
        value = result.get_dual_value(c.name)
        if c.name in dropped:
            duals[c.name] = None
        else:
            assert value is not None
            duals[c.name] = float(value)
    sm = result.get_gram_dual_matrix()
    lamb = result.get_scalar_constraint_dual_value_in_numpy(obj)
    assert isinstance(lamb, dict)
    approved_list = json.loads((runtime.APPROVED / 'allowlist.json').read_text())['exact_read_files']
    source_files = [runtime.ROOT / 'feg_setup.py'] + [runtime.ROOT / 'supplementary/helpers/certificates.py']
    source_files += [runtime.APPROVED / 'pepflow' / p.replace('\\', '/').rsplit('/', 1)[1] for p in approved_list if '/pepflow/' in p.replace('\\', '/')]
    source_hashes = {str(p.relative_to(runtime.ROOT)).replace('\\', '/'): hashlib.sha256(p.read_bytes()).hexdigest() for p in source_files}
    data = dict(N=n, N_verify=n, params_json='{"L": 1, "R": 1}', opt_value=float(problem.value),
                tau_sol=duals['initial_condition'], tau_name='initial_condition',
                relaxed_constraints=list(dropped), named_dual_values=duals, constraint_metadata=metadata,
                S_matrix=sm.matrix.tolist(), S_row_names=sm.row_names, S_col_names=sm.col_names,
                basis_vectors=[str(v) for v in ctx.basis_vectors()], basis_scalars=[str(v) for v in ctx.basis_scalars()],
                lambda_groups={name: dict(matrix=m.matrix.tolist(), row_names=m.row_names, col_names=m.col_names) for name, m in lamb.items()},
                normalization=dict(tau_name='initial_condition', initial_condition='||x_0-x_star||^2 <= R^2',
                                   performance_metric='||A(x_N)||^2', bound_value=float(problem.value), bound_formula='4*L**2*R**2/N**2'),
                certificate_provenance=dict(solve_id=str(uuid.uuid4()), pep_type='primal', solver_status=problem.status,
                    source_hashes=source_hashes, solver=dict(api='CVXPrimalSolver.build_problem', cvxpy_version=version('cvxpy'),
                        effective_name=problem.solver_stats.solver_name, settings=options, failure=failure)))
    return ctx, pb, obj, result, entries, data


def summarize(data):
    print('N, objective, status:', data['N'], data['opt_value'], data['certificate_provenance']['solver_status'])
    print('basis:', data['basis_vectors'])
    print('S eigenvalues:', np.linalg.eigvalsh(data['S_matrix']))
    for name, value in data['named_dual_values'].items():
        if value is not None and abs(value) > 1e-6:
            print(name, value)



