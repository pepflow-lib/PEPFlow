"""Current-run-only algebra exploration, independent of PEPFlow internals.

Reads no artifacts. Algorithm coefficients are transcribed from this run's setup.
Numerical checks below do not constitute an all-N proof.
"""

import json
import math
import operator
from pathlib import Path

import numpy as np


def candidate(N):
    N = operator.index(N)
    if N < 1:
        raise ValueError("N must be a positive integer")
    theta = [1.0]
    for _ in range(N):
        theta.append((1 + math.sqrt(1 + 4 * theta[-1] ** 2)) / 2)
    h = np.zeros((N + 1, N + 1))
    for i in range(N):
        h[i + 1, :i] = (1 - 1 / theta[i + 1]) * h[i, :i] + np.array(theta[:i]) / theta[
            i + 1
        ]
        h[i + 1, i] = 1 + (theta[i] - 1) / theta[i + 1]
    D = h.sum(axis=1)
    delta = np.diff(D)
    beta = np.zeros(N + 1)
    alpha = np.zeros(N)
    for j in range(N):
        beta[j] = (h[N, j] + (alpha[j - 1] * delta[j - 1] if j else 0)) / (
            2 * D[N] - D[j]
        )
        alpha[j] = beta[: j + 1].sum()
    beta[N] = 1 - alpha[N - 1]
    alpha_closed = np.cumsum(h[N, :N]) / (2 * D[N] - D[:N])
    assert np.max(np.abs(alpha - alpha_closed)) < 1e-12
    eye = np.eye(N + 1)
    A = np.diag(beta / 2)
    for j in range(N + 1):
        A += beta[j] * (np.outer(eye[j], h[j]) + np.outer(h[j], eye[j])) / 2
    for i in range(N):
        d = h[i + 1] - h[i]
        e = eye[i] - eye[i + 1]
        A += (
            alpha[i]
            * (np.outer(eye[i + 1], d) + np.outer(d, eye[i + 1]) + np.outer(e, e))
            / 2
        )
    q = 2 * D[N] + 1
    B = A - q / 2 * np.outer(beta, beta)
    S = np.block(
        [[np.array([[1 / (2 * q)]]), -beta[None, :] / 2], [-beta[:, None] / 2, A]]
    )
    return dict(N=N, theta=theta, h=h, D=D, alpha=alpha, beta=beta, A=A, B=B, S=S)


def original_basis_matrix(data, L=1.0):
    """Return S for [x_0, x_star, g_0, ..., g_N] with unscaled gradients."""
    N = data["N"]
    translated = data["S"].copy()
    translated[0, 0] *= L
    translated[1:, 1:] /= L
    transform = np.zeros((N + 2, N + 3))
    transform[0, 0], transform[0, 1] = 1.0, -1.0
    transform[1:, 2:] = np.eye(N + 1)
    return transform.T @ translated @ transform


