"""Exact coefficient-map algebra and current-study sample checks; no solver.

The identities are conditional on the displayed nonzero denominators. This
script does not claim the separate all-horizon positivity proof is complete.
Existing study contamination is preserved. Only the companion JSON is written.
"""

import hashlib
import json
from pathlib import Path

import numpy as np
import sympy as sp

HERE = Path(__file__).resolve().parent
STUDY = HERE.parent
REPO_ROOT = STUDY.parent.parent
NAME = STUDY.name
READ_FILES = {}


def read_json(path):
    data = path.read_bytes()
    READ_FILES[str(path.relative_to(REPO_ROOT)).replace("\\", "/")] = hashlib.sha256(
        data
    ).hexdigest()
    return json.loads(data)


def exact_zero(expression):
    return sp.cancel(sp.expand(expression)) == 0


def symbolic_checks():
    t, bp, b, bn = sp.symbols("t beta_previous beta beta_next", real=True)
    u, v, w = sp.symbols("a_next b_next c_next", real=True)
    y, z, q, r, f0, f1 = sp.symbols("y z q r F_current F_next", real=True)
    e = sp.Matrix([1, 0])
    G = sp.Matrix([[u, v], [v, w]])
    E = sp.Matrix([[1 - 1 / t, 1 / t], [0, 1]])
    d = sp.Matrix([1, t])
    cross = (b * e - bn * E.T * e) / 2
    delta = bn - (d.T * G * d)[0]
    h = E.T * G * d + cross
    A = E.T * G * E + h * h.T / delta
    state = sp.Matrix([y, z])
    x_next = (e.T * E * state)[0]
    state_next = E * state - d * r
    V = bp * f0 + (state.T * A * state)[0] + (b - bp) * y * q - bp * q * q / 2
    V_next = (
        b * f1
        + (state_next.T * G * state_next)[0]
        + (bn - b) * state_next[0] * r
        - b * r * r / 2
    )
    star = f0 - q * (y + q) + q * q / 2
    chain = f1 - f0 + r * (y + q - x_next) + (q - r) ** 2 / 2
    square = delta * (r + (h.T * state)[0] / delta) ** 2
    step = exact_zero(V_next - V - (b - bp) * star - b * chain + square)

    # Fractional-linear form of exactly the same Riccati map.
    D = d * d.T / bn
    F = cross * cross.T / bn
    Et = E + d * cross.T / bn
    Ei = Et.inv()
    M11, M12 = Et.T - F * Ei * D, F * Ei
    M21, M22 = -Ei * D, Ei
    denominator = M21 * G + M22
    map_difference = A * denominator - (M11 * G + M12)
    transfer = all(exact_zero(entry) for entry in map_difference)
    det_Et = exact_zero(Et.det() - (1 - 1 / t) / 2)
    det_denominator = exact_zero(denominator.det() - delta / (bn * Et.det()))

    # Exact bordered-tail identities establish the Riccati formula even when
    # the physical initial state y_1=z_1 has only one independent direction.
    Tp, eta, alpha_future = sp.symbols("T eta alpha_future", real=True)
    Tn = (1 - 1 / t) * Tp
    future_k = sp.Matrix([-eta / Tp, eta / Tp - alpha_future]) / 2
    future_next = sp.Matrix([-eta / Tn, eta / Tn - alpha_future]) / 2
    future_columns = all(exact_zero(entry) for entry in future_k - E.T * future_next)
    eta_next = bn * Tn - b * Tp
    first_column = sp.Matrix([-eta_next / Tp, eta_next / Tp - (bn - b)]) / 2
    first_column_identity = all(exact_zero(entry) for entry in first_column - cross)
    gradient_tail_row = exact_zero(
        -(d.T * future_next)[0] - (alpha_future * t + eta * (1 - t) / Tn) / 2
    )

    # Terminal step: both final stars are present.
    a_end = 1 - b
    V_end_previous = bp * f0 + a_end**2 * y * y / 2 + (b - bp) * y * q - bp * q * q / 2
    star_end = f1 - r * y + r * r / 2
    chain_end = f1 - f0 + r * q + (q - r) ** 2 / 2
    square_end = (r - a_end * y) ** 2 / 2
    terminal = exact_zero(
        f1
        - V_end_previous
        - (b - bp) * star
        - b * chain_end
        - a_end * star_end
        + square_end
    )

    # Initial collapse y_1=z_1=s-q_0, with the sum of A_0 entries fixed by
    # the global kernel/Schur argument described in the companion derivation.
    K, s = sp.symbols("K s", real=True)
    alpha0 = 1 / (K - 1)
    a0 = (K - 2) / (2 * (K - 1) ** 2)
    delta0 = K / (2 * (K - 1) ** 2)
    formal0 = a0 * (s - q) ** 2 + alpha0 * (s - q) * q
    base = exact_zero(s * s / (2 * K) - formal0 - delta0 * (q - s / K) ** 2)
    aa = sp.symbols("a0", real=True)
    schur = sp.Matrix(
        [[1 / (2 * K) - aa, -alpha0 / 2 + aa], [-alpha0 / 2 + aa, alpha0 - aa]]
    )
    kernel = all(
        exact_zero(entry) for entry in (schur * sp.Matrix([K, 1])).subs(aa, a0)
    )
    result = dict(
        step_polynomial_identity=step,
        terminal_polynomial_identity=terminal,
        base_polynomial_identity=base,
        initial_schur_kernel_identity=kernel,
        riccati_transfer_cross_multiplication=transfer,
        transfer_state_matrix_determinant=det_Et,
        transfer_denominator_determinant=det_denominator,
        tail_future_columns_identity=future_columns,
        tail_first_column_identity=first_column_identity,
        tail_gradient_row_identity=gradient_tail_row,
    )
    assert all(result.values())
    return result


