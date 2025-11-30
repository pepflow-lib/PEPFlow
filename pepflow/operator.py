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

import itertools
import numbers
import uuid
from functools import cached_property
from typing import TYPE_CHECKING

import attrs
import numpy as np

from pepflow import constraint as ct
from pepflow import math_expression as me
from pepflow import pep_context as pc
from pepflow import registry as reg
from pepflow import scalar as sc
from pepflow import utils
from pepflow import vector as vt

if TYPE_CHECKING:
    from pepflow.parameter import Parameter


@attrs.frozen
class Duplet:
    """
    A data class that represents, for some given operator :math:`A`,
    the tuple :math:`\\{x, Ax\\}`.

    Attributes:
        point (:class:`Vector`): A vector :math:`x`.
        output (:class:`Vector`): A vector that represents :math:`Ax`.
        name (str): The unique name of the :class:`Duplet` object.
    """

    point: vt.Vector
    output: vt.Vector
    oper: Operator
    name: str | None
    uid: uuid.UUID = attrs.field(factory=uuid.uuid4, init=False)

    def expand(self) -> tuple[vt.Vector, vt.Vector]:
        return self.point, self.output


@attrs.frozen
class AddedOper:
    """Represents left_oper + right_oper."""

    left_oper: Operator
    right_oper: Operator


@attrs.frozen
class ScaledOper:
    """Represents scalar * base_oper."""

    scale: float
    base_oper: Operator


