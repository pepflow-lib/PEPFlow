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
from pgm_setup import f,g
from pepflow.lyapunov_utils import vectors_in_column_space

b3=json.loads((NOTEBOOK_DIR/"state/pgm_b3.json").read_text())
ctx,pb,lyap,sample=construct(b3,verbose=False)
pm=pf.ExpressionManager(ctx,resolve_parameters={"L":sp.S.One,"R":sp.S.One})
n=b3["N_verify"]
base=[("d0",ctx["x_0"]-ctx["x_star"]),("astar",f.grad(ctx["x_star"]))]
for j in range(n+1):
    base.extend([(f"d{j}",ctx[f"x_{j}"]-ctx["x_star"]),(f"a{j}",f.grad(ctx[f"x_{j}"]))])
    if j:
        base.append((f"s{j}",g.grad(ctx[f"x_{j}"])))
pairs=base+[(a+"-"+b,x-y) for (a,x),(b,y) in combinations(base,2)]
pairs += [(f"a{j}+s{j}",f.grad(ctx[f"x_{j}"])+g.grad(ctx[f"x_{j}"])) for j in range(1,n+1)]
seen=[]
clean=[]
for label,v in pairs:
    co=np.asarray(pm.eval_vector(v).coords,dtype=float)
    if np.linalg.norm(co)>1e-7 and not any(np.allclose(co,c,atol=1e-10,rtol=0) for c in seen):
        clean.append((label,v))
        seen.append(co)
data=[]
for k in range(1,n):
    good=vectors_in_column_space(lyap[k],[v for _,v in clean],pep_context=ctx,
           resolve_parameters={"L":sp.S.One,"R":sp.S.One},rtol=1e-4,atol=1e-4)
    labels=[label for label,v in clean if any(v is g for g in good)]
    print(k,labels)
    data.append({"k":k,"labels":labels})
(NOTEBOOK_DIR/"supplementary/b4-scan.json").write_text(json.dumps(data,indent=2))

