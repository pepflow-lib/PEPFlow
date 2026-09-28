"""Saved-certificate grouping trials; no new solves."""
import json
import sys
from pathlib import Path


def main():
    root = Path(__file__).resolve().parent.parent
    sys.path[:0] = [str(root / "supplementary/approved"), str(root / "supplementary/h"), str(root)]
    from runtime import configure
    configure()
    import numpy as np
    import pepflow as pf
    from certificate import inventory, verify, certificate_id
    from pgm_setup import get_pep_setup
    state = json.loads((root / "state/pgm_b2.json").read_text())
    assert certificate_id(state) == state["certificate_id"]
    ctx, pb, _ = get_pep_setup(state["N_verify"], {"L": 1, "R": 1})
    pb.set_relaxed_constraints(state["relaxed_constraints"])
    checks, _, _ = verify(ctx, pb, {"L": 1, "R": 1}, state)
    assert checks["passed"]
    pm = pf.ExpressionManager(ctx, resolve_parameters=json.loads(state["params_json"]))
    N = state["N_verify"]
    terms = []
    for c, origin, owner, _ in inventory(ctx, pb):
        value = state["named_dual_values"][c.name]
        if origin != "interpolation" or value is None:
            continue
        residual = c.lhs-c.rhs
        if c.cmp == pf.Comparator.GE:
            residual = -residual
        coords = pm.eval_scalar(value*residual)
        first, second = c.name.split(":")[1].split(",")
        index = int(second[2:])
        terms.append((c.name, index, owner, np.asarray(coords.inner_prod_coords, dtype=float)))
    D = np.asarray(state["numerical_decomposition"]["D"])
    E = np.asarray(state["numerical_decomposition"]["ell_coords"])
    assert np.max(np.abs(D-np.diag(np.diag(D)))) == 0
    pieces = [D[j,j]*np.outer(E[j], E[j]) for j in range(len(D))]
    latest = []
    for row in E:
        inds = []
        for coeff, label in zip(row, state["basis_vectors"]):
            if abs(coeff) > 1e-6 and "x_" in label and "star" not in label:
                inds.append(int(label.split("x_")[1].rstrip(")")))
        latest.append(max(inds, default=0))
    trials = []
    for star_shift in (-1, 0, 1):
        for s_shift in (-1, 0, 1):
            mats = [np.zeros_like(pieces[0])]
            for k in range(1, N+1):
                total = np.zeros_like(pieces[0])
                for name, j, owner, matrix in terms:
                    assigned = j+star_shift if "x_star" in name else j
                    if max(1,min(N,assigned)) <= k:
                        total += matrix
                for matrix, j in zip(pieces, latest):
                    if max(1,min(N,j+s_shift)) <= k:
                        total -= matrix
                mats.append(total)
            sv = [np.linalg.svd(m, compute_uv=False).tolist() for m in mats]
            ranks = [int(np.linalg.matrix_rank(m, tol=1e-4)) for m in mats]
            trial = dict(star_shift=star_shift, s_shift=s_shift, ranks=ranks, singular_values=sv)
            trials.append(trial)
            print(star_shift, s_shift, ranks)
    print("Factor latest indices:", latest)
    (root / "supplementary/b3-ldl-trials.json").write_text(json.dumps(trials, indent=2))


if __name__ == "__main__":
    main()
