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

import numbers
import uuid
import warnings
from typing import TYPE_CHECKING

import attrs
import sympy as sp

from pepflow import constraint as ct
from pepflow import math_expression as me
from pepflow import pep_context as pc
from pepflow import registry as reg
from pepflow import scalar as sc
from pepflow import utils
from pepflow import vector as vt

if TYPE_CHECKING:
    from pepflow.math_expression import MathExpr
    from pepflow.parameter import Parameter
    from pepflow.scalar import Scalar
    from pepflow.utils import NUMERICAL_TYPE
    from pepflow.vector import Vector


@attrs.frozen
class Triplet:
    """
    A data class that represents, for some given function :math:`f`,
    the tuple :math:`\\{x, f(x), \\nabla f(x)\\}`.

    Subgradients :math:`\\widetilde{\\nabla} f(x)` are represented by gradients as they
    are effectively treated the same in the context of PEP.

    Attributes:
        point (:class:`Vector`): A vector :math:`x`.
        func_val (:class:`Scalar`): The function value :math:`f(x)`.
        grad (:class:`Vector`): The gradient :math:`\\nabla f(x)` or
            a subgradient :math:`\\widetilde{\\nabla} f(x)`.
        name (str): The unique name of the :class:`Triplet` object.
    """

    point: Vector
    func_val: Scalar
    grad: Vector
    func: Function
    name: str | None
    uid: uuid.UUID = attrs.field(factory=uuid.uuid4, init=False)

    def expand(self) -> tuple[vt.Vector, sc.Scalar, vt.Vector]:
        """
        Return the `point`, `func_value`, and `grad` member variables of a
        :class:`Triplet` as a tuple.
        """
        return self.point, self.func_val, self.grad


@attrs.frozen
class AddedFunc:
    """Represents left_func + right_func."""

    left_func: Function
    right_func: Function


@attrs.frozen
class ScaledFunc:
    """Represents scalar * base_func."""

    scale: float
    base_func: Function


