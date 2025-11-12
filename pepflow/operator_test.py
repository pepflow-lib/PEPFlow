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

from pepflow import constraint as ct
from pepflow import expression_manager as exm
from pepflow import operator as oper
from pepflow import pep as pep
from pepflow import pep_context as pc
from pepflow import registry as reg
from pepflow import vector


@pytest.fixture
def pep_context() -> Iterator[pc.PEPContext]:
    """Prepare the pep context and reset the context to None at the end."""

    ctx = pc.PEPContext("test").set_as_current()
    yield ctx
    pc.set_current_context(None)
    pc.GLOBAL_CONTEXT_DICT.clear()
    reg.REGISTERED_FUNC_AND_OPER_DICT.clear()


def test_operator_add_tag(pep_context: pc.PEPContext) -> None:
    A1 = oper.Operator(is_basis=True, tags=["A1"])
    A2 = oper.Operator(is_basis=True, tags=["A2"])

    A_add = A1 + A2
    assert A_add.__repr__() == "A1+A2"

    A_sub = A1 - A2
    assert A_sub.__repr__() == "A1-A2"

    A_sub = A1 - (A2 + A1)
    assert A_sub.__repr__() == "A1-(A2+A1)"

    A_sub = A1 - (A2 - A1)
    assert A_sub.__repr__() == "A1-(A2-A1)"


def test_operator_mul_tag(pep_context: pc.PEPContext) -> None:
    A = oper.Operator(is_basis=True, tags=["A"])

    A_mul = A * 0.1
    assert A_mul.__repr__() == "0.1*A"

    A_rmul = 0.1 * A
    assert A_rmul.__repr__() == "0.1*A"

    A_neg = -A
    assert A_neg.__repr__() == "-A"

    A_truediv = A / 0.1
    assert A_truediv.__repr__() == "1/0.1*A"


def test_operator_add_and_mul_tag(pep_context: pc.PEPContext) -> None:
    A1 = oper.Operator(is_basis=True, tags=["A1"])
    A2 = oper.Operator(is_basis=True, tags=["A2"])

    A_add_mul = (A1 + A2) * 0.1
    assert A_add_mul.__repr__() == "0.1*(A1+A2)"

    A_add_mul = A1 + A2 * 0.1
    assert A_add_mul.__repr__() == "A1+0.1*A2"

    A_neg_add = -(A1 + A2)
    assert A_neg_add.__repr__() == "-(A1+A2)"

    A_rmul_add = 0.1 * (A1 + A2)
    assert A_rmul_add.__repr__() == "0.1*(A1+A2)"

    A_rmul_add = A1 + 5 * (A2 + 3 * A1)
    assert A_rmul_add.__repr__() == "A1+5*(A2+3*A1)"

    A_multiple_add = A1 + A1 + A1 + A1 + A1 + A1
    assert A_multiple_add.__repr__() == "A1+A1+A1+A1+A1+A1"


def test_operator_call(pep_context: pc.PEPContext) -> None:
    A = oper.Operator(is_basis=True, tags=["A"])
    x = vector.Vector(is_basis=True, eval_expression=None, tags=["x"])
    assert A.apply(x) == A(x)


def test_operator_repr(pep_context: pc.PEPContext):
    A = oper.Operator(is_basis=True, tags=["A"])
    assert str(A) == "A"


def test_add_point_with_output_restriction(pep_context: pc.PEPContext):
    A = oper.Operator(
        is_basis=True,
        tags=["A"],
    )
    x = vector.Vector(is_basis=True)
    x.add_tag("x")
    zero_duplet = A.add_point_with_output_restriction(x, vector.Vector.zero())

    assert zero_duplet.name == "x_0"
    assert zero_duplet.point.tag == "x"
    assert zero_duplet.output.__repr__() == "0"

    assert len(pep_context.oper_to_duplets) == 1
    assert len(pep_context.oper_to_duplets[A]) == 1

    A_duplet = pep_context.oper_to_duplets[A][0]
    assert A_duplet.name == "x_0"
    assert A_duplet.point.tag == "x"
    assert A_duplet.output.__repr__() == "0"

    em = exm.ExpressionManager(pep_context)
    np.testing.assert_allclose(em.eval_vector(A_duplet.output).coords, np.array([0]))
    np.testing.assert_allclose(em.eval_vector(A_duplet.point).coords, np.array([1]))


