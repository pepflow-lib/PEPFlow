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

import warnings
from collections import defaultdict
from typing import TYPE_CHECKING

import attrs
import natsort
import pandas as pd

from pepflow import constraint as ct
from pepflow import utils

if TYPE_CHECKING:
    from pepflow.function import Function, Triplet
    from pepflow.operator import Duplet, Operator
    from pepflow.pep_result import PEPResult
    from pepflow.scalar import Scalar
    from pepflow.vector import Vector

# A global variable for storing the current context that manages objects
# such as vectors and scalars.
CURRENT_CONTEXT: PEPContext | None = None
# Keep the track of all previous created contexts.
GLOBAL_CONTEXT_DICT: dict[str, PEPContext] = {}


@attrs.frozen
class ConstraintData:
    """
    A data class that will store a :class:`Function`'s or :class:`Operator`'s
    interpolation conditions.

    Functions and operators can have multiple groups of interpolations conditions.
    There are typically two types of groups. One group is composed of associated
    :class:`ScalarConstraint` objects. The other is an individual
    :class:`PSDConstraint` object.

    Attributes:
        func_or_oper (:class:`Function` | :class:`Operator): The associated
            :class:`Function` or :class:`Operator`.
        sc_dict (dict[str, list[:class:`ScalarConstraint`]]): A dictionary in which
            the keys are the name of the groups of :class:`ScalarConstraint` objects and
            the values are a list of associated :class:`ScalarConstraint` objects.
        psd_dict (dict[str, :class:`PSDConstraint`]): A dictionary in which the keys
            are the names of the types of the :class:`PSDConstraint` objects and the values
            are the :class:`PSDConstraint` objects.
    """

    func_or_oper: Function | Operator
    sc_dict: dict[str, list[ct.ScalarConstraint]] = attrs.field(factory=dict)
    psd_dict: dict[str, ct.PSDConstraint] = attrs.field(factory=dict)

    def add_sc_constraint(
        self, constraint_type: str, scal_constraint: list[ct.ScalarConstraint]
    ) -> None:
        """Add a new list of :class:`ScalarConstraint` objects.

        Args:
            constraint_type (str): The name to refer to the group of scalar
                constraints repesented by `scal_constraint`.
            scal_constraint (list[:class:`ScalarConstraint`]): The new list of
                :class:`ScalarConstraint` objects to add.
        """
        self.sc_dict[constraint_type] = scal_constraint

    def add_psd_constraint(
        self, constraint_type: str, psd_constraint: ct.PSDConstraint
    ) -> None:
        """Add a new :class:`PSDConstraint` object.

        Args:
            constraint_type (str): The name to refer to the group of scalar
                constraints repesented by `scal_constraint`.
            psd_constraint (:class:`PSDConstraint`): The new list of
                :class:`ScalarConstraint` objects to add.
        """
        self.psd_dict[constraint_type] = psd_constraint

    def process_scalar_constraint_with_result(
        self, result: PEPResult
    ) -> dict[str, pd.DataFrame]:
        sc_df_dict = {}
        for name, sc in self.sc_dict.items():
            df = pd.DataFrame(
                [
                    (
                        constraint.name,
                        *utils.name_to_vector_tuple(constraint.name),
                    )
                    for constraint in sc
                ],
                columns=["constraint_name", "col_point", "row_point"],
            )
            order_col = natsort.natsorted(df["col_point"].unique())
            order_row = natsort.natsorted(df["row_point"].unique())
            df["row"] = df["row_point"].map(lambda x: order_row.index(x))
            df["col"] = df["col_point"].map(lambda x: order_col.index(x))
            df["dual_value"] = df["constraint_name"].map(
                lambda x: result.get_dual_value(x)
            )
            df.attrs = {"order_row": order_row, "order_col": order_col}
            sc_df_dict[name] = df
        return sc_df_dict


def get_current_context() -> PEPContext | None:
    """
    Return the current global :class:`PEPContext`.

    Returns:
        :class:`PEPContext`: The current global :class:`PEPContext`.
    """
    return CURRENT_CONTEXT


def set_current_context(ctx: PEPContext | None):
    """
    Change the current global :class:`PEPContext`.

    Args:
        ctx (:class:`PEPContext`): The :class:`PEPContext` to set as the new
            global :class:`PEPContext`.

    Example:
        >>> ctx = pf.PEPContext(ctx).set_as_current()
    """
    global CURRENT_CONTEXT
    assert ctx is None or isinstance(ctx, PEPContext)
    CURRENT_CONTEXT = ctx


