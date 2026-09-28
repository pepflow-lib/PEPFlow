"""Record an explicit all-index candidate without asserting all-horizon PSD."""

import hashlib
import inspect
import json
import sys
from pathlib import Path

import numpy as np
import sympy as sp

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
sys.path.insert(0, str(ROOT))
sys.dont_write_bytecode = True

# Imports follow repository-path and runtime setup.
import pepflow as pf  # noqa: E402
from pepflow.pep_runner import _load_setup_module  # noqa: E402


def chain_weight(n, k):
    """Candidate a_k for integer n>=1 and 0<=k<n; endpoint values use flow."""
    n, k = sp.Integer(n), sp.Integer(k)
    if k == -1:
        return sp.S.Zero
    if k == n:
        return sp.S.One
    if n < 1 or not 0 <= k < n:
        raise ValueError("Require n>=1 and -1<=k<=n")
    d = (n + 2) * (n + 3)
    return sp.factor(
        (k + 1)
        * (2 * n * (n + 1) * (k + 4) - k * (k + 2) * (k + 3))
        / (n * (n + 1) * (2 * d - k**2 - 7 * k - 8))
    )


def candidate_lambda(n, row, col):
    """Exact candidate on chain/star edges; all other interpolation weights zero."""
    n = int(n)
    points = [f"x_{i}" for i in range(n)] + ["x_1" if n == 1 else f"y_{n}"]
    if row == "x_star" and col in points:
        i = points.index(col)
        return chain_weight(n, i) - chain_weight(n, i - 1)
    if row in points[:-1] and col == points[points.index(row) + 1]:
        return chain_weight(n, points.index(row))
    return sp.S.Zero


def candidate_S(ctx, obj, n, smoothness):
    """Pure Gram candidate from the quadratic parts of interpolation residuals."""
    n = int(n)
    points = [f"x_{i}" for i in range(n)] + ["x_1" if n == 1 else f"y_{n}"]
    labels = ["x_star", *points]
    tau = 2 * smoothness / sp.Integer((n + 2) * (n + 3))
    result = tau * (ctx["x_0"] - ctx["x_star"]) ** 2
    for row in labels:
        for col in labels:
            weight = candidate_lambda(n, row, col)
            if weight == 0:
                continue
            xi, xj = ctx[row], ctx[col]
            gi, gj = obj.grad(xi), obj.grad(xj)
            result += weight * (gj * (xi - xj) + (gi - gj) ** 2 / (2 * smoothness))
    return result


if __name__ == "__main__":
    samples = json.loads((HERE / "chain_exact_search.json").read_text())
    for sample in samples:
        n = sample["N"]
        assert sample["status"] == "finite_horizon_exact_candidate"
        assert [chain_weight(n, i) for i in range(n)] == [
            sp.Rational(x) for x in sample["a"]
        ]
        assert all(
            candidate_lambda(n, *name[2:].split(",")) == sp.Rational(value)
            for name, value in sample["multipliers"].items()
        )
    state_path = HERE.parent / "state" / "fgm_rational_test_b2.json"
    state = json.loads(state_path.read_text())
    n = state["N_verify"]
    mod = _load_setup_module(str(HERE.parent / "fgm_rational_test_setup.py"))
    ctx, pb, obj = mod.get_pep_setup(sp.Integer(n), {"L": sp.S.One, "R": sp.S.One})
    obj.get_interpolation_constraints(ctx)
    pm = pf.ExpressionManager(ctx, resolve_parameters={"L": sp.S.One, "R": sp.S.One})
    lamb = sp.Matrix(
        [
            [candidate_lambda(n, r, c) for c in state["lambda_col_names"]]
            for r in state["lambda_row_names"]
        ]
    )
    expression = candidate_S(ctx, obj, n, mod.L)
    evaluated = pm.eval_scalar(expression, sympy_mode=True)
    exact_gram = sp.Matrix(evaluated.inner_prod_coords)
    assert not exact_gram.atoms(sp.Float)
    assert sp.Matrix(evaluated.func_coords).is_zero_matrix
    assert evaluated.offset == 0
    sample = next(sample for sample in samples if sample["N"] == n)
    assert exact_gram == sp.Matrix(sample["S_exact"])
    lambda_error = float(
        np.max(np.abs(np.asarray(lamb, dtype=float) - state["lambda_matrix"]))
    )
    gram_error = float(
        np.max(np.abs(np.asarray(exact_gram, dtype=float) - state["S_matrix"]))
    )
    assert lambda_error <= 1e-4 and gram_error <= 1e-4
    lamb_source = (
        inspect.getsource(chain_weight) + "\n" + inspect.getsource(candidate_lambda)
    )
    lamb_source += "\ndef lamb(ri, ci):\n    return candidate_lambda(int(N), ri, ci)\n"
    s_source = inspect.getsource(candidate_S)
    s_source += "\nS_guess = candidate_S(ctx, obj, int(N), L)\n"
    record = {
        "method": "Exact chain/star flow ansatz, equal-gradient kernel equations, then explicit rational index formula",
        "derivation": [
            "Set d=(N+2)(N+3), c=4/d, t_k=k(k+7)/8 for gradient-query points.",
            "The gradient coefficient in y_N is h_(N,j)=(j+2)/2-j(j+1)(j+2)/(2N(N+1)).",
            "Its partial sum H_(N,k)=(k+1)(k+4)/4-k(k+1)(k+2)(k+3)/(8N(N+1)).",
            "The proposed kernel S*(1,0,c,...,c)^T=0 gives a_k=c*H_(N,k)/(1-c*(1+t_k)).",
            "Star weights b_k=a_k-a_(k-1), with a_(-1)=0 and a_N=1, enforce function-value balance.",
        ],
        "formula_domain": "Candidate for integer N>=1, 0<=k<N, L>0; exact PSD checked only at L=1, N=1..6.",
        "finite_horizons_exactly_checked": [sample["N"] for sample in samples],
        "lambda_max_abs_difference_at_selected_sample": lambda_error,
        "S_max_abs_difference_at_selected_sample": gram_error,
        "comparison_atol": 1e-4,
        "candidate_zero_function_and_offset": True,
        "finite_horizon_exact_psd": True,
        "unresolved": "All-horizon PSD/sign argument for the rational Gram candidate; no all-N analytic proof claimed.",
    }
    state["lamb_code"] = lamb_source
    state["S_code"] = s_source
    state["formula_status"] = {"lambda": "candidate", "S": "candidate"}
    state["closed_form_search"]["attempts"].append(record)
    state["closed_form_search"]["unresolved_components"] = [
        "all-horizon candidate signs and Gram PSD proof"
    ]
    state["closed_form_search"]["completed"] = True
    state["closed_form_search"]["reference_policy"] = (
        "User prohibits other examples/reference history; only current sample and generic source used for S structure search and reverse LDL."
    )
    state["analytic_candidate_evidence"] = record
    state["analytic_candidate_source_hashes"] = {
        str(path.relative_to(ROOT)).replace("\\", "/"): hashlib.sha256(
            path.read_bytes()
        ).hexdigest()
        for path in [Path(__file__).resolve(), HERE / "chain_exact_search.py"]
    }
    state["analytic_full_pep_verified"] = False
    state["lyapunov_proof_verified"] = False
    for name in ["fgm_rational_test_b2.json", "fgm_rational_test_relaxed.json"]:
        (HERE.parent / "state" / name).write_text(
            json.dumps(state, indent=2, allow_nan=False) + "\n", encoding="utf-8"
        )
    print(json.dumps(record, indent=2))
    print("Original coherent numerical certificate preserved:", state["certificate_id"])
