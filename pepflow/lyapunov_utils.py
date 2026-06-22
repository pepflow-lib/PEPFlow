# Copyright: 2026 The PEPFlow Developers
#
# Licensed to the Apache Software Foundation (ASF) under one
# or more contributor license agreements.  See the NOTICE file
# distributed with this work for additional information
# regarding copyright ownership.  The ASF licenses this file
# to you under the Apache License, Version 2.0 (the
# "License"); you may not use this file except in compliance
# with the License.  You may obtain a copy of the License at
#
#   http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing,
# software distributed under the License is distributed on an
# "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY
# KIND, either express or implied.  See the License for the
# specific language governing permissions and limitations
# under the License.

from __future__ import annotations

import warnings
from itertools import combinations
from math import comb
from typing import TYPE_CHECKING

import numpy as np
from scipy.linalg import ldl

from pepflow import expression_manager as exm
from pepflow import ipython_utils
from pepflow import pep_context as pc
from pepflow import utils
from pepflow.pep_result import MatrixWithNames

if TYPE_CHECKING:
    from pepflow.scalar import Scalar
    from pepflow.vector import Vector


def vectors_in_column_space(
    V: Scalar,
    vecs: list[Vector],
    pep_context: pc.PEPContext | None = None,
    *,
    resolve_parameters: dict[str, utils.NUMERICAL_TYPE] | None = None,
    rtol: float = 1e-7,
    atol: float = 1e-7,
) -> list[Vector]:
    """Collect vectors that lie in the column space of ``V``.

    Args:
        V (:class:`Scalar`): Scalar expression built from vector inner products.
            Its evaluated matrix is used for the column-space test.
        vecs (list[:class:`Vector`]): Candidate vectors to test for membership
            in ``col(V)``.
        pep_context (:class:`PEPContext` | None): The :class:`PEPContext` object
            we consider. `None` if we consider the current global
            :class:`PEPContext` object.
        resolve_parameters (dict[str, :class:`NUMERICAL_TYPE`] | None): A
            dictionary that maps the name of parameters to the numerical values.
        rtol (float): Relative tolerance for numerical checks.
        atol (float): Absolute tolerance for numerical checks.

    Returns:
        list[:class:`Vector`]: Vectors that lie in ``col(V)`` within the given
        tolerances.
    """
    if not vecs:
        return []

    if pep_context is None:
        pep_context = pc.get_current_context()
    if pep_context is None:
        raise RuntimeError("Did you forget to create a context?")
    pm = exm.ExpressionManager(pep_context, resolve_parameters=resolve_parameters)
    V_coords = np.asarray(pm.eval_scalar(V).inner_prod_coords, dtype=float)

    # Build an orthonormal basis for the column space of V.
    U, singular_values, _ = np.linalg.svd(V_coords, full_matrices=False)
    scale = singular_values[0] if singular_values.size else 0.0
    tol = atol + rtol * scale
    rank = np.sum(singular_values > tol)
    column_space_basis = U[:, :rank]

    # Detect column-space membership using projection residuals.
    vector_coords = np.column_stack(
        [np.asarray(pm.eval_vector(v).coords, dtype=float) for v in vecs]
    )
    projections = column_space_basis @ (column_space_basis.T @ vector_coords)
    residuals = np.linalg.norm(vector_coords - projections, axis=0)
    vector_norms = np.linalg.norm(vector_coords, axis=0)
    is_in_column_space = residuals <= atol + rtol * vector_norms

    collected_column_space_vectors = [
        vec for vec, in_column_space in zip(vecs, is_in_column_space) if in_column_space
    ]
    return collected_column_space_vectors


