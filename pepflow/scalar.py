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

from pepflow import constraint as ctr
from pepflow import math_expression as me
from pepflow import pep_context as pc
from pepflow import utils

if TYPE_CHECKING:
    from pepflow.parameter import Parameter
    from pepflow.vector import Vector, VectorByBasisRepresentation


def is_numerical_or_scalar(val: Any) -> bool:
    return utils.is_numerical_or_parameter(val) or isinstance(val, Scalar)


def is_numerical_or_evaluatedscalar(val: Any) -> bool:
    return utils.is_numerical_or_parameter(val) or isinstance(val, EvaluatedScalar)


@attrs.frozen
class ScalarRepresentation:
    op: utils.Op
    left_scalar: Vector | Scalar | float
    right_scalar: Vector | Scalar | float


@attrs.frozen
class ScalarByBasisRepresentation:
    """A representation of a Scalar as a linear combination of basis Scalars."""

    # The following represents `coef1*f1 + coef2*f2 + ...`
    func_coeffs: defaultdict[Scalar, Any] = attrs.field(
        factory=lambda: defaultdict(int)
    )
    # The following represents `sum coef_ij*<v_i, v_j>`.
    # We should sort the vector in key so that <v_i, v_j> and <v_j, v_i> use the same entry.
    inner_prod_coeffs: defaultdict[tuple[Vector, Vector], Any] = attrs.field(
        factory=lambda: defaultdict(int)
    )
    offset: Any = 0

    def __repr__(self) -> str:
        terms = []
        for key, val in self.func_coeffs.items():
            # TODO: Add the correct parentheses where needed
            if utils.is_numerical_or_parameter(val):
                coeff_str = utils.numerical_str(val)
            else:
                coeff_str = repr(val)
            terms.append(f"{coeff_str}*{repr(key)}")
        for key, val in self.inner_prod_coeffs.items():
            # TODO: Add the correct parentheses where needed
            if utils.is_numerical_or_parameter(val):
                coeff_str = utils.numerical_str(val)
            else:
                coeff_str = repr(val)
            vec0_repr, vec1_repr = repr(key[0]), repr(key[1])
            if vec0_repr != vec1_repr:
                terms.append(f"{coeff_str}*⟨{vec0_repr},{vec1_repr}⟩")
            else:
                terms.append(f"{coeff_str}*|{vec0_repr}|^2")
        return " + ".join(terms) if terms else "0"

    def __add__(
        self, other: ScalarByBasisRepresentation
    ) -> ScalarByBasisRepresentation:
        if not isinstance(other, ScalarByBasisRepresentation):
            return NotImplemented
        new_func_coeffs = defaultdict(int, self.func_coeffs)
        for key, val in other.func_coeffs.items():
            new_func_coeffs[key] += val

        new_inner_prod_coeffs = defaultdict(int, self.inner_prod_coeffs)
        for key, val in other.inner_prod_coeffs.items():
            new_inner_prod_coeffs[key] += val

        new_offset = self.offset + other.offset

        return ScalarByBasisRepresentation(
            func_coeffs=new_func_coeffs,
            inner_prod_coeffs=new_inner_prod_coeffs,
            offset=new_offset,
        )

    def __radd__(
        self, other: ScalarByBasisRepresentation
    ) -> ScalarByBasisRepresentation:
        return self.__add__(other)

    def __sub__(
        self, other: ScalarByBasisRepresentation
    ) -> ScalarByBasisRepresentation:
        if not isinstance(other, ScalarByBasisRepresentation):
            return NotImplemented
        new_func_coeffs = defaultdict(int, self.func_coeffs)
        for key, val in other.func_coeffs.items():
            new_func_coeffs[key] -= val

        new_inner_prod_coeffs = defaultdict(int, self.inner_prod_coeffs)
        for key, val in other.inner_prod_coeffs.items():
            new_inner_prod_coeffs[key] -= val

        new_offset = self.offset - other.offset

        return ScalarByBasisRepresentation(
            func_coeffs=new_func_coeffs,
            inner_prod_coeffs=new_inner_prod_coeffs,
            offset=new_offset,
        )

    def __mul__(
        self, other: utils.NUMERICAL_TYPE | Parameter
    ) -> ScalarByBasisRepresentation:
        if not utils.is_numerical_or_parameter(other):
            return NotImplemented

        new_func_coeffs = defaultdict(int)
        for key, val in self.func_coeffs.items():
            new_func_coeffs[key] = val * other

        new_inner_prod_coeffs = defaultdict(int)
        for key, val in self.inner_prod_coeffs.items():
            new_inner_prod_coeffs[key] = val * other

        new_offset = self.offset * other

        return ScalarByBasisRepresentation(
            func_coeffs=new_func_coeffs,
            inner_prod_coeffs=new_inner_prod_coeffs,
            offset=new_offset,
        )

    def __rmul__(
        self, other: utils.NUMERICAL_TYPE | Parameter
    ) -> ScalarByBasisRepresentation:
        return self.__mul__(other)

    def __neg__(self) -> ScalarByBasisRepresentation:
        return self.__rmul__(-1)

    def __truediv__(
        self, other: utils.NUMERICAL_TYPE | Parameter
    ) -> ScalarByBasisRepresentation:
        if not utils.is_numerical_or_parameter(other):
            return NotImplemented

        new_func_coeffs = defaultdict(int)
        for key, val in self.func_coeffs.items():
            new_func_coeffs[key] = val / other

        new_inner_prod_coeffs = defaultdict(int)
        for key, val in self.inner_prod_coeffs.items():
            new_inner_prod_coeffs[key] = val / other

        new_offset = self.offset / other

        return ScalarByBasisRepresentation(
            func_coeffs=new_func_coeffs,
            inner_prod_coeffs=new_inner_prod_coeffs,
            offset=new_offset,
        )


