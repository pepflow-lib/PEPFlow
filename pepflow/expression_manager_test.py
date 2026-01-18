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
import sympy as sp

from pepflow import expression_manager as exm
from pepflow import function as fc
from pepflow import pep as pep
from pepflow import pep_context as pc
from pepflow import scalar as sc
from pepflow import vector as vt


@pytest.fixture
def pep_context() -> Iterator[pc.PEPContext]:
    """Prepare the pep context and reset the context to None at the end."""

    ctx = pc.PEPContext("test").set_as_current()
    yield ctx
    pc.set_current_context(None)
    pc.GLOBAL_CONTEXT_DICT.clear()


def test_expression_manager_on_basis_scalar(pep_context: pc.PEPContext):
    s1 = sc.Scalar(is_basis=True, eval_expression=None, tags=["s1"])
    s2 = sc.Scalar(is_basis=True, eval_expression=None, tags=["s2"])
    pm = exm.ExpressionManager(pep_context)

    np.testing.assert_allclose(pm.eval_scalar(s1).func_coords, np.array([1, 0]))
    np.testing.assert_allclose(pm.eval_scalar(s2).func_coords, np.array([0, 1]))

    s3 = sc.Scalar(is_basis=True, eval_expression=None, tags=["s3"])  # noqa: F841
    pm = exm.ExpressionManager(pep_context)

    np.testing.assert_allclose(pm.eval_scalar(s1).func_coords, np.array([1, 0, 0]))
    np.testing.assert_allclose(pm.eval_scalar(s2).func_coords, np.array([0, 1, 0]))


def test_expression_manager_on_basis_scalar_sympy_mode(pep_context: pc.PEPContext):
    s1 = sc.Scalar(is_basis=True, eval_expression=None, tags=["s1"])
    s2 = sc.Scalar(is_basis=True, eval_expression=None, tags=["s2"])
    pm = exm.ExpressionManager(pep_context)

    np.testing.assert_equal(
        pm.eval_scalar(s1, sympy_mode=True).func_coords,
        np.array([sp.S(1), sp.S(0)]),
        strict=True,
    )
    np.testing.assert_equal(
        pm.eval_scalar(s2, sympy_mode=True).func_coords,
        np.array([sp.S(0), sp.S(1)]),
        strict=True,
    )
    s3 = sc.Scalar(is_basis=True, eval_expression=None, tags=["s3"])  # noqa: F841
    pm = exm.ExpressionManager(pep_context)

    np.testing.assert_equal(
        pm.eval_scalar(s1, sympy_mode=True).func_coords,
        np.array([sp.S(1), sp.S(0), sp.S(0)]),
        strict=True,
    )
    np.testing.assert_equal(
        pm.eval_scalar(s2, sympy_mode=True).func_coords,
        np.array([sp.S(0), sp.S(1), sp.S(0)]),
        strict=True,
    )


