import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent/"helpers"))
from runtime import configure, NOTEBOOK_DIR
configure()
import json
import numpy as np
import sympy as sp
import pepflow as pf
from fractions import Fraction
from certificates import capture, verify, save, aid_terms

dense=json.loads((NOTEBOOK_DIR/"state/pgm_dense.json").read_text())
drop=[]
for name in dense["named_dual_values"]:
    if ":" not in name:
        continue
    owner,pair=name.split(":")
    a,b=pair.split(",")
    keep = a=="x_star" or (a!="x_star" and b!="x_star" and int(b[2:])==int(a[2:])+1)
    if not keep:
        drop.append(name)
ctx,pb,result,data=capture(6,drop)
checks,_=verify(ctx,pb,data,dense["opt_value"])
data["checks"]=checks
save(NOTEBOOK_DIR/"supplementary/b2-sparse-candidate.json",data)
print("Sparse objective",data["opt_value"],"checks",checks)
for name,v in data["named_dual_values"].items():
    if v is not None:
        print(name,v,Fraction(v).limit_denominator(10000))
pm=pf.ExpressionManager(ctx,resolve_parameters={"L":sp.S.One,"R":sp.S.One})
terms=aid_terms(ctx,6)
aid=sum((c*u**2 for _,_,c,u in terms),pf.Scalar.zero())
A=np.asarray(pm.eval_scalar(aid).inner_prod_coords,dtype=float)
S=np.asarray(data["S_matrix"])
scale=np.sum(A*S)/np.sum(A*A)
print("Aid best normalization",scale,"residual",np.max(np.abs(scale*A-S)))
for scale in [1,1/4,1/8,1/16]:
    print("Aid scale",scale,"residual",np.max(np.abs(scale*A-S)))

