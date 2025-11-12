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
from pepflow import function as fc
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


def test_function_add_tag(pep_context: pc.PEPContext) -> None:
    f1 = fc.Function(is_basis=True, tags=["f1"])
    f2 = fc.Function(is_basis=True, tags=["f2"])

    f_add = f1 + f2
    assert repr(f_add) == "f1+f2"

    f_sub = f1 - f2
    assert repr(f_sub) == "f1-f2"

    f_sub = f1 - (f2 + f1)
    assert repr(f_sub) == "f1-(f2+f1)"

    f_sub = f1 - (f2 - f1)
    assert repr(f_sub) == "f1-(f2-f1)"


def test_function_mul_tag(pep_context: pc.PEPContext) -> None:
    f = fc.Function(is_basis=True, tags=["f"])

    f_mul = f * 0.1
    assert repr(f_mul) == "0.1*f"

    f_rmul = 0.1 * f
    assert repr(f_rmul) == "0.1*f"

    f_neg = -f
    assert repr(f_neg) == "-f"

    f_truediv = f / 0.1
    assert repr(f_truediv) == "1/0.1*f"


def test_function_add_and_mul_tag(pep_context: pc.PEPContext) -> None:
    f1 = fc.Function(is_basis=True, tags=["f1"])
    f2 = fc.Function(is_basis=True, tags=["f2"])

    f_add_mul = (f1 + f2) * 0.1
    assert repr(f_add_mul) == "0.1*(f1+f2)"

    f_add_mul = f1 + f2 * 0.1
    assert repr(f_add_mul) == "f1+0.1*f2"

    f_neg_add = -(f1 + f2)
    assert repr(f_neg_add) == "-(f1+f2)"

    f_rmul_add = 0.1 * (f1 + f2)
    assert repr(f_rmul_add) == "0.1*(f1+f2)"

    f_rmul_add = f1 + 5 * (f2 + 3 * f1)
    assert repr(f_rmul_add) == "f1+5*(f2+3*f1)"

    f_multiple_add = f1 + f1 + f1 + f1 + f1 + f1
    assert repr(f_multiple_add) == "f1+f1+f1+f1+f1+f1"


def test_function_call(pep_context: pc.PEPContext) -> None:
    f = fc.Function(is_basis=True, tags=["f"])
    x = vector.Vector(is_basis=True, eval_expression=None, tags=["x"])
    assert f.func_val(x) == f(x)


def test_function_repr(pep_context: pc.PEPContext):
    f = fc.Function(is_basis=True, tags=["f"])
    assert str(f) == "f"


def test_add_point_with_grad_restriction(pep_context: pc.PEPContext):
    f = fc.Function(
        is_basis=True,
        tags=["f"],
    )
    x_star = vector.Vector(is_basis=True)
    x_star.add_tag("x_star")
    star_triplet = f.add_point_with_grad_restriction(x_star, vector.Vector.zero())

    assert star_triplet.name == "x_star_f(x_star)_0"
    assert repr(star_triplet.grad) == "0"
    assert repr(star_triplet.func_val) == "f(x_star)"

    assert len(pep_context.func_to_triplets) == 1
    assert len(pep_context.func_to_triplets[f]) == 1

    f_triplet = pep_context.func_to_triplets[f][0]
    assert f_triplet.name == "x_star_f(x_star)_0"
    assert repr(f_triplet.grad) == "0"
    assert repr(f_triplet.func_val) == "f(x_star)"

    em = exm.ExpressionManager(pep_context)
    np.testing.assert_allclose(em.eval_vector(f_triplet.grad).coords, np.array([0]))
    np.testing.assert_allclose(em.eval_vector(f_triplet.point).coords, np.array([1]))


def test_add_point_with_grad_restriction_scaled(pep_context: pc.PEPContext):
    f = fc.Function(
        is_basis=True,
        tags=["f"],
    )
    g = 5 * f
    x_star = vector.Vector(is_basis=True)
    x_star.add_tag("x_star")
    star_triplet = g.add_point_with_grad_restriction(x_star, vector.Vector.zero())

    assert star_triplet.name == "x_star_f(x_star)*5_0"
    assert repr(star_triplet.grad) == "0"
    assert repr(star_triplet.func_val) == "f(x_star)*5"

    assert len(pep_context.func_to_triplets) == 1
    assert len(pep_context.func_to_triplets[f]) == 1

    f_triplet = pep_context.func_to_triplets[f][0]
    assert f_triplet.name == "x_star_f(x_star)_grad_f(x_star)"
    assert repr(f_triplet.grad) == "grad_f(x_star)"
    assert repr(f_triplet.func_val) == "f(x_star)"

    em = exm.ExpressionManager(pep_context)
    np.testing.assert_allclose(em.eval_vector(f_triplet.grad).coords, np.array([0]))
    np.testing.assert_allclose(em.eval_vector(f_triplet.point).coords, np.array([1]))