def select_independent_subset(
    vecs: list[Vector],
    pep_context: pc.PEPContext | None = None,
    *,
    resolve_parameters: dict[str, utils.NUMERICAL_TYPE] | None = None,
    tol: float = 1e-7,
) -> tuple[list[Vector], list[int]]:
    """Select linearly independent vectors in input order using greedy Gram-Schmidt.

    Args:
        vecs (list[:class:`Vector`]): Candidate vectors.
        pep_context (:class:`PEPContext` | None): The :class:`PEPContext` object
            we consider. `None` if we consider the current global
            :class:`PEPContext` object.
        resolve_parameters (dict[str, :class:`NUMERICAL_TYPE`] | None): A
            dictionary that maps the name of parameters to the numerical values.
        tol (float): Relative tolerance for independence checks.

    Returns:
        tuple[list[Vector], list[int]]: The selected vectors and their indices in
        ``vecs``.

    Note:
        The order of ``vecs`` matters because vectors are selected greedily.

    Example:
        >>> import pepflow as pf
        >>> ctx = pf.PEPContext("ctx").set_as_current()
        >>> e1 = pf.Vector(is_basis=True, tags=["e_1"])
        >>> e2 = pf.Vector(is_basis=True, tags=["e_2"])
        >>> selected, _ = select_independent_subset(
        ...     [e1, 2 * e1, e1 + e2, e2], pep_context=ctx
        ... )
        >>> selected == [e1, e1 + e2]
        True
    """
    if pep_context is None:
        pep_context = pc.get_current_context()
    if pep_context is None:
        raise RuntimeError("Did you forget to create a context?")
    pm = exm.ExpressionManager(pep_context, resolve_parameters=resolve_parameters)

    orthonormal_basis = []
    selected = []
    idx = []

    for i, v in enumerate(vecs):
        v_coords = np.asarray(pm.eval_vector(v).coords, dtype=float)
        v_norm = np.linalg.norm(v_coords)
        if v_norm == 0:
            continue

        # Remove components already spanned by selected vectors.
        r = v_coords.copy()
        for basis_vec in orthonormal_basis:
            r -= basis_vec * (basis_vec @ r)

        # Select vectors with a non-negligible residual direction.
        r_norm = np.linalg.norm(r)
        if r_norm > tol * v_norm:
            new_basis_vec = r / r_norm
            orthonormal_basis.append(new_basis_vec)
            selected.append(v)
            idx.append(i)

    return selected, idx


def find_symmetric_coefficient_matrix(
    V: Scalar,
    vecs: list[Vector],
    pep_context: pc.PEPContext | None = None,
    *,
    resolve_parameters: dict[str, utils.NUMERICAL_TYPE] | None = None,
    indep_tol: float = 1e-7,
    span_tol: float = 1e-5,
) -> np.ndarray:
    """Find the symmetric coefficient matrix for the inner-product part of ``V``.

    Finds a coefficient matrix ``A`` such that the inner-product part of ``V``
    satisfies

    .. math:: V \\approx [v_1 \\; \\cdots \\; v_m] A [v_1 \\; \\cdots \\; v_m]^\\top.

    Equivalently, finds ``A[i, j]`` such that

    .. math:: V \\approx \\sum_{i \\le j} A_{ij} B_{ij},

    where

    .. math:: B_{ii} = v_i v_i^\\top,\\quad B_{ij} = v_i v_j^\\top + v_j v_i^\\top \\quad (i < j).

    Args:
        V (:class:`Scalar`): Scalar expression whose inner-product coefficients
            are decomposed.
        vecs (list[:class:`Vector`]): Vector list used to build the
            decomposition basis.
        pep_context (:class:`PEPContext` | None): The :class:`PEPContext` object
            we consider. `None` if we consider the current global
            :class:`PEPContext` object.
        resolve_parameters (dict[str, :class:`NUMERICAL_TYPE`] | None): A
            dictionary that maps the name of parameters to the numerical values.
        indep_tol (float): Tolerance for linear-independence rank checks of ``vecs``.
        span_tol (float): Tolerance for checking whether ``V`` is represented
            by the span of ``vecs``.

    Raises:
        ValueError: If inputs have incompatible shapes or ``vecs`` are linearly
            dependent.

    Returns:
        np.ndarray: Symmetric coefficient matrix.
    """
    if pep_context is None:
        pep_context = pc.get_current_context()
    if pep_context is None:
        raise RuntimeError("Did you forget to create a context?")
    pm = exm.ExpressionManager(pep_context, resolve_parameters=resolve_parameters)

    V_coords = np.asarray(pm.eval_scalar(V).inner_prod_coords, dtype=float)
    vecs_coords = [
        np.asarray(pm.eval_vector(u).coords, dtype=float).ravel() for u in vecs
    ]

    return _find_symmetric_coefficient_matrix_from_coords(
        V_coords,
        vecs_coords,
        indep_tol=indep_tol,
        span_tol=span_tol,
    )


