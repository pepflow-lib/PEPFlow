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
from typing import TYPE_CHECKING, Any

import attrs
import numpy as np
import sympy as sp

from pepflow import math_expression as me
from pepflow import pep_context as pc
from pepflow import utils
from pepflow.scalar import Scalar, ScalarRepresentation

if TYPE_CHECKING:
    from pepflow.parameter import Parameter


def is_numerical_or_vector(val: Any) -> bool:
    return utils.is_numerical_or_parameter(val) or isinstance(val, Vector)


def is_numerical_or_evaluated_vector(val: Any) -> bool:
    return utils.is_numerical_or_parameter(val) or isinstance(val, EvaluatedVector)


@attrs.frozen
class VectorRepresentation:
    op: utils.Op
    left_vector: Vector | utils.NUMERICAL_TYPE | Parameter
    right_vector: Vector | utils.NUMERICAL_TYPE | Parameter


@attrs.frozen
class VectorByBasisRepresentation:
    """A representation of a Vector as a linear combination of basis Vectors."""

    # coeffs can be numerical or parameter type.
    coeffs: defaultdict[Vector, Any] = attrs.field(factory=lambda: defaultdict(int))

    def __repr__(self) -> str:
        # TODO: Improve representation for parameters and Scalar types.
        terms = []
        for vec, coeff in self.coeffs.items():
            if utils.is_numerical_or_parameter(coeff):
                coeff_str = utils.numerical_str(coeff)
            else:
                coeff_str = repr(coeff)
            terms.append(f"{coeff_str}*{repr(vec)}")
        return " + ".join(terms) if terms else "0"

    def __add__(
        self, other: VectorByBasisRepresentation
    ) -> VectorByBasisRepresentation:
        if not isinstance(other, VectorByBasisRepresentation):
            return NotImplemented

        new_coeffs = self.coeffs.copy()
        for vec, coeff in other.coeffs.items():
            if vec in new_coeffs:
                new_coeffs[vec] += coeff
            else:
                new_coeffs[vec] = coeff
        return VectorByBasisRepresentation(coeffs=new_coeffs)

    def __radd__(
        self, other: VectorByBasisRepresentation
    ) -> VectorByBasisRepresentation:
        return self.__add__(other)

    def __sub__(
        self, other: VectorByBasisRepresentation
    ) -> VectorByBasisRepresentation:
        if not isinstance(other, VectorByBasisRepresentation):
            return NotImplemented

        new_coeffs = self.coeffs.copy()
        for vec, coeff in other.coeffs.items():
            if vec in new_coeffs:
                new_coeffs[vec] -= coeff
            else:
                new_coeffs[vec] = -coeff
        return VectorByBasisRepresentation(coeffs=new_coeffs)

    def __mul__(
        self, scalar: utils.NUMERICAL_TYPE | Parameter
    ) -> VectorByBasisRepresentation:
        if not utils.is_numerical_or_parameter(scalar):
            return NotImplemented

        new_coeffs = defaultdict(int)
        for vec, coeff in self.coeffs.items():
            new_coeffs[vec] = coeff * scalar
        return VectorByBasisRepresentation(coeffs=new_coeffs)

    def __rmul__(
        self, scalar: utils.NUMERICAL_TYPE | Parameter
    ) -> VectorByBasisRepresentation:
        return self.__mul__(scalar)

    def __truediv__(
        self, scalar: utils.NUMERICAL_TYPE | Parameter
    ) -> VectorByBasisRepresentation:
        if not utils.is_numerical_or_parameter(scalar):
            return NotImplemented

        new_coeffs = defaultdict(int)
        for vec, coeff in self.coeffs.items():
            new_coeffs[vec] = coeff / scalar
        return VectorByBasisRepresentation(coeffs=new_coeffs)

    def __eq__(self, other: Any) -> bool:
        if not isinstance(other, VectorByBasisRepresentation):
            return False
        return self.coeffs == other.coeffs


@attrs.frozen
class ZeroVector:
    """A special class to represent 0 in Vector."""

    pass


