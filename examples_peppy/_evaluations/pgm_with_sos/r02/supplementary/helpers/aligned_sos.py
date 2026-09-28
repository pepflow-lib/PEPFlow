"""Align the supplied square factors with the same saved numerical Gram slack."""

import numpy as np
from scipy.linalg import polar

import pepflow as pf


def aligned_squares(certificate, ctx):
    S = np.asarray(certificate["S_matrix"], dtype=float)
    values, vectors = np.linalg.eigh((S + S.T) / 2)
    assert values.min() >= 0, "This exact numerical alignment requires a PSD saved S"
    sqrt_S = (vectors * np.sqrt(values)) @ vectors.T
    decomposition = certificate["numerical_decomposition"]
    D = np.asarray(decomposition["D"], dtype=float)
    E = np.asarray(decomposition["ell_coords"], dtype=float)
    assert np.array_equal(D, np.diag(np.diag(D))) and np.diag(D).min() >= 0
    supplied_factors = np.sqrt(np.diag(D))[:, None] * E
    Q, _ = polar(supplied_factors @ sqrt_S)
    aligned = Q @ sqrt_S
    assert np.allclose(aligned.T @ aligned, S, atol=1e-10, rtol=0)
    basis = ctx.basis_vectors()
    pieces = {
        label: sum((float(coef) * v for coef, v in zip(row, basis)), pf.Vector.zero())
        ** 2
        for label, row in zip(decomposition["piece_labels"], aligned)
    }
    return pieces, dict(
        method="polar alignment of supplied factors to saved S",
        factors=aligned.tolist(),
        factor_max_change=float(np.max(abs(aligned - supplied_factors))),
        reconstruction_max_abs=float(np.max(abs(aligned.T @ aligned - S))),
    )
