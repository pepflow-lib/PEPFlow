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

import collections
from typing import Iterator

import numpy as np
import pytest
import sympy as sp

from pepflow import expression_manager as exm
from pepflow import parameter
from pepflow import pep as pep
from pepflow import pep_context as pc
from pepflow import registry as reg
from pepflow import scalar, vector


@pytest.fixture
def pep_context() -> Iterator[pc.PEPContext]:
    """Prepare the pep context and reset the context to None at the end."""

    ctx = pc.PEPContext("test").set_as_current()
    yield ctx
    pc.set_current_context(None)
    pc.GLOBAL_CONTEXT_DICT.clear()
    reg.REGISTERED_FUNC_AND_OPER_DICT.clear()


def test_scalar_add_tag(pep_context: pc.PEPContext):
    s1 = scalar.Scalar(is_basis=True, eval_expression=None, tags=["s1"])
    s2 = scalar.Scalar(is_basis=True, eval_expression=None, tags=["s2"])

    s_add = s1 + s2
    assert repr(s_add) == "s1+s2"

    s_add = s1 + 0.1
    assert repr(s_add) == "s1+0.1"

    s_radd = 0.1 + s1
    assert repr(s_radd) == "0.1+s1"

    s_sub = s1 - s2
    assert repr(s_sub) == "s1-s2"

    s_sub = s1 - (s2 + s1)
    assert repr(s_sub) == "s1-(s2+s1)"

    s_sub = s1 - (s2 - s1)
    assert repr(s_sub) == "s1-(s2-s1)"

    s_sub = s1 - 0.1
    assert repr(s_sub) == "s1-0.1"

    s_rsub = 0.1 - s1
    assert repr(s_rsub) == "0.1-s1"


def test_scalar_mul_tag(pep_context: pc.PEPContext):
    s = scalar.Scalar(is_basis=True, eval_expression=None, tags=["s"])

    s_mul = s * 0.1
    assert repr(s_mul) == "s*0.1"

    s_rmul = 0.1 * s
    assert repr(s_rmul) == "0.1*s"

    s_neg = -s
    assert repr(s_neg) == "-s"

    s_truediv = s / 0.1
    assert repr(s_truediv) == "1/0.1*s"


def test_scalar_add_and_mul_tag(pep_context: pc.PEPContext):
    s1 = scalar.Scalar(is_basis=True, eval_expression=None, tags=["s1"])
    s2 = scalar.Scalar(is_basis=True, eval_expression=None, tags=["s2"])

    s_add_mul = (s1 + s2) * 0.1
    assert repr(s_add_mul) == "(s1+s2)*0.1"

    s_add_mul = s1 + s2 * 0.1
    assert repr(s_add_mul) == "s1+s2*0.1"

    s_neg_add = -(s1 + s2)
    assert repr(s_neg_add) == "-(s1+s2)"

    s_rmul_add = 0.1 * (s1 + s2)
    assert repr(s_rmul_add) == "0.1*(s1+s2)"


def test_scalar_hash_different(pep_context: pc.PEPContext):
    s1 = scalar.Scalar(is_basis=True, eval_expression=None)
    s2 = scalar.Scalar(is_basis=True, eval_expression=None)
    assert s1.uid != s2.uid


def test_scalar_tag(pep_context: pc.PEPContext):
    s1 = scalar.Scalar(is_basis=True, eval_expression=None)
    s1.add_tag(tag="my_tag")
    assert s1.tags == ["my_tag"]
    assert s1.tag == "my_tag"


def test_scalar_repr(pep_context: pc.PEPContext):
    s1 = scalar.Scalar(is_basis=True, tags=["s1"])
    print(s1)  # it should be fine without tag
    s1.add_tag("my_tag")
    assert str(s1) == "my_tag"


def test_scalar_in_a_list(pep_context: pc.PEPContext):
    s1 = scalar.Scalar(is_basis=True, eval_expression=None)
    s2 = scalar.Scalar(is_basis=True, eval_expression=None)
    s3 = scalar.Scalar(is_basis=True, eval_expression=None)
    assert s1 in [s1, s2]
    assert s3 not in [s1, s2]


def test_scalar_eval_and_repr_with_parameter(pep_context: pc.PEPContext):
    p1 = vector.Vector(is_basis=True, tags=["p1"])
    s1 = scalar.Scalar(is_basis=True, eval_expression=None, tags=["s1"])
    pm = parameter.Parameter(name="pm")
    s2 = pm * s1 + p1 * p1 * pm

    eval_s2 = s2.eval(resolve_parameters={"pm": 3})
    np.testing.assert_allclose(eval_s2.inner_prod_coords, np.array([[3]]))
    np.testing.assert_allclose(eval_s2.func_coords, np.array([3]))
    assert (
        s2.repr_by_basis(resolve_parameters={"pm": 2.3}, greedy_square=True)
        == "2.3*s1 + 2.3*|p1|^2"
    )