@attrs.frozen
class EvaluatedVector:
    """
    The concrete representation of the abstract :class:`Vector`.

    Each abstract basis :class:`Vector` object has a unique concrete
    representation as a unit vector. The concrete representations of
    linear combinations of abstract basis :class:`Vector` objects are
    linear combinations of the unit vectors. This information is stored
    in the `coords` attribute.

    :class:`EvaluatedVector` objects can be constructed as linear combinations
    of other :class:`EvaluatedVector` objects. Let `a` and `b` be some numeric
    data type. Let `x` and `y` be :class:`EvaluatedVector` objects. Then, we
    can form a new :class:`EvaluatedVector` object: `a*x+b*y`.

    Attributes:
        coords (np.ndarray): The concrete representation of an
            abstract :class:`Vector`.
    """

    coords: np.ndarray

    @classmethod
    def zero(cls, num_basis_vectors: int, sympy_mode: bool = False):
        coords = np.zeros(num_basis_vectors)
        if sympy_mode:
            coords = coords * sp.S(0)
        return EvaluatedVector(coords=coords)

    def __add__(self, other):
        if isinstance(other, EvaluatedVector):
            return EvaluatedVector(coords=self.coords + other.coords)
        elif utils.is_numerical(other) or utils.is_sympy_expr(other):
            return EvaluatedVector(coords=self.coords + other)
        else:
            return NotImplemented

    def __radd__(self, other):
        return self.__add__(other)

    def __sub__(self, other):
        if isinstance(other, EvaluatedVector):
            return EvaluatedVector(coords=self.coords - other.coords)
        elif utils.is_numerical(other) or utils.is_sympy_expr(other):
            return EvaluatedVector(coords=self.coords - other)
        else:
            return NotImplemented

    def __rsub__(self, other):
        if isinstance(other, EvaluatedVector):
            return EvaluatedVector(coords=other.coords - self.coords)
        elif utils.is_numerical(other) or utils.is_sympy_expr(other):
            return EvaluatedVector(coords=other - self.coords)
        else:
            return NotImplemented

    def __mul__(self, other):
        if utils.is_numerical(other) or utils.is_sympy_expr(other):
            return EvaluatedVector(coords=self.coords * other)
        return NotImplemented

    def __rmul__(self, other):
        if utils.is_numerical(other) or utils.is_sympy_expr(other):
            return EvaluatedVector(coords=other * self.coords)
        return NotImplemented

    def __truediv__(self, other):
        if utils.is_numerical(other) or utils.is_sympy_expr(other):
            return EvaluatedVector(coords=self.coords / other)
        return NotImplemented