def test_expression_manager_eval_scalar(pep_context: pc.PEPContext):
    s1 = sc.Scalar(is_basis=True, tags=["s1"])
    s2 = sc.Scalar(is_basis=True, tags=["s2"])
    s3 = 2 * s1 + s2 / 4 + 5
    s4 = s3 + s1
    s5 = s4 + 5

    p1 = vt.Vector(is_basis=True, tags=["p1"])
    p2 = vt.Vector(is_basis=True, tags=["p2"])
    s6 = p1 * p2

    p3 = vt.Vector(is_basis=True, tags=["p3"])
    p4 = vt.Vector(is_basis=True, tags=["p4"])
    s7 = 5 * p3 * p4

    s8 = s6 + s7

    pm = exm.ExpressionManager(pep_context)

    np.testing.assert_allclose(pm.eval_scalar(s3).func_coords, np.array([2, 0.25]))
    np.testing.assert_allclose(pm.eval_scalar(s3).offset, 5)
    np.testing.assert_allclose(pm.eval_scalar(s4).func_coords, np.array([3, 0.25]))
    np.testing.assert_allclose(pm.eval_scalar(s5).func_coords, np.array([3, 0.25]))
    np.testing.assert_allclose(pm.eval_scalar(s5).offset, 10)

    # sympy mode
    np.testing.assert_equal(
        pm.eval_scalar(s3, sympy_mode=True).func_coords,
        np.array([sp.S(2), sp.S(1) / 4]),
        strict=True,
    )
    np.testing.assert_equal(
        pm.eval_scalar(s4, sympy_mode=True).func_coords,
        np.array([sp.S(3), sp.S(1) / 4]),
        strict=True,
    )
    np.testing.assert_equal(
        pm.eval_scalar(s5, sympy_mode=True).func_coords,
        np.array([sp.S(3), sp.S(1) / 4]),
        strict=True,
    )

    np.testing.assert_allclose(pm.eval_vector(p1).coords, np.array([1, 0, 0, 0]))
    np.testing.assert_allclose(pm.eval_vector(p2).coords, np.array([0, 1, 0, 0]))
    np.testing.assert_allclose(pm.eval_vector(p3).coords, np.array([0, 0, 1, 0]))
    np.testing.assert_allclose(pm.eval_vector(p4).coords, np.array([0, 0, 0, 1]))

    np.testing.assert_allclose(
        pm.eval_scalar(s6).inner_prod_coords,
        np.array(
            [
                [0.0, 0.5, 0.0, 0.0],
                [0.5, 0.0, 0.0, 0.0],
                [0.0, 0.0, 0.0, 0.0],
                [0.0, 0.0, 0.0, 0.0],
            ]
        ),
    )
    np.testing.assert_allclose(
        pm.eval_scalar(s7).inner_prod_coords,
        np.array(
            [
                [0.0, 0.0, 0.0, 0.0],
                [0.0, 0.0, 0.0, 0.0],
                [0.0, 0.0, 0.0, 2.5],
                [0.0, 0.0, 2.5, 0.0],
            ]
        ),
    )

    np.testing.assert_allclose(
        pm.eval_scalar(s8).inner_prod_coords,
        np.array(
            [
                [0.0, 0.5, 0.0, 0.0],
                [0.5, 0.0, 0.0, 0.0],
                [0.0, 0.0, 0.0, 2.5],
                [0.0, 0.0, 2.5, 0.0],
            ]
        ),
    )

    # sympy mode
    np.testing.assert_equal(
        pm.eval_scalar(s6, sympy_mode=True).inner_prod_coords,
        np.array(
            [
                [0, 1, 0, 0],
                [1, 0, 0, 0],
                [0, 0, 0, 0],
                [0, 0, 0, 0],
            ]
        )
        / sp.S(2),
        strict=True,
    )
    np.testing.assert_equal(
        pm.eval_scalar(s7, sympy_mode=True).inner_prod_coords,
        np.array(
            [
                [0, 0, 0, 0],
                [0, 0, 0, 0],
                [0, 0, 0, 5],
                [0, 0, 5, 0],
            ]
        )
        / sp.S(2),
        strict=True,
    )

    np.testing.assert_equal(
        pm.eval_scalar(s8, sympy_mode=True).inner_prod_coords,
        np.array(
            [
                [0, 1, 0, 0],
                [1, 0, 0, 0],
                [0, 0, 0, 5],
                [0, 0, 5, 0],
            ]
        )
        / sp.S(2),
        strict=True,
    )


def test_expression_manager_on_basis_vector(pep_context: pc.PEPContext):
    p1 = vt.Vector(is_basis=True, eval_expression=None, tags=["p1"])
    p2 = vt.Vector(is_basis=True, eval_expression=None, tags=["p2"])
    pm = exm.ExpressionManager(pep_context)

    np.testing.assert_allclose(pm.eval_vector(p1).coords, np.array([1, 0]))
    np.testing.assert_allclose(pm.eval_vector(p2).coords, np.array([0, 1]))

    p3 = vt.Vector(is_basis=True, eval_expression=None, tags=["p3"])  # noqa: F841
    pm = exm.ExpressionManager(pep_context)

    np.testing.assert_allclose(pm.eval_vector(p1).coords, np.array([1, 0, 0]))
    np.testing.assert_allclose(pm.eval_vector(p2).coords, np.array([0, 1, 0]))


def test_expression_manager_on_basis_vector_sympy_mode(pep_context: pc.PEPContext):
    p1 = vt.Vector(is_basis=True, eval_expression=None, tags=["p1"])
    p2 = vt.Vector(is_basis=True, eval_expression=None, tags=["p2"])
    pm = exm.ExpressionManager(pep_context)

    np.testing.assert_equal(
        pm.eval_vector(p1, sympy_mode=True).coords,
        np.array([sp.S(1), sp.S(0)]),
        strict=True,
    )
    np.testing.assert_equal(
        pm.eval_vector(p2, sympy_mode=True).coords,
        np.array([sp.S(0), sp.S(1)]),
        strict=True,
    )

    p3 = vt.Vector(is_basis=True, eval_expression=None, tags=["p3"])  # noqa: F841
    pm = exm.ExpressionManager(pep_context)

    np.testing.assert_equal(
        pm.eval_vector(p1, sympy_mode=True).coords,
        np.array([sp.S(1), sp.S(0), sp.S(0)]),
        strict=True,
    )
    np.testing.assert_equal(
        pm.eval_vector(p2, sympy_mode=True).coords,
        np.array([sp.S(0), sp.S(1), sp.S(0)]),
        strict=True,
    )