class PEPContext:
    """
    A :class:`PEPContext` object is a context manager which maintains
    the abstract mathematical objects of the Primal and Dual PEP.

    Attributes:
        name (str): The unique name of the :class:`PEPContext` object.

    Note:
        If the provided name matches the name of a previously created
        :class:`PEPContext` object, the previously created :class:`PEPContext`
        will be overwritten in the `GLOBAL_CONTEXT_DICT`.

    Example:
        >>> ctx = pf.PEPContext("ctx").set_as_current()
    """

    def __init__(self, name: str):
        if name in GLOBAL_CONTEXT_DICT.keys():
            warnings.warn(
                "The provided name was already used. The older PEPContext will be overwritten. PEPBuilders constructed with the older PEPContext should be remade."
            )
        self.name = name
        self.vectors: list[Vector] = []
        self.scalars: list[Scalar] = []
        self.func_to_triplets: dict[Function, list[Triplet]] = defaultdict(list)
        # self.func_to_triplets will contain all stationary_triplets. They are not mutually exclusive.
        self.func_to_stationary_triplets: dict[Function, list[Triplet]] = defaultdict(
            list
        )
        self.oper_to_duplets: dict[Operator, list[Duplet]] = defaultdict(list)
        # self.oper_to_duplets will contain all fixed_duplets and zero_duplets. They are not mutually exclusive.
        self.oper_to_fixed_duplets: dict[Operator, list[Duplet]] = defaultdict(list)
        self.oper_to_zero_duplets: dict[Operator, list[Duplet]] = defaultdict(list)

        self.tag_to_vectors_or_scalars: dict[str, Vector | Scalar] = {}
        self.vector_to_triplet_or_duplet: dict[
            Vector, tuple[list[Triplet], list[Duplet]]
        ] = defaultdict(lambda: ([], []))
        GLOBAL_CONTEXT_DICT[name] = self

    def set_as_current(self) -> PEPContext:
        """
        Set this :class:`PEPContext` object as the global context.

        Returns:
            :class:`PEPContext`: This :class:`PEPContext` object.

        Example:
            >>> ctx = pf.PEPContext("ctx").set_as_current()
        """
        set_current_context(self)
        return self

    def add_vector(self, vector: Vector) -> None:
        self.vectors.append(vector)

    def add_scalar(self, scalar: Scalar) -> None:
        self.scalars.append(scalar)

    def add_tag_to_vectors_or_scalars(
        self, tag: str, vec_or_sc: Vector | Scalar
    ) -> None:
        if tag in self.tag_to_vectors_or_scalars:
            warnings.warn(
                f"The given tag {tag} was already associated with a Vector or Scalar in this PEPContext {self.name}. You can no longer access the old object by {tag}."
            )
        self.tag_to_vectors_or_scalars[tag] = vec_or_sc

    def add_triplet(self, triplet_to_add: Triplet) -> None:
        for triplet in self.func_to_triplets[triplet_to_add.func]:
            if (
                triplet.point.uid == triplet_to_add.point.uid
            ):  # TODO: Using other way instead of uid to determine if two points are the same or not
                raise ValueError(
                    f"In this PEPContext {self.name}, the function {triplet_to_add.func} already is associated with a triplet that contains the same point {triplet_to_add.point.tag}."
                )
        self.func_to_triplets[triplet_to_add.func].append(triplet_to_add)
        self.vector_to_triplet_or_duplet[triplet_to_add.point][0].append(triplet_to_add)

    def add_stationary_triplet(
        self, function: Function, stationary_triplet: Triplet
    ) -> None:
        self.func_to_stationary_triplets[function].append(stationary_triplet)

    def add_duplet(self, duplet_to_add: Duplet) -> None:
        for duplet in self.oper_to_duplets[duplet_to_add.oper]:
            if (
                duplet.point.uid == duplet_to_add.point.uid
            ):  # TODO: Using other way instead of uid to determine if two points are the same or not
                raise ValueError(
                    f"In this PEPContext {self.name}, the operator {duplet_to_add.oper} already is associated with a duplet that contains the same point {duplet_to_add.point.tag}."
                )
        self.oper_to_duplets[duplet_to_add.oper].append(duplet_to_add)
        self.vector_to_triplet_or_duplet[duplet_to_add.point][1].append(duplet_to_add)

    def add_fixed_duplet(self, fixed_duplet: Duplet) -> None:
        self.oper_to_fixed_duplets[fixed_duplet.oper].append(fixed_duplet)

    def add_zero_duplet(self, zero_duplet: Duplet) -> None:
        self.oper_to_zero_duplets[zero_duplet.oper].append(zero_duplet)

    # TODO: Find a better way to declare the return type while keeping type checker happy.
    def get_by_tag(self, tag: str):
        """
        Under this :class:`PEPContext`, get the :class:`Vector` or
        :class:`Scalar` object associated with the provided `tag`.

        Args:
            tag (str): The tag of the :class:`Vector` or :class:`Scalar` object
                we want to retrieve.

        Returns:
            :class:`Vector` | :class:`Scalar`: The :class:`Vector` or
            :class:`Scalar` object associated with the provided `tag`.
        """
        if (vec_or_sc := self.tag_to_vectors_or_scalars[tag]) is not None:
            return vec_or_sc
        raise ValueError("Cannot find the vector, scalar, or function of given tag.")

    def get_triplet_by_point_tag(
        self, point_or_tag: Vector | str, func: Function
    ) -> Triplet:
        """Returns a triplet of the given point or its tag in the function."""
        from pepflow.vector import Vector

        if func not in self.func_to_triplets:
            raise ValueError(
                f"Cannot find the triplets associated with {func=} in the context."
            )
        triplets = self.func_to_triplets[func]
        if isinstance(point_or_tag, Vector):
            for t in triplets:
                if (
                    t.point == point_or_tag
                ):  # TODO: Using other way instead of uid to determine if two points are the same or not
                    return t
        else:
            for t in triplets:
                if point_or_tag in t.point.tags:
                    return t
        raise ValueError(f"Cannot find the triplet associated with {point_or_tag}")

    def clear(self) -> None:
        """Reset this :class:`PEPContext` object."""
        self.vectors.clear()
        self.scalars.clear()
        self.func_to_triplets.clear()
        self.func_to_stationary_triplets.clear()
        self.oper_to_duplets.clear()
        self.oper_to_fixed_duplets.clear()
        self.oper_to_zero_duplets.clear()
        self.tag_to_vectors_or_scalars.clear()

    def tracked_point(self, func_or_oper: Function | Operator) -> list[Vector]:
        """
        Returns a list of the visited vectors :math:`\\{x_i\\}` associated with
        `func_or_oper` under this :class:`PEPContext`.

        Each function :math:`f` used in Primal and Dual PEP is associated with
        a set of triplets :math:`\\{x_i, f(x_i), \\nabla f(x_i)\\}` visited by
        the considered algorithm. We can also consider a subgradient
        :math:`\\widetilde{\\nabla} f(x)` instead of the gradient.

        Args:
            func_or_oper (:class:`Function` | :class:`Operator`): This is either
                the function associated with the set of triplets
                :math:`\\{x_i, f(x_i), \\nabla f(x_i)\\}` or the operator
                associated with the set of duplets :math:`\\{x_i, A(x_i)\\}`.

        Returns:
            list[:class:`Vector`]: The list of the visited vectors
            :math:`\\{x_i\\}`.
        """

        if (triplets := self.func_to_triplets.get(func_or_oper)) is not None:  # ty: ignore
            return natsort.natsorted(
                [t.point for t in triplets],
                key=lambda x: x.tag,
            )
        elif (duplets := self.oper_to_duplets.get(func_or_oper)) is not None:  # ty: ignore
            return natsort.natsorted(
                [t.point for t in duplets],
                key=lambda x: x.tag,
            )
        raise ValueError(
            "The provided Function or Operator does not have any associated triplets or duplets in this context."
        )

    def tracked_grad(self, func: Function) -> list[Vector]:
        """
        This function returns a list of the visited
        gradients :math:`\\{\\nabla f(x_i)\\}` under this :class:`PEPContext`.

        Each function :math:`f` used in Primal and Dual PEP is associated with
        a set of triplets :math:`\\{x_i, f(x_i), \\nabla f(x_i)\\}` visited by
        the considered algorithm. We can also consider a subgradient
        :math:`\\widetilde{\\nabla} f(x)` instead of the gradient
        :math:`\\nabla f(x_i)`.

        Args:
            func (:class:`Function`): The function associated with the set
                of triplets :math:`\\{x_i, f(x_i), \\nabla f(x_i)\\}`.

        Returns:
            list[:class:`Vector`]: The list of the visited gradients
            :math:`\\{\\nabla f(x_i)\\}`.
        """
        if (triplets := self.func_to_triplets.get(func)) is not None:
            return natsort.natsorted(
                [t.grad for t in triplets], key=lambda x: x.__repr__()
            )
        raise ValueError(
            "The provided Function does not have any associated triplets in this context."
        )

    def tracked_func_val(self, func: Function) -> list[Scalar]:
        """
        This function returns a list of the visited
        function values :math:`\\{f(x_i)\\}` under this :class:`PEPContext`.

        Each function :math:`f` used in Primal and Dual PEP is associated with
        a set of triplets :math:`\\{x_i, f(x_i), \\nabla f(x_i)\\}` visited by
        the considered algorithm. We can also consider a subgradient
        :math:`\\widetilde{\\nabla} f(x)` instead of the gradient
        :math:`\\nabla f(x_i)`.

        Args:
            func (:class:`Function`): The function associated with the set of
                triplets :math:`\\{x_i, f(x_i), \\nabla f(x_i)\\}`.

        Returns:
            list[:class:`Scalar`]: The list of the visited function values
            :math:`\\{f(x_i)\\}`.
        """
        if (triplets := self.func_to_triplets.get(func)) is not None:
            return natsort.natsorted(
                [t.func_val for t in triplets],
                key=lambda x: x.__repr__(),
            )
        raise ValueError(
            "The provided Function does not have any associated triplets in this context."
        )

    def tracked_output(self, oper: Operator) -> list[Vector]:
        """
        This function returns a list of the visited
        outputs :math:`\\{A(x_i)\\}` under this :class:`PEPContext`.

        Each operator :math:`A` used in Primal and Dual PEP is associated with
        a set of duplets :math:`\\{x_i, A(x_i)\\}` visited by the considered
        algorithm.

        Args:
            oper (:class:`Operator`): The operator associated with the set
                of duplets :math:`\\{x_i, A(x_i)\\}`.

        Returns:
            list[:class:`Vector`]: The list of the visited outputs
            :math:`\\{A(x_i)\\}`.
        """
        if (duplets := self.oper_to_duplets.get(oper)) is not None:
            return natsort.natsorted(
                [t.output for t in duplets], key=lambda x: x.__repr__()
            )
        raise ValueError(
            "The provided Operator does not have any associated duplets in this context."
        )

    def order_of_point(self, func_or_oper: Function | Operator) -> list[str]:
        if (triplets := self.func_to_triplets.get(func_or_oper)) is not None:  # ty: ignore
            return natsort.natsorted([t.point.tag for t in triplets])
        elif (duplets := self.oper_to_duplets.get(func_or_oper)) is not None:  # ty: ignore
            return natsort.natsorted([t.point.tag for t in duplets])
        raise ValueError(
            "The provided Function or Operator does not have any associated triplets or duplets in this context."
        )

    def get_constraint_data(self, func_or_oper: Function | Operator) -> ConstraintData:
        from pepflow.operator import LinearOperatorTranspose

        if (
            func_or_oper not in self.func_to_triplets.keys()
            and func_or_oper not in self.oper_to_duplets.keys()
        ):
            raise ValueError(
                "This function or operator has no associated triplets or duplets for this given context."
            )
        if isinstance(func_or_oper, LinearOperatorTranspose):
            raise ValueError(
                "Do not pass in an object of the class LinearOperatorTranspose."
            )

        return func_or_oper.get_interpolation_constraints_by_group(self)

    def basis_vectors(self) -> list[Vector]:
        """
        Return a list of the basis :class:`Vector` objects managed by this
        :class:`PEPContext`.

        The order is of the list is in terms of when the basis :class:`Vector` objects
        are added.

        Returns:
            list[:class:`Vector`]: A list of the basis :class:`Vector` objects
            managed by this :class:`PEPContext`.
        """
        return [
            p for p in self.vectors if p.is_basis
        ]  # Note the order is always the same as added time

    def basis_scalars(self) -> list[Scalar]:
        """
        Return a list of the basis :class:`Scalar` objects managed by this
        :class:`PEPContext`.

        The order is of the list is in terms of when the basis :class:`Scalar` objects
        are added.

        Returns:
            list[:class:`Scalar`]: A list of the basis :class:`Scalar` objects
            managed by this :class:`PEPContext`.

        Example:
            >>> import pepflow as pf
            >>> f = pf.SmoothConvexFunction(is_basis=True, tags=["f"], L=1)
            >>> ctx = pf.PEPContext("ctx").set_as_current()
            >>> f.set_stationary_point("x_star")
            >>> ctx.basis_scalars()
        """
        return [
            s for s in self.scalars if s.is_basis
        ]  # Note the order is always the same as added time

    def basis_vectors_math_exprs(self) -> list[str]:
        """
        Return a list of the math expressions of the basis :class:`Vector` objects
        managed by this :class:`PEPContext`.

        The order is of the list is in terms of when the basis :class:`Vector` objects
        are added.

        Returns:
            list[str]: A list of the tags of the basis :class:`Vector` objects
            managed by this :class:`PEPContext`.
        """
        return [
            p.__repr__() for p in self.vectors if p.is_basis
        ]  # Note the order is always the same as added time

    def basis_scalars_math_exprs(self) -> list[str]:
        """
        Return a list of the math expressions of the basis :class:`Scalar` objects
        managed by this :class:`PEPContext`.

        The order is of the list is in terms of when the basis :class:`Scalar` objects
        are added.

        Returns:
            list[str]: A list of the tags of the basis :class:`Scalar` objects
            managed by this :class:`PEPContext`.
        """
        return [
            s.__repr__() for s in self.scalars if s.is_basis
        ]  # Note the order is always the same as added time

    def __getitem__(self, tag: str):
        """Return :class:`Vector` or :class:`Scalar: object stored in this
        :class:`PEPContext` object through its tag."""
        return self.get_by_tag(tag)
