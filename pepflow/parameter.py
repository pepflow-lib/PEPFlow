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

import uuid
from collections import defaultdict
from typing import Any, FrozenSet, Tuple

import attrs
import sympy as sp

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
class Monomial:
    """Auxiliary class that serves as a key in a dictionary attribute of
    ParameterByDictRepresentation. Represents terms of the form a^n * b^m * ..."""

    powers: FrozenSet[Tuple[Parameter, int]]

    def __repr__(self) -> str:
        terms = [
            f"{param_with_name}^{exp}" if exp != 1 else str(param_with_name)
            for param_with_name, exp in sorted(
                self.powers, key=lambda x: (x[0].name, x[1])
            )
        ]
        return "*".join(terms)

    def __mul__(self, other: Monomial) -> Monomial:
        if not isinstance(other, Monomial):
            return NotImplemented
        new_powers = dict(self.powers)
        for param_with_name, exp in other.powers:
            new_powers[param_with_name] = new_powers.get(param_with_name, 0) + exp
        new_frozen_powers = frozenset(
            (param_with_name, exp)
            for param_with_name, exp in new_powers.items()
            if exp != 0
        )
        return Monomial(powers=new_frozen_powers)


@attrs.frozen
class ParameterByDictRepresentation:
    """A representation of a Parameter as a polynomial p(a, b, ...),
    where a, b, ... are Parameter objects with names."""

    # p(a, b, ...) = coeff_1 * a^{n_1} * b^{m_1} * ... + coeff_2 * a^{n_2} * b^{m_2} * ... * + ...
    numerator_polynomial_dict: defaultdict[Monomial, int | float | sp.Number] = (
        attrs.field(factory=lambda: defaultdict(int))
    )

    # TODO: implement denominator_polynomial_dict

    offset: int | float | sp.Number = 0

    # Generate an automatic id
    uid: uuid.UUID = attrs.field(factory=uuid.uuid4, init=False)

    def __repr__(self) -> str:
        terms = []
        if self.offset != 0:
            terms.append(repr(self.offset))
        for monomial, coeff in self.numerator_polynomial_dict.items():
            # TODO: Add the correct parentheses where needed
            if coeff == 1:
                terms.append(f"{repr(monomial)}")
            else:
                if utils.is_numerical_or_parameter(coeff):
                    coeff_str = utils.numerical_str(coeff)
                else:
                    coeff_str = repr(coeff)
                terms.append(f"{coeff_str}*{repr(monomial)}")
        return " + ".join(terms) if terms else "0"

    def __add__(
        self, other: utils.NUMERICAL_TYPE | ParameterByDictRepresentation
    ) -> utils.NUMERICAL_TYPE | ParameterByDictRepresentation:
        if not (
            utils.is_numerical(other)
            or isinstance(other, ParameterByDictRepresentation)
        ):
            return NotImplemented

        if utils.is_numerical(other):
            return ParameterByDictRepresentation(
                offset=self.offset + other,
                numerator_polynomial_dict=self.numerator_polynomial_dict,
            )

        assert isinstance(
            other, ParameterByDictRepresentation
        )  # to make type checker happy
        new_offset = self.offset + other.offset
        new_dict = self.numerator_polynomial_dict.copy()
        for monomial, coeff in other.numerator_polynomial_dict.items():
            if monomial in new_dict:
                new_dict[monomial] += coeff
                if new_dict[monomial] == 0:
                    del new_dict[monomial]
            else:
                new_dict[monomial] = coeff

        # TODO: Better to return zero when it is zero

        return ParameterByDictRepresentation(
            offset=new_offset, numerator_polynomial_dict=new_dict
        )

    def __radd__(
        self, other: utils.NUMERICAL_TYPE | ParameterByDictRepresentation
    ) -> utils.NUMERICAL_TYPE | ParameterByDictRepresentation:
        return self.__add__(other)

    def __neg__(
        self,
    ) -> ParameterByDictRepresentation:
        new_dict = defaultdict(int)
        for monomial, coeff in self.numerator_polynomial_dict.items():
            new_dict[monomial] = -coeff  # ty: ignore
        new_offset = -self.offset
        return ParameterByDictRepresentation(
            offset=new_offset, numerator_polynomial_dict=new_dict
        )

    def __sub__(
        self, other: utils.NUMERICAL_TYPE | ParameterByDictRepresentation
    ) -> utils.NUMERICAL_TYPE | ParameterByDictRepresentation:
        return self.__add__(-other)

    def __rsub__(
        self, other: utils.NUMERICAL_TYPE | ParameterByDictRepresentation
    ) -> utils.NUMERICAL_TYPE | ParameterByDictRepresentation:
        return (-self).__add__(other)

    def __mul__(
        self, other: utils.NUMERICAL_TYPE | ParameterByDictRepresentation
    ) -> utils.NUMERICAL_TYPE | ParameterByDictRepresentation:
        if not (
            utils.is_numerical(other)
            or isinstance(other, ParameterByDictRepresentation)
        ):
            return NotImplemented

        if isinstance(other, ParameterByDictRepresentation):
            # TODO: Allow multiplication between ParameterByDictRepresentation
            return NotImplemented

        new_dict = defaultdict(int)
        for monomial, coeff in self.numerator_polynomial_dict.items():
            new_dict[monomial] = coeff * other
            if new_dict[monomial] == 0:
                del new_dict[monomial]

        new_offset = self.offset * other

        return ParameterByDictRepresentation(
            numerator_polynomial_dict=new_dict,
            offset=new_offset,
        )

    def __rmul__(
        self, other: utils.NUMERICAL_TYPE | ParameterByDictRepresentation
    ) -> utils.NUMERICAL_TYPE | ParameterByDictRepresentation:
        return self.__mul__(other)

    def __truediv__(
        self, other: utils.NUMERICAL_TYPE | ParameterByDictRepresentation
    ) -> utils.NUMERICAL_TYPE | ParameterByDictRepresentation:
        if not (
            utils.is_numerical(other)
            or isinstance(other, ParameterByDictRepresentation)
        ):
            return NotImplemented

        return self.__mul__(1 / other)

    def __rtruediv__(
        self, other: utils.NUMERICAL_TYPE | ParameterByDictRepresentation
    ) -> utils.NUMERICAL_TYPE | ParameterByDictRepresentation:
        return (1 / self).__mul__(other)

    def is_zero(self) -> bool:
        return self.offset == 0 and not self.numerator_polynomial_dict

    def __hash__(self):
        return hash(self.uid)

    def __eq__(self, other):
        if not isinstance(other, ParameterByDictRepresentation):
            return NotImplemented
        return self.uid == other.uid

    def equiv(self, other: Any) -> bool:
        if not isinstance(other, ParameterByDictRepresentation):
            return False

        if (
            self.numerator_polynomial_dict.keys()
            != other.numerator_polynomial_dict.keys()
        ):
            return False

        for monomial in self.numerator_polynomial_dict:
            diff = utils.simplify_if_param_or_sympy_expr(
                self.numerator_polynomial_dict[monomial]
                - other.numerator_polynomial_dict[monomial]
            )
            if not utils.num_or_param_or_sympy_expr_is_zero(diff):
                return False

        diff_offset = utils.simplify_if_param_or_sympy_expr(self.offset - other.offset)
        if not utils.num_or_param_or_sympy_expr_is_zero(diff_offset):
            return False

        return True


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

    eval_expression: ParameterRepresentation | ParameterByDictRepresentation | None = (
        None
    )

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

        if isinstance(self.eval_expression, ParameterByDictRepresentation):
            return repr(self.eval_expression)

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

        if isinstance(self.eval_expression, ParameterByDictRepresentation):
            return NotImplemented  # TODO: implement this

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

    def equiv(self, other: Any) -> bool:
        if not isinstance(other, Parameter):
            return NotImplemented

        return utils.num_or_param_or_sympy_expr_is_zero(
            utils.simplify_if_param_or_sympy_expr(self - other)
        )

    def simplify(self) -> Parameter:
        """
        Flatten the `eval_expression` of a :class:`Parameter` object into a
        :class:`ParameterByDictRepresentation` consisting of generating terms and their coefficients.

        Returns:
            :class:`Parameter`: A new :class:`Parameter` object whose
            `eval_expression` is flattened into a
            :class:`ParameterByDictRepresentation`.
        """

        def _simplify(
            parameter_or_number: Parameter | utils.NUMERICAL_TYPE,
        ) -> ParameterByDictRepresentation | utils.NUMERICAL_TYPE:
            if isinstance(parameter_or_number, Parameter):
                # We know after simplification, the eval_expression is always
                # ParameterByDictRepresentation
                return parameter_or_number.simplify().eval_expression  # type: ignore
            elif isinstance(parameter_or_number, sp.Basic):
                simplified_result = parameter_or_number.simplify()
                assert isinstance(
                    simplified_result, utils.NUMERICAL_TYPE
                )  # to make type checker happy
                return simplified_result
            else:
                return parameter_or_number

        if self.name is not None:
            # The Monomial created in this conditional should be unique for each name.
            # If we keep `name = self.name`, another will be created each time we apply simplify repeatedly.
            name = None
            monomial_key = Monomial(frozenset({(self, 1)}))
            eval_expression = ParameterByDictRepresentation(
                numerator_polynomial_dict=defaultdict(int, {monomial_key: 1}),
                offset=0,
            )
        else:
            name = None
            if isinstance(self.eval_expression, ParameterByDictRepresentation):
                eval_expression = self.eval_expression
            else:
                assert isinstance(
                    self.eval_expression, ParameterRepresentation
                )  # to make type checker happy
                left_eval_expression = _simplify(self.eval_expression.left_param)
                right_eval_expression = _simplify(self.eval_expression.right_param)
                if self.eval_expression.op == utils.Op.ADD:
                    eval_expression = left_eval_expression + right_eval_expression
                elif self.eval_expression.op == utils.Op.SUB:
                    eval_expression = left_eval_expression - right_eval_expression
                elif self.eval_expression.op == utils.Op.MUL:
                    eval_expression = left_eval_expression * right_eval_expression
                elif self.eval_expression.op == utils.Op.DIV:
                    eval_expression = left_eval_expression / right_eval_expression
                else:
                    raise NotImplementedError(
                        "Only add,sub,mul,div are supported for Parameter simplification."
                    )

        return Parameter(name=name, eval_expression=eval_expression)
