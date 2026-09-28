"""Exact rational remainder and Schur-elimination exploration from own candidates."""
import json
import sys
from pathlib import Path
from typing import Any


def main():
    root = Path(__file__).resolve().parent.parent
    sys.path[:0] = [str(root / "supplementary/approved"), str(root / "supplementary/h"), str(root)]
    from runtime import configure
    configure()
    import sympy as sp
    import pepflow as pf
    from certificate import inventory
    from pgm_setup import get_pep_setup, f
    b4 = json.loads((root / "state/pgm_b4.json").read_text())
    ns: dict[str, Any] = {"sp": sp}
    exec(b4["lamb_code"], ns)
    candidate = ns["candidate_multiplier"]
    outputs = []
    for N in (4,6):
        ctx, pb, _ = get_pep_setup(N, {"L": 1, "R": 1})
        pm = pf.ExpressionManager(ctx, resolve_parameters={"L": sp.S.One, "R": sp.S.One})
        weighted = pf.Scalar.zero()
        terms = []
        for c, origin, _, _ in inventory(ctx, pb):
            weight = candidate(c.name, N)
            residual = c.lhs-c.rhs
            if c.cmp == pf.Comparator.GE:
                residual = -residual
            weighted += weight*residual
            if origin == "interpolation" and weight != 0:
                j = int(c.name.split(",")[1][2:])
                terms.append((j, weight*residual))
        S_expr = weighted-pb.performance_metric+sp.Rational(1,4*N)
        S = sp.Matrix(pm.eval_scalar(S_expr, sympy_mode=True).inner_prod_coords)
        remaining = S.copy()
        pieces = []
        for j in reversed(range(S.rows)):
            pivot = remaining[j,j]
            if pivot == 0:
                print("zero pivot",N,j,list(remaining[:,j]),flush=True)
                assert all(v == 0 for v in remaining[:,j])
                continue
            row = remaining[:,j]/pivot
            piece = pivot*row*row.T
            remaining -= piece
            remaining = remaining.applyfunc(sp.factor)
            label = b4["basis_vectors"][j] if N == 4 else str(ctx.basis_vectors()[j])
            latest = int(label.split("x_")[1].rstrip(")")) if "star" not in label else 0
            pieces.append((latest,piece,pivot))
        assert remaining == sp.zeros(S.rows)
        for k in range(1,N):
            T = sum((term for j,term in terms if j <= k), pf.Scalar.zero())
            M = sp.Matrix(pm.eval_scalar(T, sympy_mode=True).inner_prod_coords)
            for j,piece,_ in pieces:
                if j <= k:
                    M -= piece
            vectors = [ctx["x_0"]-ctx["x_star"],ctx[f"x_{k}"]-ctx["x_star"],
                       f.grad(ctx[f"x_{k}"])-f.grad(ctx["x_star"]),f.grad(ctx[f"x_{k}"])]
            B = sp.Matrix.hstack(*[sp.Matrix(pm.eval_vector(v,sympy_mode=True).coords) for v in vectors])
            P = (B.T*B).inv()*B.T
            C = (P*M*P.T).applyfunc(sp.factor)
            assert M == B*C*B.T
            print(N,k,"A",C[1,1],"B",C[2,2],"cross",2*C[1,3], flush=True)
            outputs.append({"N":N,"k":k,"C":[[str(v) for v in row] for row in C.tolist()]})
    (root / "supplementary/b5-exact-coefficients.json").write_text(json.dumps(outputs,indent=2))


if __name__ == "__main__":
    main()
