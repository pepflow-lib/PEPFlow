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

import pytest

from pepflow import pep_context as pc
from pepflow import registry as reg
from pepflow.function import SmoothConvexFunction
from pepflow.operator import Operator
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


def test_get_triplet_by_point_tag(pep_context: pc.PEPContext):
    f = SmoothConvexFunction(L=1, is_basis=True, tags=["f"])
    p1 = Vector(is_basis=True, tags=["x_1"])
    p2 = Vector(is_basis=True, tags=["x_3"])
    # Add triplet into context
    fv1 = f(p1)
    gf2 = f.grad(p2)

    t1 = pep_context.get_triplet_by_point_tag(p1, f)
    t2 = pep_context.get_triplet_by_point_tag("x_3", f)

    assert t1.func_val == fv1
    assert t2.grad == gf2

    with pytest.raises(ValueError, match="Cannot find the triplet associated with x_9"):
        pep_context.get_triplet_by_point_tag("x_9", f)


def test_tracked_points_func(pep_context: pc.PEPContext):
    f = SmoothConvexFunction(L=1, is_basis=True, tags=["f"])

    p1 = Vector(is_basis=True, tags=["x_1"])
    p2 = Vector(is_basis=True, tags=["x_3"])
    p3 = Vector(is_basis=True, tags=["x_2"])
    p_star = Vector(is_basis=True, tags=["x_*"])

    _ = f.generate_triplet(p1)
    _ = f.generate_triplet(p2)
    _ = f.generate_triplet(p3)
    _ = f.generate_triplet(p_star)

    assert pep_context.order_of_point(f) == ["x_1", "x_2", "x_3", "x_*"]
    assert pep_context.tracked_point(f) == [p1, p3, p2, p_star]


def test_tracked_points_oper(pep_context: pc.PEPContext):
    A = Operator(
        is_basis=True,
        tags=["A"],
    )

    p1 = Vector(is_basis=True, tags=["x_1"])
    p2 = Vector(is_basis=True, tags=["x_3"])
    p3 = Vector(is_basis=True, tags=["x_2"])
    p_star = Vector(is_basis=True, tags=["x_*"])

    _ = A.generate_duplet(p1)
    _ = A.generate_duplet(p2)
    _ = A.generate_duplet(p3)
    _ = A.generate_duplet(p_star)

    assert pep_context.order_of_point(A) == ["x_1", "x_2", "x_3", "x_*"]
    assert pep_context.tracked_point(A) == [p1, p3, p2, p_star]


def test_get_by_tag(pep_context: pc.PEPContext):
    p1 = Vector(is_basis=True, tags=["x1"])
    p2 = Vector(is_basis=True, tags=["x2"])
    p3 = (p1 + p2).add_tag("p3")

    assert pep_context.get_by_tag("x1") == p1
    assert pep_context.get_by_tag("p3") == p3
    pc.set_current_context(None)


def test_basis_vectors(pep_context: pc.PEPContext):
    p1 = Vector(is_basis=True, tags=["x1"])
    p2 = Vector(is_basis=True, tags=["x2"])
    _ = p1 + p2  # not basis
    ps = Vector(is_basis=True, tags=["x_star"])
    p0 = Vector(is_basis=True, tags=["x0"])

    assert pep_context.basis_vectors() == [p1, p2, ps, p0]


def test_basis_scalars(pep_context: pc.PEPContext):
    p1 = Vector(is_basis=True, tags=["x1"])
    p2 = Vector(is_basis=True, tags=["x2"])
    _ = p1 * p2  # not basis
    s1 = Scalar(is_basis=True, tags=["s2"])
    s2 = Scalar(is_basis=True, tags=["s1"])

    assert pep_context.basis_scalars() == [s1, s2]


def test_tracked_point_func(pep_context: pc.PEPContext):
    f = SmoothConvexFunction(L=1, is_basis=True, tags=["f"])
    p1 = Vector(is_basis=True, tags=["x2"])
    p2 = Vector(is_basis=True, tags=["x1"])

    _ = f.generate_triplet(p1)
    _ = f.generate_triplet(p2)

    assert pep_context.tracked_point(f) == [p2, p1]


def test_tracked_point_oper(pep_context: pc.PEPContext):
    A = Operator(
        is_basis=True,
        tags=["A"],
    )
    p1 = Vector(is_basis=True, tags=["x2"])
    p2 = Vector(is_basis=True, tags=["x1"])

    _ = A.generate_duplet(p1)
    _ = A.generate_duplet(p2)

    assert pep_context.tracked_point(A) == [p2, p1]