def test_add_point_with_grad_restriction_linear_combination(pep_context: pc.PEPContext):
    f = fc.Function(is_basis=True, tags=["f"])
    g = fc.Function(is_basis=True, tags=["g"])
    g.add_tag("g")
    h = 3 * f + 2 * g
    h.add_tag("h")

    x_star = vector.Vector(is_basis=True, tags=["x_star"])
    star_triplet = h.add_point_with_grad_restriction(x_star, vector.Vector.zero())

    assert star_triplet.name == "x_star_3*f(x_star)+g(x_star)*2_0"
    assert star_triplet.grad.__repr__() == "0"
    assert star_triplet.func_val.__repr__() == "3*f(x_star)+g(x_star)*2"

    assert len(pep_context.func_to_triplets) == 2
    assert len(pep_context.func_to_triplets[f]) == 1
    assert len(pep_context.func_to_triplets[g]) == 1

    f_triplet = pep_context.func_to_triplets[f][0]
    g_triplet = pep_context.func_to_triplets[g][0]
    assert f_triplet.name == "x_star_f(x_star)_grad_f(x_star)"
    assert g_triplet.name == "x_star_g(x_star)_grad_g(x_star)"

    em = exm.ExpressionManager(pep_context)
    np.testing.assert_allclose(em.eval_vector(f_triplet.grad).coords, np.array([0, 1]))
    np.testing.assert_allclose(
        em.eval_vector(g_triplet.grad).coords, np.array([0, -1.5])
    )


def test_stationary_point(pep_context: pc.PEPContext):
    f = fc.Function(
        is_basis=True,
        tags=["f"],
    )
    f.set_stationary_point("x_star")

    assert len(pep_context.func_to_triplets) == 1
    assert len(pep_context.func_to_triplets[f]) == 1

    f_triplet = pep_context.func_to_triplets[f][0]
    assert f_triplet.name == "x_star_f(x_star)_grad_f(x_star)"
    assert f_triplet.grad.__repr__() == "grad_f(x_star)"
    assert f_triplet.func_val.__repr__() == "f(x_star)"

    em = exm.ExpressionManager(pep_context)
    np.testing.assert_allclose(em.eval_vector(f_triplet.grad).coords, np.array([0]))
    np.testing.assert_allclose(em.eval_vector(f_triplet.point).coords, np.array([1]))


def test_stationary_point_scaled(pep_context: pc.PEPContext):
    f = fc.Function(
        is_basis=True,
        tags=["f"],
    )
    g = 5 * f
    g.set_stationary_point("x_star")

    assert len(pep_context.func_to_triplets) == 1
    assert len(pep_context.func_to_triplets[f]) == 1

    f_triplet = pep_context.func_to_triplets[f][0]
    assert f_triplet.name == "x_star_f(x_star)_grad_f(x_star)"
    assert f_triplet.grad.__repr__() == "grad_f(x_star)"
    assert f_triplet.func_val.__repr__() == "f(x_star)"

    em = exm.ExpressionManager(pep_context)
    np.testing.assert_allclose(em.eval_vector(f_triplet.grad).coords, np.array([0]))
    np.testing.assert_allclose(em.eval_vector(f_triplet.point).coords, np.array([1]))