@attrs.frozen
class Vector:
    """
    A :class:`Vector` object represents an element of a vector space.

    Examples include a point or a gradient.

    :class:`Vector` objects can be constructed as linear combinations of
    other :class:`Vector` objects. Let `a` and `b` be some numeric data type.
    Let `x` and `y` be :class:`Vector` objects. Then, we can form a new
    :class:`Vector` object: `a*x+b*y`.

    The inner product of two :class:`Vector` objects can also be taken.
    Let `x` and `y` be :class:`Vector` objects. Then, their inner product is
    `x*y` and returns a :class:`Scalar` object.

    Attributes:
        is_basis (bool): `True` if this vector is not formed through a linear
            combination of other vectors. `False` otherwise.
        tags (list[str]): A list that contains tags that can be used to
            identify the :class:`Vector` object. Tags should be unique.
        math_expr (:class:`MathExpr`): A :class:`MathExpr` object with a
            member variable that contains a mathematical expression
            represented as a string.

    Example:
        >>> import pepflow as pf
        >>> ctx = pf.PEPContext("ctx").set_as_current()
        >>> x_0 = pf.Vector(is_basis=True).add_tag("x_0")

    Note:
        Basis :class:`Vector` objects should be defined using the constructor
        as shown in the example but composite :class:`Vector` objects should
        be created using operations on :class:`Vector` objects.
    """

    # If true, the vector is the basis for the evaluations of G
    is_basis: bool

    # The representation of vector used for evaluation.
    eval_expression: (
        VectorRepresentation | VectorByBasisRepresentation | ZeroVector | None
    ) = None

    # Human tagged value for the Vector
    tags: list[str] = attrs.field(factory=list)

    # Mathematical expression
    math_expr: me.MathExpr = attrs.field(factory=me.MathExpr)

    # Generate an automatic id
    uid: uuid.UUID = attrs.field(factory=uuid.uuid4, init=False)

    def __attrs_post_init__(self):
        if self.is_basis:
            assert self.eval_expression is None
        else:
            assert self.eval_expression is not None

        pep_context = pc.get_current_context()
        if pep_context is None:
            raise RuntimeError("Did you forget to create a context?")
        pep_context.add_vector(self)
        for tag in self.tags:
            pep_context.add_tag_to_vectors_or_scalars(tag, self)

        if self.tags:  # If tag is provided, make math_expr based on tag
            self.math_expr.expr_str = self.tag

    @staticmethod
    def zero() -> Vector:
        """A static method that returns a :class:`Vector` object that
        corresponds to zero.

        Returns:
            :class:`Vector`: A zero :class:`Vector` object.
        """
        return Vector(
            is_basis=False,
            eval_expression=ZeroVector(),
            math_expr=me.MathExpr(expr_str="0"),
        )

    @property
    def tag(self):
        """Returns the most recently added tag.

        Returns:
            str: The most recently added tag of this :class:`Vector` object.
        """
        if len(self.tags) == 0:
            raise ValueError("This Vector object doesn't have a tag.")
        return self.tags[-1]

    def add_tag(self, tag: str) -> "Vector":
        """Add a new tag for this :class:`Vector` object.

        Args:
            tag (str): The new tag to be added to the `tags` list.

        Returns:
            The instance itself.
        """
        pep_context = pc.get_current_context()
        if pep_context is None:
            raise RuntimeError("Did you forget to create a context?")
        pep_context.add_tag_to_vectors_or_scalars(tag, self)
        self.tags.append(tag)
        return self

    def __repr__(self):
        if self.tags:
            return self.tag
        if isinstance(self.math_expr, me.MathExpr):
            return repr(self.math_expr)
        return super().__repr__()

    def _repr_latex_(self):
        return utils.str_to_latex(repr(self))

    # TODO: Add a validator that `is_basis` and `eval_expression` are properly setup.
    def __add__(self, other):
        if not isinstance(other, Vector):
            return NotImplemented
        return Vector(
            is_basis=False,
            eval_expression=VectorRepresentation(utils.Op.ADD, self, other),
            tags=[],
            math_expr=me.MathExpr(f"{repr(self)}+{repr(other)}"),
        )

    def __radd__(self, other):
        # TODO: Come up with better way to handle this.
        if other.__repr__() == "0":
            return self
        if not isinstance(other, Vector):
            return NotImplemented
        return Vector(
            is_basis=False,
            eval_expression=VectorRepresentation(utils.Op.ADD, other, self),
            tags=[],
            math_expr=me.MathExpr(f"{repr(other)}+{repr(self)}"),
        )

    def __sub__(self, other):
        if not isinstance(other, Vector):
            return NotImplemented
        expr_other = utils.parenthesize_tag(other)
        return Vector(
            is_basis=False,
            eval_expression=VectorRepresentation(utils.Op.SUB, self, other),
            tags=[],
            math_expr=me.MathExpr(f"{repr(self)}-{expr_other}"),
        )

    def __rsub__(self, other):
        if not isinstance(other, Vector):
            return NotImplemented
        expr_self = utils.parenthesize_tag(self)
        return Vector(
            is_basis=False,
            eval_expression=VectorRepresentation(utils.Op.SUB, other, self),
            tags=[],
            math_expr=me.MathExpr(f"{repr(other)}-{expr_self}"),
        )

    def __mul__(self, other):
        if not is_numerical_or_vector(other):
            return NotImplemented
        expr_self = utils.parenthesize_tag(self)
        if utils.is_numerical_or_parameter(other):
            expr_other = utils.numerical_str(other)
            return Vector(
                is_basis=False,
                eval_expression=VectorRepresentation(utils.Op.MUL, self, other),
                tags=[],
                math_expr=me.MathExpr(f"{expr_self}*{expr_other}"),
            )
        else:
            expr_other = utils.parenthesize_tag(other)
            return Scalar(
                is_basis=False,
                eval_expression=ScalarRepresentation(utils.Op.MUL, self, other),
                tags=[],
                math_expr=me.MathExpr(f"{expr_self}*{expr_other}"),
            )

    def __rmul__(self, other):
        if not is_numerical_or_vector(other):
            return NotImplemented
        expr_self = utils.parenthesize_tag(self)
        if utils.is_numerical_or_parameter(other):
            expr_other = utils.numerical_str(other)
            return Vector(
                is_basis=False,
                eval_expression=VectorRepresentation(utils.Op.MUL, other, self),
                tags=[],
                math_expr=me.MathExpr(f"{expr_other}*{expr_self}"),
            )
        else:
            expr_other = utils.parenthesize_tag(other)
            return Scalar(
                is_basis=False,
                eval_expression=ScalarRepresentation(utils.Op.MUL, other, self),
                tags=[],
                math_expr=me.MathExpr(f"{expr_other}*{expr_self}"),
            )

    def __pow__(self, power):
        if power != 2:
            return NotImplemented
        return Scalar(
            is_basis=False,
            eval_expression=ScalarRepresentation(utils.Op.MUL, self, self),
            tags=[],
            math_expr=me.MathExpr(rf"|{repr(self)}|^{power}"),
        )

    def __neg__(self):
        expr_self = utils.parenthesize_tag(self)
        return Vector(
            is_basis=False,
            eval_expression=VectorRepresentation(utils.Op.MUL, -1, self),
            tags=[],
            math_expr=me.MathExpr(f"-{expr_self}"),
        )

    def __truediv__(self, other):
        if not utils.is_numerical_or_parameter(other):
            return NotImplemented
        expr_self = utils.parenthesize_tag(self)
        expr_other = f"1/{utils.numerical_str(other)}"
        return Vector(
            is_basis=False,
            eval_expression=VectorRepresentation(utils.Op.DIV, self, other),
            tags=[],
            math_expr=me.MathExpr(f"{expr_other}*{expr_self}"),
        )

    def __hash__(self):
        return hash(self.uid)

    def __eq__(self, other):
        if not isinstance(other, Vector):
            return NotImplemented
        return self.uid == other.uid

    def simplify(self, tag: str | None = None) -> Vector:
        """
        Simplify the mathematical expression of this :class:`Vector` object.

        Returns:
            :class:`Vector`: A new :class:`Vector` object with the simplified
            mathematical expression.
        """

        def _simplify(
            vector_or_float: Vector | utils.NUMERICAL_TYPE | Parameter,
        ) -> VectorByBasisRepresentation | utils.NUMERICAL_TYPE | Parameter:
            if isinstance(vector_or_float, Vector):
                # We know after simplification, the eval_expression is always VectorByBasisRepresentation.
                return vector_or_float.simplify().eval_expression  # type: ignore
            else:
                return vector_or_float

        if self.is_basis:
            # VectorByBasisRepresentation and the original basis vector are representating the
            # the same basis vector. However, we do not wanna introduce another basis vector in the context.
            # So we have to keep this is_basis = False but the eval_expression should be the same.
            is_basis = False
            eval_expression = VectorByBasisRepresentation(
                coeffs=defaultdict(int, {self: 1})
            )
        else:
            is_basis = False
            if isinstance(self.eval_expression, ZeroVector):
                eval_expression = VectorByBasisRepresentation(
                    coeffs=defaultdict(int, {})
                )
            elif isinstance(self.eval_expression, VectorByBasisRepresentation):
                eval_expression = self.eval_expression
            else:
                assert isinstance(self.eval_expression, VectorRepresentation)
                left_eval_exression = _simplify(self.eval_expression.left_vector)
                right_eval_exression = _simplify(self.eval_expression.right_vector)
                if self.eval_expression.op == utils.Op.ADD:
                    eval_expression = left_eval_exression + right_eval_exression
                elif self.eval_expression.op == utils.Op.SUB:
                    eval_expression = left_eval_exression - right_eval_exression
                elif self.eval_expression.op == utils.Op.MUL:
                    eval_expression = left_eval_exression * right_eval_exression
                elif self.eval_expression.op == utils.Op.DIV:
                    eval_expression = left_eval_exression / right_eval_exression
                else:
                    raise NotImplementedError(
                        "Division is not supported in simplification yet."
                    )

        return Vector(
            is_basis=is_basis,
            eval_expression=eval_expression,
            tags=[tag] if tag is not None else [],
            math_expr=me.MathExpr(
                expr_str=str(eval_expression)
            ),  # TODO(Jaewook): Fix this to use simplified_expr
        )

    def eval(
        self,
        ctx: pc.PEPContext | None = None,
        *,
        resolve_parameters: dict[str, utils.NUMERICAL_TYPE] | None = None,
        sympy_mode: bool = False,
    ) -> np.ndarray:
        """
        Return the concrete representation of this :class:`Vector`.

        Concrete representations of :class:`Vector` objects are
        :class:`EvaluatedVector` objects.

        Args:
            ctx (:class:`PEPContext` | None): The :class:`PEPContext` object
                we consider. `None` if we consider the current global
                :class:`PEPContext` object.
            resolve_parameters (dict[str, :data:`NUMERICAL_TYPE`] | `None`): A
                dictionary that maps the name of parameters to the numerical
                values.
            sympy_mode (bool): If true, then the input should be defined completely
                in terms of SymPy objects and should not mix Python numeric objects.
                Will raise an error if sympy_mode is `True` and the input contains a
                Python numeric object. By default `False`.

        Returns:
            :class:`EvaluatedVector`: The concrete representation of
            this :class:`Vector`.
        """
        from pepflow.expression_manager import ExpressionManager

        # Note this can be inefficient.
        if ctx is None:
            ctx = pc.get_current_context()
        if ctx is None:
            raise RuntimeError("Did you forget to create a context?")
        em = ExpressionManager(ctx, resolve_parameters=resolve_parameters)
        return em.eval_vector(self, sympy_mode=sympy_mode).coords

    def repr_by_basis(
        self,
        ctx: pc.PEPContext | None = None,
        *,
        resolve_parameters: dict[str, utils.NUMERICAL_TYPE] | None = None,
        sympy_mode: bool = False,
    ) -> str:
        """
        Express this :class:`Vector` object as the linear combination of
        the basis :class:`Vector` objects of the given :class:`PEPContext`.

        This linear combination is expressed as a `str` where, to refer to
        the basis :class:`Vector` objects, we use their tags.

        Args:
            ctx (:class:`PEPContext`): The :class:`PEPContext` object
                whose basis :class:`Vector` objects we consider. `None` if
                we consider the current global :class:`PEPContext` object.
            resolve_parameters (dict[str, :class:`NUMERICAL_TYPE`] | `None`): A
                dictionary that maps the name of parameters to the numerical values.
            sympy_mode (bool): If true, then the input should be defined completely
                in terms of SymPy objects and should not mix Python numeric objects.
                Will raise an error if sympy_mode is `True` and the input contains a
                Python numeric object. By default `False`.

        Returns:
            str: The representation of this :class:`Vector` object in terms of
            the basis :class:`Vector` objects of the given :class:`PEPContext`.
        """
        from pepflow.expression_manager import ExpressionManager

        # Note this can be inefficient.
        if ctx is None:
            ctx = pc.get_current_context()
        if ctx is None:
            raise RuntimeError("Did you forget to create a context?")
        em = ExpressionManager(ctx, resolve_parameters=resolve_parameters)
        return em.repr_vector_by_basis(self, sympy_mode=sympy_mode)