@attrs.frozen
class ZeroScalar:
    """A special class to represent 0 in scalar."""

    pass


@attrs.frozen
class EvaluatedScalar:
    """
    The concrete representation of the abstract :class:`Scalar`.

    Each abstract basis :class:`Scalar` object has a unique concrete
    representation as a unit vector. The concrete representations of
    linear combinations of abstract basis :class:`Scalar` objects
    are linear combinations of the unit vectors. This information is
    stored in the `func_coords` attribute.

    Abstract :class:`Scalar` objects can be formed through taking the
    inner product of two abstract :class:`Vector` objects. The
    concrete representation of an abstract :class:`Scalar` object formed
    this way is the outer product of the concrete representations of the
    two abstract :class:`Vector` objects, i.e., a matrix. This information
    is stored in the `inner_prod_coords` attribute.

    Abstract :class:`Scalar` objects can be added or subtracted with
    numeric data types. This information is stored in the `offset`
    attribute.

    :class:`EvaluatedScalar` objects can be constructed as linear combinations
    of other :class:`EvaluatedScalar` objects. Let `a` and `b` be some numeric
    data type. Let `u` and `v` be :class:`EvaluatedScalar` objects. Then, we
    can form a new :class:`EvaluatedScalar` object: `a*u+b*v`.

    Attributes:
        func_coords (np.ndarray): The vector component of the concrete
            representation of the abstract :class:`Scalar`.
        inner_prod_coords (np.ndarray): The matrix component of the concrete
            representation of the abstract :class:`Scalar`. An alias is
            `matrix`.
        offset (float): The constant component of the concrete
            representation of the abstract :class:`Scalar`.
    """

    func_coords: np.ndarray
    inner_prod_coords: np.ndarray
    offset: float

    @property
    def matrix(self) -> np.ndarray:
        """A short alias for inner_prod_coords."""
        return self.inner_prod_coords

    @classmethod
    def zero(
        cls, num_basis_scalars: int, num_basis_vectors: int, sympy_mode: bool = False
    ):
        if sympy_mode:
            return EvaluatedScalar(
                func_coords=np.zeros(num_basis_scalars) * sp.S(0),
                inner_prod_coords=np.zeros((num_basis_vectors, num_basis_vectors))
                * sp.S(0),
                offset=sp.S(0),
            )
        return EvaluatedScalar(
            func_coords=np.zeros(num_basis_scalars),
            inner_prod_coords=np.zeros((num_basis_vectors, num_basis_vectors)),
            offset=0.0,
        )

    def __add__(self, other):
        if utils.is_numerical(other) or utils.is_sympy_expr(other):
            return EvaluatedScalar(
                func_coords=self.func_coords,
                inner_prod_coords=self.inner_prod_coords,
                offset=self.offset + other,
            )
        if isinstance(other, EvaluatedScalar):
            return EvaluatedScalar(
                func_coords=self.func_coords + other.func_coords,
                inner_prod_coords=self.inner_prod_coords + other.inner_prod_coords,
                offset=self.offset + other.offset,
            )
        return NotImplemented

    def __radd__(self, other):
        if utils.is_numerical(other) or utils.is_sympy_expr(other):
            return EvaluatedScalar(
                func_coords=self.func_coords,
                inner_prod_coords=self.inner_prod_coords,
                offset=other + self.offset,
            )
        if isinstance(other, EvaluatedScalar):
            return EvaluatedScalar(
                func_coords=other.func_coords + self.func_coords,
                inner_prod_coords=other.inner_prod_coords + self.inner_prod_coords,
                offset=other.offset + self.offset,
            )
        return NotImplemented

    def __sub__(self, other):
        if utils.is_numerical(other) or utils.is_sympy_expr(other):
            return EvaluatedScalar(
                func_coords=self.func_coords,
                inner_prod_coords=self.inner_prod_coords,
                offset=self.offset - other,
            )
        elif isinstance(other, EvaluatedScalar):
            return EvaluatedScalar(
                func_coords=self.func_coords - other.func_coords,
                inner_prod_coords=self.inner_prod_coords - other.inner_prod_coords,
                offset=self.offset - other.offset,
            )
        return NotImplemented

    def __rsub__(self, other):
        if utils.is_numerical(other) or utils.is_sympy_expr(other):
            return EvaluatedScalar(
                func_coords=-self.func_coords,
                inner_prod_coords=-self.inner_prod_coords,
                offset=other - self.offset,
            )
        if isinstance(other, EvaluatedScalar):
            return EvaluatedScalar(
                func_coords=other.func_coords - self.func_coords,
                inner_prod_coords=other.inner_prod_coords - self.inner_prod_coords,
                offset=other.offset - self.offset,
            )
        return NotImplemented

    def __mul__(self, other):
        if utils.is_numerical(other) or utils.is_sympy_expr(other):
            return EvaluatedScalar(
                func_coords=self.func_coords * other,
                inner_prod_coords=self.inner_prod_coords * other,
                offset=self.offset * other,
            )
        return NotImplemented

    def __rmul__(self, other):
        if utils.is_numerical(other) or utils.is_sympy_expr(other):
            return EvaluatedScalar(
                func_coords=other * self.func_coords,
                inner_prod_coords=other * self.inner_prod_coords,
                offset=other * self.offset,
            )
        return NotImplemented

    def __neg__(self):
        return self.__rmul__(other=-1)

    def __truediv__(self, other):
        if utils.is_numerical(other) or utils.is_sympy_expr(other):
            return EvaluatedScalar(
                func_coords=self.func_coords / other,
                inner_prod_coords=self.inner_prod_coords / other,
                offset=self.offset / other,
            )
        return NotImplemented