def compare_selected(path):
    """Check the current run's selected sparse certificate in its own ordering."""
    selected = json.loads(Path(path).read_text(encoding="utf-8-sig"))
    data = candidate(selected["N"])
    N, h, alpha, beta, A = [data[k] for k in ["N", "h", "alpha", "beta", "A"]]
    labels = ["z_0", "x_star", "grad_f(z_0)"] + [
        f"grad_f(x_{i})" for i in range(1, N + 1)
    ]
    natural = original_basis_matrix(data)
    order = [labels.index(label) for label in selected["S_row_names"]]
    S_original = natural[np.ix_(order, order)]
    names = ["z_0"] + [f"x_{i}" for i in range(1, N + 1)]
    expected_lambda = np.zeros_like(selected["lambda_matrix"], dtype=float)
    rows, cols = selected["lambda_row_names"], selected["lambda_col_names"]
    for i in range(N):
        expected_lambda[rows.index(names[i]), cols.index(names[i + 1])] = alpha[i]
    for i in range(N + 1):
        expected_lambda[rows.index("x_star"), cols.index(names[i])] = beta[i]
    # Independent compact entry formula, derived algebraically from the sum.
    A_entry = np.diag(np.r_[alpha, 0.5])
    alpha_extended = np.r_[alpha, 1.0]
    for i in range(N + 1):
        for j in range(i + 1, N + 1):
            entry = (
                alpha_extended[j] * h[j, i]
                - alpha[j - 1] * h[j - 1, i]
                - (alpha[i] if j == i + 1 else 0)
            ) / 2
            A_entry[i, j] = A_entry[j, i] = entry
    # Function-balance coefficients from the actual selected support convention.
    balance = beta.copy()
    balance[:-1] -= alpha
    balance[1:] += alpha
    balance[-1] -= 1
    values, vectors = np.linalg.eigh(S_original)
    factor = vectors * np.sqrt(np.maximum(values, 0))[None, :]
    # Assemble interpolation Gram coefficients directly in original coordinates.
    eye = np.eye(N + 3)
    position = [eye[0] - np.r_[0.0, 0.0, h[i]] for i in range(N + 1)]
    gradients = eye[2:]
    radius = eye[0] - eye[1]
    tau = data["S"][0, 0]
    gram = tau * np.outer(radius, radius)
    sym = lambda a, b: (np.outer(a, b) + np.outer(b, a)) / 2  # noqa: E731 - retain the archived numerical helper
    for i in range(N + 1):
        gram += beta[i] * (
            sym(gradients[i], eye[1] - position[i])
            + np.outer(gradients[i], gradients[i]) / 2
        )
    for i in range(N):
        difference = gradients[i] - gradients[i + 1]
        gram += alpha[i] * (
            sym(gradients[i + 1], position[i] - position[i + 1])
            + np.outer(difference, difference) / 2
        )
    gram = gram[np.ix_(order, order)]
    # S = tau*(r-q*sum beta_i*g_i)^2 + sum_{i<j} (-B_ij)*(g_i-g_j)^2.
    # This identity is general. Positivity of all the latter weights is NOT proved all-N.
    q = 2 * data["D"][N] + 1
    ell = [np.r_[1.0, -1.0, -q * beta]]
    weights = [tau]
    for i in range(N + 1):
        for j in range(i + 1, N + 1):
            ell.append(gradients[i] - gradients[j])
            weights.append(-data["B"][i, j])
    ell = np.array(ell)[:, order]
    weights = np.array(weights)
    schur_reconstruction = ell.T @ np.diag(weights) @ ell
    return {
        "selected_certificate_id": selected["certificate_id"],
        "basis": selected["S_row_names"],
        "candidate_S_original": S_original.tolist(),
        "candidate_lambda": expected_lambda.tolist(),
        "candidate_S_eigenvalues": values.tolist(),
        "selected_S_eigenvalues": np.linalg.eigvalsh(selected["S_matrix"]).tolist(),
        "max_abs_S_difference": float(
            np.max(np.abs(S_original - selected["S_matrix"]))
        ),
        "max_abs_lambda_difference": float(
            np.max(np.abs(expected_lambda - selected["lambda_matrix"]))
        ),
        "A_entry_reconstruction_residual": float(np.max(np.abs(A - A_entry))),
        "function_balance_residual": float(np.max(np.abs(balance))),
        "candidate_factor_reconstruction_residual": float(
            np.max(np.abs(S_original - factor @ factor.T))
        ),
        "candidate_identity_gram_residual": float(np.max(np.abs(S_original - gram))),
        "candidate_identity_function_residual": float(np.max(np.abs(balance))),
        "candidate_identity_offset_residual": float(
            abs(tau - 1 / (2 * (2 * data["D"][N] + 1)))
        ),
        "rank_one_plus_schur_decomposition": {
            "weights": weights.tolist(),
            "ell_coords": ell.tolist(),
            "minimum_weight": float(weights.min()),
            "reconstruction_residual": float(
                np.max(np.abs(S_original - schur_reconstruction))
            ),
            "all_N_sign_proof": False,
        },
        "tau_difference": abs(float(data["S"][0, 0]) - selected["tau_sol"]),
    }


def summary(data):
    N, beta, B, S, D = [data[k] for k in ["N", "beta", "B", "S", "D"]]
    off = B.copy()
    np.fill_diagonal(off, 0)
    terminal_schur = B[:-1, :-1] - np.outer(B[:-1, -1], B[-1, :-1]) / B[-1, -1]
    terminal_off = terminal_schur.copy()
    np.fill_diagonal(terminal_off, 0)
    return {
        "N": N,
        "bound": 1 / (2 * (2 * D[N] + 1)),
        "min_beta": float(beta.min()),
        "sum_beta": float(beta.sum()),
        "schur_eigenvalues": np.linalg.eigvalsh(B).tolist(),
        "max_schur_offdiagonal": float(off.max()),
        "positive_offdiagonals_all_touch_terminal": bool(
            np.all(np.argwhere(np.triu(B, 1) > 1e-12)[:, 1] == N)
        ),
        "terminal_schur_max_offdiagonal": float(terminal_off.max()),
        "min_S_eigenvalue": float(np.linalg.eigvalsh(S).min()),
        "null_residual": float(np.max(np.abs(S @ np.r_[2 * D[N] + 1, np.ones(N + 1)]))),
    }


if __name__ == "__main__":
    # Parent clarified N<=12 after earlier explorations; only these are accepted.
    results = [summary(candidate(N)) for N in [1, 2, 3, 4, 5, 7, 10]]
    data = candidate(4)
    selected = Path(__file__).with_name("b2_selected_pending_search.json")
    print(
        json.dumps(
            {
                "N4": {
                    k: v.tolist() if isinstance(v, np.ndarray) else v
                    for k, v in data.items()
                },
                "accepted_checks": results,
                "selected_comparison": compare_selected(selected),
                "scope_note": "Earlier N=20,50,100 experiments predated communication of the N<=12 limit and are excluded from accepted handoff evidence.",
                "all_N_PSD_proved": False,
            },
            indent=2,
        )
    )
