# This saved notebook fragment shares its caller's execution namespace.
# These names are supplied by the notebook cells or serialized proof source.
# ty: ignore[unresolved-reference]
# ruff: noqa: F821


def coeff_pattern(k, N, a):
    if k == 0:
        return sp.zeros(0, 0)
    q = sp.S(1) / (2 * a * N)
    return sp.Matrix([[0, -q, 0, 0], [-q, 0, 0, 0], [0, 0, 0, q], [0, 0, q, 0]])


formula_residuals = {}
for k in range(N_int + 1):
    guessed = np.array(coeff_pattern(k, N_int, sp.S(1)), dtype=float)
    error = float(np.max(np.abs(guessed - coeff_by_k[k]), initial=0.0))
    assert error <= 1e-4
    expected_functions = [0, 0] if k == 0 else [k / N_int, 1 / N_int]
    function_error = float(
        np.max(
            np.abs(np.array(function_coeff_by_k[k]) - expected_functions), initial=0.0
        )
    )
    assert function_error <= 1e-4 and abs(offset_by_k[k]) <= 1e-5
    formula_residuals[str(k)] = dict(
        quadratic=error, function=function_error, offset=abs(offset_by_k[k])
    )
    print(f"k={k}: candidate formula errors", formula_residuals[str(k)])
print("Coefficient formulas are finite-sample candidates, not an analytic proof.")