def analytic_sample(N):
    theta = np.ones(N + 1)
    for j in range(N):
        theta[j + 1] = (1 + np.sqrt(1 + 4 * theta[j] ** 2)) / 2
    H = np.zeros((N + 1, N + 1))
    for j in range(1, N):
        H[j] = (1 - 1 / theta[j]) * H[j - 1]
        H[j, j - 1] += 1 - 1 / theta[j]
        H[j, :j] += theta[:j] / theta[j]
    H[N] = H[N - 1]
    H[N, N - 1] += 1
    C_total = float(H[N].sum())
    K = 2 * C_total + 1
    beta = np.ones(N + 1)
    beta[:N] = np.cumsum(H[N, :N]) / (2 * C_total - H[:N].sum(axis=1))
    alpha = np.diff(np.r_[0, beta])
    e = np.array([1.0, 0.0])
    terminal = alpha[N] ** 2 * np.outer(e, e) / 2
    A = {N - 1: terminal}
    deltas = {N: 0.5, 0: K / (2 * (K - 1) ** 2)}
    transfers, local_h = {}, {}
    for k in range(N - 2, -1, -1):
        t = theta[k + 1]
        E = np.array([[1 - 1 / t, 1 / t], [0, 1.0]])
        d = np.array([1.0, t])
        B = beta[k + 1]
        cross = (beta[k] * e - B * E.T @ e) / 2
        delta = B - d @ A[k + 1] @ d
        h = E.T @ A[k + 1] @ d + cross
        assert delta > 0
        A[k] = E.T @ A[k + 1] @ E + np.outer(h, h) / delta
        deltas[k + 1], local_h[k] = float(delta), h
        D, F = np.outer(d, d) / B, np.outer(cross, cross) / B
        Et = E + np.outer(d, cross) / B
        Ei = np.linalg.inv(Et)
        transfers[k] = np.block([[Et.T - F @ Ei @ D, F @ Ei], [-Ei @ D, Ei]])
    from_products = {N - 1: terminal}
    product_errors, product_denominators = {}, {}
    for k in range(N - 1):
        product = np.eye(4)
        for j in range(k, N - 1):
            product = product @ transfers[j]
        numerator = product[:2, :2] @ terminal + product[:2, 2:]
        denominator = product[2:, :2] @ terminal + product[2:, 2:]
        from_products[k] = np.linalg.solve(denominator.T, numerator.T).T
        product_errors[k] = float(np.max(np.abs(from_products[k] - A[k])))
        product_denominators[k] = float(np.linalg.det(denominator))
    assert max(product_errors.values(), default=0) < 1e-10

    # Explicit tail-Gram inverse representation, independently formed from H.
    M = np.zeros((N + 2, N + 2))
    M[0, 0] = 1 / (2 * K)
    M[0, 1:] = M[1:, 0] = -alpha / 2
    for i in range(N + 1):
        M[i + 1, i + 1] = beta[i] if i < N else 0.5
        for j in range(i + 1, N + 1):
            value = (
                beta[j] * H[j, i]
                - beta[j - 1] * H[j - 1, i]
                - beta[i] * int(j == i + 1)
            ) / 2
            M[i + 1, j + 1] = M[j + 1, i + 1] = value
    T = np.ones(N + 1)
    for j in range(1, N):
        T[j] = T[j - 1] * (1 - 1 / theta[j])
    T[N] = T[N - 1]
    eta = beta * T - np.r_[0, beta[:-1] * T[:-1]]
    tail_errors, tail_minimum_eigenvalues = {}, {}
    for k in range(N):
        Btail = (
            np.array(
                [
                    [-eta[j] / T[k], eta[j] / T[k] - alpha[j]]
                    for j in range(k + 1, N + 1)
                ]
            ).T
            / 2
        )
        tail = M[k + 2 :, k + 2 :]
        tail_formula = Btail @ np.linalg.solve(tail, Btail.T)
        tail_errors[k] = float(np.max(np.abs(tail_formula - A[k])))
        tail_minimum_eigenvalues[k] = float(np.linalg.eigvalsh(tail).min())
    assert max(tail_errors.values()) < 1e-10
    kernel_residual = float(np.max(np.abs(M @ np.r_[K, np.ones(N + 1)])))
    base_a_error = abs(A[0].sum() - (K - 2) / (2 * (K - 1) ** 2))
    assert kernel_residual < 1e-10 and base_a_error < 1e-10
    coefficients = {0: np.array([[1 / (2 * K)]]), N: np.zeros((0, 0))}
    for k in range(1, N):
        full = np.zeros((3, 3))
        full[:2, :2] = A[k]
        full[0, 2] = full[2, 0] = alpha[k] / 2
        full[2, 2] = -beta[k - 1] / 2
        if k == 1:
            collapse = np.array([[1.0, 0.0], [1.0, 1 - theta[1]], [0.0, 1.0]])
            coefficients[k] = collapse.T @ full @ collapse
        elif k == N - 1:
            coefficients[k] = full[np.ix_([0, 2], [0, 2])]
        else:
            coefficients[k] = full
    return dict(
        theta=theta,
        H=H,
        K=K,
        beta=beta,
        alpha=alpha,
        A=A,
        deltas=deltas,
        local_h=local_h,
        coefficients=coefficients,
        product_errors=product_errors,
        product_denominators=product_denominators,
        tail_errors=tail_errors,
        tail_minimum_eigenvalues=tail_minimum_eigenvalues,
        kernel_residual=kernel_residual,
        base_a_error=base_a_error,
    )