def test_add_point_with_output_restriction_scaled(pep_context: pc.PEPContext):
    A = oper.Operator(
        is_basis=True,
        tags=["A"],
    )
    B = 5 * A
    x = vector.Vector(is_basis=True, tags=["x"])
    zero_triplet = B.add_point_with_output_restriction(x, vector.Vector.zero())

    assert zero_triplet.name == "x_0"
    assert zero_triplet.output.__repr__() == "0"

    assert len(pep_context.oper_to_duplets) == 1
    assert len(pep_context.oper_to_duplets[A]) == 1

    A_duplet = pep_context.oper_to_duplets[A][0]
    assert A_duplet.name == "x_A(x)"
    assert A_duplet.point.tag == "x"
    assert A_duplet.output.__repr__() == "A(x)"

    em = exm.ExpressionManager(pep_context)
    np.testing.assert_allclose(em.eval_vector(A_duplet.output).coords, np.array([0]))
    np.testing.assert_allclose(em.eval_vector(A_duplet.point).coords, np.array([1]))


def test_add_point_with_output_restriction_linear_combination(
    pep_context: pc.PEPContext,
):
    A = oper.Operator(is_basis=True, tags=["A"])
    B = oper.Operator(is_basis=True, tags=["B"])
    C = 3 * A + 2 * B
    C.add_tag("C")

    x = vector.Vector(is_basis=True)
    x.add_tag("x")
    zero_triplet = C.add_point_with_output_restriction(x, vector.Vector.zero())

    assert zero_triplet.name == "x_0"
    assert zero_triplet.output.__repr__() == "0"

    assert len(pep_context.oper_to_duplets) == 2
    assert len(pep_context.oper_to_duplets[A]) == 1
    assert len(pep_context.oper_to_duplets[B]) == 1

    A_duplet = pep_context.oper_to_duplets[A][0]
    B_duplet = pep_context.oper_to_duplets[B][0]
    assert A_duplet.name == "x_A(x)"
    assert B_duplet.name == "x_B(x)"

    em = exm.ExpressionManager(pep_context)
    np.testing.assert_allclose(em.eval_vector(A_duplet.output).coords, np.array([0, 1]))
    np.testing.assert_allclose(
        em.eval_vector(B_duplet.output).coords, np.array([0, -1.5])
    )


def test_set_zero_point(pep_context: pc.PEPContext):
    A = oper.Operator(
        is_basis=True,
        tags=["A"],
    )
    A.set_zero_point("x")

    with pytest.raises(
        ValueError,
        match="You are trying to add a zero point to an operator that already has a zero point.",
    ):
        A.set_zero_point("y")

    assert len(pep_context.oper_to_duplets) == 1
    assert len(pep_context.oper_to_duplets[A]) == 1
    assert len(pep_context.oper_to_zero_duplets[A]) == 1

    A_duplet = pep_context.oper_to_duplets[A][0]
    assert A_duplet.name == "x_A(x)"
    assert A_duplet.output.__repr__() == "A(x)"

    em = exm.ExpressionManager(pep_context)
    np.testing.assert_allclose(em.eval_vector(A_duplet.output).coords, np.array([0]))
    np.testing.assert_allclose(em.eval_vector(A_duplet.point).coords, np.array([1]))


def test_set_zero_point_scaled(pep_context: pc.PEPContext):
    A = oper.Operator(
        is_basis=True,
        tags=["A"],
    )
    B = 5 * A
    B.set_zero_point("x")

    assert len(pep_context.oper_to_duplets) == 1
    assert len(pep_context.oper_to_duplets[A]) == 1

    A_duplet = pep_context.oper_to_duplets[A][0]
    assert A_duplet.name == "x_A(x)"
    assert A_duplet.output.__repr__() == "A(x)"

    em = exm.ExpressionManager(pep_context)
    np.testing.assert_allclose(em.eval_vector(A_duplet.output).coords, np.array([0]))
    np.testing.assert_allclose(em.eval_vector(A_duplet.point).coords, np.array([1]))


def test_set_zero_point_additive(pep_context: pc.PEPContext):
    A = oper.Operator(is_basis=True, tags=["A"])
    B = oper.Operator(is_basis=True, tags=["B"])
    C = A + B
    C.add_tag("C")

    C.set_zero_point("x")
    assert len(pep_context.oper_to_duplets) == 2
    assert len(pep_context.oper_to_duplets[A]) == 1
    assert len(pep_context.oper_to_duplets[B]) == 1

    A_duplet = pep_context.oper_to_duplets[A][0]
    B_duplet = pep_context.oper_to_duplets[B][0]
    assert A_duplet.name == "x_A(x)"
    assert B_duplet.name == "x_B(x)"

    em = exm.ExpressionManager(pep_context)
    np.testing.assert_allclose(em.eval_vector(A_duplet.output).coords, np.array([0, 1]))
    np.testing.assert_allclose(
        em.eval_vector(B_duplet.output).coords, np.array([0, -1])
    )


