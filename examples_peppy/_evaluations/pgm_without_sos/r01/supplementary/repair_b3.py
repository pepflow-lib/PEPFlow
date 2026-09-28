"""Diagnose saved-minus-analytic remainder correction."""
import json
import sys
from pathlib import Path


def main():
    root=Path(__file__).resolve().parent.parent
    sys.path[:0]=[str(root/"supplementary/approved"),str(root/"supplementary/h"),str(root)]
    from runtime import configure
    configure()
    import numpy as np
    import pepflow as pf
    from analytic import finite_pieces
    from pgm_setup import get_pep_setup,f,g,L
    records=[]
    for path in ("state/pgm_b2.json","supplementary/b2_n6.json"):
        state=json.loads((root/path).read_text())
        N=state["N_verify"]
        ctx,_,_=get_pep_setup(N,json.loads(state["params_json"]))
        pm=pf.ExpressionManager(ctx,resolve_parameters=json.loads(state["params_json"]))
        pieces,assignment=finite_pieces(ctx,f,g,L,N)
        matrices={name:pm.eval_scalar(piece).inner_prod_coords.astype(float) for name,piece in pieces.items()}
        correction=np.asarray(state["S_matrix"])-sum(matrices.values())
        terminal=sum(matrix for name,matrix in matrices.items() if assignment[name]==N-1)
        eigen=np.linalg.eigvalsh(terminal+correction)
        print(N,"terminal min eigen",eigen.min(),"correction norm",np.linalg.norm(correction),flush=True)
        records.append({"N":N,"terminal_min_eigen":float(eigen.min()),"correction_fro":float(np.linalg.norm(correction))})
    (root/"supplementary/b3-correction-probe.json").write_text(json.dumps(records,indent=2))


if __name__=="__main__":
    main()