def _find_symmetric_coefficient_matrix_from_coords(
    V_coords: np.ndarray,
    vecs: list[np.ndarray],
    *,
    indep_tol: float = 1e-7,
    span_tol: float = 1e-5,
) -> np.ndarray:
    """Numerical backend for symmetric decomposition from pre-evaluated coords."""
    num_vecs = len(vecs)

    # Handle the empty-basis case before stacking vecs.
    if num_vecs == 0:
        if np.linalg.norm(V_coords, ord="fro") > span_tol:
            raise ValueError("The columns of V_coords are not contained in span(vecs).")
        return np.zeros((0, 0))

    vecs_matrix = np.stack(vecs, axis=1)
    vecs_rank = np.linalg.matrix_rank(vecs_matrix, tol=indep_tol)

    # Check whether the columns of V_coords lie in span(vecs).
    projection_coeffs, *_ = np.linalg.lstsq(vecs_matrix, V_coords, rcond=None)
    projection_residual = np.linalg.norm(
        V_coords - vecs_matrix @ projection_coeffs, ord="fro"
    )
    if projection_residual > span_tol * max(1.0, np.linalg.norm(V_coords, ord="fro")):
        raise ValueError("The columns of V_coords are not contained in span(vecs).")

    # Require an independent vector basis for the coefficient matrix
    if vecs_rank < num_vecs:
        raise ValueError(
            f"vecs are linearly dependent: {num_vecs} vectors but rank is {vecs_rank}."
        )

    # Build flattened symmetric outer-product basis matrices.
    row_idx, col_idx = np.triu_indices(num_vecs)
    flattened_outer_products = np.einsum(
        "ai,bj->ijab", vecs_matrix, vecs_matrix
    ).reshape(num_vecs, num_vecs, -1)
    flattened_basis = flattened_outer_products[row_idx, col_idx]

    # Symmetrize off-diagonal basis entries: v_i v_j^T -> v_i v_j^T + v_j v_i^T.
    off_diagonal = row_idx != col_idx
    flattened_basis[off_diagonal] += flattened_outer_products[
        col_idx[off_diagonal], row_idx[off_diagonal]
    ]

    # Solve the vectorized least-squares problem for the coefficients
    stacked_basis = flattened_basis.T
    V_flattened = V_coords.reshape(-1)
    coeffs, *_ = np.linalg.lstsq(stacked_basis, V_flattened, rcond=None)

    # Place solved coefficients back into a symmetric matrix
    coeff_matrix = np.zeros((num_vecs, num_vecs))
    for i, j, c in zip(row_idx, col_idx, coeffs):
        coeff_matrix[i, j] = c
        coeff_matrix[j, i] = c
    return coeff_matrix