@attrs.frozen
class Scalar:
    """
    A :class:`Scalar` object represents linear combination of functions values,
    inner products of :class:`Point` objects, and constant scalar values.

    :class:`Scalar` objects can be constructed as linear combinations of
    other :class:`Scalar` objects. Let `a` and `b` be some numeric data type.
    Let `x` and `y` be :class:`Scalar` objects. Then, we can form a new
    :class:`Scalar` object: `a*x+b*y`.

    Attributes:
        is_basis (bool): True if this scalar is not formed through a linear
            combination of other scalars. False otherwise.
        tags (list[str]): A list that contains tags that can be used to
            identify the :class:`Vector` object. Tags should be unique.
        math_expr (:class:`MathExpr`): A :class:`MathExpr` object with a
            member variable that contains a mathematical expression
            represented as a string.

    Example:
        >>> import pepflow as pf
        >>> ctx = pf.PEPContext("cts").set_as_current()
        >>> s1 = pf.Scalar(is_basis=True, tags=["s1"])

    Note:
        Basis :class:`Scalar` objects should be defined using the constructor
        as shown in the example but composite :class:`Scalar` objects should
        be created using operations on :class:`Scalar` objects.
    """

    # If true, the scalar is the basis for the evaluations of F
    is_basis: bool

    # The representation of scalar used for evaluation.
    eval_expression: ScalarRepresentation | ZeroScalar | None = None

    # Human tagged value for the scalar
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
        pep_context.add_scalar(self)
        for tag in self.tags:
            pep_context.add_tag_to_vectors_or_scalars(tag, self)

        if self.tags:  # If tag is provided, make math_expr based on tag
            self.math_expr.expr_str = self.tag

    @staticmethod
    def zero() -> Scalar:
        """A static method that returns a :class:`Scalar` object that
        corresponds to zero.

        Returns:
            :class:`Scalar`: A zero :class:`Scalar` object.
        """
        return Scalar(
            is_basis=False,
            eval_expression=ZeroScalar(),
            math_expr=me.MathExpr(expr_str="0"),
        )

    @property
    def tag(self):
        """Returns the most recently added tag.

        Returns:
            str: The most recently added tag of this :class:`Scalar` object.
        """
        if len(self.tags) == 0:
            raise ValueError("This Scalar object doesn't have a tag.")
        return self.tags[-1]

    def add_tag(self, tag: str) -> "Scalar":
        """Add a new tag for this :class:`Scalar` object.

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

    def __add__(self, other):
        if not is_numerical_or_scalar(other):
            return NotImplemented
        if utils.is_numerical_or_parameter(other):
            expr_other = utils.numerical_str(other)
        else:
            expr_other = repr(other)
        return Scalar(
            is_basis=False,
            eval_expression=ScalarRepresentation(utils.Op.ADD, self, other),
            tags=[],
            math_expr=me.MathExpr(expr_str=f"{repr(self)}+{expr_other}"),
        )

    def __radd__(self, other):
        if not is_numerical_or_scalar(other):
            return NotImplemented
        if utils.is_numerical_or_parameter(other):
            expr_other = utils.numerical_str(other)
        else:
            expr_other = repr(other)
        return Scalar(
            is_basis=False,
            eval_expression=ScalarRepresentation(utils.Op.ADD, other, self),
            tags=[],
            math_expr=me.MathExpr(expr_str=f"{expr_other}+{repr(self)}"),
        )

    def __sub__(self, other):
        if not is_numerical_or_scalar(other):
            return NotImplemented
        if utils.is_numerical_or_parameter(other):
            expr_other = utils.numerical_str(other)
        else:
            expr_other = utils.parenthesize_tag(other)
        expr_self = repr(self)
        return Scalar(
            is_basis=False,
            eval_expression=ScalarRepresentation(utils.Op.SUB, self, other),
            tags=[],
            math_expr=me.MathExpr(expr_str=f"{expr_self}-{expr_other}"),
        )

    def __rsub__(self, other):
        if not is_numerical_or_scalar(other):
            return NotImplemented
        expr_self = utils.parenthesize_tag(self)
        if utils.is_numerical_or_parameter(other):
            expr_other = utils.numerical_str(other)
        else:
            expr_other = repr(other.math_expr)
        return Scalar(
            is_basis=False,
            eval_expression=ScalarRepresentation(utils.Op.SUB, other, self),
            tags=[],
            math_expr=me.MathExpr(expr_str=f"{expr_other}-{expr_self}"),
        )

    def __mul__(self, other):
        if not utils.is_numerical_or_parameter(other):
            return NotImplemented
        expr_self = utils.parenthesize_tag(self)
        expr_other = utils.numerical_str(other)
        return Scalar(
            is_basis=False,
            eval_expression=ScalarRepresentation(utils.Op.MUL, self, other),
            tags=[],
            math_expr=me.MathExpr(expr_str=f"{expr_self}*{expr_other}"),
        )

    def __rmul__(self, other):
        if not utils.is_numerical_or_parameter(other):
            return NotImplemented
        expr_self = utils.parenthesize_tag(self)
        expr_other = utils.numerical_str(other)
        return Scalar(
            is_basis=False,
            eval_expression=ScalarRepresentation(utils.Op.MUL, other, self),
            tags=[],
            math_expr=me.MathExpr(expr_str=f"{expr_other}*{expr_self}"),
        )

    def __neg__(self):
        expr_self = utils.parenthesize_tag(self)
        return Scalar(
            is_basis=False,
            eval_expression=ScalarRepresentation(utils.Op.MUL, -1, self),
            tags=[],
            math_expr=me.MathExpr(expr_str=f"-{expr_self}"),
        )

    def __truediv__(self, other):
        if not utils.is_numerical_or_parameter(other):
            return NotImplemented
        expr_self = utils.parenthesize_tag(self)
        expr_other = f"1/{utils.numerical_str(other)}"
        return Scalar(
            is_basis=False,
            eval_expression=ScalarRepresentation(utils.Op.DIV, self, other),
            tags=[],
            math_expr=me.MathExpr(expr_str=f"{expr_other}*{expr_self}"),
        )

    def __hash__(self):
        return hash(self.uid)

    def __eq__(self, other):
        if not isinstance(other, Scalar):
            return NotImplemented
        return self.uid == other.uid

    def simplify(self, tag: str | None = None) -> Scalar:
        """
        Simplify the mathematical expression of this :class:`Scalar` object.

        Returns:
            :class:`Scalar`: A new :class:`Scalar` object with the simplified
            mathematical expression.
        """
        from pepflow.vector import Vector

        def _simplify(
            scalar_or_float: Scalar | utils.NUMERICAL_TYPE | Parameter | Vector,
        ) -> (
            ScalarByBasisRepresentation
            | utils.NUMERICAL_TYPE
            | Parameter
            | VectorByBasisRepresentation
        ):
            if isinstance(scalar_or_float, (Scalar, Vector)):
                # We know after simplification, the eval_expression is always
                # ScalarByBasisRepresentation or VectorByBasisRepresentation.
                return scalar_or_float.simplify().eval_expression  # type: ignore
            else:
                return scalar_or_float

        if self.is_basis:
            # ScalarByBasisRepresentation and the original basis vector are representating the
            # the same basis vector. However, we do not wanna introduce another basis vector in the context.
            # So we have to keep this is_basis = False but the eval_expression should be the same.
            is_basis = False
            eval_expression = ScalarByBasisRepresentation(
                func_coeffs=defaultdict(int, {self: 1}),
                inner_prod_coeffs=defaultdict(int, {}),
                offset=0,
            )
        else:
            is_basis = False
            if isinstance(self.eval_expression, ZeroScalar):
                eval_expression = ScalarByBasisRepresentation(
                    func_coeffs=defaultdict(int, {}),
                    inner_prod_coeffs=defaultdict(int, {}),
                    offset=0,
                )
            elif isinstance(self.eval_expression, ScalarByBasisRepresentation):
                eval_expression = self.eval_expression
            else:
                assert isinstance(self.eval_expression, ScalarRepresentation)
                left_eval_exression = _simplify(self.eval_expression.left_scalar)
                right_eval_exression = _simplify(self.eval_expression.right_scalar)
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
                        "Only add,sub,mul,div are supported for Vector simplification."
                    )

        return Scalar(
            is_basis=is_basis,
            eval_expression=eval_expression,
            tags=[tag] if tag is not None else [],
            math_expr=me.MathExpr(
                expr_str=str(eval_expression)
            ),  # TODO: Fix this to use simplified_expr
        )

    def le(self, other: Scalar | float | int, name: str) -> ctr.ScalarConstraint:
        """
        Generate a :class:`ScalarConstraint` object that represents the inequality
        `self` <= `other`.

        Args:
            other (:class:`Scalar` | float | int): The other side of the
                relation.
            name (str): The name of the generated :class:`ScalarConstraint` object.

        Returns:
            :class:`ScalarConstraint`: An object that represents the inequality
            `self` <= `other`.
        """
        return ctr.ScalarConstraint(self, other, cmp=utils.Comparator.LE, name=name)

    def lt(self, other: Scalar | float | int, name: str) -> ctr.ScalarConstraint:
        """
        Generate a :class:`ScalarConstraint` object that represents the inequality
        `self` < `other`.

        Args:
            other (:class:`Scalar` | float | int): The other side of the
                relation.
            name (str): The name of the generated :class:`ScalarConstraint` object.

        Returns:
            :class:`ScalarConstraint`: An object that represents the inequality
            `self` < `other`.
        """
        return ctr.ScalarConstraint(self, other, cmp=utils.Comparator.LE, name=name)

    def ge(self, other: Scalar | float | int, name: str) -> ctr.ScalarConstraint:
        """
        Generate a :class:`ScalarConstraint` object that represents the inequality
        `self` >= `other`.

        Args:
            other (:class:`Scalar` | float | int): The other side of the
                relation.
            name (str): The name of the generated :class:`ScalarConstraint` object.

        Returns:
            :class:`ScalarConstraint`: An object that represents the inequality
            `self` >= `other`.
        """
        return ctr.ScalarConstraint(self, other, cmp=utils.Comparator.GE, name=name)

    def gt(self, other: Scalar | float | int, name: str) -> ctr.ScalarConstraint:
        """
        Generate a :class:`ScalarConstraint` object that represents the inequality
        `self` > `other`.

        Args:
            other (:class:`Scalar` | float | int): The other side of the
                relation.
            name (str): The name of the generated :class:`ScalarConstraint` object.

        Returns:
            :class:`ScalarConstraint`: An object that represents the inequality
            `self` > `other`.
        """
        return ctr.ScalarConstraint(self, other, cmp=utils.Comparator.GE, name=name)

    def eq(self, other: Scalar | float | int, name: str) -> ctr.ScalarConstraint:
        """
        Generate a :class:`ScalarConstraint` object that represents the inequality
        `self` = `other`.

        Args:
            other (:class:`Scalar` | float | int): The other side of the
                relation.
            name (str): The name of the generated :class:`ScalarConstraint` object.

        Returns:
            :class:`ScalarConstraint`: An object that represents the inequality
            `self` = `other`.
        """
        return ctr.ScalarConstraint(self, other, cmp=utils.Comparator.EQ, name=name)

    def eval(
        self,
        ctx: pc.PEPContext | None = None,
        *,
        resolve_parameters: dict[str, utils.NUMERICAL_TYPE] | None = None,
        sympy_mode: bool = False,
    ) -> EvaluatedScalar:
        """
        Return the concrete representation of this :class:`Scalar`.

        Concrete representations of :class:`Scalar` objects are
        :class:`EvaluatedScalar` objects.

        Args:
            ctx (:class:`PEPContext` | None): The :class:`PEPContext` object
                we consider. `None` if we consider the current global
                :class:`PEPContext` object.
            resolve_parameters (dict[str, :class:`NUMERICAL_TYPE`] | `None`): A
                dictionary that maps the name of parameters to the numerical values.
            sympy_mode (bool): If true, then the input should be defined completely
                in terms of SymPy objects and should not mix Python numeric objects.
                Will raise an error if sympy_mode is `True` and the input contains a
                Python numeric object. By default `False`.

        Returns:
            :class:`EvaluatedScalar`: The concrete representation of
            this :class:`Scalar`.
        """
        from pepflow.expression_manager import ExpressionManager

        # Note this can be inefficient.
        if ctx is None:
            ctx = pc.get_current_context()
        if ctx is None:
            raise RuntimeError("Did you forget to create a context?")
        em = ExpressionManager(ctx, resolve_parameters=resolve_parameters)
        return em.eval_scalar(self, sympy_mode=sympy_mode)

    def repr_by_basis(
        self,
        ctx: pc.PEPContext | None = None,
        *,
        greedy_square: bool = False,
        resolve_parameters: dict[str, utils.NUMERICAL_TYPE] | None = None,
        sympy_mode: bool = False,
    ) -> str:
        """Express this :class:`Scalar` object in terms of the basis :class:`Vector`
        and :class:`Scalar` objects of the given :class:`PEPContext`.

        A :class:`Scalar` can be formed by linear combinations of basis
        :class:`Scalar` objects. A :class:`Scalar` can also be formed through
        the inner product of two basis :class:`Vector` objects. This function
        returns the representation of this :class:`Scalar` object in terms of
        the basis :class:`Vector` and :class:`Scalar` objects as a `str`.

        Args:
            ctx (:class:`PEPContext`): The :class:`PEPContext` object
                whose basis :class:`Vector` and :class:`Scalar` objects we
                consider. `None` if we consider the current global
                :class:`PEPContext` object.
            greedy_square (bool): If `greedy_square` is true, the function will
                try to return :math:`\\|a-b\\|^2` whenever possible. If not,
                the function will return
                :math:`\\|a\\|^2 - 2 * \\langle a, b \\rangle + \\|b\\|^2` instead.
                `True` by default.
            resolve_parameters (dict[str, :class:`NUMERICAL_TYPE`] | `None`): A
                dictionary that maps the name of parameters to the numerical values.
            sympy_mode (bool): If true, then the input should be defined completely
                in terms of SymPy objects and should not mix Python numeric objects.
                Will raise an error if sympy_mode is `True` and the input contains a
                Python numeric object. By default `False`.

        Returns:
            str: The representation of this :class:`Scalar` object in terms of
            the basis :class:`Vector` and :class:`Scalar` objects of the given
            :class:`PEPContext`.

        Example:
            >>> import pepflow as pf
            >>> import sympy as sp
            >>> ctx = pf.PEPContext("ctx").set_as_current()
            >>> xi = pf.Vector(is_basis=True, tags=["x_i"])
            >>> xj = pf.Vector(is_basis=True, tags=["x_j"])
            >>> em = pf.ExpressionManager(ctx)
            >>> term = 2 / sp.S(3) * (xi + xj) ** 2 + 1 / sp.S(3) * (xi - xj) ** 2
            >>> term_str = term.repr_by_basis(ctx, sympy_mode=True)
            >>> pf.pprint_str(term_str)
        """
        from pepflow.expression_manager import ExpressionManager

        # Note this can be inefficient.
        if ctx is None:
            ctx = pc.get_current_context()
        if ctx is None:
            raise RuntimeError("Did you forget to create a context?")
        em = ExpressionManager(ctx, resolve_parameters=resolve_parameters)
        return em.repr_scalar_by_basis(
            self, greedy_square=greedy_square, sympy_mode=sympy_mode
        )
