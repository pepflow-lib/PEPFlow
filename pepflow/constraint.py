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

from typing import TYPE_CHECKING

import attrs
import numpy as np

if TYPE_CHECKING:
    from pepflow.scalar import Scalar
    from pepflow.utils import Comparator

from pepflow import utils


@attrs.frozen
class Constraint:
    pass


@attrs.frozen
class ScalarConstraint(Constraint):
    """A :class:`ScalarConstraint` object that represents inequalities and
    equalities of :class:`Scalar` objects.

    Denote an arbitrary :class:`Scalar` objects as `x` and `y`.
    :class:`ScalarConstraint` objects represent: `x <= y`, `x >= y`, and `x = y`.

    Attributes:
        lhs (:class:`Scalar`): The :class:`Scalar` object on the left hand side of
            the relation.
        rhs (:class:`Scalar`): The :class:`Scalar` object on the right hand side of
            the relation.
        cmp (:class:`Comparator`): :class:`Comparator` is an enumeration
            that can be either `GE`, `LE`, or `EQ`. They represent `>=`, `<=`,
            or `=` respectively.
        name (str): The unique name of the :class:`Comparator` object.
        associated_dual_var_constraints (list[tuple[:class:`Comparator`, float]]):
            A list of all the constraints imposed on the associated dual
            variable of this :class:`ScalarConstraint` object.

    Example:
        >>> s1 = scalar.Scalar(is_basis=True, tags=["s1"])
        >>> s2 = scalar.Scalar(is_basis=True, tags=["s2"])
        >>> (s1).le(s2, name="constraint_1")
    """

    lhs: Scalar | float
    rhs: Scalar | float
    cmp: Comparator
    name: str

    # Used to represent the constraint on primal variable in dual PEP.
    associated_dual_var_constraints: list[tuple[Comparator, float]] = attrs.field(
        factory=list
    )

    def __attrs_post_init__(self):
        assert self.cmp in [
            utils.Comparator.EQ,
            utils.Comparator.GE,
            utils.Comparator.LE,
        ]

    @classmethod
    def make(
        cls: type[ScalarConstraint],
        lhs: Scalar | float,
        op: str,
        rhs: Scalar | float,
        name: str,
    ) -> ScalarConstraint:
        """
        A static method to construct a :class:`ScalarConstraint` object.

        Args:
            lhs (:class:`Scalar` | float): The :class:`Scalar` object on the
                left hand side of the relation.
            op (str): A `str` which represents the type of relation. Possible options
                are `le`, `ge`, `lt`, `gt`, `eq`, `<=`, `>=`, `<`, `>`, or `==`.
            rhs (:class:`Scalar` | float): The :class:`Scalar` object on the
                right hand side of the relation.
            name (str): The unique name of the constructed :class:`Comparator` object.
        """
        cmp = utils.Comparator.from_str(op)
        return cls(lhs, rhs, cmp, name)

    def dual_le(self, val: float) -> None:
        """
        Generates a `<=` constraint on the dual variable associated with this
        constraint.

        Denote the associated dual variable of this constraint as `lambd`.
        This generates a relation of the form `lambd <= val`.

        Args:
            val (float): The other object in the relation.
        """
        if not utils.is_numerical(val):
            raise ValueError(f"The input {val=} must be a numerical value")
        self.associated_dual_var_constraints.append((utils.Comparator.LE, val))

    def dual_ge(self, val: float) -> None:
        """
        Generates a `>=` constraint on the dual variable associated with this
        constraint.

        Denote the associated dual variable of this constraint as `lambd`.
        This generates a relation of the form `lambd >= val`.

        Args:
            val (float): The other object in the relation.
        """
        if not utils.is_numerical(val):
            raise ValueError(f"The input {val=} must be a numerical value")
        self.associated_dual_var_constraints.append((utils.Comparator.GE, val))

    def dual_eq(self, val: float) -> None:
        """
        Generates a `=` constraint on the dual variable associated with this
        constraint.

        Denote the associated dual variable of this constraint as `lambd`.
        This generates a relation of the form `lambd = val`.

        Args:
            val (float): The other object in the relation.
        """
        if not utils.is_numerical(val):
            raise ValueError(f"The input {val=} must be a numerical value")
        self.associated_dual_var_constraints.append((utils.Comparator.EQ, val))