@attrs.frozen(kw_only=True)
class Operator:
    """A :class:`Operator` object represents an operator.

    :class:`Operator` objects can be constructed as linear combinations
    of other :class:`Operator` objects. Let `a` and `b` be some numeric
    data type. Let `A` and `B` be :class:`Operator` objects. Then, we
    can form a new :class:`Operator` object: `a*A+b*B`.

    A :class:`Operator` object should never be explicitly constructed. Only
    children of :class:`Operator` such as :class:`LinearOperator` or
    :class:`MonotoneOperator` should be constructed. See their respective
    documentation to see how.

    Every child class needs to implement the
    :py:func:`get_interpolation_constraints_by_group` method. This returns a
    :class:`ConstraintData` object which will store the :class:`Operator`'s
    interpolation conditions. See the :class:`ConstraintData` documentation for
    details and the :class:`LinearOperator` or :class:`MonotoneOperator` for
    examples.

    Let `A` be a :class:`Operator` object. The naming convention for a
    :class:`ScalarConstraint` object representing an interpolation condition of `A`
    between two :class:`Vector` objects `x_0` and `x_1` is
    `{A.tag}:{x_0.tag},{x_1.tag}`. The naming convention for a :class:`ScalarConstraint`
    object representing an interpolation condition of `A` using only one
    :class:`Vector` object `x_0` is `{A.tag}:{x_0.tag},{x_0.tag}`.

    If a :class:`Operator` has multiple :class:`ScalarConstraint` groups,
    then the naming convention of the individual :class:`ScalarConstraint` objects
    must differ. For example, Lipschitz Strongly Monotone Operators has a group of
    :class:`ScalarConstraint` objects representing the interpolation conditions
    related to Lipschitz Continuity and a group of :class:`ScalarConstraint` objects
    representing the interpolation conditions related to Strong Monotonicity.
    Let `A` be a :class:`Operator` object. A possible naming convention for a
    :class:`ScalarConstraint` object representing an interpolation condition related
    to the Lipschitz Continuity of `A` between two :class:`Vector` objects `x_0`
    and `x_1` is `{A.tag}_convex:{x_0.tag},{x_1.tag}`. A possible naming convention for
    a :class:`ScalarConstraint` object representing an interpolation condition related
    to the Strong Monotonicity of `A` between two :class:`Vector` objects `x_0`
    and `x_1` is `{A.tag}_SM:{x_0.tag},{x_1.tag}`.

    Attributes:
        is_basis (bool): `True` if this operator is not formed through a linear
            combination of other operators. `False` otherwise.
        tags (list[str]): A list that contains tags that can be used to
            identify the :class:`Operator` object. Tags should be unique.
        math_expr (:class:MathExpr): An object of :class:MathExpr that
            contains a mathematical expression represented as a `str`.
    """

    is_basis: bool

    composition: AddedOper | ScaledOper | None = None

    # Human tagged value for the operator
    tags: list[str] = attrs.field(factory=list)

    # Mathematical expression
    math_expr: me.MathExpr = attrs.field(factory=me.MathExpr)

    # Generate an automatic id
    uid: uuid.UUID = attrs.field(factory=uuid.uuid4, init=False)

    def __attrs_post_init__(self):
        if self.is_basis:
            assert self.composition is None
        else:
            assert self.composition is not None

        for tag in self.tags:
            if tag in reg.REGISTERED_FUNC_AND_OPER_DICT:
                print(f"Warning: operator with tag {tag} has been created before.")

            reg.REGISTERED_FUNC_AND_OPER_DICT[tag] = self

        if self.tags:  # If tag is provided, make math_expr based on tag
            self.math_expr.expr_str = self.tag

    @property
    def tag(self):
        """Returns the most recently added tag.

        Returns:
            str: The most recently added tag of this :class:`Operator` object.
        """
        if len(self.tags) == 0:
            raise ValueError("Operator should have a name.")
        return self.tags[-1]

    def add_tag(self, tag: str) -> Operator:
        """Add a new tag for this :class:`Operator` object.

        Args:
            tag (str): The new tag to be added to the `tags` list.
        """
        if tag in reg.REGISTERED_FUNC_AND_OPER_DICT:
            print(f"Warning: operator with tag {tag} has been created before.")

        reg.REGISTERED_FUNC_AND_OPER_DICT[tag] = self
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

    def get_interpolation_constraints_by_group(
        self, pep_context: pc.PEPContext | None = None
    ) -> pc.ConstraintData:
        """When implemented, structure the types of constraints as a list of related
        scalar constraints or individual PSDConstraints."""
        raise NotImplementedError(
            "This method should be implemented in the children class."
        )

    def get_interpolation_constraints(
        self, pep_context: pc.PEPContext | None = None
    ) -> list[ct.ScalarConstraint | ct.PSDConstraint]:
        interpolation_constraints = []
        cd = self.get_interpolation_constraints_by_group(pep_context)
        for scal_constraint in cd.sc_dict.values():
            interpolation_constraints.extend(scal_constraint)
        for psd_constraint in cd.psd_dict.values():
            interpolation_constraints.append(psd_constraint)
        return interpolation_constraints

    def add_duplet_to_oper(self, duplet: Duplet) -> None:
        pep_context = pc.get_current_context()
        if pep_context is None:
            raise RuntimeError("Did you forget to create a context?")
        pep_context.add_duplet(duplet)

    def add_point_with_output_restriction(
        self, point: vt.Vector, desired_output: vt.Vector
    ) -> Duplet:
        if self.is_basis:
            duplet = Duplet(
                point,
                desired_output,
                self,
                name=f"{point.__repr__()}_{desired_output.__repr__()}",
            )
            self.add_duplet_to_oper(duplet)
        else:
            if isinstance(self.composition, AddedOper):
                left_duplet = self.composition.left_oper.generate_duplet(point)
                next_desired_output = desired_output - left_duplet.output
                next_desired_output.math_expr.expr_str = (
                    f"{self.composition.right_oper.__repr__()}({point.__repr__()})"
                )
                # right_duplet
                _ = self.composition.right_oper.add_point_with_output_restriction(
                    point, next_desired_output
                )
                duplet = Duplet(
                    point,
                    desired_output,
                    self,
                    name=f"{point.__repr__()}_{desired_output.__repr__()}",
                )
            elif isinstance(self.composition, ScaledOper):
                next_desired_output = desired_output / self.composition.scale
                next_desired_output.math_expr.expr_str = (
                    f"{self.composition.base_oper.__repr__()}({point.__repr__()})"
                )
                # base_duplet
                _ = self.composition.base_oper.add_point_with_output_restriction(
                    point, next_desired_output
                )
                duplet = Duplet(
                    point,
                    desired_output,
                    self,
                    name=f"{point.__repr__()}_{desired_output.__repr__()}",
                )
            else:
                raise ValueError(
                    f"Unknown composition of operators: {self.composition}"
                )
        return duplet

    def set_zero_point(self, name: str) -> vt.Vector:
        """
        Return a zero point for this :class:`Operator` object.

        A :class:`Operator` object can only have one zero point.

        Args:
            name (str): The tag for the :class:`Vector` object which
                 will serve as the zero point.

        Returns:
            :class:`Vector`: The zero point for this :class:`Operator`
            object.
        """
        # Assert we can only add one zero point?
        pep_context = pc.get_current_context()
        if pep_context is None:
            raise RuntimeError("Did you forget to create a context?")
        if len(pep_context.oper_to_zero_duplets[self]) > 0:
            raise ValueError(
                "You are trying to add a zero point to an operator that already has a zero point."
            )
        point = vt.Vector(is_basis=True, tags=[name])
        desired_output = vt.Vector.zero()  # Zero point
        desired_output.math_expr.expr_str = f"{self.__repr__()}({name})"
        duplet = self.add_point_with_output_restriction(point, desired_output)
        pep_context.add_zero_duplet(duplet)
        return point

    def set_fixed_point(self, name: str) -> vt.Vector:
        """
        Return a fixed point for this :class:`Operator` object.

        A :class:`Operator` object can only have one fixed point.

        Args:
            name (str): The tag for the :class:`Vector` object which
                 will serve as the fixed point.

        Returns:
            :class:`Vector`: The fixed point for this :class:`Operator`
            object.
        """
        # Assert we can only add one fixed point?
        pep_context = pc.get_current_context()
        if pep_context is None:
            raise RuntimeError("Did you forget to create a context?")
        if len(pep_context.oper_to_fixed_duplets[self]) > 0:
            raise ValueError(
                "You are trying to add a fixed point to an operator that already has a fixed point."
            )
        point = vt.Vector(is_basis=True, tags=[name])
        duplet = self.add_point_with_output_restriction(point, point)
        pep_context.add_fixed_duplet(duplet)
        return point

    def generate_duplet(self, point: vt.Vector) -> Duplet:
        pep_context = pc.get_current_context()
        if pep_context is None:
            raise RuntimeError("Did you forget to create a context?")

        if not isinstance(point, vt.Vector):
            raise ValueError("The Operator can only take point as input.")

        if self.is_basis:
            for duplet in pep_context.oper_to_duplets[self]:
                if (
                    duplet.point.uid == point.uid
                ):  # TODO: Should come up better way to handle this
                    return duplet

            output = vt.Vector(
                is_basis=True,
                math_expr=me.MathExpr(
                    expr_str=f"{self.__repr__()}({point.__repr__()})"
                ),
            )

            new_duplet = Duplet(
                point,
                output,
                self,
                name=f"{point.__repr__()}_{output.__repr__()}",
            )
            self.add_duplet_to_oper(new_duplet)
            return new_duplet
        else:
            if isinstance(self.composition, AddedOper):
                left_duplet = self.composition.left_oper.generate_duplet(point)
                right_duplet = self.composition.right_oper.generate_duplet(point)
                output = left_duplet.output + right_duplet.output
            elif isinstance(self.composition, ScaledOper):
                base_duplet = self.composition.base_oper.generate_duplet(point)
                output = self.composition.scale * base_duplet.output
            else:
                raise ValueError(
                    f"Unknown composition of operators: {self.composition}"
                )
            return Duplet(
                point,
                output,
                self,
                name=f"{point.__repr__()}_{output.__repr__()}",
            )

    def apply(self, point: vt.Vector) -> vt.Vector:
        """
        Returns a :class:`Vector` object that is the output of the
        :class:`Operator` applied on the given :class:`Vector`.

        Args:
            point (:class:`Vector`): Any :class:`Vector`.

        Returns:
            :class:`Vector`: The output that results from applying the
            :class:`Operator` on the given :class:`Vector`.
        """
        duplet = self.generate_duplet(point)
        return duplet.output

    def __call__(self, point: vt.Vector) -> vt.Vector:
        return self.apply(point)

    def __add__(self, other):
        if not isinstance(other, Operator):
            return NotImplemented
        return Operator(
            is_basis=False,
            composition=AddedOper(self, other),
            tags=[],
            math_expr=me.MathExpr(expr_str=f"{self.__repr__()}+{other.__repr__()}"),
        )

    def __sub__(self, other):
        if not isinstance(other, Operator):
            return NotImplemented
        expr_other = other.__repr__()
        if isinstance(other.composition, AddedOper):
            expr_other = f"({other.__repr__()})"
        return Operator(
            is_basis=False,
            composition=AddedOper(self, -other),
            tags=[],
            math_expr=me.MathExpr(expr_str=f"{self.__repr__()}-{expr_other}"),
        )

    def __mul__(self, other):
        if not utils.is_numerical(other):
            return NotImplemented
        expr_self = self.__repr__()
        if isinstance(self.composition, AddedOper):
            expr_self = f"({self.__repr__()})"
        return Operator(
            is_basis=False,
            composition=ScaledOper(scale=other, base_oper=self),
            tags=[],
            math_expr=me.MathExpr(expr_str=f"{other:.4g}*{expr_self}"),
        )

    def __rmul__(self, other):
        if not utils.is_numerical(other):
            return NotImplemented
        expr_self = self.__repr__()
        if isinstance(self.composition, AddedOper):
            expr_self = f"({self.__repr__()})"
        return Operator(
            is_basis=False,
            composition=ScaledOper(scale=other, base_oper=self),
            tags=[],
            math_expr=me.MathExpr(expr_str=f"{other:.4g}*{expr_self}"),
        )

    def __neg__(self):
        expr_self = self.__repr__()
        if isinstance(self.composition, AddedOper):
            expr_self = f"({self.__repr__()})"
        return Operator(
            is_basis=False,
            composition=ScaledOper(scale=-1, base_oper=self),
            tags=[],
            math_expr=me.MathExpr(expr_str=f"-{expr_self}"),
        )

    def __truediv__(self, other):
        if not utils.is_numerical(other):
            return NotImplemented
        expr_self = self.__repr__()
        if isinstance(self.composition, AddedOper):
            expr_self = f"({self.__repr__()})"
        return Operator(
            is_basis=False,
            composition=ScaledOper(scale=1 / other, base_oper=self),
            tags=[],
            math_expr=me.MathExpr(expr_str=f"1/{other:.4g}*{expr_self}"),
        )

    def __hash__(self):
        return hash(self.uid)

    def __eq__(self, other):
        if not isinstance(other, Operator):
            return NotImplemented
        return self.uid == other.uid


