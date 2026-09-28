"""Replay B3 and scan interpretable basis candidates."""

import json
import sys
from pathlib import Path
from typing import Any


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
    from pgm_setup import f, g, get_pep_setup

    from pepflow.lyapunov_utils import (
        find_basis_with_sparsest_coefficients,
        vectors_in_column_space,
    )

    b3 = json.loads((root / "state/pgm_b3.json").read_text())
    namespace: dict[str, Any] = {
        "certificate": b3,
        "notebook_dir": root,
        "get_pep_setup": get_pep_setup,
    }
    for field in ("certificate_check_code", "decomposition_code", "grouping_code"):
        exec(b3[field], namespace)
    ctx, lyap, pm = namespace["ctx"], namespace["lyap"], namespace["pm"]
    params = json.loads(b3["params_json"])
    N = b3["N_verify"]
    records = []
    for k in range(1, N + 1):
        labeled = [
            ("x0-star", ctx["x_0"] - ctx["x_star"]),
            ("xk-star", ctx[f"x_{k}"] - ctx["x_star"]),
            ("xkm1-star", ctx[f"x_{k - 1}"] - ctx["x_star"]),
            ("grad_f_k-star", f.grad(ctx[f"x_{k}"]) - f.grad(ctx["x_star"])),
            ("grad_g_k+grad_f_star", g.grad(ctx[f"x_{k}"]) + f.grad(ctx["x_star"])),
            ("grad_f_k+grad_g_k", f.grad(ctx[f"x_{k}"]) + g.grad(ctx[f"x_{k}"])),
        ]
        labeled += [(str(v), v) for v in ctx.basis_vectors()]
        labeled += [(f"x{j}-star", ctx[f"x_{j}"] - ctx["x_star"]) for j in range(N + 1)]
        unique, coords = [], []
        for label, v in labeled:
            a = pm.eval_vector(v).coords.astype(float)
            if np.linalg.norm(a) < 1e-6 or any(
                np.allclose(a, b, atol=1e-7, rtol=0) for b in coords
            ):
                continue
            unique.append((label, v))
            coords.append(a)
        found = vectors_in_column_space(
            lyap[k],
            [v for _, v in unique],
            pep_context=ctx,
            resolve_parameters=params,
            rtol=1e-4,
            atol=1e-4,
        )
        names = {id(v): label for label, v in unique}
        print("k", k, "candidates:", [names[id(v)] for v in found])
        try:
            basis, C = find_basis_with_sparsest_coefficients(
                lyap[k],
                found,
                pep_context=ctx,
                resolve_parameters=params,
                zero_tol=1e-6,
                indep_tol=1e-7,
                span_tol=1e-5,
            )
            print("basis", [names[id(v)] for v in basis], "C", C)
            records.append(
                {
                    "k": k,
                    "candidates": [names[id(v)] for v in found],
                    "basis": [names[id(v)] for v in basis],
                    "C": C.tolist(),
                }
            )
        except ValueError as exc:
            print("Failed:", str(exc))
            records.append(
                {"k": k, "candidates": [names[id(v)] for v in found], "error": str(exc)}
            )
    (root / "supplementary/b4-scan.json").write_text(json.dumps(records, indent=2))


if __name__ == "__main__":
    main()
