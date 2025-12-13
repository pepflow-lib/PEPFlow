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

from __future__ import annotations

import attrs

from pepflow import utils

# Sentinel of not founding resolving parameters
NOT_FOUND = "__NOT_FOUND__"


@attrs.frozen
class ParameterRepresentation:
    op: utils.Op
    left_param: utils.NUMERICAL_TYPE | Parameter
    right_param: utils.NUMERICAL_TYPE | Parameter


def eval_parameter(
    param: Parameter | utils.NUMERICAL_TYPE,
    resolve_parameters: dict[str, utils.NUMERICAL_TYPE],
) -> utils.NUMERICAL_TYPE:
    if isinstance(param, Parameter):
        return param.get_value(resolve_parameters)
    if utils.is_numerical(param):
        return param
    if utils.is_sympy_expr(param):
        return param
    raise ValueError(f"Encounter the unknown parameter type: {param} ({type(param)})")


@attrs.frozen
class Parameter:
    """
    A :class:`Parameter` object that represents some numerial value that can be
    resolved later.

    Attributes:
        name (str | None): The name of the :class:`Parameter` object. If name is
            `None`, it means it is a composite parameter and `eval_expression`
            needs to be provided.
        eval_expression (:class:`ParameterRepresentation` | None): A datastructure
            that is used to evaluate the value of parameter.

    Example:
        >>> import pepflow as pf
        >>> ctx = pf.PEPContext("example").set_as_current()
        >>> v = pf.Vector(is_basis=True, tag=["p1"])
        >>> pm = pf.Parameter(name="param")
        >>> v2 = pm * v
        >>> v2.eval(resolve_parameters={"param": 2})

    Note:
        Basis :class:`Parameter` objects should be defined using the constructor
        as shown in the example but composite :class:`Parameter` objects should
        be created using operations on :class:`Parameter` objects.
    """

    # If name is None, it is a composite parameter.
    name: str | None

    eval_expression: ParameterRepresentation | None = None

    def __attrs_post_init__(self):
        if self.name is None and self.eval_expression is None:
            raise ValueError(
                "For a parameter, a name or an eval_expression must be specified."
            )
        if self.name is None or self.eval_expression is None:
            return

        raise ValueError(
            "For a parameter, only one of name or eval_expression should be None."
        )

    def __repr__(self):
        if self.eval_expression is None:
            return self.name

        op = self.eval_expression.op
        if op == utils.Op.POW:
            left_param = utils.parenthesize_repr(
                self.eval_expression.left_param, pow_base=True
            )
            right_param = utils.parenthesize_repr(
                self.eval_expression.right_param, pow_exponent=True
            )
        elif op == utils.Op.ADD:
            left_param = self.eval_expression.left_param.__repr__()
            right_param = self.eval_expression.right_param.__repr__()
        else:
            left_param = utils.parenthesize_repr(self.eval_expression.left_param)
            right_param = utils.parenthesize_repr(self.eval_expression.right_param)

        if op == utils.Op.ADD:
            return f"{left_param}+{right_param}"
        if op == utils.Op.SUB:
            return f"{left_param}-{right_param}"
        if op == utils.Op.MUL:
            return f"{left_param}*{right_param}"
        if op == utils.Op.DIV:
            return f"{left_param}/{right_param}"
        if op == utils.Op.POW:
            return f"{left_param}**{right_param}"

    def _repr_latex_(self):
        return utils.str_to_latex(repr(self))

    def get_value(
        self, resolve_parameters: dict[str, utils.NUMERICAL_TYPE]
    ) -> utils.NUMERICAL_TYPE:
        if self.eval_expression is None:
            val = resolve_parameters.get(self.name, NOT_FOUND)  # ty:ignore
            if val is NOT_FOUND:
                raise ValueError(f"Cannot resolve Parameter named: {self.name}")
            return val
        op = self.eval_expression.op
        left_param = eval_parameter(self.eval_expression.left_param, resolve_parameters)
        right_param = eval_parameter(
            self.eval_expression.right_param, resolve_parameters
        )

        if op == utils.Op.ADD:
            return left_param + right_param
        if op == utils.Op.SUB:
            return left_param - right_param
        if op == utils.Op.MUL:
            return left_param * right_param
        if op == utils.Op.DIV:
            return left_param / right_param
        if op == utils.Op.POW:
            return left_param**right_param

        raise ValueError(f"Encountered unknown {op=} when evaluation the point.")

    def __add__(self, other):
        if not utils.is_numerical_or_parameter(other):
            return NotImplemented
        return Parameter(
            name=None,
            eval_expression=ParameterRepresentation(
                op=utils.Op.ADD, left_param=self, right_param=other
            ),
        )

    def __radd__(self, other):
        if not utils.is_numerical_or_parameter(other):
            return NotImplemented
        return Parameter(
            name=None,
            eval_expression=ParameterRepresentation(
                op=utils.Op.ADD, left_param=other, right_param=self
            ),
        )

    def __sub__(self, other):
        if not utils.is_numerical_or_parameter(other):
            return NotImplemented
        return Parameter(
            name=None,
            eval_expression=ParameterRepresentation(
                op=utils.Op.SUB, left_param=self, right_param=other
            ),
        )

    def __rsub__(self, other):
        if not utils.is_numerical_or_parameter(other):
            return NotImplemented
        return Parameter(
            name=None,
            eval_expression=ParameterRepresentation(
                op=utils.Op.SUB, left_param=other, right_param=self
            ),
        )

    def __mul__(self, other):
        if not utils.is_numerical_or_parameter(other):
            return NotImplemented
        return Parameter(
            name=None,
            eval_expression=ParameterRepresentation(
                op=utils.Op.MUL, left_param=self, right_param=other
            ),
        )

    def __rmul__(self, other):
        if not utils.is_numerical_or_parameter(other):
            return NotImplemented
        return Parameter(
            name=None,
            eval_expression=ParameterRepresentation(
                op=utils.Op.MUL, left_param=other, right_param=self
            ),
        )

    def __neg__(self):
        return self.__rmul__(other=-1)

    def __truediv__(self, other):
        if not utils.is_numerical_or_parameter(other):
            return NotImplemented
        return Parameter(
            name=None,
            eval_expression=ParameterRepresentation(
                op=utils.Op.DIV, left_param=self, right_param=other
            ),
        )

    def __rtruediv__(self, other):
        if not utils.is_numerical_or_parameter(other):
            return NotImplemented
        return Parameter(
            name=None,
            eval_expression=ParameterRepresentation(
                op=utils.Op.DIV, left_param=other, right_param=self
            ),
        )

    def __pow__(self, other) -> Parameter:
        if not utils.is_numerical_or_parameter(other):
            return NotImplemented
        return Parameter(
            name=None,
            eval_expression=ParameterRepresentation(
                op=utils.Op.POW, left_param=self, right_param=other
            ),
        )

    def __rpow__(self, other) -> Parameter:
        if not utils.is_numerical_or_parameter(other):
            return NotImplemented
        return Parameter(
            name=None,
            eval_expression=ParameterRepresentation(
                op=utils.Op.POW, left_param=other, right_param=self
            ),
        )