def test_set_zero_point_linear_combination(pep_context: pc.PEPContext):
    A = oper.Operator(is_basis=True, tags=["A"])
    B = oper.Operator(is_basis=True, tags=["B"])
    C = 3 * A + 2 * B
    C.add_tag("C")

    C.set_zero_point("x")
    assert len(pep_context.oper_to_duplets) == 2
    assert len(pep_context.oper_to_duplets[A]) == 1
    assert len(pep_context.oper_to_duplets[B]) == 1

    A_duplet = pep_context.oper_to_duplets[A][0]
    B_duplet = pep_context.oper_to_duplets[B][0]
    assert A_duplet.name == "x_A(x)"
    assert B_duplet.name == "x_B(x)"

    em = exm.ExpressionManager(pep_context)
    np.testing.assert_allclose(em.eval_vector(A_duplet.output).coords, np.array([0, 1]))
    np.testing.assert_allclose(
        em.eval_vector(B_duplet.output).coords, np.array([0, -1.5])
    )


def test_function_generate_duplet(pep_context: pc.PEPContext):
    A = oper.Operator(is_basis=True, tags=["A"])
    B = oper.Operator(is_basis=True, tags=["B"])
    C = 5 * A + 5 * B
    C.add_tag("C")

    p1 = vector.Vector(is_basis=True)
    p1.add_tag("p1")
    p1_duplet = C.generate_duplet(p1)
    p1_duplet_1 = C.generate_duplet(p1)

    assert p1_duplet.name == f"{p1_duplet.point.tag}_{p1_duplet.output.__repr__()}"
    assert (
        p1_duplet_1.name == f"{p1_duplet_1.point.tag}_{p1_duplet_1.output.__repr__()}"
    )

    pm = exm.ExpressionManager(pep_context)

    np.testing.assert_allclose(pm.eval_vector(p1).coords, np.array([1, 0, 0]))

    np.testing.assert_allclose(
        pm.eval_vector(p1_duplet.output).coords, np.array([0, 5, 5])
    )

    np.testing.assert_allclose(
        pm.eval_vector(p1_duplet_1.output).coords, np.array([0, 5, 5])
    )


def test_set_fixed_point(pep_context: pc.PEPContext):
    A = oper.Operator(
        is_basis=True,
        tags=["A"],
    )
    A.set_fixed_point("x")

    with pytest.raises(
        ValueError,
        match="You are trying to add a fixed point to an operator that already has a fixed point.",
    ):
        A.set_fixed_point("y")

    assert len(pep_context.oper_to_duplets) == 1
    assert len(pep_context.oper_to_duplets[A]) == 1
    assert len(pep_context.oper_to_fixed_duplets[A]) == 1

    A_duplet = pep_context.oper_to_duplets[A][0]
    assert A_duplet.name == "x_x"
    assert A_duplet.output.tag == "x"

    em = exm.ExpressionManager(pep_context)
    np.testing.assert_allclose(em.eval_vector(A_duplet.output).coords, np.array([1]))
    np.testing.assert_allclose(em.eval_vector(A_duplet.point).coords, np.array([1]))


def test_set_fixed_point_scaled(pep_context: pc.PEPContext):
    A = oper.Operator(
        is_basis=True,
        tags=["A"],
    )
    B = 5 * A
    B.set_fixed_point("x")

    assert len(pep_context.oper_to_duplets) == 1
    assert len(pep_context.oper_to_duplets[A]) == 1

    A_duplet = pep_context.oper_to_duplets[A][0]
    assert A_duplet.name == "x_A(x)"
    assert A_duplet.output.__repr__() == "A(x)"

    em = exm.ExpressionManager(pep_context)
    np.testing.assert_allclose(em.eval_vector(A_duplet.output).coords, np.array([0.2]))
    np.testing.assert_allclose(em.eval_vector(A_duplet.point).coords, np.array([1]))


def test_set_fixed_point_additive(pep_context: pc.PEPContext):
    A = oper.Operator(is_basis=True, tags=["A"])
    B = oper.Operator(is_basis=True, tags=["B"])
    C = A + B
    C.add_tag("C")

    C.set_fixed_point("x")
    assert len(pep_context.oper_to_duplets) == 2
    assert len(pep_context.oper_to_duplets[A]) == 1
    assert len(pep_context.oper_to_duplets[B]) == 1

    A_duplet = pep_context.oper_to_duplets[A][0]
    B_duplet = pep_context.oper_to_duplets[B][0]
    assert A_duplet.name == "x_A(x)"
    assert B_duplet.name == "x_B(x)"

    em = exm.ExpressionManager(pep_context)
    np.testing.assert_allclose(em.eval_vector(A_duplet.output).coords, np.array([0, 1]))
    np.testing.assert_allclose(
        em.eval_vector(B_duplet.output).coords, np.array([1, -1])
    )


