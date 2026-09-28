import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent / 'helpers'))
from owned_runtime import configure, ROOT
configure()
import json
import numpy as np
from pgm_setup import get_pep_setup
from solve_runtime import solve_primal

ctx,pb,obj = get_pep_setup(4,{})
result, meta = solve_primal(ctx,pb,{'L':1,'R':1})
duals = {name: np.asarray(c.dual_value).tolist() for name,c in result.dual_var_manager.named_constraints.items()}
S = result.get_gram_dual_matrix()
data = {'N':4,'opt_value':result.opt_value,'solver':meta,'named_duals':duals,'S_matrix':S.matrix.tolist(),'basis_vectors':[str(v) for v in ctx.basis_vectors()]}
(ROOT/'state'/'pgm_dense.json').write_text(json.dumps(data,indent=2))
print('Bound',result.opt_value,'status',result.solver_status)
for name,value in duals.items():
    if np.asarray(value).ndim == 0 and float(value)>1e-6:
        print(name,round(float(value),7))
print('eig',np.linalg.eigvalsh(S.matrix))
print('basis',data['basis_vectors'])
