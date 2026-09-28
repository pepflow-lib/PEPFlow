# This saved notebook fragment shares its caller's execution namespace.
# These names are supplied by the notebook cells or serialized proof source.
# ty: ignore[unresolved-reference]
# ruff: noqa: F821

# Compare exact coefficient formulas with every selected B4 numerical matrix.
import json

import numpy as np
import sympy as sp

import pepflow as pf

b4 = json.loads((notebook_dir / "state" / "pgm_b4.json").read_text())
assert b4["numerical_reconstruction"]["certificate_id"] == b4["certificate_id"]


def coeff_pattern(index, horizon, smoothness):
    index, horizon, smoothness = sp.S(index), sp.S(horizon), sp.S(smoothness)
    if index == 0:
        return sp.zeros(0, 0)
    if index == horizon:
        return sp.Matrix([[-smoothness / (4 * horizon)]])
    d = 2 * horizon - index
    return sp.Matrix(
        [
            [-smoothness / (4 * horizon), 0, 0, 0],
            [0, smoothness * (horizon - index) / d**2, 0, -1 / (2 * d)],
            [0, 0, 1 / (2 * smoothness * d), 0],
            [0, -1 / (2 * d), 0, 0],
        ]
    )


def function_pattern(index, horizon):
    index, horizon = sp.S(index), sp.S(horizon)
    if index == 0:
        return [sp.S(0), sp.S(0)]
    if index == horizon:
        return [sp.S(1), sp.S(1)]
    return [(index + 1) / (2 * horizon - index), index / (2 * horizon - index)]


formula_comparisons = {}
for index in range(b4["N_verify"] + 1):
    candidate_C = coeff_pattern(index, b4["N_verify"], 1)
    actual_C = np.asarray(b4["coeff_by_k"][str(index)], dtype=float).reshape(
        candidate_C.shape
    )
    C_error = float(
        np.max(np.abs(actual_C - np.asarray(candidate_C, dtype=float)), initial=0.0)
    )
    function_error = float(
        np.max(
            np.abs(
                np.asarray(b4["function_coeff_by_k"][str(index)])
                - np.asarray(function_pattern(index, b4["N_verify"]), dtype=float)
            )
        )
    )
    assert C_error <= 1e-5 and function_error <= 1e-5
    formula_comparisons[str(index)] = {"quadratic": C_error, "function": function_error}
    print(
        f"k={index}: analytic coefficient comparison", formula_comparisons[str(index)]
    )
    if candidate_C.rows:
        pf.pprint_labeled_matrix(
            np.asarray(candidate_C, dtype=object),
            V_k_basis_labels(index),
            V_k_basis_labels(index),
        )