@attrs.mutable(kw_only=True)
class LinearOperatorTranspose(Operator):
    """
    The :class:`LinearOperatorTranspose` class represents the transpose of a
    bounded, linear operator.

    The :class:`LinearOperatorTranpose` class is a child of :class:`Operator`.

    The :class:`LinearOperatorTranpose` should never be instantiated directly and
    :class:`LinearOperatorTranpose` objects are used as member variables of
    :class:`LinearOperator` for the purpose of implementing the interpolation
    conditions of :class:`LinearOperator`.
    """

    def __hash__(self):
        return super().__hash__()


@attrs.mutable(kw_only=True)
class LinearOperator(Operator):
    """
    The :class:`LinearOperator` class represents a bounded, linear operator.

    The :class:`LinearOperator` class is a child of :class:`Operator`.

    A bounded linear operator has an operator norm :math:`M`.
    We can instantiate a :class:`LinearOperator` object as follows:

    Example:
        >>> import pepflow as pf
        >>> A = pf.LinearOperator(is_basis=True, tags=["A"], M=1)
    """

    M: utils.NUMERICAL_TYPE | Parameter

    def __attrs_post_init__(self):
        super().__attrs_post_init__()
        if isinstance(self.M, utils.NUMERICAL_TYPE):
            assert self.M > 0  # ty: ignore

    def __hash__(self):
        return super().__hash__()

    def add_tag(self, tag: str) -> LinearOperator:
        """Add a new tag for this :class:`Operator` object.

        Args:
            tag (str): The new tag to be added to the `tags` list.
        """
        self.tags.append(tag)
        self.T.tags.append(f"{tag}.T")
        return self

    def equality_interpolability_constraints(
        self, duplet_i, duplet_j
    ) -> ct.ScalarConstraint:
        return (duplet_i.point * duplet_j.output).eq(
            duplet_i.output * duplet_j.point,
            name=f"{self.tag}:{duplet_i.point.__repr__()}/{duplet_j.output.__repr__()},{duplet_i.output.__repr__()}/{duplet_j.point.tag}",
        )

    def matrix_SDP_interpolability_constraints_element(
        self, duplet_i, duplet_j
    ) -> sc.Scalar:
        return (
            self.M * self.M
        ) * duplet_i.point * duplet_j.point - duplet_i.output * duplet_j.output

    def get_interpolation_constraints_by_group(
        self, pep_context: pc.PEPContext | None = None
    ) -> pc.ConstraintData:
        cd = pc.ConstraintData(func_or_oper=self)
        if pep_context is None:
            pep_context = pc.get_current_context()
        if pep_context is None:
            raise RuntimeError("Did you forget to create a context?")
        scal_constraint = []
        for i in pep_context.oper_to_duplets[self]:
            for j in pep_context.oper_to_duplets[self.T]:
                scal_constraint.append(self.equality_interpolability_constraints(i, j))
        cd.add_sc_constraint("Linear Operator Equality", scal_constraint)

        if len(pep_context.oper_to_duplets[self]) > 0:
            X = [d.point for d in pep_context.oper_to_duplets[self]]
            Y = [d.output for d in pep_context.oper_to_duplets[self]]
            matrix_SDP_constraint_1 = (self.M * self.M) * np.outer(X, X) - np.outer(  # ty: ignore
                Y, Y
            )

            cd.add_psd_constraint(
                "Linear Operator PSD",
                ct.PSDConstraint(
                    matrix_SDP_constraint_1,
                    0,
                    utils.Comparator.SEQ,
                    f"{self.tag} SDP Constraint",
                ),
            )

        if len(pep_context.oper_to_duplets[self.T]) > 0:
            U = [d.point for d in pep_context.oper_to_duplets[self.T]]
            V = [d.output for d in pep_context.oper_to_duplets[self.T]]
            matrix_SDP_constraint_2 = (self.M * self.M) * np.outer(U, U) - np.outer(  # ty: ignore
                V, V
            )

            cd.add_psd_constraint(
                "Linear Operator PSD (Transpose)",
                ct.PSDConstraint(
                    matrix_SDP_constraint_2,
                    0,
                    utils.Comparator.SEQ,
                    f"{self.tag} SDP Constraint (Transpose)",
                ),
            )
        return cd

    @cached_property
    def T(self):
        if len(self.tags) == 0:
            raise ValueError("Linear Operator should have a name.")
        return LinearOperatorTranspose(is_basis=True, tags=[f"{self.tag}.T"])

    # TODO: How should we make interpolate_ineq()? There are two PSD constraints and a set of equality constraints.