def test_expression_manager_eval_vector(pep_context: pc.PEPContext):
    p1 = vt.Vector(is_basis=True, tags=["p1"])
    p2 = vt.Vector(is_basis=True, tags=["p2"])
    p3 = 2 * p1 + p2 / 4
    p4 = p3 + p1

    pm = exm.ExpressionManager(pep_context)
    np.testing.assert_allclose(pm.eval_vector(p3).coords, np.array([2, 0.25]))
    np.testing.assert_allclose(pm.eval_vector(p4).coords, np.array([3, 0.25]))

    # sympy mode
    np.testing.assert_equal(
        pm.eval_vector(p3, sympy_mode=True).coords,
        np.array([sp.S(2), sp.S(1) / 4]),
        strict=True,
    )
    np.testing.assert_equal(
        pm.eval_vector(p4, sympy_mode=True).coords,
        np.array([sp.S(3), sp.S(1) / 4]),
        strict=True,
    )


def test_repr_vector_by_basis(pep_context: pc.PEPContext) -> None:
    x = vt.Vector(is_basis=True, tags=["x_0"])
    f = fc.Function(is_basis=True, tags=["f"])
    L = 0.5
    for i in range(2):
        x = x - L * f.grad(x)
        x.add_tag(f"x_{i + 1}")

    em = exm.ExpressionManager(pep_context)
    np.testing.assert_allclose(em.eval_vector(x).coords, [1, -0.5, -0.5])
    assert em.repr_vector_by_basis(x) == "x_0 - 0.5*grad_f(x_0) - 0.5*grad_f(x_1)"


def test_repr_vector_by_basis_with_zero(pep_context: pc.PEPContext) -> None:
    x = vt.Vector(is_basis=True, tags=["x_0"])
    _ = vt.Vector(is_basis=True, tags=["x_unused"])  # Add this extra vector.
    f = fc.Function(is_basis=True, tags=["f"])
    L = 0.5
    for i in range(2):
        x = x - L * f.grad(x)
        x.add_tag(f"x_{i + 1}")

    em = exm.ExpressionManager(pep_context)
    # Note the vector representation of vector is different from the previous case
    # but the string representation is still the same.
    np.testing.assert_allclose(em.eval_vector(x).coords, [1, 0, -0.5, -0.5])
    assert em.repr_vector_by_basis(x) == "x_0 - 0.5*grad_f(x_0) - 0.5*grad_f(x_1)"


def test_repr_vector_by_basis_heavy_ball(pep_context: pc.PEPContext) -> None:
    x_prev = vt.Vector(is_basis=True, tags=["x_{-1}"])
    x = vt.Vector(is_basis=True, tags=["x_0"])
    f = fc.Function(is_basis=True, tags=["f"])

    beta = 0.5
    for i in range(2):
        x_next = x - f.grad(x) + beta * (x - x_prev)
        x_next.add_tag(f"x_{i + 1}")
        x_prev = x
        x = x_next

    em = exm.ExpressionManager(pep_context)
    np.testing.assert_allclose(em.eval_vector(x).coords, [-0.75, 1.75, -1.5, -1])
    assert (
        em.repr_vector_by_basis(x)
        == "-0.75*x_{-1} + 1.75*x_0 - 1.5*grad_f(x_0) - grad_f(x_1)"
    )


def test_repr_scalar_by_basis(pep_context: pc.PEPContext) -> None:
    x = vt.Vector(is_basis=True, tags=["x"])
    f = fc.Function(is_basis=True, tags=["f"])

    s = f(x) + x * f.grad(x)
    em = exm.ExpressionManager(pep_context)
    assert em.repr_scalar_by_basis(s, greedy_square=False) == "f(x) + ⟨x, grad_f(x)⟩"
    assert (
        em.repr_scalar_by_basis(s, greedy_square=True)
        == "f(x) - 0.5*|x-grad_f(x)|^2 + 0.5*|x|^2 + 0.5*|grad_f(x)|^2"
    )


