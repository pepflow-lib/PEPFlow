"""De novo algebra-only search using this run's selected N=4 certificate.

No optimization solver is imported or called. Only NumPy and the standard
library are used. This is exploratory evidence, not an all-N proof.
"""

import hashlib
import json
from pathlib import Path

import numpy as np

# %% Load paths and build the method coordinates, without any optimization.
HERE = Path(__file__).resolve().parent
SOURCE = HERE / "b2_selected_capture.json"
SETUP = HERE.parent / "ogm_conjecture4_setup.py"


def theta_sequence(n):
    theta = [1.0]
    for k in range(n):
        theta.append((1 + np.sqrt(1 + (8 if k == n - 1 else 4) * theta[-1] ** 2)) / 2)
    return np.array(theta)


def coordinates(n):
    """Gradient coordinates of x_0,...,x_{n-1},y_n from current setup."""
    theta = theta_sequence(n)
    eye = np.eye(n + 1)
    x = np.zeros(n + 1)
    y = x.copy()
    out = []
    for k in range(n):
        out.append(x.copy())
        y_next = x - eye[k]
        x_next = (
            y_next
            + ((theta[k] - 1) / theta[k + 1]) * (y_next - y)
            + (theta[k] / theta[k + 1]) * (y_next - x)
        )
        x, y = x_next, y_next
    out.append(y)
    return np.array(out)


def sym_outer(a, b):
    return (np.outer(a, b) + np.outer(b, a)) / 2


def gradient_block(a, coords):
    n = len(a) - 1
    eye = np.eye(n + 1)
    block = np.zeros((n + 1, n + 1))
    for j in range(n + 1):
        block += a[j] * (-sym_outer(eye[j], coords[j]) + 0.5 * np.outer(eye[j], eye[j]))
    for j, b in enumerate(np.cumsum(a)[:-1]):
        delta = eye[j] - eye[j + 1]
        block += b * (
            sym_outer(eye[j + 1], coords[j] - coords[j + 1])
            + 0.5 * np.outer(delta, delta)
        )
    return block


def inspect_candidate(name, a, coords, tau, selected_a=None):
    block = gradient_block(a, coords)
    remainder = block - np.outer(a, a) / (4 * tau)
    result = {
        "name": name,
        "a": a.tolist(),
        "chain": np.cumsum(a)[:-1].tolist(),
        "sum_a": float(sum(a)),
        "minimum_a": float(min(a)),
        "schur_eigenvalues": np.linalg.eigvalsh(remainder).tolist(),
        "schur_times_ones": (remainder @ np.ones(len(a))).tolist(),
        "remainder": remainder.tolist(),
    }
    if selected_a is not None:
        result["max_error_to_selected_a"] = float(max(abs(a - selected_a)))
    return result


# %% Closed-form candidate derived from the equal-gradient null condition.
def closed_form_weights(n):
    theta = theta_sequence(n)
    q = theta[n - 1] ** 2
    s = theta[:n] ** 2
    chain = s * (2 * q - s) / (q * (2 * q - s + 1))
    return np.diff(np.r_[0.0, chain, 1.0])