def find_basis_with_sparsest_coefficients(
    V: Scalar,
    vecs: list[Vector],
    *,
    pep_context: pc.PEPContext | None = None,
    resolve_parameters: dict[str, utils.NUMERICAL_TYPE] | None = None,
    fixed_vectors: list[Vector] | None = None,
    zero_tol: float = 1e-6,
    indep_tol: float = 1e-7,
    span_tol: float = 1e-5,
) -> tuple[list[Vector], np.ndarray]:
    """Find a basis whose coefficient matrix sparsely represents inner products.

    Among linearly independent subsets of size ``rank(vecs)``, this function
    finds a subset whose coefficient matrix for the inner-product part of ``V``
    has the maximum number of zero entries.

    Args:
        V (:class:`Scalar`): Scalar expression whose inner-product coefficients
            are decomposed.
        vecs (list[:class:`Vector`]): Candidate vectors used for subset search.
        pep_context (:class:`PEPContext` | None): The :class:`PEPContext` object
            we consider. `None` if we consider the current global
            :class:`PEPContext` object.
        resolve_parameters (dict[str, :class:`NUMERICAL_TYPE`] | None):
            A dictionary that maps the name of parameters to the numerical values.
        fixed_vectors (list[:class:`Vector`] | None): Vectors that must be
            included in every searched subset. Each vector must be present in
            ``vecs``.
        zero_tol (float): Absolute threshold for counting near-zero
            coefficients.
        indep_tol (float): Tolerance for linear-independence rank checks.
        span_tol (float): Tolerance for checking whether ``V`` is represented
            by the span of each candidate basis.

    Returns:
        tuple[list[Vector], np.ndarray]: A best basis and its sparsest
        symmetric coefficient matrix.
    """
    if pep_context is None:
        pep_context = pc.get_current_context()
    if pep_context is None:
        raise RuntimeError("Did you forget to create a context?")
    pm = exm.ExpressionManager(pep_context, resolve_parameters=resolve_parameters)

    if not vecs:
        return [], np.zeros((0, 0))

    V_coords = np.asarray(pm.eval_scalar(V).inner_prod_coords, dtype=float)
    vecs_coords = [
        np.asarray(pm.eval_vector(u).coords, dtype=float).ravel() for u in vecs
    ]
    rank = np.linalg.matrix_rank(np.stack(vecs_coords, axis=1), tol=indep_tol)
    fixed_vectors = fixed_vectors or []

    # Find fixed-vector indices for constrained subset search
    fixed_idx: list[int] = []
    if fixed_vectors:
        # Validate that every fixed vector is available in the input vectors
        not_in_vecs = [v for v in fixed_vectors if v not in vecs]
        if not_in_vecs:
            not_in_vecs_str = ", ".join(str(v) for v in not_in_vecs)
            raise ValueError(
                f"`fixed_vectors` must be contained in `vecs`. Missing: {not_in_vecs_str}"
            )

        # Collect fixed-vector indices
        fixed_idx = sorted({vecs.index(v) for v in fixed_vectors})

    if len(fixed_idx) > rank:
        raise ValueError(
            f"Too many fixed vectors: {len(fixed_idx)} > rank(vecs)={rank}."
        )

    best_basis: list[Vector] = []
    sparsest_coeff_matrix = np.zeros((0, 0))
    max_zeros = -1

    fixed_idx_set = set(fixed_idx)
    free_idx = [i for i in range(len(vecs)) if i not in fixed_idx_set]
    num_free_to_pick = rank - len(fixed_idx)

    # The search cost scales with the number of candidate subsets.
    num_subsets = comb(len(free_idx), num_free_to_pick)
    if num_subsets > 1_000:
        warnings.warn(
            f"Exhaustive subset search may be slow: checking {num_subsets} subsets."
        )

    # Search all feasible bases and keep the one with the sparsest coefficients
    for picked_free in combinations(free_idx, num_free_to_pick):
        idx = tuple(sorted(fixed_idx + list(picked_free)))
        candidate_basis = [vecs[i] for i in idx]
        candidate_basis_coords = [vecs_coords[i] for i in idx]

        # Skip subsets that do not span the same space as the input vectors
        candidate_rank = np.linalg.matrix_rank(
            np.stack(candidate_basis_coords, axis=1), tol=indep_tol
        )
        if candidate_rank < rank:
            continue

        # Sparsity score: count near-zero entries in the coefficient matrix
        coeff_matrix = _find_symmetric_coefficient_matrix_from_coords(
            V_coords,
            candidate_basis_coords,
            indep_tol=indep_tol,
            span_tol=span_tol,
        )
        num_zeros = int(np.sum(np.abs(coeff_matrix) < zero_tol))

        # Update the best basis
        if num_zeros > max_zeros:
            max_zeros = num_zeros
            best_basis = candidate_basis
            sparsest_coeff_matrix = coeff_matrix

    if max_zeros < 0 and fixed_vectors:
        fixed_s = ", ".join(str(v) for v in fixed_vectors)
        raise ValueError(
            f"No feasible independent subset satisfies `fixed_vectors`: {fixed_s}"
        )

    return best_basis, sparsest_coeff_matrix