def test_repr_scalar_by_basis2(pep_context: pc.PEPContext) -> None:
    x = vt.Vector(is_basis=True, tags=["x"])
    f = fc.Function(is_basis=True, tags=["f"])

    s = f(x) - x * f.grad(x)
    em = exm.ExpressionManager(pep_context)
    assert em.repr_scalar_by_basis(s, greedy_square=False) == "f(x) - ⟨x, grad_f(x)⟩"
    assert (
        em.repr_scalar_by_basis(s, greedy_square=True)
        == "f(x) + 0.5*|x-grad_f(x)|^2 - 0.5*|x|^2 - 0.5*|grad_f(x)|^2"
    )


def test_repr_scalar_by_basis_interpolation(pep_context: pc.PEPContext) -> None:
    xi = vt.Vector(is_basis=True, tags=["x_i"])
    xj = vt.Vector(is_basis=True, tags=["x_j"])
    f = fc.SmoothConvexFunction(is_basis=True, L=1, tags=["f"])
    fi = f(xi)  # noqa: F841
    fj = f(xj)  # noqa: F841
    interp_scalar = f.interp_ineq("x_i", "x_j", sympy_mode=False)
    em = exm.ExpressionManager(pep_context)
    expected_repr = "-f(x_i) + f(x_j) + ⟨x_i, grad_f(x_j)⟩ - ⟨x_j, grad_f(x_j)⟩ + 0.5*|grad_f(x_i)|^2 - ⟨grad_f(x_i), grad_f(x_j)⟩ + 0.5*|grad_f(x_j)|^2"
    assert em.repr_scalar_by_basis(interp_scalar, greedy_square=False) == expected_repr
    expected_square_repr = "-f(x_i) + f(x_j) - 0.5*|x_i-grad_f(x_j)|^2 + 0.5*|x_i|^2 + 0.5*|x_j-grad_f(x_j)|^2 - 0.5*|x_j|^2 + 0.5*|grad_f(x_i)-grad_f(x_j)|^2"
    assert (
        em.repr_scalar_by_basis(interp_scalar, greedy_square=True)
        == expected_square_repr
    )


def test_repr_scalar_by_basis_interpolation_sympy_mode(
    pep_context: pc.PEPContext,
) -> None:
    xi = vt.Vector(is_basis=True, tags=["x_i"])
    xj = vt.Vector(is_basis=True, tags=["x_j"])
    f = fc.SmoothConvexFunction(is_basis=True, L=1, tags=["f"])
    fi = f(xi)  # noqa: F841
    fj = f(xj)  # noqa: F841
    interp_scalar = f.interp_ineq("x_i", "x_j", sympy_mode=True)
    em = exm.ExpressionManager(pep_context)
    expected_repr = "-f(x_i) + f(x_j) + ⟨x_i, grad_f(x_j)⟩ - ⟨x_j, grad_f(x_j)⟩ + 1/2*|grad_f(x_i)|^2 - ⟨grad_f(x_i), grad_f(x_j)⟩ + 1/2*|grad_f(x_j)|^2"
    assert (
        em.repr_scalar_by_basis(interp_scalar, greedy_square=False, sympy_mode=True)
        == expected_repr
    )
    expected_square_repr = "-f(x_i) + f(x_j) - 1/2*|x_i-grad_f(x_j)|^2 + 1/2*|x_i|^2 + 1/2*|x_j-grad_f(x_j)|^2 - 1/2*|x_j|^2 + 1/2*|grad_f(x_i)-grad_f(x_j)|^2"
    assert (
        em.repr_scalar_by_basis(interp_scalar, greedy_square=True, sympy_mode=True)
        == expected_square_repr
    )


# TODO add more tests about repr_scalar_by_basis


def test_represent_matrix_by_basis(pep_context: pc.PEPContext) -> None:
    _ = vt.Vector(is_basis=True, tags=["x_1"])
    _ = vt.Vector(is_basis=True, tags=["x_2"])
    _ = vt.Vector(is_basis=True, tags=["x_3"])
    matrix = np.array([[0.5, 0.5, 0], [0.5, 2, 0], [0, 0, 3]])
    assert (
        exm.represent_matrix_by_basis(matrix, pep_context, greedy_square=True)
        == "0.5*|x_1+x_2|^2 + 1.5*|x_2|^2 + 3*|x_3|^2"
    )
