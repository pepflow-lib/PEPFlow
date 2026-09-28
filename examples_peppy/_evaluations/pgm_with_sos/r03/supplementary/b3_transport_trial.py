import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent/"helpers"))
from runtime import configure,NOTEBOOK_DIR
configure()
import json
import numpy as np
import sympy as sp
import pepflow as pf
from grouping import construct
from pgm_setup import f
rows=[]
for file in ["supplementary/N4-selected/pgm_b2.json","state/pgm_b2.json"]:
    c=json.loads((NOTEBOOK_DIR/file).read_text())
    ctx,pb,lyap,obs=construct(c,False)
    pm=pf.ExpressionManager(ctx,resolve_parameters={"L":sp.S.One,"R":sp.S.One})
    S=np.array(c["S_matrix"])
    E=np.array(c["numerical_decomposition"]["ell_coords"])
    D=np.array(c["numerical_decomposition"]["D"])
    B=E.T@np.diag(np.sqrt(np.diag(D)))
    A=B@B.T
    av,au=np.linalg.eigh(A)
    keep=av>1e-10
    Ai=(au[:,keep]/np.sqrt(av[keep]))@au[:,keep].T
    P=au[:,keep]@au[:,keep].T
    sv,su=np.linalg.eigh(S)
    assert sv.min()>=0
    Sh=(su*np.sqrt(sv))@su.T
    Bnew=Sh@Ai@B
    remainder=Sh@(np.eye(len(S))-P)@Sh
    reconstruction=Bnew@Bnew.T+remainder
    assert np.max(abs(S-reconstruction))<1e-10
    partial=np.zeros_like(S)
    psd=[]
    ranks=[]
    errors=[]
    min_eigs=[]
    for k in range(c["N_verify"]+1):
        old=np.array(obs["coordinates"][k]["gram"])
        oldCum=B[:,:3*k]@B[:,:3*k].T
        newCum=Bnew[:,:3*k]@Bnew[:,:3*k].T
        if k==c["N_verify"]:
            newCum+=remainder
        M=old+oldCum-newCum
        ranks.append(int(np.linalg.matrix_rank(M,tol=1e-4)))
        if k==0:
            bas=[]
        elif k==c["N_verify"]:
            bas=[ctx["x_0"]-ctx["x_star"]]
        else:
            bas=[ctx["x_0"]-ctx["x_star"],ctx[f"x_{k}"]-ctx["x_star"],
                 f.grad(ctx["x_star"]),f.grad(ctx[f"x_{k}"])]
        if bas:
            V=np.column_stack([pm.eval_vector(v).coords for v in bas]).astype(float)
            vi=np.linalg.pinv(V)
            C=vi@M@vi.T
            err=float(np.linalg.norm(M-V@C@V.T))
        else:
            err=float(np.linalg.norm(M))
        errors.append(err)
        psd.append(M.tolist())
    row={"N":c["N_verify"],"recipe":"symmetric_root_transport",
        "rank_profile":ranks,"basis_errors":errors,
        "reconstruction":float(np.max(abs(S-reconstruction))),
        "remainder_min_eigenvalue":float(np.linalg.eigvalsh(remainder).min()),
        "new_factors":Bnew.T.tolist(),"remainder":remainder.tolist(),
        "gram_coords":psd}
    rows.append(row)
    print("N",row["N"],"ranks",ranks,"errors",errors)
(NOTEBOOK_DIR/"supplementary/b3-transport-trial.json").write_text(json.dumps(rows,indent=2))

