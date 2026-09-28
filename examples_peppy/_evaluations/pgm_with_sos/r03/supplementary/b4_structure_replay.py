import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent/"helpers"))
from runtime import configure,NOTEBOOK_DIR
configure()
import inspect
import json
import numpy as np
import pepflow as pf
import sympy as sp
import basis
from transport_grouping import construct
state=json.loads((NOTEBOOK_DIR/"state/pgm_b4.json").read_text())
ctx,pb,lyap,_=construct(state,False)
source=inspect.getsource(basis.sample_structure)
source+="\nsample_coefficients = "+repr(state["sample_structure_coefficients"])+"\n"
source+="""
def V_k_structure(k):
    row = sample_coefficients[k]
    C = np.asarray(coeff_by_k[str(k)], dtype=float)
    if k == 0:
        C = np.zeros((0, 0))
    return sample_structure(ctx, k, N_int, C, row["f_gap_coefficient"],
                            row["g_gap_coefficient"], row["offset"])
"""
namespace=dict(vars(basis))
namespace.update(ctx=ctx,N_int=state["N_verify"],coeff_by_k=state["coeff_by_k"])
exec(compile(source,"<B4-replayed-structure>","exec"),namespace)
pm=pf.ExpressionManager(ctx,resolve_parameters={"L":sp.S.One,"R":sp.S.One})
for k,V in enumerate(lyap):
    q=pm.eval_scalar(namespace["V_k_structure"](k)-V)
    assert max(np.max(np.abs(np.asarray(q.inner_prod_coords,dtype=float))),
               np.max(np.abs(np.asarray(q.func_coords,dtype=float))),abs(float(q.offset)))<=1e-4
state["structure_code"]=source
(NOTEBOOK_DIR/"state/pgm_b4.json").write_text(json.dumps(state,indent=2))
print("Reusable structure source replay passed.")

