# Copyright: 2025 The PEPFlow Developers
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

from pepflow import expression_manager as exm
from pepflow import pep as pep
from pepflow import pep_context as pc
from pepflow import registry as reg
from pepflow import scalar, utils
from pepflow.constraint import PSDConstraint, ScalarConstraint


@pytest.fixture
def pep_context() -> Iterator[pc.PEPContext]:
    """Prepare the pep context and reset the context to None at the end."""
    ctx = pc.PEPContext("test").set_as_current()
    yield ctx
    pc.set_current_context(None)
    pc.GLOBAL_CONTEXT_DICT.clear()
    reg.REGISTERED_FUNC_AND_OPER_DICT.clear()


def test_scalar_constraint_make(pep_context: pc.PEPContext):
    s1 = scalar.Scalar(is_basis=True, tags=["s1"])
    s2 = scalar.Scalar(is_basis=True, tags=["s2"])
    s3 = 2 * s1 + s2 / 4 + 5

    c1 = ScalarConstraint.make(s3, "<=", 5, "c1")
    c2 = ScalarConstraint.make(s3, "<", 5, "c2")
    c3 = ScalarConstraint.make(s3, ">=", 5, "c3")
    c4 = ScalarConstraint.make(s3, ">", 5, "c4")
    c5 = ScalarConstraint.make(s3, "==", 5, "c5")

    pm = exm.ExpressionManager(pep_context)

    np.testing.assert_allclose(
        pm.eval_scalar(c1.lhs - c1.rhs).func_coords, np.array([2, 0.25])
    )
    np.testing.assert_allclose(pm.eval_scalar(c1.lhs - c1.rhs).offset, 0)
    assert c1.cmp == utils.Comparator.LE

    np.testing.assert_allclose(
        pm.eval_scalar(c2.lhs - c2.rhs).func_coords, np.array([2, 0.25])
    )
    np.testing.assert_allclose(pm.eval_scalar(c2.lhs - c2.rhs).offset, 0)
    assert c2.cmp == utils.Comparator.LE

    np.testing.assert_allclose(
        pm.eval_scalar(c3.lhs - c3.rhs).func_coords, np.array([2, 0.25])
    )
    np.testing.assert_allclose(pm.eval_scalar(c3.lhs - c3.rhs).offset, 0)
    assert c3.cmp == utils.Comparator.GE

    np.testing.assert_allclose(
        pm.eval_scalar(c4.lhs - c4.rhs).func_coords, np.array([2, 0.25])
    )
    np.testing.assert_allclose(pm.eval_scalar(c4.lhs - c4.rhs).offset, 0)
    assert c4.cmp == utils.Comparator.GE

    np.testing.assert_allclose(
        pm.eval_scalar(c5.lhs - c5.rhs).func_coords, np.array([2, 0.25])
    )
    np.testing.assert_allclose(pm.eval_scalar(c5.lhs - c5.rhs).offset, 0)
    assert c5.cmp == utils.Comparator.EQ


def test_scalar_constraint(pep_context: pc.PEPContext):
    s1 = scalar.Scalar(is_basis=True, tags=["s1"])
    s2 = scalar.Scalar(is_basis=True, tags=["s2"])
    s3 = 2 * s1 + s2 / 4 + 5

    c1 = s3.lt(5, "c2")
    c2 = s3.le(5, "c2")
    c3 = s3.gt(5, "c2")
    c4 = s3.ge(5, "c2")
    c5 = s3.eq(5, "c2")

    pm = exm.ExpressionManager(pep_context)

    np.testing.assert_allclose(
        pm.eval_scalar(c1.lhs - c1.rhs).func_coords, np.array([2, 0.25])
    )
    np.testing.assert_allclose(pm.eval_scalar(c1.lhs - c1.rhs).offset, 0)
    assert c1.cmp == utils.Comparator.LE

    np.testing.assert_allclose(
        pm.eval_scalar(c2.lhs - c2.rhs).func_coords, np.array([2, 0.25])
    )
    np.testing.assert_allclose(pm.eval_scalar(c2.lhs - c2.rhs).offset, 0)
    assert c2.cmp == utils.Comparator.LE

    np.testing.assert_allclose(
        pm.eval_scalar(c3.lhs - c3.rhs).func_coords, np.array([2, 0.25])
    )
    np.testing.assert_allclose(pm.eval_scalar(c3.lhs - c3.rhs).offset, 0)
    assert c3.cmp == utils.Comparator.GE

    np.testing.assert_allclose(
        pm.eval_scalar(c4.lhs - c4.rhs).func_coords, np.array([2, 0.25])
    )
    np.testing.assert_allclose(pm.eval_scalar(c4.lhs - c4.rhs).offset, 0)
    assert c4.cmp == utils.Comparator.GE

    np.testing.assert_allclose(
        pm.eval_scalar(c5.lhs - c5.rhs).func_coords, np.array([2, 0.25])
    )
    np.testing.assert_allclose(pm.eval_scalar(c5.lhs - c5.rhs).offset, 0)
    assert c5.cmp == utils.Comparator.EQ