def test_stationary_point_additive(pep_context: pc.PEPContext):
    f = fc.Function(is_basis=True, tags=["f"])
    g = fc.Function(is_basis=True, tags=["g"])
    h = f + g
    h.add_tag("h")

    h.set_stationary_point("x_star")
    assert len(pep_context.func_to_triplets) == 2
    assert len(pep_context.func_to_triplets[f]) == 1
    assert len(pep_context.func_to_triplets[g]) == 1

    f_triplet = pep_context.func_to_triplets[f][0]
    g_triplet = pep_context.func_to_triplets[g][0]
    assert f_triplet.name == "x_star_f(x_star)_grad_f(x_star)"
    assert g_triplet.name == "x_star_g(x_star)_grad_g(x_star)"

    em = exm.ExpressionManager(pep_context)
    np.testing.assert_allclose(em.eval_vector(f_triplet.grad).coords, np.array([0, 1]))
    np.testing.assert_allclose(em.eval_vector(g_triplet.grad).coords, np.array([0, -1]))


def test_stationary_point_linear_combination(pep_context: pc.PEPContext):
    f = fc.Function(is_basis=True, tags=["f"])
    g = fc.Function(is_basis=True, tags=["g"])
    h = 3 * f + 2 * g
    h.add_tag("h")

    h.set_stationary_point("x_star")
    assert len(pep_context.func_to_triplets) == 2
    assert len(pep_context.func_to_triplets[f]) == 1
    assert len(pep_context.func_to_triplets[g]) == 1

    f_triplet = pep_context.func_to_triplets[f][0]
    g_triplet = pep_context.func_to_triplets[g][0]
    assert f_triplet.name == "x_star_f(x_star)_grad_f(x_star)"
    assert g_triplet.name == "x_star_g(x_star)_grad_g(x_star)"

    em = exm.ExpressionManager(pep_context)
    np.testing.assert_allclose(em.eval_vector(f_triplet.grad).coords, np.array([0, 1]))
    np.testing.assert_allclose(
        em.eval_vector(g_triplet.grad).coords, np.array([0, -1.5])
    )


def test_function_generate_triplet(pep_context: pc.PEPContext):
    f = fc.Function(is_basis=True, tags=["f"])
    g = fc.Function(is_basis=True, tags=["g"])
    h = 5 * f + 5 * g
    h.add_tag("h")

    p1 = vector.Vector(is_basis=True)
    p1.add_tag("p1")
    p1_triplet = h.generate_triplet(p1)
    p1_triplet_1 = h.generate_triplet(p1)

    assert (
        p1_triplet.name
        == f"{p1_triplet.point.tag}_{p1_triplet.func_val.__repr__()}_{p1_triplet.grad.__repr__()}"
    )
    assert (
        p1_triplet_1.name
        == f"{p1_triplet_1.point.tag}_{p1_triplet_1.func_val.__repr__()}_{p1_triplet_1.grad.__repr__()}"
    )

    pm = exm.ExpressionManager(pep_context)

    np.testing.assert_allclose(pm.eval_vector(p1).coords, np.array([1, 0, 0]))

    np.testing.assert_allclose(
        pm.eval_vector(p1_triplet.grad).coords, np.array([0, 5, 5])
    )
    np.testing.assert_allclose(
        pm.eval_scalar(p1_triplet.func_val).func_coords, np.array([5, 5])
    )

    np.testing.assert_allclose(
        pm.eval_vector(p1_triplet_1.grad).coords, np.array([0, 5, 5])
    )
    np.testing.assert_allclose(
        pm.eval_scalar(p1_triplet_1.func_val).func_coords, np.array([5, 5])
    )


def test_smooth_interpolability_constraints(pep_context: pc.PEPContext):
    f = fc.SmoothConvexFunction(is_basis=True, L=1, tags=["f"])
    _ = f.set_stationary_point("x_opt")

    x_0 = vector.Vector(is_basis=True)
    x_0.add_tag("x_0")
    _ = f.generate_triplet(x_0)

    all_interpolation_constraints = f.get_interpolation_constraints()

    pm = exm.ExpressionManager(pep_context)

    np.testing.assert_allclose(
        pm.eval_scalar(
            all_interpolation_constraints[1].lhs - all_interpolation_constraints[1].rhs
        ).func_coords,
        [1, -1],
    )
    np.testing.assert_allclose(
        pm.eval_scalar(
            all_interpolation_constraints[1].lhs - all_interpolation_constraints[1].rhs
        ).inner_prod_coords,
        [[0.0, 0.0, 0.0], [0.0, 0.0, 0.0], [0.0, 0.0, 0.5]],
    )

    np.testing.assert_allclose(
        pm.eval_scalar(
            all_interpolation_constraints[1].lhs - all_interpolation_constraints[1].rhs
        ).offset,
        0,
    )
