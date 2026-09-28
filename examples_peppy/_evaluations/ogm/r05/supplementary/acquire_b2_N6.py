"""Acquire coherent N=6 certificates for B3 confirmation, retain selected N=4."""

import json
import sys
from pathlib import Path


def main():
    root = Path(__file__).resolve().parents[1]
    sys.path.insert(0, str(root / "supplementary/helpers"))
    # local helper resolved by the notebook runtime path
    from runtime import configure  # ty: ignore[unresolved-import]

    configure()
    import numpy as np

    # local helper resolved by the notebook runtime path
    from certificate import capture  # ty: ignore[unresolved-import]
    from ogm_setup import get_pep_setup, theta_sequence

    import pepflow as pf

    original = json.loads((root / "state/ogm_b2.json").read_text())
    N = 6
    dense = capture(N)
    (root / "supplementary/b2-dense-N6.json").write_text(
        json.dumps(dense, indent=2), encoding="utf-8"
    )
    tags = ["z_0"] + [f"x_{i}" for i in range(1, N + 1)]
    keep = {f"f:{tags[i]},{tags[i + 1]}" for i in range(N)} | {
        f"f:x_star,{tag}" for tag in tags
    }
    relaxed = [
        name
        for name, meta in dense["constraint_metadata"].items()
        if meta["origin"] == "interpolation" and name not in keep
    ]
    data = capture(N, relaxed, dense["opt_value"])
    assert data["numerical_certificate_verified"]
    theta = theta_sequence(N)
    expected = {f"f:x_star,{tags[i]}": 2 * theta[i] / theta[N] ** 2 for i in range(N)}
    expected[f"f:x_star,{tags[N]}"] = 1 / theta[N]
    expected.update(
        {
            f"f:{tags[i]},{tags[i + 1]}": 2 * theta[i] ** 2 / theta[N] ** 2
            for i in range(N)
        }
    )
    lambda_error = max(
        abs(data["named_dual_values"][name] - val) for name, val in expected.items()
    )
    ctx, _, obj = get_pep_setup(N, json.loads(data["params_json"]))
    pm = pf.ExpressionManager(ctx, resolve_parameters=json.loads(data["params_json"]))
    w = ctx[f"z_{N}"] - ctx["x_star"] - theta[N] * obj.grad(ctx[f"x_{N}"])
    coordinates = np.asarray(pm.eval_vector(w).coords, dtype=float)
    candidate_S = np.outer(coordinates, coordinates) / (2 * theta[N] ** 2)
    S_error = float(np.max(np.abs(candidate_S - np.asarray(data["S_matrix"]))))
    assert lambda_error < 1e-4 and S_error < 1e-4
    for key in (
        "closed_form_search",
        "formula_status",
        "lamb_code",
        "S_code",
        "sparsity_recipe",
    ):
        data[key] = original[key]
    data["closed_form_search"] = {
        **original["closed_form_search"],
        "reuse_source_certificate_id": original["certificate_id"],
        "additional_horizon_comparison": {
            "N": N,
            "lambda_max_abs_error": lambda_error,
            "S_gram_max_abs_error": S_error,
        },
    }
    data["candidate_S_matrix"] = candidate_S.tolist()
    data["analytic_full_pep_verified"] = False
    data["lyapunov_proof_verified"] = False
    data["require_analytic_full_pep"] = False
    (root / "supplementary/b2-certificate-N6.json").write_text(
        json.dumps(data, indent=2, allow_nan=False), encoding="utf-8"
    )
    print("Additional certificate:", data["certificate_id"])
    print("Numerical checks:", data["numerical_checks"])
    print("Candidate discrepancies:", lambda_error, S_error)


if __name__ == "__main__":
    main()