def test_PSD_constraint_make(pep_context: pc.PEPContext):
    A = np.empty([5, 5], dtype=scalar.Scalar)
    B = np.empty([5, 5], dtype=scalar.Scalar)
    C = np.empty([3, 3], dtype=scalar.Scalar)

    _ = PSDConstraint.make(A, "<<", 0, "c1")
    _ = PSDConstraint.make(A, ">>", 0, "c2")
    _ = PSDConstraint.make(A, "==", 0, "c3")
    _ = PSDConstraint.make(A, "<<", B, "c4")
    _ = PSDConstraint.make(A, ">>", B, "c5")
    _ = PSDConstraint.make(A, "==", B, "c6")

    with pytest.raises(
        ValueError,
        match="The shape of the lhs should match the rhs.",
    ):
        PSDConstraint.make(A, "<<", C, "error")

    with pytest.raises(
        ValueError,
        match="The shape of the lhs should match the rhs.",
    ):
        PSDConstraint.make(A, ">>", C, "error")

    with pytest.raises(
        ValueError,
        match="The shape of the lhs should match the rhs.",
    ):
        PSDConstraint.make(A, "==", C, "error")

    with pytest.raises(
        ValueError,
        match="The cmp should be PEQ, SEQ, or EQ.",
    ):
        PSDConstraint.make(A, "<=", C, "error")


def test_PSD_constraint_dual_peq(pep_context: pc.PEPContext):
    A = np.empty([5, 5], dtype=scalar.Scalar)
    B = np.empty([5, 5], dtype=scalar.Scalar)
    C = np.empty([3, 3], dtype=scalar.Scalar)

    c1 = PSDConstraint.make(A, "<<", 0, "c1")
    c2 = PSDConstraint.make(0, ">>", A, "C2")

    c1.dual_peq(B)
    c1.dual_peq(0)

    assert c1.associated_dual_var_constraints[0] == (utils.Comparator.PEQ, B)
    assert c1.associated_dual_var_constraints[1] == (utils.Comparator.PEQ, 0)

    with pytest.raises(
        ValueError,
        match="The input must be the same shape as the matrix associated with the LHS of this PSDConstraint.",
    ):
        c1.dual_peq(C)

    with pytest.raises(
        ValueError,
        match="The input must be the same shape as the matrix associated with the RHS of this PSDConstraint.",
    ):
        c2.dual_peq(C)


def test_PSD_constraint_dual_seq(pep_context: pc.PEPContext):
    A = np.empty([5, 5], dtype=scalar.Scalar)
    B = np.empty([5, 5], dtype=scalar.Scalar)
    C = np.empty([3, 3], dtype=scalar.Scalar)

    c1 = PSDConstraint.make(A, "<<", 0, "c1")
    c2 = PSDConstraint.make(0, ">>", A, "C2")

    c1.dual_seq(B)
    c1.dual_seq(0)

    assert c1.associated_dual_var_constraints[0] == (utils.Comparator.SEQ, B)
    assert c1.associated_dual_var_constraints[1] == (utils.Comparator.SEQ, 0)

    with pytest.raises(
        ValueError,
        match="The input must be the same shape as the matrix associated with the LHS of this PSDConstraint.",
    ):
        c1.dual_seq(C)

    with pytest.raises(
        ValueError,
        match="The input must be the same shape as the matrix associated with the RHS of this PSDConstraint.",
    ):
        c2.dual_seq(C)


def test_PSD_constraint_dual_eq(pep_context: pc.PEPContext):
    A = np.empty([5, 5], dtype=scalar.Scalar)
    B = np.empty([5, 5], dtype=scalar.Scalar)
    C = np.empty([3, 3], dtype=scalar.Scalar)

    c1 = PSDConstraint.make(A, "<<", 0, "c1")
    c2 = PSDConstraint.make(0, ">>", A, "C2")

    c1.dual_eq(B)
    c1.dual_eq(0)

    assert c1.associated_dual_var_constraints[0] == (utils.Comparator.EQ, B)
    assert c1.associated_dual_var_constraints[1] == (utils.Comparator.EQ, 0)

    with pytest.raises(
        ValueError,
        match="The input must be the same shape as the matrix associated with the LHS of this PSDConstraint.",
    ):
        c1.dual_eq(C)

    with pytest.raises(
        ValueError,
        match="The input must be the same shape as the matrix associated with the RHS of this PSDConstraint.",
    ):
        c2.dual_eq(C)
