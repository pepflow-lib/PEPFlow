import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent / 'helpers'))
import runtime
import json
import numpy as np
import pepflow as pf
from pgm_setup import get_pep_setup

N=int(sys.argv[1]) if len(sys.argv)>1 else 4
ctx,pb,obj = get_pep_setup(N, {'L':1,'R':1})
constraints = list(pb.init_conditions)
for owner in ctx.func_to_triplets:
    constraints.extend(owner.get_interpolation_constraints(ctx))
solver = pf.CVXPrimalSolver(pb.performance_metric, constraints, ctx)
problem = solver.build_problem(resolve_parameters={'L':1,'R':1})
value = problem.solve(solver='CLARABEL')
result = pf.PEPResult(opt_value=value, dual_var_manager=solver.dual_var_manager, pep_type=pf.PEPType.PRIMAL, solver_status=problem.status, context=ctx)
rows = {c.name:float(result.get_dual_value(c.name)) for c in constraints}
S = np.asarray(result.get_gram_dual_matrix().matrix,dtype=float)
data=dict(N=N,opt_value=float(value),status=problem.status,duals=rows,S_matrix=S.tolist(),basis=[str(v) for v in ctx.basis_vectors()],solver='CLARABEL',options={})
(runtime.ATTEMPT/'state/pgm_dense.json').write_text(json.dumps(data,indent=2))
print(value,problem.status)
for name,val in rows.items():
    if val>1e-6: print(name,round(val,7))
print('basis',data['basis'])
print('S eigenvalues',np.linalg.eigvalsh(S))

