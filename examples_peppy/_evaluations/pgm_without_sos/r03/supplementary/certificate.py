"""Selected certificate acquisition with explicit frozen solver policy."""
import runpy
from pathlib import Path
runpy.run_path(str(Path(__file__).with_name('runtime.py')))
import json
import numpy as np
import pepflow as pf
from pgm_setup import get_pep_setup

ROOT = Path(__file__).resolve().parents[1]

def solve(n, dropped=()):
    ctx, pb, obj = get_pep_setup(n, {'L': 1, 'R': 1})
    entries = [(c, 'initial', None, None) for c in pb.init_conditions]
    for owner in ctx.func_to_triplets:
        groups = owner.get_interpolation_constraints_by_group(ctx)
        entries += [(c, 'interpolation', str(owner), str(group)) for group, cs in groups.sc_dict.items() for c in cs]
    pb.set_relaxed_constraints(list(dropped))
    active = [c for c, *_ in entries if c.name not in dropped]
    solver = pf.CVXPrimalSolver(perf_metric=pb.performance_metric, constraints=active, context=ctx)
    problem = solver.build_problem(resolve_parameters={'L': 1, 'R': 1})
    value = problem.solve(solver='CLARABEL')
    result = pf.PEPResult(opt_value=value, dual_var_manager=solver.dual_var_manager, pep_type=pf.PEPType.PRIMAL, solver_status=problem.status, context=ctx)
    duals = {c.name: None if c.name in dropped else float(result.get_dual_value(c.name)) for c, *_ in entries}
    meta = {c.name: dict(origin=origin, owner=owner, group=group, kind='scalar', comparator=c.cmp.value, shape=[], relaxed=c.name in dropped) for c, origin, owner, group in entries}
    s = result.get_gram_dual_matrix()
    data = dict(N=n, opt_value=float(value), solver_status=problem.status, named_dual_values=duals, constraint_metadata=meta, S_matrix=np.asarray(s.matrix,float).tolist(), S_row_names=list(s.row_names), S_col_names=list(s.col_names), basis_vectors=[str(v) for v in ctx.basis_vectors()], basis_scalars=[str(v) for v in ctx.basis_scalars()], relaxed_constraints=list(dropped), solver_options={'solver':'CLARABEL'})
    return ctx, pb, result, entries, data

if __name__ == '__main__':
    _, _, _, _, dense = solve(4)
    (ROOT/'state/pgm_dense.json').write_text(json.dumps(dense,indent=2))
    print('dense',dense['opt_value'], dense['solver_status'])
    print('basis', dense['basis_vectors'])
    for name, value in dense['named_dual_values'].items():
        if value is not None and value > 1e-6:
            print(name, round(value,7))
    print('S eigenvalues', np.linalg.eigvalsh(dense['S_matrix']))
