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

from typing import Iterator

import numpy as np
import pytest

from pepflow import lyapunov_utils
from pepflow import pep_context as pc
from pepflow import registry as reg
from pepflow import scalar, vector
from pepflow.pep_result import MatrixWithNames


@pytest.fixture
def pep_context() -> Iterator[pc.PEPContext]:
    """Prepare the pep context and reset global state at the end."""

    ctx = pc.PEPContext("test").set_as_current()
    yield ctx
    pc.set_current_context(None)
    pc.GLOBAL_CONTEXT_DICT.clear()
    reg.REGISTERED_FUNC_AND_OPER_DICT.clear()


@pytest.fixture
def basis_vectors(pep_context: pc.PEPContext):
    e1 = vector.Vector(is_basis=True, tags=["e_1"])
    e2 = vector.Vector(is_basis=True, tags=["e_2"])
    return e1, e2


def test_vectors_in_column_space_filters_candidates(
    pep_context: pc.PEPContext, basis_vectors
):
    e1, e2 = basis_vectors
    two_e1 = 2 * e1
    candidates = [e1, e2, two_e1, e1 + e2]

    selected = lyapunov_utils.vectors_in_column_space(
        e1**2, candidates, pep_context=pep_context
    )

    assert selected == [e1, two_e1]


def test_vectors_in_column_space_handles_degenerate_cases(
    pep_context: pc.PEPContext,
):
    zero_dim_V = scalar.Scalar.zero()

    assert (
        lyapunov_utils.vectors_in_column_space(zero_dim_V, [], pep_context=pep_context)
        == []
    )

    e1 = vector.Vector(is_basis=True, tags=["e_1"])
    zero_vector = vector.Vector.zero()

    assert (
        lyapunov_utils.vectors_in_column_space(
            scalar.Scalar.zero(), [], pep_context=pep_context
        )
        == []
    )
    assert lyapunov_utils.vectors_in_column_space(
        scalar.Scalar.zero(), [zero_vector, e1], pep_context=pep_context
    ) == [zero_vector]


def test_select_independent_subset_skips_dependent_vectors(
    pep_context: pc.PEPContext, basis_vectors
):
    e1, e2 = basis_vectors
    e1_plus_e2 = e1 + e2
    candidates = [e1, 2 * e1, e1_plus_e2, e2]

    selected, indices = lyapunov_utils.select_independent_subset(
        candidates, pep_context=pep_context
    )

    assert selected == [e1, e1_plus_e2]
    assert indices == [0, 2]


def test_find_symmetric_coefficient_matrix_recovers_known_coefficients(
    pep_context: pc.PEPContext, basis_vectors
):
    e1, e2 = basis_vectors
    V = 2 * e1**2 + 3 * (e1 * e2) + 5 * e2**2

    coeff_matrix = lyapunov_utils.find_symmetric_coefficient_matrix(
        V, [e1, e2], pep_context=pep_context
    )

    expected = np.array([[2.0, 1.5], [1.5, 5.0]])
    np.testing.assert_allclose(coeff_matrix, expected, atol=1e-10)


def test_find_symmetric_coefficient_matrix_helper_handles_edge_cases():
    coeff_matrix = lyapunov_utils._find_symmetric_coefficient_matrix_from_coords(
        np.zeros((0, 0)), []
    )

    np.testing.assert_allclose(coeff_matrix, np.zeros((0, 0)))

    with pytest.raises(ValueError, match="not contained in span"):
        lyapunov_utils._find_symmetric_coefficient_matrix_from_coords(np.eye(1), [])

    with pytest.raises(ValueError, match="not contained in span"):
        lyapunov_utils._find_symmetric_coefficient_matrix_from_coords(
            np.eye(2), [np.array([1.0, 0.0])]
        )

    with pytest.raises(ValueError, match="not contained in span"):
        lyapunov_utils._find_symmetric_coefficient_matrix_from_coords(
            np.array([[0.0, 0.0], [0.0, 1.0]]),
            [np.array([1.0, 0.0])],
        )

    with pytest.raises(ValueError, match="vecs are linearly dependent"):
        lyapunov_utils._find_symmetric_coefficient_matrix_from_coords(
            np.array([[1.0, 0.0], [0.0, 0.0]]),
            [np.array([1.0, 0.0]), np.array([2.0, 0.0])],
        )