def test_set_fixed_point_linear_combination(pep_context: pc.PEPContext):
    A = oper.Operator(is_basis=True, tags=["A"])
    B = oper.Operator(is_basis=True, tags=["B"])
    C = 3 * A + 2 * B
    C.add_tag("C")

    C.set_fixed_point("x")
    assert len(pep_context.oper_to_duplets) == 2
    assert len(pep_context.oper_to_duplets[A]) == 1
    assert len(pep_context.oper_to_duplets[B]) == 1

    A_duplet = pep_context.oper_to_duplets[A][0]
    B_duplet = pep_context.oper_to_duplets[B][0]
    assert A_duplet.name == "x_A(x)"
    assert B_duplet.name == "x_B(x)"

    em = exm.ExpressionManager(pep_context)
    np.testing.assert_allclose(em.eval_vector(A_duplet.output).coords, np.array([0, 1]))
    np.testing.assert_allclose(
        em.eval_vector(B_duplet.output).coords, np.array([0.5, -1.5])
    )


def test_linear_operator(pep_context: pc.PEPContext):
    A = oper.LinearOperator(is_basis=True, M=1, tags=["A"])
    x = vector.Vector(is_basis=True)
    x.add_tag("x")
    y = A(x)
    y.add_tag("y")
    u = vector.Vector(is_basis=True)
    u.add_tag("u")
    v = A.T(u)
    v.add_tag("v")

    assert len(pep_context.oper_to_duplets[A]) == 1
    assert len(pep_context.oper_to_duplets[A.T]) == 1


def test_linear_operator_interpolability_constraints(pep_context: pc.PEPContext):
    A = oper.LinearOperator(is_basis=True, M=1, tags=["A"])
    x = vector.Vector(is_basis=True)
    x.add_tag("x")
    y = A(x)
    y.add_tag("y")
    u = vector.Vector(is_basis=True)
    u.add_tag("u")
    v = A.T(u)
    v.add_tag("v")

    x_1 = vector.Vector(is_basis=True)
    x_1.add_tag("x_1")
    y_1 = A(x_1)
    y_1.add_tag("y_1")

    inter_constrs = A.get_interpolation_constraints()

    assert len(inter_constrs) == 4

    pm = exm.ExpressionManager(pep_context)

    np.testing.assert_allclose(
        pm.eval_scalar(inter_constrs[0].lhs).matrix, pm.eval_scalar(x * v).matrix
    )
    np.testing.assert_allclose(
        pm.eval_scalar(inter_constrs[0].rhs).matrix, pm.eval_scalar(u * y).matrix
    )

    np.testing.assert_allclose(
        pm.eval_scalar(inter_constrs[1].lhs).matrix, pm.eval_scalar(x_1 * v).matrix
    )

    np.testing.assert_allclose(
        pm.eval_scalar(inter_constrs[1].rhs).matrix, pm.eval_scalar(u * y_1).matrix
    )

    if isinstance(inter_constrs[2], ct.PSDConstraint):
        if isinstance(inter_constrs[2].lhs, np.ndarray) and isinstance(
            inter_constrs[2].rhs, float
        ):
            assert inter_constrs[2].rhs == 0
            assert inter_constrs[2].lhs.shape == (2, 2)
            assert (inter_constrs[2].lhs - inter_constrs[2].rhs).shape == (2, 2)
            assert np.empty(
                (inter_constrs[2].lhs - inter_constrs[2].rhs).shape
            ).shape == (2, 2)
            np.testing.assert_allclose(
                pm.eval_scalar(inter_constrs[2].lhs[0, 0]).matrix,
                pm.eval_scalar(x * x - y * y).matrix,
            )
            np.testing.assert_allclose(
                pm.eval_scalar(inter_constrs[2].lhs[1, 1]).matrix,
                pm.eval_scalar(x_1 * x_1 - y_1 * y_1).matrix,
            )
            np.testing.assert_allclose(
                pm.eval_scalar(inter_constrs[2].lhs[0, 1]).matrix,
                pm.eval_scalar(x * x_1 - y * y_1).matrix,
            )

            np.testing.assert_allclose(
                pm.eval_scalar(inter_constrs[2].lhs[1, 0]).matrix,
                pm.eval_scalar(x * x_1 - y * y_1).matrix,
            )

    if isinstance(inter_constrs[3], ct.PSDConstraint):
        if isinstance(inter_constrs[3].lhs, np.ndarray) and isinstance(
            inter_constrs[3].rhs, float
        ):
            assert inter_constrs[3].rhs == 0
            assert inter_constrs[3].lhs.shape == (1, 1)
            np.testing.assert_allclose(
                pm.eval_scalar(inter_constrs[3].lhs[0, 0]).matrix,
                pm.eval_scalar(u * u - v * v).matrix,
            )
