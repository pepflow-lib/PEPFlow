"""Exact positive-polynomial identities for the selected SOS pivots."""

import json
import sys
from pathlib import Path


def main():
    root = Path(__file__).resolve().parent.parent
    sys.path[:0] = [
        str(root / "supplementary/approved"),
        str(root / "supplementary/h"),
        str(root),
    ]
    # local helper resolved by the notebook runtime path
    from runtime import configure  # ty: ignore[unresolved-import]

    configure()
    import numpy as np
    import sympy as sp

    # local helper resolved by the notebook runtime path
    from analytic import (  # ty: ignore[unresolved-import]
        finite_pieces,
        sos_coefficients,
    )
    from pgm_setup import L, f, g, get_pep_setup

    import pepflow as pf

    k, n = sp.symbols("k n", nonnegative=True)
    N = k + 1 + n
    alpha, beta, gamma, *_ = sos_coefficients(k, N)
    A = k**2 + 2 * k * n + 4 * k + 4 * n + 3
    B = (
        k**4
        + 4 * k**3 * n
        + 8 * k**3
        + 4 * k**2 * n**2
        + 22 * k**2 * n
        + 18 * k**2
        + 12 * k * n**2
        + 28 * k * n
        + 16 * k
        + 4 * n**2
        + 10 * n
        + 5
    )
    P = (
        k**4
        + 5 * k**3 * n
        + 3 * k**3
        + 8 * k**2 * n**2
        + 13 * k**2 * n
        + 3 * k**2
        + 4 * k * n**3
        + 16 * k * n**2
        + 13 * k * n
        + k
        + 4 * n**3
        + 10 * n**2
        + 5 * n
    )
    identities = [
        alpha - A / (2 * (k + 2 * n + 1) ** 2),
        beta - B / (2 * (k + 2 * n + 1) ** 2 * A),
        gamma - k * P / ((k + 2 * n + 2) ** 2 * B),
    ]
    residuals = [sp.factor(v) for v in identities]
    assert residuals == [0, 0, 0]
    assert all(coef > 0 for poly in (A, B, P) for coef in sp.Poly(poly, k, n).coeffs())
    print("Pivot positive-polynomial identities:", residuals)
    print("A and B have positive constants; all coefficients of A,B,P are positive.")
    print("For k,n>=0: alpha,beta>0, gamma>=0; all square divisions are defined.")
    comparisons = []
    for filename in ("state/pgm_b2.json", "supplementary/b2_n6.json"):
        state = json.loads((root / filename).read_text())
        ctx, _, _ = get_pep_setup(state["N_verify"], {"L": 1, "R": 1})
        pieces, _ = finite_pieces(ctx, f, g, L, state["N_verify"])
        pm = pf.ExpressionManager(
            ctx, resolve_parameters={"L": sp.S.One, "R": sp.S.One}
        )
        ev = pm.eval_scalar(sum(pieces.values(), pf.Scalar.zero()), sympy_mode=True)
        error = float(
            np.max(
                np.abs(
                    np.asarray(ev.inner_prod_coords, dtype=float)
                    - np.asarray(state["S_matrix"])
                )
            )
        )
        print("Same S comparison", state["N_verify"], error)
        assert error < 1e-5
        comparisons.append({"N": state["N_verify"], "S_max_error": error})
    (root / "supplementary/b5-signs-discovery.json").write_text(
        json.dumps(
            {
                "exact_pivot_identities": True,
                "positive_polynomial_coefficients": True,
                "domain": "k>=0, n=N-k-1>=0; L>0; step used for k<=N-2",
                "same_S_comparisons": comparisons,
            },
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
