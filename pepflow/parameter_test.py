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

from pepflow import pep_context as pc
from pepflow import registry as reg
from pepflow.expression_manager import ExpressionManager
from pepflow.parameter import Parameter
from pepflow.scalar import Scalar
from pepflow.vector import Vector


@pytest.fixture
def pep_context() -> Iterator[pc.PEPContext]:
    """Prepare the pep context and reset the context to None at the end."""

    ctx = pc.PEPContext("test").set_as_current()
    yield ctx
    pc.set_current_context(None)
    pc.GLOBAL_CONTEXT_DICT.clear()
    reg.REGISTERED_FUNC_AND_OPER_DICT.clear()


def test_parameter_interact_with_scalar(pep_context: pc.PEPContext):
    pm1 = Parameter("pm1")
    s1 = Scalar(is_basis=True, tags=["s1"])

    _ = pm1 + s1
    _ = s1 + pm1
    _ = pm1 - s1
    _ = s1 - pm1
    _ = s1 * pm1
    _ = pm1 * s1
    _ = s1 / pm1


def test_parameter_interact_with_point(pep_context: pc.PEPContext):
    pm1 = Parameter("pm1")
    p1 = Vector(is_basis=True, tags=["p1"])

    _ = p1 * pm1
    _ = pm1 * p1
    _ = p1 / pm1


def test_parameter_composition_with_point_and_scalar(pep_context: pc.PEPContext):
    pm1 = Parameter("pm1")
    pm2 = Parameter("pm2")
    p1 = Vector(is_basis=True, tags=["p1"])
    s1 = Scalar(is_basis=True, tags=["s1"])

    s2 = s1 + pm1 + pm2 * p1**2
    assert str(s2) == "s1+pm1+pm2*|p1|^2"


def test_parameter_composition(pep_context: pc.PEPContext):
    pm1 = Parameter("pm1")
    pm2 = Parameter("pm2")

    pp = (pm1 + 2) * pm2
    assert str(pp) == "(pm1+2)*pm2"
    assert pp.get_value({"pm1": 3, "pm2": 6}) == 30

    pp2 = (pm1 + sp.Rational(1, 2)) * pm2
    assert str(pp2) == "(pm1+1/2)*pm2"
    assert pp2.get_value({"pm1": sp.Rational(1, 3), "pm2": sp.Rational(6, 5)}) == 1


def test_expression_manager_eval_with_parameter(pep_context: pc.PEPContext):
    pm1 = Parameter("pm1")
    p1 = Vector(is_basis=True, tags=["p1"])
    p2 = Vector(is_basis=True, tags=["p2"])
    p3 = pm1 * p1 + p2 / 4

    em = ExpressionManager(pep_context, {"pm1": 2.3})
    np.testing.assert_allclose(em.eval_vector(p3).coords, np.array([2.3, 0.25]))

    em = ExpressionManager(pep_context, {"pm1": 3.4})
    np.testing.assert_allclose(em.eval_vector(p3).coords, np.array([3.4, 0.25]))


def test_expression_manager_eval_with_parameter_scalar(pep_context: pc.PEPContext):
    pm1 = Parameter("pm1")
    pm2 = Parameter("pm2")
    p1 = Vector(is_basis=True, tags=["p1"])
    p2 = Vector(is_basis=True, tags=["p2"])
    s1 = Scalar(is_basis=True, tags=["s1"])
    s2 = pm1 * p1 * p2 + pm2 + s1

    em = ExpressionManager(pep_context, {"pm1": 2.4, "pm2": 4.3})
    assert np.isclose(em.eval_scalar(s2).offset, 4.3)
    np.testing.assert_allclose(em.eval_scalar(s2).func_coords, np.array([1]))
    np.testing.assert_allclose(
        em.eval_scalar(s2).inner_prod_coords, np.array([[0, 1.2], [1.2, 0]])
    )