def test_zero_scalar(pep_context):
    _ = scalar.Scalar(is_basis=True, tags=["s1"])
    _ = vector.Vector(is_basis=True, tags=["p1"])
    s0 = scalar.Scalar.zero()

    pm = exm.ExpressionManager(pep_context)
    np.testing.assert_allclose(pm.eval_scalar(s0).func_coords, np.array([0]))
    np.testing.assert_allclose(pm.eval_scalar(s0).inner_prod_coords, np.array([[0]]))

    # sympy mode
    np.testing.assert_equal(
        pm.eval_scalar(s0, sympy_mode=True).func_coords,
        np.array([sp.S(0)]),
        strict=True,
    )
    np.testing.assert_equal(
        pm.eval_scalar(s0, sympy_mode=True).inner_prod_coords,
        np.array([[sp.S(0)]]),
        strict=True,
    )

    _ = vector.Vector(is_basis=True, tags=["p2"])
    pm = exm.ExpressionManager(pep_context)
    np.testing.assert_allclose(pm.eval_scalar(s0).func_coords, np.array([0]))
    np.testing.assert_allclose(
        pm.eval_scalar(s0).inner_prod_coords, np.array([[0, 0], [0, 0]])
    )

    # sympy mode
    np.testing.assert_equal(
        pm.eval_scalar(s0, sympy_mode=True).func_coords,
        np.array([sp.S(0)]),
        strict=True,
    )
    np.testing.assert_equal(
        pm.eval_scalar(s0, sympy_mode=True).inner_prod_coords,
        np.array([[sp.S(0), sp.S(0)], [sp.S(0), sp.S(0)]]),
        strict=True,
    )


def make_rep(funcs=None, inners=None, offset=0):
    return scalar.ScalarByBasisRepresentation(
        func_coeffs=collections.defaultdict(int, funcs or {}),
        inner_prod_coeffs=collections.defaultdict(int, inners or {}),
        offset=offset,
    )


def test_scalar_by_basis_operations(pep_context):
    f1 = scalar.Scalar(is_basis=True, tags=["f1"])
    f2 = scalar.Scalar(is_basis=True, tags=["f2"])
    v1 = vector.Vector(is_basis=True, tags=["v1"])
    v2 = vector.Vector(is_basis=True, tags=["v2"])

    a = make_rep(funcs={f1: 2}, inners={(v1, v2): 3}, offset=1)
    b = make_rep(funcs={f1: 5, f2: 4}, inners={(v1, v2): 4}, offset=2)

    c = a + b
    assert c.func_coeffs[f1] == 7
    assert c.func_coeffs[f2] == 4
    assert c.inner_prod_coeffs[(v1, v2)] == 7
    assert c.offset == 3

    c = a - b
    assert c.func_coeffs[f1] == -3
    assert c.func_coeffs.get(f2, 0) == -4
    assert c.inner_prod_coeffs[(v1, v2)] == -1
    assert c.offset == -1

    d = a * 3
    assert d.func_coeffs[f1] == 6
    assert d.inner_prod_coeffs[(v1, v2)] == 9
    assert d.offset == 3

    c = 2 * a
    assert c.func_coeffs[f1] == 4
    assert c.inner_prod_coeffs[(v1, v2)] == 6
    assert c.offset == 2

    d = a / 2
    assert d.func_coeffs[f1] == 1
    assert d.inner_prod_coeffs[(v1, v2)] == 1.5
    assert d.offset == 0.5

    e = -a
    assert e.func_coeffs[f1] == -2
    assert e.inner_prod_coeffs[(v1, v2)] == -3
    assert e.offset == -1


def test_scalar_by_basis_with_parameter_coeffs(pep_context):
    f1 = scalar.Scalar(is_basis=True, tags=["f1"])
    v1 = vector.Vector(is_basis=True, tags=["v1"])
    v2 = vector.Vector(is_basis=True, tags=["v2"])
    pm = parameter.Parameter(name="pm")
    a = make_rep(funcs={f1: 2}, inners={(v1, v2): 3}, offset=4)

    b = a * pm
    assert b.func_coeffs[f1] == 2 * pm
    assert b.inner_prod_coeffs[(v1, v2)] == 3 * pm
    assert b.offset == 4 * pm

    d = a / pm
    assert isinstance(d.func_coeffs[f1], parameter.Parameter)
    assert isinstance(d.inner_prod_coeffs[(v1, v2)], parameter.Parameter)
    assert isinstance(d.offset, parameter.Parameter)