def numerical_checks(b4, probe):
    reports = []
    for N in (4, 6, 8):
        certificate = read_json(HERE / "b3_samples" / f"N{N}" / "certificate.json")
        if N == 6:
            assert b4["certificate_id"] == certificate["certificate_id"]
            saved_C = {
                int(k): np.asarray(value, float).reshape((len(value), len(value)))
                for k, value in b4["coeff_by_k"].items()
            }
        else:
            sample = next(item for item in probe["samples"] if item["N"] == N)
            assert sample["certificate_id"] == certificate["certificate_id"]
            saved_C = {
                row["k"]: np.asarray(row["adopted_C"], float).reshape(
                    (len(row["adopted_C"]), len(row["adopted_C"]))
                )
                for row in sample["observations"]
            }
        result = analytic_sample(N)
        L = float(json.loads(certificate["params_json"])["L"])
        errors = {
            k: float(
                np.max(np.abs(L * result["coefficients"][k] - saved_C[k]), initial=0)
            )
            for k in range(N + 1)
        }
        assert max(errors.values()) < 1e-7
        saved_D = np.diag(certificate["numerical_decomposition"]["D"])
        pivot_errors = {
            j: abs(result["deltas"][j] - saved_D[N - j]) for j in range(N + 1)
        }
        assert max(pivot_errors.values()) < 1e-7
        reports.append(
            {
                "N": N,
                "certificate_id": certificate["certificate_id"],
                "coefficient_max_abs_by_k": errors,
                "pivot_max_abs_by_gradient": pivot_errors,
                "finite_product_vs_riccati": result["product_errors"],
                "finite_product_denominator_determinants": result[
                    "product_denominators"
                ],
                "tail_Gram_vs_riccati": result["tail_errors"],
                "tail_Gram_minimum_eigenvalues": result["tail_minimum_eigenvalues"],
                "initial_A_sum_error": result["base_a_error"],
                "global_kernel_max_abs": result["kernel_residual"],
                "K": result["K"],
                "theta": result["theta"].tolist(),
                "alpha": result["alpha"].tolist(),
                "beta": result["beta"].tolist(),
                "A_by_k": {k: value.tolist() for k, value in result["A"].items()},
                "C_by_k": {
                    k: (L * value).tolist()
                    for k, value in result["coefficients"].items()
                },
                "delta_by_gradient": result["deltas"],
                "h_by_k": {k: value.tolist() for k, value in result["local_h"].items()},
            }
        )
        print(
            f"N={N}: coefficients max={max(errors.values()):.3e}; "
            f"pivots max={max(pivot_errors.values()):.3e}; "
            f"finite-product max={max(result['product_errors'].values()):.3e}"
        )
    return reports


def main():
    checks = symbolic_checks()
    print("Exact symbolic checks:", checks)
    b4 = read_json(STUDY / "state" / f"{NAME}_b4.json")
    probe = read_json(HERE / "block4_n8_basis_probe.json")
    assert b4["independent_reproduction"] is False
    assert b4["numerical_reconstruction"]["passed"]
    samples = numerical_checks(b4, probe)
    report = {
        "exact_symbolic_checks": checks,
        "sample_checks": samples,
        "read_files_sha256": READ_FILES,
        "solver_called": False,
        "all_N_coefficient_fit_used": False,
        "contamination_status_unchanged": True,
        "coefficient_definitions": "Explicit finite product of 4x4 transfer matrices with final 2x2 inverse; equivalent backward Riccati and tail-Gram inverse.",
        "conditional_domain": "L>0, beta_(k+1)>0, theta_(k+1)>1, delta_(k+1)>0; global kernel and tail positive definiteness establish normalization and denominators.",
        "positivity_proof_owned_by_separate_global_certificate_argument": True,
        "analytic_full_pep_verified_by_this_script": False,
        "lyapunov_proof_verified_by_this_script": False,
    }
    (HERE / "block5_coefficients_derivation.json").write_text(
        json.dumps(report, indent=2, allow_nan=False) + "\n", encoding="utf-8"
    )


if __name__ == "__main__":
    main()