# %% Compare actual candidate formulas, including the failed naive candidate.
def main():
    selected = json.loads(SOURCE.read_text())
    n = selected["N"]
    theta = theta_sequence(n)
    target = 1 / (2 * (2 * theta[n - 1] ** 2 + 1))
    tau = selected["tau_sol"]
    lam = np.array(selected["lambda_matrix"])
    order = list(range(n)) + [n + 1]
    a = lam[n, order]
    chain = np.array([lam[i, i + 1] if i < n - 1 else lam[i, n + 1] for i in range(n)])
    slack = np.array(selected["S_matrix"])
    coords = coordinates(n)
    block = gradient_block(a, coords)
    remainder = block - np.outer(a, a) / (4 * tau)
    naive = np.r_[4 * target * theta[:n], 2 * target]
    # At the conjectured rate a constant-gradient worst case makes the slack
    # quadratic vanish. PSD then requires H*1=0. Its pre-Schur form is linear:
    # B(a)*1 = a/(4*tau). Solve with sum(a)=1, without any SDP solve.
    linear = np.column_stack(
        [
            gradient_block(e, coords) @ np.ones(n + 1) - e / (4 * target)
            for e in np.eye(n + 1)
        ]
    )
    exact_null_a, _, _, _ = np.linalg.lstsq(
        np.vstack([linear, np.ones(n + 1)]), np.r_[np.zeros(n + 1), 1], rcond=None
    )
    closed_a = closed_form_weights(n)
    algebra_checks = []
    for check_n in range(1, 11):
        check_theta = theta_sequence(check_n)
        check_q = check_theta[check_n - 1] ** 2
        check_coords = coordinates(check_n)
        check_a = closed_form_weights(check_n)
        check = inspect_candidate(
            "closed-form candidate", check_a, check_coords, 1 / (2 * (2 * check_q + 1))
        )
        algebra_checks.append(
            {
                "N": check_n,
                "min_star_weight": check["minimum_a"],
                "sum_star_weight_error": abs(check["sum_a"] - 1),
                "minimum_schur_eigenvalue": check["schur_eigenvalues"][0],
                "smallest_nonnull_schur_eigenvalue": check["schur_eigenvalues"][1],
                "null_residual_max": max(abs(v) for v in check["schur_times_ones"]),
                "terminal_coordinate_formula_error": float(
                    max(
                        abs(
                            -check_coords[-1, :-1]
                            - (
                                2 * check_theta[:-1]
                                - (2 * check_theta[:-1] - 1)
                                * check_theta[:-1] ** 2
                                / check_q
                            )
                        )
                    )
                ),
            }
        )
    report = {
        "scope": "Current-run setup and selected certificate only; no new SDP solves, git/history, prior examples/results, or external mathematical sources.",
        "contamination_flag": "Parent reports existing run flag persists; no prior target result contents were read by this investigator.",
        "files_read": [
            p.relative_to(HERE.parents[2]).as_posix()
            for p in (SOURCE, SETUP, HERE / "b2_formula_search.json")
        ],
        "source_hashes": {
            p.name: hashlib.sha256(p.read_bytes()).hexdigest() for p in [SOURCE, SETUP]
        },
        "commands_consulted": [
            "Get-ChildItem -LiteralPath 'examples_peppy/ogm_conjecture4' -Force | Select-Object Name,Mode",
            "Get-Content -LiteralPath 'examples_peppy/ogm_conjecture4/ogm_conjecture4_setup.py'",
            "Get-Content -LiteralPath 'examples_peppy/ogm_conjecture4/supplementary/b2_selected_capture.json'",
            "Get-ChildItem -LiteralPath 'examples_peppy/ogm_conjecture4/state' | Select-Object Name",
            "@'\nimport json,numpy as np\nfrom pathlib import Path\np=Path('examples_peppy/ogm_conjecture4/supplementary/b2_selected_capture.json')\nd=json.loads(p.read_text());S=np.array(d['S_matrix']);a=np.array(d['lambda_matrix'])[4,[0,1,2,3,5]];t=d['tau_sol'];th=[1.]\nfor k in range(4): th.append((1+np.sqrt(1+(8 if k==3 else 4)*th[-1]**2))/2)\nH=S[2:,2:]-np.outer(a,a)/(4*t)\nprint('theta',th,'tau',t,'target',1/(2*(2*th[3]**2+1)))\nprint('a',a,'a/(4tau)',a/(4*t),'a/(4tau theta)',a[:4]/(4*t*np.array(th[:4])))\nprint('a cumulative',np.cumsum(a),'a sum',sum(a))\nprint('S eig',np.linalg.eigvalsh(S));print('Schur H',H);print('H eig',np.linalg.eigvalsh(H));print('H ones',H@np.ones(5))\n'@ | python -",
            "python examples_peppy/ogm_conjecture4/supplementary/b2_formula_search.py",
            "@'\nimport json\nfrom pathlib import Path\np=Path('examples_peppy/ogm_conjecture4/supplementary/b2_formula_search.json')\nd=json.loads(p.read_text())\nprint(json.dumps(d['algebra_only_N_checks'],indent=2))\n'@ | python -",
        ],
        "file_mutations": "Only supplementary/b2_formula_search.py was created/edited using apply_patch, and its execution creates/updates supplementary/b2_formula_search.json. No other files changed by this investigator.",
        "N": n,
        "theta": theta.tolist(),
        "target_tau": target,
        "selected_tau": tau,
        "star_weights": a.tolist(),
        "chain_weights": chain.tolist(),
        "chain_cumulative_balance_error": float(max(abs(chain - np.cumsum(a)[:-1]))),
        "star_sum_error": float(abs(sum(a) - 1)),
        "a_over_4tau": (a / (4 * tau)).tolist(),
        "a_over_4tau_theta": (a[:n] / (4 * tau * theta[:n])).tolist(),
        "slack_reconstruction_gradient_block_error": float(
            np.max(abs(block - slack[2:, 2:]))
        ),
        "selected_schur_eigenvalues": np.linalg.eigvalsh(remainder).tolist(),
        "selected_schur_max_abs": float(np.max(abs(remainder))),
        "selected_schur_frobenius_norm": float(np.linalg.norm(remainder)),
        "selected_schur_times_ones": (remainder @ np.ones(n + 1)).tolist(),
        "constant_gradient_distances": (-coords @ np.ones(n + 1)).tolist(),
        "null_linear_singular_values": np.linalg.svd(linear, compute_uv=False).tolist(),
        "closed_form_vs_linear_null_solution_max_error": float(
            max(abs(closed_a - exact_null_a))
        ),
        "closed_form": {
            "notation": "q=theta_(N-1)^2, s_i=theta_i^2, b_-1=0, b_N=1",
            "chain": "b_i=s_i*(2*q-s_i)/(q*(2*q-s_i+1)), i=0,...,N-1",
            "star": "a_i=b_i-b_(i-1), i=0,...,N-1; a_y=1/(q+1)",
            "status": "Candidate formula derived algebraically; numerical PSD checks only, no all-N PSD proof and no assertion that it is the exact selected floating-point certificate.",
        },
        "algebra_only_N_checks": algebra_checks,
        "excluded_historical_explorations": {
            "note": "Before the parent relayed the inherited explicit-authorization constraint above N=12, this investigator also ran algebra-only checks at N=20 and N=30, with no SDP. They are recorded honestly here and excluded from accepted sampled evidence. This frozen script reruns only N=1,...,10.",
            "checks": [
                {
                    "N": 20,
                    "min_star_weight": 0.008053413704265044,
                    "minimum_schur_eigenvalue": 2.2206297715900884e-15,
                    "smallest_nonnull_schur_eigenvalue": 6.260428831697893e-08,
                    "null_residual_max": 1.5432100042289676e-14,
                },
                {
                    "N": 30,
                    "min_star_weight": 0.003799354143835698,
                    "minimum_schur_eigenvalue": -4.093773571660928e-15,
                    "smallest_nonnull_schur_eigenvalue": 6.4418038063206684e-09,
                    "null_residual_max": 4.7455095408821535e-14,
                },
            ],
        },
        "candidates": [
            inspect_candidate(
                "naive a_i=4*tau*theta_i; a_y=2*tau", naive, coords, target, a
            ),
            inspect_candidate(
                "linear constant-gradient null conditions plus sum(a)=1",
                exact_null_a,
                coords,
                target,
                a,
            ),
            inspect_candidate(
                "closed form b_i=s_i*(2*q-s_i)/(q*(2*q-s_i+1)); a_i=b_i-b_(i-1)",
                closed_a,
                coords,
                target,
                a,
            ),
        ],
        "derivations": [
            "With chain b_i=lambda_(x_i,x_(i+1)) (x_N label here means y_N) and star a_i=lambda_(star,x_i), scalar function balance gives b_i=sum_(j<=i) a_j and sum_(j<=N) a_j=1.",
            "Write d=x0-xstar and G=(g0,...,g_(N-1),g_y). The ideal reconstructed slack is tau||d||^2-<d,sum a_i g_i>+G^T B G = tau||d-sum a_i g_i/(2*tau)||^2+G^T H G, H=B-aa^T/(4*tau).",
            "For equal gradients, the setup gives x_i=d-(theta_i^2-1)g, i<N, and y_N=d-theta_(N-1)^2*g. With sum(a)=1, 1^T B 1=theta_(N-1)^2+1/2=1/(4*target_tau).",
            "At target_tau, PSD of H requires H*1=0, equivalently B(a)*1=a/(4*target_tau). These are linear necessary conditions; positivity still needs checking.",
            "Let y_N=d-sum h_i*g_i, q=theta_(N-1)^2, r_i=theta_i^2-1. The null condition is (2*q-r_i)*a_i=(r_i-r_(i-1))*b_(i-1)+h_i. Hence (2*q-r_i)*b_i=sum_(j<=i)h_j.",
            "The setup recurrence gives h_i=2*theta_i-(2*theta_i-1)*theta_i^2/q. This follows by telescoping product_(k=i+1 to N-1)(1-1/theta_k)=theta_i^2/q, using theta_k^2-theta_k=theta_(k-1)^2.",
            "sum_(j<=i)h_j=2*theta_i^2-theta_i^4/q because sum theta_j=theta_i^2 and sum (2*theta_j-1)*theta_j^2=theta_i^4. Substitution yields the reported closed-form b_i and a_i.",
            "Nonnegativity of these weights follows since b(s)=s*(2q-s)/(q*(2q-s+1)) is increasing for 0<=s<=q: b'(s)=[1-(2q+1)/(2q-s+1)^2]/q>=0. Also b(q)=q/(q+1). An all-N proof that H is PSD remains unresolved here.",
        ],
    }
    path = HERE / "b2_formula_search.json"
    path.write_text(json.dumps(report, indent=2) + "\n")
    print(
        json.dumps(
            {
                k: report[k]
                for k in [
                    "N",
                    "theta",
                    "target_tau",
                    "chain_cumulative_balance_error",
                    "slack_reconstruction_gradient_block_error",
                    "null_linear_singular_values",
                    "candidates",
                ]
            },
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