@attrs.frozen
class PSDConstraint(Constraint):
    """A :class:`PSDConstraint` object that represents positive semidefinite
    constraints.

    Denote matrices as `X` and `Y`. :class:`PSDConstraint` objects represent:
    `X << Y`, `X >> Y`, and `X = Y`.

    Attributes:
        lhs (np.ndarray | float): The matrix on the left hand side of the relation.
            The np.ndarray is composed of :class:`Scalar` objects.
        rhs (np.ndarray | float): The matrix on the right hand side of the relation.
            The np.ndarray is composed of :class:`Scalar` objects.
        cmp (:class:`Comparator`): :class:`Comparator` is an enumeration
            that can be either `SEQ`, `PEQ`, or `EQ`. They represent `>>`, `<<`,
            or `=` respectively.
        name (str): The unique name of the :class:`Comparator` object.
        associated_dual_var_constraints (list[tuple[:class:`Comparator`, float]]):
            A list of all the constraints imposed on the associated dual
            variable of this :class:`PSDConstraint` object.
    """

    lhs: np.ndarray | float
    rhs: np.ndarray | float
    cmp: utils.Comparator
    name: str

    # Used to represent the constraint on primal variable in dual PEP.
    associated_dual_var_constraints: list[
        tuple[utils.Comparator, np.ndarray | float]
    ] = attrs.field(factory=list)

    def __attrs_post_init__(self):
        if self.cmp not in [
            utils.Comparator.PEQ,
            utils.Comparator.SEQ,
            utils.Comparator.EQ,
        ]:
            raise ValueError("The cmp should be PEQ, SEQ, or EQ.")

        if isinstance(self.lhs, np.ndarray) and isinstance(self.rhs, np.ndarray):
            if not self.lhs.shape == self.rhs.shape:
                raise ValueError("The shape of the lhs should match the rhs.")

    @classmethod
    def make(
        cls: type[PSDConstraint],
        lhs: np.ndarray | float,
        op: str,
        rhs: np.ndarray | float,
        name: str,
    ) -> PSDConstraint:
        """
        A static method to construct a :class:`PSDConstraint` object.

        Args:
            lhs (np.ndarray | float): The np.ndarray object on the
                left hand side of the relation.
            op (str): A `str` which represents the type of relation. Possible options
                are `peq`, `seq`, `eq`, `<<`, `>>`, or `==`.
            rhs (np.ndarray | float): The np.ndarray object on the
                right hand side of the relation.
            name (str): The unique name of the constructed :class:`Comparator` object.
        """
        cmp = utils.Comparator.from_str(op)
        return cls(lhs, rhs, cmp, name)

    def is_compatiable_shape(self, val: np.ndarray | float) -> None:
        """Check that if val is a np.ndarray whether it is of the same shape as the LHS and RHS."""
        if isinstance(self.lhs, np.ndarray) and isinstance(val, np.ndarray):
            if self.lhs.shape != val.shape:
                raise ValueError(
                    "The input must be the same shape as the matrix associated with the LHS of this PSDConstraint."
                )
        elif isinstance(self.rhs, np.ndarray) and isinstance(val, np.ndarray):
            if self.rhs.shape != val.shape:
                raise ValueError(
                    "The input must be the same shape as the matrix associated with the RHS of this PSDConstraint."
                )

    def dual_peq(self, val: np.ndarray | float) -> None:
        """
        Generates a `<<` constraint on the dual variable associated with this
        constraint.

        Denote the associated dual variable of this constraint as `lambd`.
        This generates a relation of the form `lambd << val`.

        Args:
            val (np.ndarray | float): The other object in the relation.
        """
        self.is_compatiable_shape(val)
        self.associated_dual_var_constraints.append((utils.Comparator.PEQ, val))

    def dual_seq(self, val: np.ndarray | float) -> None:
        """
        Generates a `>>` constraint on the dual variable associated with this
        constraint.

        Denote the associated dual variable of this constraint as `lambd`.
        This generates a relation of the form `lambd >> val`.

        Args:
            val (np.ndarray | float): The other object in the relation.
        """
        self.is_compatiable_shape(val)
        self.associated_dual_var_constraints.append((utils.Comparator.SEQ, val))

    def dual_eq(self, val: np.ndarray | float) -> None:
        """
        Generates a `=` constraint on the dual variable associated with this
        constraint.

        Denote the associated dual variable of this constraint as `lambd`.
        This generates a relation of the form `lambd = val`.

        Args:
            val (np.ndarray | float): The other object in the relation.
        """
        self.is_compatiable_shape(val)
        self.associated_dual_var_constraints.append((utils.Comparator.EQ, val))