def test_expression_manager_eval_composition(pep_context: pc.PEPContext):
    pm1 = Parameter("pm1")
    pm2 = Parameter("pm2")
    p1 = Vector(is_basis=True, tags=["p1"])
    p2 = Vector(is_basis=True, tags=["p2"])
    s1 = Scalar(is_basis=True, tags=["s1"])

    s2 = 1 / pm1 * p1 * p2 + (pm2 + 1) * s1
    em = ExpressionManager(pep_context, {"pm1": 0.5, "pm2": 4.3})
    assert np.isclose(em.eval_scalar(s2).offset, 0)
    np.testing.assert_allclose(em.eval_scalar(s2).func_coords, np.array([5.3]))
    np.testing.assert_allclose(
        em.eval_scalar(s2).inner_prod_coords, np.array([[0, 1.0], [1.0, 0]])
    )


def test_parameter_with_sympy_symbolic(pep_context: pc.PEPContext):
    pm1 = Parameter("pm1")
    pm2 = Parameter("pm2")
    p1 = Vector(is_basis=True, tags=["p1"])
    p2 = Vector(is_basis=True, tags=["p2"])
    s1 = Scalar(is_basis=True, tags=["s1"])

    s2 = 1 / pm1 * p1 * p2 + (pm2 + 1) * s1
    em = ExpressionManager(pep_context, {"pm1": sp.Symbol("L"), "pm2": sp.Symbol("M")})
    evaled_s2 = em.eval_scalar(s2, sympy_mode=True)

    assert evaled_s2.offset == 0
    np.testing.assert_equal(evaled_s2.func_coords, [sp.Symbol("M") + 1])
    np.testing.assert_equal(
        evaled_s2.inner_prod_coords,
        [[sp.S(0), 1 / sp.Symbol("L") / 2], [1 / sp.Symbol("L") / 2, sp.S(0)]],
    )


def test_parameter_power(pep_context: pc.PEPContext):
    pm1 = Parameter("pm1")
    pm2 = Parameter("pm2")
    pm3 = Parameter("pm3")

    pp = pm1**2
    assert str(pp) == "pm1**2"
    assert pp.get_value({"pm1": sp.sqrt(2)}) == 2

    pp2 = pm1**pm2
    assert str(pp2) == "pm1**{pm2}"
    assert pp2.get_value({"pm1": 4, "pm2": 1 / 2}) == 2

    pp3 = pm1 ** (pm2**pm3)
    assert str(pp3) == "pm1**{pm2**{pm3}}"
    assert pp3.get_value({"pm1": sp.sqrt(2), "pm2": 2, "pm3": 3}) == 16

    pp4 = (pm1 + pm2) ** pm3
    assert str(pp4) == "(pm1+pm2)**{pm3}"
    assert pp4.get_value(
        {"pm1": sp.sqrt(2), "pm2": sp.sqrt(2), "pm3": 3}
    ) == 16 * sp.sqrt(2)
    assert pp4.get_value({"pm1": sp.pi, "pm2": sp.pi, "pm3": 3}) == 8 * sp.pi**3

    pp4_mul = (pm1 * pm2) ** pm3
    assert str(pp4_mul) == "(pm1*pm2)**{pm3}"

    pp4_pow = (pm1**pm2) ** pm3
    assert str(pp4_pow) == "(pm1**{pm2})**{pm3}"

    pp5 = 2**pm1
    assert str(pp5) == "2**{pm1}"
    assert isinstance(pp5, Parameter)
    assert pp5.get_value({"pm1": sp.pi}) == 2**sp.pi
    assert pp5.get_value({"pm1": 2}) == 4

    pp6 = np.sqrt(2) ** pm1
    assert str(pp6) == "1.414**{pm1}"
    assert not pp6.get_value({"pm1": 2}) == 2

    pp7 = sp.sqrt(2) ** pm1
    assert str(pp7) == "(sqrt(2))**{pm1}"
    assert pp7.get_value({"pm1": 2}) == 2


def test_parameter_comparison(pep_context: pc.PEPContext):
    pm1 = Parameter("pm1")
    pm2 = Parameter("pm2")
    pm3 = Parameter("pm1")  # same name as pm1 so we treat them as equal

    assert pm1 == pm3
    assert pm1 != pm2

    pp1 = (pm1 + 2) * pm2
    pp2 = (pm1 + 2) * pm2
    pp3 = (pm2 + 2) * pm1

    assert pp1 == pp2
    assert not pp1 == pp3
