# This saved notebook fragment shares its caller's execution namespace.
# These names are supplied by the notebook cells or serialized proof source.
# ty: ignore[unresolved-reference]
# ruff: noqa: F821


def coeff_pattern(k, N, a):
    if k == 0:
        return np.zeros((0, 0))
    C = np.zeros((4, 4))
    C[0, 1] = C[1, 0] = -1 / (2 * a * N)
    C[2, 3] = C[3, 2] = 1 / (2 * a * N)
    return C


fit_residuals = {}
for k in required_indices:
    fit_residuals[str(k)] = {
        "quadratic": max_abs(
            coeff_by_k[k] - coeff_pattern(k, N_int, float(params_sp["alpha"]))
        ),
        "h": abs(
            function_samples[k]["h"]
            - (0 if k == 0 else 1 / (float(params_sp["alpha"]) * N_int))
        ),
        "f": abs(function_samples[k]["f"] - k / N_int),
        "offset": abs(function_samples[k]["offset"]),
    }
    assert max(fit_residuals[str(k)].values()) < 1e-4
print("Candidate formula comparison:", fit_residuals)