def test_tracked_grad(pep_context: pc.PEPContext):
    f = SmoothConvexFunction(L=1, is_basis=True, tags=["f"])
    p1 = Vector(is_basis=True, tags=["x2"])
    p2 = Vector(is_basis=True, tags=["x1"])

    triplet1 = f.generate_triplet(p1)
    triplet2 = f.generate_triplet(p2)

    assert pep_context.tracked_grad(f) == [triplet2.grad, triplet1.grad]


def test_tracked_func_val(pep_context: pc.PEPContext):
    f = SmoothConvexFunction(L=1, is_basis=True, tags=["f"])
    p1 = Vector(is_basis=True, tags=["x2"])
    p2 = Vector(is_basis=True, tags=["x1"])

    triplet1 = f.generate_triplet(p1)
    triplet2 = f.generate_triplet(p2)

    assert pep_context.tracked_func_val(f) == [triplet2.func_val, triplet1.func_val]


def test_tracked_output(pep_context: pc.PEPContext):
    A = Operator(
        is_basis=True,
        tags=["A"],
    )
    p1 = Vector(is_basis=True, tags=["x2"])
    p2 = Vector(is_basis=True, tags=["x1"])

    duplet1 = A.generate_duplet(p1)
    duplet2 = A.generate_duplet(p2)

    assert pep_context.tracked_output(A) == [duplet2.output, duplet1.output]


def test_order_of_point_func(pep_context: pc.PEPContext):
    f = SmoothConvexFunction(L=1, is_basis=True, tags=["f"])
    p1 = Vector(is_basis=True, tags=["x2"])
    p2 = Vector(is_basis=True, tags=["x1"])

    _ = f.generate_triplet(p1)
    _ = f.generate_triplet(p2)

    assert pep_context.order_of_point(f) == [p2.tag, p1.tag]


def test_order_of_point_oper(pep_context: pc.PEPContext):
    A = Operator(
        is_basis=True,
        tags=["A"],
    )
    p1 = Vector(is_basis=True, tags=["x2"])
    p2 = Vector(is_basis=True, tags=["x1"])

    _ = A.generate_duplet(p1)
    _ = A.generate_duplet(p2)

    assert pep_context.order_of_point(A) == [p2.tag, p1.tag]


def test_get_func_or_oper_by_tag(pep_context: pc.PEPContext) -> None:
    f = reg.declare_func(SmoothConvexFunction, "f", L=1)
    g = reg.declare_func(SmoothConvexFunction, "g", L=1)
    A = Operator(
        is_basis=True,
        tags=["A"],
    )
    A.add_tag("A1")
    # h = f + g #TODO need to discuss this point
    h = (f + g).add_tag("h")
    f.add_tag("f1")
    g.add_tag("g1")
    assert reg.get_func_or_oper_by_tag("f") == f
    assert reg.get_func_or_oper_by_tag("f1") == f
    assert reg.get_func_or_oper_by_tag("g") == g
    assert reg.get_func_or_oper_by_tag("g1") == g
    # assert reg.get_func_or_oper_by_tag("f+g") == h #TODO need to discuss this point
    assert reg.get_func_or_oper_by_tag("h") == h  # TODO need to discuss this point
    assert reg.get_func_or_oper_by_tag("A") == A
    assert reg.get_func_or_oper_by_tag("A1") == A


def test_tag_to_vectors_or_scalars(pep_context: pc.PEPContext):
    f = SmoothConvexFunction(L=1, is_basis=True, tags=["f"])
    p1 = Vector(is_basis=True, tags=["x2"])
    p2 = Vector(is_basis=True, tags=["x1"])

    _ = f.generate_triplet(p1)
    _ = f.generate_triplet(p2)

    assert pep_context.tag_to_vectors_or_scalars["x2"] == p1
    assert pep_context.tag_to_vectors_or_scalars["x1"] == p2


def test_vector_to_triplet_or_duplet(pep_context: pc.PEPContext):
    f = SmoothConvexFunction(L=1, is_basis=True, tags=["f"])
    p1 = Vector(is_basis=True, tags=["x2"])
    p2 = Vector(is_basis=True, tags=["x1"])

    t1 = f.generate_triplet(p1)
    t2 = f.generate_triplet(p2)

    A = Operator(
        is_basis=True,
        tags=["A"],
    )

    d1 = A.generate_duplet(p1)
    d2 = A.generate_duplet(p2)

    assert pep_context.vector_to_triplet_or_duplet[p1] == ([t1], [d1])
    assert pep_context.vector_to_triplet_or_duplet[p2] == ([t2], [d2])
