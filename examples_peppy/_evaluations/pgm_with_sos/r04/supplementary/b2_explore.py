import json
from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).resolve().parent / "helpers"))
import runtime
import numpy as np
from fractions import Fraction
import pgm_setup as mod
from pepflow.pep_result import PEPResult
from pepflow.utils import PEPType


def acquire(n, relaxed):
    ctx, pb, obj = mod.get_pep_setup(n, {"L": 1, "R": 1})
    if relaxed:
        pb.set_relaxed_constraints(relaxed)
    problem, solver, options = runtime.solve_builder(ctx, pb, {"L": 1, "R": 1})
    result = PEPResult(problem.value, solver.dual_var_manager, PEPType.PRIMAL, problem.status, ctx)
    duals = {name: float(c.dual_value) for name,c in solver.dual_var_manager.named_constraints.items() if np.asarray(c.dual_value).ndim == 0}
    data = {"N":n,"opt_value":problem.value,"status":problem.status,"solver_options":options,"named_dual_values":duals,"S_matrix":result.get_gram_dual_matrix().matrix.tolist(),"basis_vectors":[str(v) for v in ctx.basis_vectors()],"relaxed_constraints":relaxed}
    return ctx,pb,result,data

if __name__ == "__main__":
    ctx,pb,result,dense = acquire(4, [])
    (runtime.ROOT / 'state/pgm_dense.json').write_text(json.dumps(dense,indent=2))
    for name,value in dense['named_dual_values'].items():
        if value > 1e-6:
            print(name,round(value,7),str(Fraction(value).limit_denominator(1000)))
    print('S rank',np.linalg.matrix_rank(dense['S_matrix'],tol=1e-4))
    drop = [name for name,value in dense['named_dual_values'].items() if value < 1e-6 and name != 'initial_condition']
    ctx,pb,result,sparse = acquire(4,drop)
    (runtime.ROOT / 'supplementary/b2-sparse-search.json').write_text(json.dumps(sparse,indent=2))
    print('dropped',len(drop),'sparse status',sparse['status'],'value',sparse['opt_value'])
    for name,value in sparse['named_dual_values'].items():
        if value > 1e-6:
            print(name,round(value,7),str(Fraction(value).limit_denominator(1000)))