def complete_basis_with_sparsifying_last_vector(
    V: Scalar,
    fixed_basis_vectors: list[Vector],
    pep_context: pc.PEPContext | None = None,
    *,
    resolve_parameters: dict[str, utils.NUMERICAL_TYPE] | None = None,
    rtol: float = 1e-10,
    normalize_last: bool = False,
) -> tuple[np.ndarray, np.ndarray]:
    """Complete a basis with a vector that sparsifies the coefficient matrix.

    Given fixed columns ``fixed_basis_vectors = [v_1, ..., v_{r-1}]``, this
    routine chooses a final vector ``v_r`` in ``col(V)`` and may
    shift it by a linear combination of ``fixed_basis_vectors`` to eliminate the
    last off-diagonal block of the coefficient matrix when possible.

    Args:
        V (:class:`Scalar`): Symmetric scalar expression with
            ``inner_prod_coords``.
        fixed_basis_vectors (list[:class:`Vector`]): Fixed basis vectors.
        pep_context (:class:`PEPContext` | None): The :class:`PEPContext` object
            we consider. `None` if we consider the current global
            :class:`PEPContext` object.
        resolve_parameters (dict[str, :class:`NUMERICAL_TYPE`] | None): A
            dictionary that maps the name of parameters to the numerical values.
        rtol (float): Relative numerical tolerance.
        normalize_last (bool): If ``True``, rescale the final vector so the
            last diagonal coefficient becomes ``+1`` or ``-1``.

    Returns:
        tuple[np.ndarray, np.ndarray]: The adjusted final vector and the
        updated coefficient matrix.
    """
    if pep_context is None:
        pep_context = pc.get_current_context()
    if pep_context is None:
        raise RuntimeError("Did you forget to create a context?")
    pm = exm.ExpressionManager(pep_context, resolve_parameters=resolve_parameters)

    V_coords = np.asarray(pm.eval_scalar(V).inner_prod_coords, dtype=float)
    fixed_basis_matrix = np.stack(
        [
            np.asarray(pm.eval_vector(v).coords, dtype=float).ravel()
            for v in fixed_basis_vectors
        ],
        axis=1,
    )

    def _orthonormal_column_basis(A: np.ndarray) -> np.ndarray:
        """Orthonormal basis for col(A) via SVD."""
        U, singular_values, _ = np.linalg.svd(A, full_matrices=False)
        if singular_values.size == 0:
            return np.zeros((A.shape[0], 0))
        tol = rtol * singular_values[0]
        rank = int(np.sum(singular_values > tol))
        return U[:, :rank]

    num_fixed = fixed_basis_matrix.shape[1]
    rank = num_fixed + 1

    # Build an orthonormal basis for col(V)
    range_basis = _orthonormal_column_basis(V_coords)
    if range_basis.shape[1] != rank:
        raise ValueError(
            f"col(V) dimension is {range_basis.shape[1]}, "
            f"expected r={rank}. Adjust rtol or check inputs."
        )

    # Check that fixed vectors lie in col(V)
    projected_fixed = range_basis @ (range_basis.T @ fixed_basis_matrix)
    projection_residual = np.linalg.norm(
        fixed_basis_matrix - projected_fixed, ord="fro"
    ) / max(np.linalg.norm(fixed_basis_matrix, ord="fro"), 1.0)
    if projection_residual > 1e3 * rtol:
        raise ValueError(
            "Columns of fixed_basis_vectors are not in col(V) "
            f"(projection residual ratio {projection_residual:.2e})."
        )

    # Build an orthonormal basis for the fixed-vector span and check independence
    fixed_orthonormal_basis = _orthonormal_column_basis(projected_fixed)
    if fixed_orthonormal_basis.shape[1] != num_fixed:
        raise ValueError(
            "fixed_basis_vectors columns appear dependent (numerically) inside col(V)."
        )

    # Pick the final direction in col(V) to complete the basis
    range_complement = range_basis - fixed_orthonormal_basis @ (
        fixed_orthonormal_basis.T @ range_basis
    )
    complement_basis = _orthonormal_column_basis(range_complement)
    initial_last_vector = complement_basis[:, 0]

    # Compute the coefficient matrix for the completed basis
    completed_basis_vectors = [fixed_basis_matrix[:, i] for i in range(num_fixed)] + [
        initial_last_vector
    ]
    coeff_matrix = _find_symmetric_coefficient_matrix_from_coords(
        V_coords,
        completed_basis_vectors,
        indep_tol=rtol,
    )

    cross_coeffs = coeff_matrix[:-1, -1]
    last_coeff = coeff_matrix[-1, -1]

    # Sparsify by shifting only the last vector
    if abs(last_coeff) <= rtol:
        # If the last coefficient is zero, the restricted shift cannot remove cross terms
        sparsifying_last_vector = initial_last_vector
        block_diag_coeff_matrix = coeff_matrix
    else:
        # Otherwise choose a shift that eliminates the last cross-block
        shift_coeffs = cross_coeffs / last_coeff
        sparsifying_last_vector = (
            initial_last_vector + fixed_basis_matrix @ shift_coeffs
        )

        fixed_block = coeff_matrix[:-1, :-1]
        shifted_fixed_block = (
            fixed_block - np.outer(cross_coeffs, cross_coeffs) / last_coeff
        )
        block_diag_coeff_matrix = np.zeros((rank, rank), dtype=float)
        block_diag_coeff_matrix[:-1, :-1] = shifted_fixed_block
        block_diag_coeff_matrix[-1, -1] = last_coeff

        # Optionally normalize the last coefficient to +/-1
        if normalize_last:
            last_vector_scale = np.sqrt(abs(block_diag_coeff_matrix[-1, -1]))
            sparsifying_last_vector = sparsifying_last_vector * last_vector_scale
            block_diag_coeff_matrix[-1, -1] = np.sign(block_diag_coeff_matrix[-1, -1])

    return sparsifying_last_vector, block_diag_coeff_matrix