def test_find_symmetric_coefficient_matrix_helper_allows_tiny_residual_rank():
    coeff_matrix = lyapunov_utils._find_symmetric_coefficient_matrix_from_coords(
        np.diag([2.0, 3.0, 1e-8]),
        [np.array([1.0, 0.0, 0.0]), np.array([0.0, 1.0, 0.0])],
    )

    expected = np.array([[2.0, 0.0], [0.0, 3.0]])
    np.testing.assert_allclose(coeff_matrix, expected, atol=1e-7)


def test_find_basis_with_sparsest_coefficients_selects_sparse_basis(
    pep_context: pc.PEPContext, basis_vectors
):
    e1, e2 = basis_vectors
    w = e1 + e2
    V = w**2 + 2 * e2**2

    basis, coeff_matrix = lyapunov_utils.find_basis_with_sparsest_coefficients(
        V,
        [e1, e2, w],
        pep_context=pep_context,
    )

    assert basis == [e2, w]
    np.testing.assert_allclose(
        coeff_matrix, np.array([[2.0, 0.0], [0.0, 1.0]]), atol=1e-10
    )


def test_find_basis_with_sparsest_coefficients_respects_fixed_vectors(
    pep_context: pc.PEPContext, basis_vectors
):
    e1, e2 = basis_vectors
    w = e1 + e2
    V = w**2 + 2 * e2**2

    basis, coeff_matrix = lyapunov_utils.find_basis_with_sparsest_coefficients(
        V,
        [e1, e2, w],
        pep_context=pep_context,
        fixed_vectors=[e1],
    )

    assert e1 in basis
    assert len(basis) == 2
    assert coeff_matrix.shape == (2, 2)


def test_find_basis_with_sparsest_coefficients_warns_for_large_subset_search(
    pep_context: pc.PEPContext,
):
    e1 = vector.Vector(is_basis=True, tags=["e_1"])
    e2 = vector.Vector(is_basis=True, tags=["e_2"])
    basis = [e1, e2]
    for i in range(150):
        basis.append(e1 + (i + 1) * e2)
    V = e1**2 + e2**2

    with pytest.warns(UserWarning, match="checking 11476 subsets"):
        lyapunov_utils.find_basis_with_sparsest_coefficients(
            V, basis, pep_context=pep_context
        )


def test_complete_basis_with_sparsifying_last_vector_eliminates_last_cross_block(
    pep_context: pc.PEPContext, basis_vectors
):
    e1, e2 = basis_vectors
    e3 = vector.Vector(is_basis=True, tags=["e_3"])
    V = 2 * e1**2 + 3 * e2**2 + 5 * e3**2

    v_last, coeff_matrix = lyapunov_utils.complete_basis_with_sparsifying_last_vector(
        V, [e1, e2], pep_context=pep_context, rtol=1e-12
    )

    np.testing.assert_allclose(coeff_matrix[:2, 2], np.zeros(2), atol=1e-10)
    assert v_last.shape == (3,)


def test_ldl_decompose_with_reversed_basis_returns_labeled_factors(
    pep_context: pc.PEPContext, basis_vectors
):
    e1, e2 = basis_vectors
    S = MatrixWithNames(
        matrix=np.diag([2.0, 3.0]),
        row_names=[repr(e1), repr(e2)],
        col_names=[repr(e1), repr(e2)],
    )

    D, ell = lyapunov_utils.ldl_decompose_with_reversed_basis(
        S, [e1, e2], print_output=False
    )

    np.testing.assert_allclose(D, np.diag([3.0, 2.0]))
    assert len(ell) == 2
