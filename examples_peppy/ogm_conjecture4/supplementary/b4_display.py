# Loaded by the OGM notebook, which supplies this module's required globals.
# Not a standalone script; validate it through notebook execution.
# ty: ignore[unresolved-reference]
# ruff: noqa: F821

"""Formatting only: labeled rational approximations and full function terms."""

from fractions import Fraction


def show_coefficient_sample(k):
    C = coeff_by_k[k]
    labels = V_k_basis_labels(k)
    rational_display = np.empty(C.shape, dtype=object)
    for i, j in np.ndindex(C.shape):
        fraction = Fraction(float(C[i, j])).limit_denominator(1000000)
        rational_display[i, j] = (
            str(fraction.numerator)
            if fraction.denominator == 1
            else rf"\frac{{{fraction.numerator}}}{{{fraction.denominator}}}"
        )
    print(
        f"k={k}: C in order {labels}; fractions approximate the saved floating-point values"
    )
    pf.pprint_labeled_matrix(rational_display, labels, labels, precision=0)
    values = np.asarray(function_coordinate_samples[k], float)
    # Include all nonzero coordinates, even ones at solver-noise scale.
    indices = np.flatnonzero(values != 0)
    if indices.size:
        entries = []
        for value in values[indices]:
            if 0 < abs(value) < 1e-6:
                mantissa, exponent = f"{value:.16e}".split("e")
                entries.append(rf"{mantissa}\times 10^{{{int(exponent)}}}")
            else:
                entries.append(str(value))
        pf.pprint_labeled_matrix(
            np.asarray(entries, dtype=object).reshape(-1, 1),
            [b3["basis_scalars"][i] for i in indices],
            ["coefficient"],
            precision=0,
        )
    else:
        print("Function-value coordinates: all zero")
    print("Scalar offset: 0")