@attrs.frozen(kw_only=True)
class Function:
    """A :class:`Function` object represents a function.

    :class:`Function` objects can be constructed as linear combinations
    of other :class:`Function` objects. Let `a` and `b` be some numeric
    data type. Let `f` and `g` be :class:`Function` objects. Then, we
    can form a new :class:`Function` object: `a*f+b*g`.

    A :class:`Function` object should never be explicitly constructed. Only
    children of :class:`Function` such as :class:`ConvexFunction` or
    :class:`SmoothConvexFunction` should be constructed. See their respective
    documentation to see how.

    Every child class needs to implement the
    :py:func:`get_interpolation_constraints_by_group` method. This returns a
    :class:`ConstraintData` object which will store the :class:`Function`'s
    interpolation conditions. See the :class:`ConstraintData` documentation for
    details and the :class:`ConvexFunction` or :class:`SmoothConvexFunction` for
    examples.

    Let `f` be a :class:`Function` object. The naming convention for a
    :class:`ScalarConstraint` object representing an interpolation condition of `f`
    between two :class:`Vector` objects `x_0` and `x_1` is
    `{f.tag}:{x_0.tag},{x_1.tag}`. The naming convention for a :class:`ScalarConstraint`
    object representing an interpolation condition of `f` using only one
    :class:`Vector` object `x_0` is `{f.tag}:{x_0.tag},{x_0.tag}`.

    If a :class:`Function` has multiple :class:`ScalarConstraint` groups,
    then the naming convention of the individual :class:`ScalarConstraint` objects
    must differ. For example, Convex Lipschitz functions has a group of
    :class:`ScalarConstraint` objects representing the interpolation conditions
    related to convexity and a group of :class:`ScalarConstraint` objects
    representing the interpolation conditions related to Lipschitz Continuity.
    Let `f` be a :class:`Function` object. A possible naming convention for a
    :class:`ScalarConstraint` object representing an interpolation condition related
    to the convexity of `f` between two :class:`Vector` objects `x_0` and `x_1` is
    `{f.tag}_convex:{x_0.tag},{x_1.tag}`. A possible naming convention for a
    :class:`ScalarConstraint` object representing an interpolation condition related
    to the Lipschitz Continuity of `f` between two :class:`Vector` objects `x_0`
    and `x_1` is `{f.tag}_LC:{x_0.tag},{x_1.tag}`.

    Attributes:
        is_basis (bool): `True` if this function is not formed through a linear
            combination of other functions. `False` otherwise.
        tags (list[str]): A list that contains tags that can be used to
            identify the :class:`Function` object. Tags should be unique.
        math_expr (:class:`MathExpr`): A :class:`MathExpr` object with a
            member variable that contains a mathematical expression
            represented as a string.
    """

    is_basis: bool

    composition: AddedFunc | ScaledFunc | None = None

    # Human tagged value for the function
    tags: list[str] = attrs.field(factory=list)

    # Mathematical expression
    math_expr: MathExpr = attrs.field(factory=me.MathExpr)

    # Generate an automatic id
    uid: uuid.UUID = attrs.field(factory=uuid.uuid4, init=False)

    def __attrs_post_init__(self):
        if self.is_basis:
            assert self.composition is None
        else:
            assert self.composition is not None

        for tag in self.tags:
            if tag in reg.REGISTERED_FUNC_AND_OPER_DICT:
                warnings.warn(
                    f"Warning: function or operator with tag {tag} has been created before."
                )

            reg.REGISTERED_FUNC_AND_OPER_DICT[tag] = self

        if self.tags:  # If tag is provided, make math_expr based on tag
            self.math_expr.expr_str = self.tag

    @property
    def tag(self):
        """Returns the most recently added tag.

        Returns:
            str: The most recently added tag of this :class:`Function` object.
        """
        if len(self.tags) == 0:
            raise ValueError("This Function object doesn't have a tag.")
        return self.tags[-1]

    def add_tag(self, tag: str) -> Function:
        """Add a new tag for this :class:`Function` object.

        Args:
            tag (str): The new tag to be added to the `tags` list.

        Returns:
            The instance itself.
        """
        if tag in reg.REGISTERED_FUNC_AND_OPER_DICT:
            print(
                f"Warning: function or operator with tag {tag} has been created before."
            )

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
        :class:`ScalarConstraint` or individual :class:`PSDConstraint` objects."""
        raise NotImplementedError(
            "This method should be implemented in the children of Function."
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

    def add_triplet_to_func(self, triplet: Triplet) -> None:
        pep_context = pc.get_current_context()
        if pep_context is None:
            raise RuntimeError("Did you forget to create a context?")
        pep_context.add_triplet(triplet)

    def add_point_with_grad_restriction(
        self, point: vt.Vector, desired_grad: vt.Vector
    ) -> Triplet:
        if self.is_basis:
            func_val = sc.Scalar(
                is_basis=True,
                math_expr=me.MathExpr(
                    expr_str=f"{self.__repr__()}({point.__repr__()})"
                ),
            )
            triplet = Triplet(
                point,
                func_val,
                desired_grad,
                self,
                name=utils.triplet_tag(point, func_val, desired_grad),
            )
            self.add_triplet_to_func(triplet)
        else:
            if isinstance(self.composition, AddedFunc):
                left_triplet = self.composition.left_func.generate_triplet(point)
                next_desired_grad = desired_grad - left_triplet.grad
                next_desired_grad.math_expr.expr_str = utils.grad_tag(
                    f"{self.composition.right_func.__repr__()}({point.__repr__()})"
                )
                right_triplet = (
                    self.composition.right_func.add_point_with_grad_restriction(
                        point, next_desired_grad
                    )
                )
                triplet = Triplet(
                    point,
                    left_triplet.func_val + right_triplet.func_val,
                    desired_grad,
                    self,
                    name=utils.triplet_tag(
                        point,
                        left_triplet.func_val + right_triplet.func_val,
                        desired_grad,
                    ),
                )
            elif isinstance(self.composition, ScaledFunc):
                next_desired_grad = desired_grad / self.composition.scale
                next_desired_grad.math_expr.expr_str = utils.grad_tag(
                    f"{self.composition.base_func.__repr__()}({point.__repr__()})"
                )
                base_triplet = (
                    self.composition.base_func.add_point_with_grad_restriction(
                        point, next_desired_grad
                    )
                )
                triplet = Triplet(
                    point,
                    base_triplet.func_val * self.composition.scale,
                    desired_grad,
                    self,
                    name=utils.triplet_tag(
                        point,
                        base_triplet.func_val * self.composition.scale,
                        desired_grad,
                    ),
                )
            else:
                raise ValueError(
                    f"Unknown composition of functions: {self.composition}"
                )
        return triplet

    def set_stationary_point(self, name: str) -> vt.Vector:
        """
        Return a stationary point for this :class:`Function` object.

        A :class:`Function` object can only have one stationary point.

        Args:
            name (str): The tag for the :class:`Vector` object which
                 will serve as the stationary point.

        Returns:
            :class:`Vector`: The stationary point for this :class:`Function`
            object.

        Example:
            >>> import pepflow as pf
            >>> f = pf.SmoothConvexFunction(is_basis=True, tags=["f"], L=1)
            >>> ctx = pf.PEPContext("ctx").set_as_current()
            >>> f.set_stationary_point("x_star")
        """
        # Assert we can only add one stationary point?
        pep_context = pc.get_current_context()
        if pep_context is None:
            raise RuntimeError("Did you forget to create a context?")
        if len(pep_context.func_to_stationary_triplets[self]) > 0:
            raise ValueError(
                "You are trying to add a stationary point to a function that already has a stationary point."
            )
        point = vt.Vector(is_basis=True, tags=[name])
        desired_grad = vt.Vector.zero()  # Zero point
        desired_grad.math_expr.expr_str = utils.grad_tag(f"{self.__repr__()}({name})")
        triplet = self.add_point_with_grad_restriction(point, desired_grad)
        pep_context.add_stationary_triplet(self, triplet)
        return point

    def generate_triplet(self, point: vt.Vector) -> Triplet:
        pep_context = pc.get_current_context()
        if pep_context is None:
            raise RuntimeError("Did you forget to create a context?")

        if not isinstance(point, vt.Vector):
            raise ValueError("The Function can only take point as input.")

        if self.is_basis:
            for triplet in pep_context.func_to_triplets[self]:
                if (
                    triplet.point.uid == point.uid
                ):  # TODO: make different way to determine this point
                    return triplet

            func_val = sc.Scalar(
                is_basis=True,
                math_expr=me.MathExpr(
                    expr_str=f"{self.__repr__()}({point.__repr__()})"
                ),
            )
            grad = vt.Vector(
                is_basis=True,
                math_expr=me.MathExpr(
                    expr_str=utils.grad_tag(f"{self.__repr__()}({point.__repr__()})")
                ),
            )

            new_triplet = Triplet(
                point,
                func_val,
                grad,
                self,
                name=utils.triplet_tag(point, func_val, grad),
            )
            self.add_triplet_to_func(new_triplet)
            return new_triplet
        else:
            if isinstance(self.composition, AddedFunc):
                left_triplet = self.composition.left_func.generate_triplet(point)
                right_triplet = self.composition.right_func.generate_triplet(point)
                func_val = left_triplet.func_val + right_triplet.func_val
                grad = left_triplet.grad + right_triplet.grad
            elif isinstance(self.composition, ScaledFunc):
                base_triplet = self.composition.base_func.generate_triplet(point)
                func_val = self.composition.scale * base_triplet.func_val
                grad = self.composition.scale * base_triplet.grad
            else:
                raise ValueError(
                    f"Unknown composition of functions: {self.composition}"
                )
            return Triplet(
                point,
                func_val,
                grad,
                self,
                name=utils.triplet_tag(point, func_val, grad),
            )

    def grad(self, point: vt.Vector) -> vt.Vector:
        """
        Returns a :class:`Vector` object that is the gradient of the
        :class:`Function` at the given :class:`Vector`.

        This function should be used to return subgradients as well as gradients
        and subgradients are effectively treated the same in the context of PEP.

        Args:
            point (:class:`Vector`): Any :class:`Vector`.

        Returns:
            :class:`Vector`: The gradient of the :class:`Function` at the
            given :class:`Vector`.

        Example:
            >>> import pepflow as pf
            >>> ctx = pf.PEPContext("ctx").set_as_current()
            >>> x_0 = pf.Vector(is_basis=True, tags=["x_0"])
            >>> f = pf.SmoothConvexFunction(is_basis=True, L=1, tags=["f"])
            >>> f.grad(x_0)
        """
        triplet = self.generate_triplet(point)
        return triplet.grad

    def func_val(self, point: vt.Vector) -> sc.Scalar:
        """
        Returns a :class:`Scalar` object that is the function value of the
        :class:`Function` at the given :class:`Vector`.

        Args:
            point (:class:`Vector`): Any :class:`Vector`.

        Returns:
            :class:`Vector`: The function value of the :class:`Function` at the
            given :class:`Vector`.
        """
        triplet = self.generate_triplet(point)
        return triplet.func_val

    def __call__(self, point: vt.Vector) -> sc.Scalar:
        return self.func_val(point)

    def __add__(self, other):
        if not isinstance(other, Function):
            return NotImplemented
        return Function(
            is_basis=False,
            composition=AddedFunc(self, other),
            tags=[],
            math_expr=me.MathExpr(expr_str=f"{repr(self)}+{repr(other)}"),
        )

    def __sub__(self, other):
        if not isinstance(other, Function):
            return NotImplemented
        expr_other = repr(other)
        if isinstance(other.composition, AddedFunc):
            expr_other = f"({repr(other)})"
        return Function(
            is_basis=False,
            composition=AddedFunc(self, -other),
            tags=[],
            math_expr=me.MathExpr(expr_str=f"{repr(self)}-{expr_other}"),
        )

    def __mul__(self, other):
        if not utils.is_numerical(other):
            return NotImplemented
        expr_self = repr(self)
        if isinstance(self.composition, AddedFunc):
            expr_self = f"({repr(self)})"
        return Function(
            is_basis=False,
            composition=ScaledFunc(scale=other, base_func=self),
            tags=[],
            math_expr=me.MathExpr(expr_str=f"{other:.4g}*{expr_self}"),
        )

    def __rmul__(self, other):
        if not utils.is_numerical(other):
            return NotImplemented
        expr_self = repr(self)
        if isinstance(self.composition, AddedFunc):
            expr_self = f"({repr(self)})"
        return Function(
            is_basis=False,
            composition=ScaledFunc(scale=other, base_func=self),
            tags=[],
            math_expr=me.MathExpr(expr_str=f"{other:.4g}*{expr_self}"),
        )

    def __neg__(self):
        expr_self = repr(self)
        if isinstance(self.composition, AddedFunc):
            expr_self = f"({repr(self)})"
        return Function(
            is_basis=False,
            composition=ScaledFunc(scale=-1, base_func=self),
            tags=[],
            math_expr=me.MathExpr(expr_str=f"-{expr_self}"),
        )

    def __truediv__(self, other):
        if not utils.is_numerical(other):
            return NotImplemented
        expr_self = repr(self)
        if isinstance(self.composition, AddedFunc):
            expr_self = f"({repr(self)})"
        return Function(
            is_basis=False,
            composition=ScaledFunc(scale=1 / other, base_func=self),
            tags=[],
            math_expr=me.MathExpr(expr_str=f"1/{other:.4g}*{expr_self}"),
        )

    def __hash__(self):
        return hash(self.uid)

    def __eq__(self, other):
        if not isinstance(other, Function):
            return NotImplemented
        return self.uid == other.uid

    def prox(
        self, x: Vector, stepsize: numbers.Number | Parameter, tag: str | None = None
    ) -> Vector:
        """Apply the proximal operator on the input :math:`x`.

        Define the proximal operator as

        .. math:: \\text{prox}_{\\gamma f}(x) := \\arg\\min_u \\left\\{ \\gamma f(u) + \\frac{1}{2} \\|u - x\\|^2 \\right\\}.

        This function returns the output :class:`Vector` :math:`u` found from
        applying the proximal operator with respect to some :class:`Function` :math:`f`
        on the input :class:`Vector` :math:`x` with stepsize :math:`\\gamma`. Consider
        the following equivalence relationship:

        .. math:: \\arg\\min_u \\left\\{ \\gamma f(u) + \\frac{1}{2} \\|u - x\\|^2 \\right\\} \\Longleftrightarrow x - u \\in \\gamma \\partial f(u) \\Longleftrightarrow u = x - \\gamma \\widetilde{\\nabla} f(u) \\text{ where } \\widetilde{\\nabla} f(u)\\in\\partial f(u).

        Args:
            x (:class:`Vector`): The input point.
            stepsize (numbers.Number | :class:`Parameter`): The stepsize.
            tag (str | None): By default set to `None`. Pass a tag to add
                to the output of the proximal operator applied the input point.

        Returns:
            :class:`Vector`: The output of the proximal operator applied on `x`.

        Note:
            For children of :class:`Function` for which the proximal operator is
            not defined, overwrite the function to raise `NotImplemented`.
        """

        u_expr = f"prox_{{{stepsize}*{self.__repr__()}}}({x.__repr__()})"
        func_val_u = sc.Scalar(
            is_basis=True,
            math_expr=me.MathExpr(expr_str=f"{self.__repr__()}({u_expr})"),
        )
        grad_u = vt.Vector(
            is_basis=True,
            math_expr=me.MathExpr(
                expr_str=utils.grad_tag(f"{self.__repr__()}({u_expr})")
            ),
        )

        u = x - stepsize * grad_u
        u.math_expr.expr_str = u_expr

        if tag:
            u.add_tag(tag)
            func_val_u.add_tag(f"{self.__repr__()}({tag})")
            grad_u.add_tag(utils.grad_tag(f"{self.__repr__()}({tag})"))

        new_triplet = Triplet(
            u,
            func_val_u,
            grad_u,
            self,
            name=utils.triplet_tag(u, func_val_u, grad_u),
        )
        self.add_triplet_to_func(new_triplet)
        return u


@attrs.frozen(kw_only=True, repr=False)
class ConvexFunction(Function):
    """
    The :class:`ConvexFunction` class represents a closed, convex, and proper (CCP)
    function, i.e., a convex function whose epigraph is a non-empty closed set.

    The :class:`ConvexFunction` class is a child of :class:`Function`.

    A CCP function typically has no parameters. We can instantiate a
    :class:`ConvexFunction` object as follows:

    Example:
        >>> import pepflow as pf
        >>> f = pf.ConvexFunction(is_basis=True, tags=["f"])
    """

    def __attrs_post_init__(self):
        super().__attrs_post_init__()

    def __hash__(self):
        return super().__hash__()

    def convex_interpolability_constraints(
        self, triplet_i: Triplet, triplet_j: Triplet
    ) -> ct.ScalarConstraint:
        point_i = triplet_i.point
        func_val_i = triplet_i.func_val

        point_j = triplet_j.point
        func_val_j = triplet_j.func_val
        grad_j = triplet_j.grad

        func_diff = func_val_j - func_val_i
        cross_term = grad_j * (point_i - point_j)

        return (func_diff + cross_term).le(
            0,
            name=f"{self.__repr__()}:{point_i.__repr__()},{point_j.__repr__()}",
        )

    def get_interpolation_constraints_by_group(
        self, pep_context: pc.PEPContext | None = None
    ) -> pc.ConstraintData:
        """Return a :class:`ConstraintData` object that manages the function's
        groups of interpolation conditions."""
        cd = pc.ConstraintData(func_or_oper=self)
        if pep_context is None:
            pep_context = pc.get_current_context()
        if pep_context is None:
            raise RuntimeError("Did you forget to create a context?")
        scal_constraint = []
        for i in pep_context.func_to_triplets[self]:
            for j in pep_context.func_to_triplets[self]:
                if i == j:
                    continue
                scal_constraint.append(self.convex_interpolability_constraints(i, j))
        cd.add_sc_constraint("Convex Function", scal_constraint)
        return cd

    def interp_ineq(
        self,
        p1: vt.Vector | str,
        p2: vt.Vector | str,
        pep_context: pc.PEPContext | None = None,
        sympy_mode: bool = False,
    ) -> sc.Scalar:
        """Generate the interpolation inequality :class:`Scalar` object between two
        :class:`Vector` objects through the objects themselves or their tags.

        The interpolation inequality between two points :math:`p_1, p_2` for a
        CCP function :math:`f` is

        .. math:: f(p_2) - f(p_1) + \\langle \\widetilde{\\nabla} f(p_2), p_1 - p_2 \\rangle,

        where :math:`\\widetilde{\\nabla} f(p_2) \\in\\partial f(p_2)`.

        References:
            A. B. Taylor, J. M. Hendrickx, and F. Glineur. Smooth strongly convex interpolation
            and exact worst-case performance of first-order methods. Mathematical Programming,
            161(1-2):307–345, 2017.

        Args:
            p1 (:class:`Vector` | str): A :class:`Vector` :math:`p_1` point or its tag.
            p2 (:class:`Vector` | str): A :class:`Vector` :math:`p_2` point or its tag.

        Example:
            >>> import pepflow as pf
            >>> ctx = pf.PEPContext("ctx").set_as_current()
            >>> xi = pf.Vector(is_basis=True, tags=["x_i"])
            >>> xj = pf.Vector(is_basis=True, tags=["x_j"])
            >>> f = pf.ConvexFunction(is_basis=True, L=1, tags=["f"])
            >>> fi, fj = f(xi), f(xj)
            >>> f.interp_ineq("x_i", "x_j")
        """
        del sympy_mode  # No need for this case
        if pep_context is None:
            pep_context = pc.get_current_context()
        if pep_context is None:
            raise RuntimeError("Did you forget to specify a context?")
        x1, f1, _ = pep_context.get_triplet_by_point_tag(p1, func=self).expand()
        x2, f2, g2 = pep_context.get_triplet_by_point_tag(p2, func=self).expand()
        return f2 - f1 + g2 * (x1 - x2)


@attrs.frozen(kw_only=True, repr=False)
class SmoothConvexFunction(Function):
    """
    The :class:`SmoothConvexFunction` class represents a smooth, convex function.

    The :class:`SmoothConvexFunction` class is a child of :class:`Function`.

    A smooth, convex function has a smoothness parameter :math:`L`.
    We can instantiate a :class:`SmoothConvexFunction` object as follows:

    Example:
        >>> import pepflow as pf
        >>> f = pf.SmoothConvexFunction(is_basis=True, tags=["f"], L=1)
    """

    L: NUMERICAL_TYPE | Parameter

    def __attrs_post_init__(self):
        super().__attrs_post_init__()
        if isinstance(self.L, utils.NUMERICAL_TYPE):
            assert self.L > 0

    def __hash__(self):
        return super().__hash__()

    def smooth_convex_interpolability_constraints(
        self, triplet_i, triplet_j
    ) -> ct.ScalarConstraint:
        point_i = triplet_i.point
        func_val_i = triplet_i.func_val
        grad_i = triplet_i.grad

        point_j = triplet_j.point
        func_val_j = triplet_j.func_val
        grad_j = triplet_j.grad

        func_diff = func_val_j - func_val_i
        cross_term = grad_j * (point_i - point_j)
        quad_term = 1 / (2 * self.L) * (grad_i - grad_j) ** 2

        return (func_diff + cross_term + quad_term).le(
            0,
            name=f"{self.__repr__()}:{point_i.__repr__()},{point_j.__repr__()}",
        )

    def get_interpolation_constraints_by_group(
        self, pep_context: pc.PEPContext | None = None
    ) -> pc.ConstraintData:
        """Return a :class:`ConstraintData` object that manages the function's
        groups of interpolation conditions."""
        cd = pc.ConstraintData(func_or_oper=self)
        if pep_context is None:
            pep_context = pc.get_current_context()
        if pep_context is None:
            raise RuntimeError("Did you forget to create a context?")
        scal_constraint = []
        for i in pep_context.func_to_triplets[self]:
            for j in pep_context.func_to_triplets[self]:
                if i == j:
                    continue
                scal_constraint.append(
                    self.smooth_convex_interpolability_constraints(i, j)
                )
        cd.add_sc_constraint("Smooth Convex Function", scal_constraint)
        return cd

    def interp_ineq(
        self,
        p1: vt.Vector | str,
        p2: vt.Vector | str,
        pep_context: pc.PEPContext | None = None,
        sympy_mode: bool = False,
    ) -> sc.Scalar:
        """Generate the interpolation inequality :class:`Scalar` object between two
        :class:`Vector` objects through the objects themselves or their tags.

        The interpolation inequality between two points :math:`p_1, p_2` for a
        smooth, convex function :math:`f` is

        .. math:: f(p_2) - f(p_1) + \\langle \\nabla f(p_2), p_1 - p_2 \\rangle + \\tfrac{1}{2} \\lVert \\nabla f(p_1) - \\nabla f(p_2) \\rVert^2.

        References:
            A. B. Taylor, J. M. Hendrickx, and F. Glineur. Smooth strongly convex
            interpolation and exact worst-case performance of first-order methods.
            Mathematical Programming, 161(1-2):307–345, 2017.

        Args:
            p1 (:class:`Vector` | str): A :class:`Vector` :math:`p_1` point or its tag.
            p2 (:class:`Vector` | str): A :class:`Vector` :math:`p_2` point or its tag.

        Example:
            >>> import pepflow as pf
            >>> ctx = pf.PEPContext("ctx").set_as_current()
            >>> xi = pf.Vector(is_basis=True, tags=["x_i"])
            >>> xj = pf.Vector(is_basis=True, tags=["x_j"])
            >>> f = pf.SmoothConvexFunction(is_basis=True, L=1, tags=["f"])
            >>> fi, fj = f(xi), f(xj)
            >>> f.interp_ineq("x_i", "x_j")
        """
        if pep_context is None:
            pep_context = pc.get_current_context()
        if pep_context is None:
            raise RuntimeError("Did you forget to specify a context?")

        x1, f1, g1 = pep_context.get_triplet_by_point_tag(p1, func=self).expand()
        x2, f2, g2 = pep_context.get_triplet_by_point_tag(p2, func=self).expand()
        if sympy_mode and isinstance(self.L, float):
            raise ValueError(
                "Cannot use sympy mode with float L in SmoothConvexFunction. "
                "Please use an integer number or sympy.Rational for L."
            )
        coef = sp.S(1) / sp.S(2 * self.L) if sympy_mode else 1 / (2 * self.L)
        return f2 - f1 + g2 * (x1 - x2) + coef * (g1 - g2) ** 2
