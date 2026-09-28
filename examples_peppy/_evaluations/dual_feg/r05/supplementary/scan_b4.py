"""Explore interpretable bases from the verified partial sums."""
import json
import sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
NOTEBOOK_DIR=ROOT
sys.path.insert(0,str(ROOT/"supplementary"))
from certificate_capture import get_pep_setup
import numpy as np
import pepflow as pf
from pepflow.lyapunov_utils import vectors_in_column_space, find_basis_with_sparsest_coefficients, find_symmetric_coefficient_matrix
certificate=json.loads((ROOT/"state/dual_feg_b3.json").read_text())
for field in ["certificate_check_code","decomposition_code","grouping_code"]:
    exec(compile(certificate[field],field,"exec"),globals())
assert certificate_checked and grouping_checked
ctx.set_as_current()
params_sp={"L":sp.Integer(1),"R":sp.Integer(1)}
N_int=certificate["N_verify"]
scan={}
for k in range(1,N_int+1):
    pairs=[("A_N",obj(ctx[f"x_{N_int}"])),(f"z_{k}",ctx[f"z_{k}"]),
           (f"x_{k}-x_N",ctx[f"x_{k}"]-ctx[f"x_{N_int}"]),
           ("x_0-x_N",ctx["x_0"]-ctx[f"x_{N_int}"]),
           (f"x_{k}-x_0",ctx[f"x_{k}"]-ctx["x_0"])]
    for i in range(N_int+1):
        for prefix in ["x","z","a"]:
            pairs.append((f"{prefix}_{i}",ctx[f"{prefix}_{i}"]))
    for i in range(N_int):
        for prefix in ["y","b"]:
            pairs.append((f"{prefix}_{i}",ctx[f"{prefix}_{i}"]))
    pairs += [(f"x_{i}-x_N",ctx[f"x_{i}"]-ctx[f"x_{N_int}"]) for i in range(N_int)]
    unique=[]
    seen=[]
    for label,v in pairs:
        coords=np.asarray(pm.eval_vector(v).coords,dtype=float)
        if np.linalg.norm(coords)<=1e-12 or any(np.allclose(coords,w,atol=1e-12,rtol=0) for w in seen):
            continue
        seen.append(coords)
        unique.append((label,v))
    candidates=[v for _,v in unique]
    inside=vectors_in_column_space(lyap[k],candidates,pep_context=ctx,resolve_parameters={n:v for n,v in params_sp.items()},atol=1e-4,rtol=1e-4)
    labels={id(v):label for label,v in unique}
    print(k,"Candidates", [labels[id(v)] for v in inside],flush=True)
    chosen,C=find_basis_with_sparsest_coefficients(lyap[k],inside,pep_context=ctx,resolve_parameters={n:v for n,v in params_sp.items()},zero_tol=1e-6,indep_tol=1e-7,span_tol=1e-5)
    print("Chosen",[labels[id(v)] for v in chosen],"C",C,flush=True)
    scan[k]={"candidates":[labels[id(v)] for v in inside],"basis":[labels[id(v)] for v in chosen],"C":C.tolist()}
(ROOT/"supplementary/b4-scan.json").write_text(json.dumps(scan,indent=2))


