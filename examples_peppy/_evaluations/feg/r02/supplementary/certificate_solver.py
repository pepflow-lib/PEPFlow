import runpy
from pathlib import Path
runpy.run_path(str(Path(__file__).with_name('runtime.py')))
import json
import uuid
import hashlib
import numpy as np
import sympy as sp
import pepflow as pf
from feg_setup import get_pep_setup

ROOT = Path(__file__).resolve().parents[1]
PARAMS = {'L': sp.Integer(1), 'R': sp.Integer(1)}


def solve_capture(n, relaxed=()):
    ctx, pb, op = get_pep_setup(n, PARAMS)
    pb.set_relaxed_constraints(list(relaxed))
    entries = [(c, 'initial', None, None) for c in pb.init_conditions]
    for owner in [*ctx.func_to_triplets, *ctx.oper_to_duplets]:
        groups = ctx.get_constraint_data(owner)
        entries.extend((c, 'interpolation', str(owner), str(group)) for group, cs in groups.sc_dict.items() for c in cs)
        entries.extend((c, 'interpolation', str(owner), str(group)) for group, c in groups.psd_dict.items())
    assert len({c.name for c, *_ in entries}) == len(entries)
    active = [c for c, *_ in entries if c.name not in relaxed]
    solver = pf.CVXPrimalSolver(perf_metric=pb.performance_metric, constraints=active, context=ctx)
    problem = solver.build_problem(resolve_parameters=PARAMS)
    options = {'solver': 'CLARABEL'}
    try:
        val = problem.solve(**options)
    except Exception as exc:
        print('CLARABEL failure:', repr(exc))
        options = {'solver': 'SCS', 'eps': 1e-7, 'max_iters': 200000}
        val = problem.solve(**options)
    result = pf.PEPResult(opt_value=val, dual_var_manager=solver.dual_var_manager, pep_type=pf.PEPType.PRIMAL, solver_status=problem.status, context=ctx)
    meta, duals = {}, {}
    for c, origin, owner, group in entries:
        scalar = isinstance(c, pf.ScalarConstraint)
        v = result.get_dual_value(c.name)
        dropped = c.name in relaxed
        assert dropped or v is not None
        meta[c.name] = dict(origin=origin, owner=owner, group=group, kind='scalar' if scalar else 'psd', comparator=c.cmp.value, shape=[] if scalar else list(np.asarray(c.lhs-c.rhs).shape), relaxed=dropped)
        duals[c.name] = None if dropped else float(v) if scalar else np.asarray(v).tolist()
    S = result.get_gram_dual_matrix()
    lambdas = result.get_scalar_constraint_dual_value_in_numpy(op)
    state = dict(N=n,N_verify=n,opt_value=float(val),tau_sol=float(result.get_dual_value('initial_condition')),tau_name='initial_condition',relaxed_constraints=list(relaxed),S_matrix=np.asarray(S.matrix).tolist(),S_row_names=list(S.row_names),S_col_names=list(S.col_names),basis_vectors=[str(v) for v in ctx.basis_vectors()],basis_scalars=[str(v) for v in ctx.basis_scalars()],constraint_metadata=meta,named_dual_values=duals,solver_options=options,solver_status=problem.status,solve_id=str(uuid.uuid4()))
    state['lambda_groups'] = {str(g):dict(matrix=np.asarray(m.matrix).tolist(),row_names=list(m.row_names),col_names=list(m.col_names)) for g,m in lambdas.items()}
    return ctx,pb,op,result,state


if __name__ == '__main__':
    ctx,pb,op,result,data = solve_capture(6)
    (ROOT/'state/feg_dense.json').write_text(json.dumps(data,indent=2))
    print('Dense',data['opt_value'],data['solver_status'])
    print('Basis',data['basis_vectors'])
    print('S eigenvalues',np.linalg.eigvalsh(data['S_matrix']))
    for name,val in data['named_dual_values'].items():
        if val is not None and abs(val)>1e-6:
            print(name,round(val,8))
