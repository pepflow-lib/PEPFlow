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

from pepflow import function as fc
from pepflow import pep
from pepflow import pep_context as pc
from pepflow import registry as reg


@pytest.fixture
def pep_context() -> Iterator[pc.PEPContext]:
    """Prepare the pep context and reset the context to None at the end."""

    ctx = pc.PEPContext("test").set_as_current()
    yield ctx
    pc.set_current_context(None)
    pc.GLOBAL_CONTEXT_DICT.clear()
    reg.REGISTERED_FUNC_AND_OPER_DICT.clear()
    reg.REGISTERED_FUNC_AND_OPER_DICT.clear()


def test_add_initial_constraint_twice(pep_context: pc.PEPContext) -> None:
    builder = pep.PEPBuilder(pep_context)

    f = reg.declare_func(fc.SmoothConvexFunction, "f", L=1)
    x = builder.add_init_point("x_0")
    x_star = f.set_stationary_point("x_star")
    builder.add_initial_constraint(((x - x_star) ** 2).le(1, name="initial_condition"))
    with pytest.raises(
        ValueError,
        match="An initial constraint with the same name as initial_condition already exists.",
    ):
        builder.add_initial_constraint(
            ((x - x_star) ** 2).le(1, name="initial_condition")
        )