@attrs.mutable(kw_only=True)
class MonotoneOperator(Operator):
    """
    The :class:`MonotoneOperator` class represents a monotone operator.

    The :class:`MonotoneOperator` class is a child of :class:`Operator`.

    We can instantiate a :class:`MonotoneOperator` object as follows:

    Example:
        >>> import pepflow as pf
        >>> ctx = pf.PEPContext("example").set_as_current()
        >>> pep_builder = pf.PEPBuilder()
        >>> A = pep_builder.declare_oper(pf.MonotoneOperator)
    """

    def __attrs_post_init__(self):
        super().__attrs_post_init__()

    def __repr__(self):
        return super().__repr__()

    def __hash__(self):
        return super().__hash__()

    def add_tag(self, tag: str) -> MonotoneOperator:
        """Add a new tag for this :class:`MonotoneOperator` object.

        Args:
            tag (str): The new tag to be added to the `tags` list.
        """
        self.tags.append(tag)
        return self

    def inequality_interpolability_constraints(
        self, duplet_i, duplet_j
    ) -> ct.ScalarConstraint:
        return (
            (duplet_i.point - duplet_j.point) * (duplet_i.output - duplet_j.output)
        ).ge(
            0,
            name=f"{self.tag}:{duplet_i.point.tag},{duplet_j.point.tag}",
        )

    def get_interpolation_constraints_by_group(
        self, pep_context: pc.PEPContext | None = None
    ) -> pc.ConstraintData:
        cd = pc.ConstraintData(func_or_oper=self)
        if pep_context is None:
            pep_context = pc.get_current_context()
        if pep_context is None:
            raise RuntimeError("Did you forget to create a context?")
        scal_constraint = []
        # We order the points in this case because the interpolation
        # constraints are symmetric, i.e., <A x_1 - A x_0, x_1 - x_0> >= 0
        # is the same as <A x_0 - A x_1, x_0 - x_1> >= 0.
        ordered_duplets = [
            pep_context.get_duplet_by_point_tag(points.tag, self)
            for points in pep_context.tracked_point(self)
        ]
        for i, j in itertools.combinations(ordered_duplets, 2):
            scal_constraint.append(self.inequality_interpolability_constraints(i, j))
        cd.add_sc_constraint("Monotone Operator Inequality", scal_constraint)

        return cd

    def interp_ineq(
        self,
        p1: vt.Vector | str,
        p2: vt.Vector | str,
        pep_context: pc.PEPContext | None = None,
    ) -> sc.Scalar:
        """Generate the interpolation inequality :class:`Scalar` object between two
        :class:`Vector` objects through the objects themselves or their tags.

        The interpolation inequality between two points :math:`p_1, p_2` for a
        monotone operator :math:`A` is

        .. math:: \\langle \\nabla A(p_1) - A(p_2), p_1 - p_2 \\rangle >= 0.

        Args:
            p1 (:class:`Vector` | str): A :class:`Vector` :math:`p_1` point or its tag.
            p2 (:class:`Vector` | str): A :class:`Vector` :math:`p_2` point or its tag.
        """
        if pep_context is None:
            pep_context = pc.get_current_context()
        if pep_context is None:
            raise RuntimeError("Did you forget to specify a context?")

        x1, u1 = pep_context.get_duplet_by_point_tag(p1, op=self).expand()
        x2, u2 = pep_context.get_duplet_by_point_tag(p2, op=self).expand()
        return (x1 - x2) * (u1 - u2)

    def resolvent_step(self, x_0: vt.Vector, stepsize: numbers.Number) -> vt.Vector:
        """Perform a resolvent step.

        Define the resolvent operator as

        .. math:: \\J_{\\gamma A} := (A+\\gamma A)^{-1}.

        This function performs a resolvent step with respect to some
        :class:`MonotoneOperator` :math:`A` on the :class:`Vector` :math:`x_0`
        with stepsize :math:`\\gamma`:

        Args:
            x_0 (:class:`Vector`): The initial point.
            stepsize (int | float | Parameter): The stepsize.
        """
        x_tag = f"J_{{{stepsize}*{self.tag}}}({x_0.tag})"
        Ax = vt.Vector(is_basis=True)
        Ax.add_tag(f"{self.tag}({x_tag})")
        x = x_0 - stepsize * Ax
        x.add_tag(f"{x_tag}")
        new_duplet = Duplet(
            x,
            Ax,
            self,
            name=f"{x.tag}_{Ax.tag}",
        )
        self.add_duplet_to_oper(new_duplet)
        return x
