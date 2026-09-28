import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent/"helpers"))
from runtime import configure,NOTEBOOK_DIR
configure()
import json
import numpy as np
import pepflow as pf
import sympy as sp
from itertools import combinations
from grouping import construct
from pgm_setup import f
from pepflow.lyapunov_utils import vectors_in_column_space,find_basis_with_sparsest_coefficients
b3=json.loads((NOTEBOOK_DIR/"state/pgm_b3.json").read_text())
ctx,pb,lyap,sample=construct(b3,verbose=False)
pm=pf.ExpressionManager(ctx,resolve_parameters={"L":sp.S.One,"R":sp.S.One})
rows=[]
for k in range(1,b3["N_verify"]+1):
    pairs=[("d0",ctx["x_0"]-ctx["x_star"])]
    if k<b3["N_verify"]:
        pairs += [("dk",ctx[f"x_{k}"]-ctx["x_star"]),
                  ("astar",f.grad(ctx["x_star"])),("ak",f.grad(ctx[f"x_{k}"]))]
        pairs += [(a+"-"+b,x-y) for (a,x),(b,y) in combinations(list(pairs),2)]
    vecs=vectors_in_column_space(lyap[k],[v for _,v in pairs],pep_context=ctx,
        resolve_parameters={"L":sp.S.One,"R":sp.S.One},rtol=1e-4,atol=1e-4)
    basis,C=find_basis_with_sparsest_coefficients(lyap[k],vecs,pep_context=ctx,
        resolve_parameters={"L":sp.S.One,"R":sp.S.One},zero_tol=1e-6,indep_tol=1e-7,span_tol=1e-5)
    labels=[label for v in basis for label,u in pairs if u is v]
    row={"k":k,"candidate_count":len(vecs),"selected_labels":labels,
         "basis_size":len(basis),"required_rank":sample["rank_profile"][k],
         "C":C.tolist(),"zero_count":int(np.sum(abs(C)<1e-6))}
    rows.append(row)
    print(row)
(NOTEBOOK_DIR/"supplementary/b4-sparse-basis-trial.json").write_text(json.dumps(rows,indent=2))