def ldl_decompose_with_reversed_basis(
    S: MatrixWithNames, basis: list[Vector], print_output: bool = True
) -> tuple[np.ndarray, list[Vector]]:
    """Run LDL on a reversed-basis matrix and return labeled factors.

    This routine assumes the input basis and matrix labels follow the same
    "earlier iterates first" convention. It reverses both orders, runs LDL,
    and applies LDL permutation to labels/basis when needed.

    Args:
        S (:class:`MatrixWithNames`): Named symmetric matrix to decompose.
        basis (list[:class:`Vector`]): Basis vectors aligned with ``S.row_names``.
        print_output (bool): Whether to pretty-print ``L^T`` (labeled) and ``D``.

    Raises:
        ValueError: If reversed basis labels do not match reversed matrix labels.

    Returns:
        tuple[np.ndarray, list[:class:`Vector`]]: The diagonal/block-diagonal
        matrix ``D`` from LDL and the linear forms ``ell`` built from rows of
        the labeled transpose of the LDL lower factor.
    """
    # Assuming the original basis is ordered by gradients at earlier iterates first,
    # reverse the basis order so gradients at later iterates appear first.
    S_reversed = S.matrix[::-1, :][:, ::-1]
    names_rev = S.row_names[::-1]
    reversed_basis = basis[::-1]

    # Check that matrix labels and basis vectors stay aligned
    basis_names_rev = [repr(v) for v in reversed_basis]
    if names_rev != basis_names_rev:
        raise ValueError(
            "Reversed matrix labels and reversed basis labels do not match. "
            f"names_rev={names_rev}, basis_names_rev={basis_names_rev}"
        )

    # Apply any LDL permutation consistently to factors, labels, and basis
    lower_factor, D, perm = ldl(S_reversed)
    perm = np.asarray(perm, dtype=int)
    if not np.array_equal(perm, np.arange(len(perm))):
        lower_factor = lower_factor[perm, :]
        names_rev = [names_rev[i] for i in perm]
        reversed_basis = [reversed_basis[i] for i in perm]

    # Build the linear forms from rows of the transposed lower factor
    lower_factor_T = lower_factor.T
    ell = [
        lower_factor_T[i, :].T @ reversed_basis for i in range(lower_factor_T.shape[0])
    ]

    # Optionally display the labeled LDL factors
    if print_output:
        row_labels = [rf"\ell_{{{i + 1}}}" for i in range(lower_factor.shape[0])]
        labeled_lower_factor_T = MatrixWithNames(
            matrix=lower_factor_T,
            row_names=row_labels,
            col_names=names_rev,
        )
        labeled_lower_factor_T.pprint()
        ipython_utils.pprint_matrix(D)

    return D, ell
