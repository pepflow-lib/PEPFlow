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

import functools
import math
from typing import TYPE_CHECKING

import numpy as np
import sympy as sp

from pepflow import parameter as pm
from pepflow import pep_context as pc
from pepflow import scalar as sc
from pepflow import utils
from pepflow import vector as vt

if TYPE_CHECKING:
    from pepflow.utils import NUMERICAL_TYPE


class ExpressionManager:
    """
    A class handling concrete representations of abstract :class:`Vector` and
    :class:`Scalar` objects managed by a particular :class:`PEPContext` object.

    Attributes:
        context (:class:`PEPContext`): The :class:`PEPContext` object which
            manages the abstract :class:`Vector` and :class:`Scalar` objects
            of interest.
        resolve_parameters (dict[str, :data:`NUMERICAL_TYPE`] | `None`): A
            dictionary that maps the name of parameters to the numerical values.
    """

    def __init__(
        self,
        pep_context: pc.PEPContext,
        resolve_parameters: dict[str, NUMERICAL_TYPE] | None = None,
    ):
        self.context = pep_context
        self._basis_vectors = []
        self._basis_vector_uid_to_index = {}
        self._basis_scalars = []
        self._basis_scalar_uid_to_index = {}
        self.resolve_parameters = resolve_parameters or {}
        for vector in self.context.vectors:
            if vector.is_basis:
                self._basis_vectors.append(vector)
                self._basis_vector_uid_to_index[vector.uid] = (
                    len(self._basis_vectors) - 1
                )
        for scalar in self.context.scalars:
            if scalar.is_basis:
                self._basis_scalars.append(scalar)
                self._basis_scalar_uid_to_index[scalar.uid] = (
                    len(self._basis_scalars) - 1
                )

        self._num_basis_vectors = len(self._basis_vectors)
        self._num_basis_scalars = len(self._basis_scalars)

    def get_index_of_basis_vector(self, vector: vt.Vector) -> int:
        return self._basis_vector_uid_to_index[vector.uid]

    def get_index_of_basis_scalar(self, scalar: sc.Scalar) -> int:
        return self._basis_scalar_uid_to_index[scalar.uid]

    def get_tag_of_basis_vector_index(self, index: int) -> str:
        return self._basis_vectors[index].__repr__()

    def get_tag_of_basis_scalar_index(self, index: int) -> str:
        return self._basis_scalars[index].__repr__()

    @functools.cache
    def eval_vector(
        self, vector: vt.Vector | pm.Parameter | float | int, sympy_mode: bool = False
    ):
        """
        Return the concrete representation of the :class:`Vector`, :class:`Parameter`,
        `float`, or `int`.

        Concrete representations of :class:`Vector` objects are
        :class:`EvaluatedVector` objects. Concrete representations of `float` or `int`
        arguments are themselves. If a :class:`Parameter` object is passed in, the
        function will return the corresponding value stored in `resolve_parameters`.

        Args:
            vector (:class:`Vector`, :class:`Parameter`, float, int): The abstract
                :class:`Vector`, :class:`Parameter`, `float`, or `int` object whose
                concrete representation we want to find.
            sympy_mode (bool): If true, then the input should be defined completely
                in terms of SymPy objects and should not mix Python numeric objects.
                Will raise an error if sympy_mode is `True` and the input contains a
                Python numeric object. By default `False`.
        Returns:
            :class:`EvaluatedVector` | float | int: The concrete representation of
            the `vector` argument.

        Example:
            >>> import pepflow as pf
            >>> import numpy as np
            >>> ctx = pf.PEPContext("ctx").set_as_current()
            >>> f = pf.SmoothConvexFunction(is_basis=True, tags=["f"], L=1)
            >>> x_0 = pf.Vector(is_basis=True, tags=["x_0"])
            >>> pm.eval_vector(x_0).coords == np.array([1])
        """
        if sympy_mode and isinstance(vector, float):
            raise ValueError(
                f"Encountered a floating number {vector} when evaluating a vector in sympy_mode."
                " In order to use sympy mode, please convert every floating number into a"
                " sympy.Rational value. For example, convert 1/2 into sympy.S(1)/2."
            )

        if utils.is_numerical(vector):
            return vector
        if isinstance(vector, pm.Parameter):
            return vector.get_value(self.resolve_parameters)
        if not isinstance(vector, vt.Vector):
            raise ValueError(
                f"Encountered unknown type of vector to evaluate with: {type(vector)=}"
            )

        if vector.is_basis:
            index = self.get_index_of_basis_vector(vector)
            array = np.zeros(self._num_basis_vectors)
            if sympy_mode:
                array = array * sp.S(0)
            array[index] = sp.S(1) if sympy_mode else 1
            return vt.EvaluatedVector(coords=array)
        assert vector.eval_expression is not None  # To make typecheck happy

        assert vector.eval_expression is not None  # To make typecheck happy

        if isinstance(vector.eval_expression, vt.ZeroVector):
            return vt.EvaluatedVector.zero(
                num_basis_vectors=self._num_basis_vectors, sympy_mode=sympy_mode
            )
        # TODO: add test for this
        if isinstance(vector.eval_expression, vt.VectorByBasisRepresentation):
            array = np.zeros(self._num_basis_vectors)
            if sympy_mode:
                array = array * sp.S(0)
            for basis_vector, coef in vector.eval_expression.coeffs.items():
                index = self.get_index_of_basis_vector(basis_vector)
                array[index] += self.eval_vector(coef)  # we may need to resolve coef.
            return vt.EvaluatedVector(coords=array)

        op = vector.eval_expression.op
        left_evaled_vector = self.eval_vector(
            vector.eval_expression.left_vector, sympy_mode=sympy_mode
        )
        right_evaled_vector = self.eval_vector(
            vector.eval_expression.right_vector, sympy_mode=sympy_mode
        )
        if op == utils.Op.ADD:
            return left_evaled_vector + right_evaled_vector
        if op == utils.Op.SUB:
            return left_evaled_vector - right_evaled_vector
        if op == utils.Op.MUL:
            return left_evaled_vector * right_evaled_vector
        if op == utils.Op.DIV:
            return left_evaled_vector / right_evaled_vector

        raise ValueError(f"Encountered unknown {op=} when evaluation the vector.")

    @functools.cache
    def eval_scalar(
        self, scalar: sc.Scalar | pm.Parameter | float | int, sympy_mode: bool = False
    ):
        """
        Return the concrete representation of the :class:`Scalar`, :class:`Parameter`,
        `float`, or `int`.

        Concrete representations of :class:`Scalar` objects are
        :class:`EvaluatedScalar` objects. Concrete representations of `float` or `int`
        arguments are themselves. If a :class:`Parameter` object is passed in, the
        function will return the corresponding value stored in `resolve_parameters`.

        Args:
            scalar (:class:`Scalar`, :class:`Parameter`, float, int): The abstract
                :class:`Scalar`, :class:`Parameter`, `float`, or `int` object whose
                concrete representation we want to find.
            sympy_mode (bool): If true, then the input should be defined completely
                in terms of SymPy objects and should not mix Python numeric objects.
                Will raise an error if sympy_mode is `True` and the input contains a
                Python numeric object. By default `False`.

        Returns:
            :class:`EvaluatedScalar` | float | int: The concrete representation of
            the `scalar` argument.

        Example:
            >>> import pepflow as pf
            >>> import numpy as np
            >>> ctx = pf.PEPContext("ctx").set_as_current()
            >>> f = pf.SmoothConvexFunction(is_basis=True, tags=["f"], L=1)
            >>> x_0 = pf.Vector(is_basis=True, tags=["x_0"])
            >>> f_0 = f(x_0)
            >>> pm = pf.ExpressionManager(ctx)
            >>> pm.eval_scalar(f_0).func_coords == np.array([1, 0])
            >>> pm.eval_scalar(x_0**2).inner_prod_coords == np.array([[1, 0], [0, 0]])
        """
        if sympy_mode and isinstance(scalar, float):
            raise ValueError(
                f"Encountered a floating number {scalar} when evaluating a scalar in sympy_mode."
                " In order to use sympy mode, please convert every floating number into a"
                " sympy.Rational value. For example, convert 1/2 into sympy.S(1)/2."
            )

        if utils.is_numerical(scalar):
            return scalar
        if isinstance(scalar, pm.Parameter):
            return scalar.get_value(self.resolve_parameters)
        if not isinstance(scalar, sc.Scalar):
            raise ValueError(
                f"Encounter unknown type of scalar to evaludated with: {type(scalar)=}"
            )

        if scalar.is_basis:
            index = self.get_index_of_basis_scalar(scalar)
            array = np.zeros(self._num_basis_scalars)
            if sympy_mode:
                array = array * sp.S(0)
            array[index] = sp.S(1) if sympy_mode else 1
            matrix = np.zeros((self._num_basis_vectors, self._num_basis_vectors))
            if sympy_mode:
                matrix = matrix * sp.S(0)
            return sc.EvaluatedScalar(
                func_coords=array,
                inner_prod_coords=matrix,
                offset=sp.S(0) if sympy_mode else float(0.0),
            )
        assert scalar.eval_expression is not None  # To make typecheck happy

        if isinstance(scalar.eval_expression, sc.ZeroScalar):
            return sc.EvaluatedScalar.zero(
                num_basis_scalars=self._num_basis_scalars,
                num_basis_vectors=self._num_basis_vectors,
                sympy_mode=sympy_mode,
            )

        op = scalar.eval_expression.op
        # The special inner product usage.
        if (
            op == utils.Op.MUL
            and isinstance(scalar.eval_expression.left_scalar, vt.Vector)
            and isinstance(scalar.eval_expression.right_scalar, vt.Vector)
        ):
            array = (
                np.zeros(self._num_basis_scalars) * sp.S(0)
                if sympy_mode
                else np.zeros(self._num_basis_scalars)
            )
            return sc.EvaluatedScalar(
                func_coords=array,
                inner_prod_coords=utils.SOP(
                    self.eval_vector(
                        scalar.eval_expression.left_scalar, sympy_mode=sympy_mode
                    ).coords,
                    self.eval_vector(
                        scalar.eval_expression.right_scalar, sympy_mode=sympy_mode
                    ).coords,
                    sympy_mode=sympy_mode,
                ),
                offset=sp.S(0) if sympy_mode else float(0.0),
            )

        left_evaled_scalar = self.eval_scalar(
            scalar.eval_expression.left_scalar, sympy_mode=sympy_mode
        )
        right_evaled_scalar = self.eval_scalar(
            scalar.eval_expression.right_scalar, sympy_mode=sympy_mode
        )
        if op == utils.Op.ADD:
            return left_evaled_scalar + right_evaled_scalar
        if op == utils.Op.SUB:
            return left_evaled_scalar - right_evaled_scalar
        if op == utils.Op.MUL:
            return left_evaled_scalar * right_evaled_scalar
        if op == utils.Op.DIV:
            return left_evaled_scalar / right_evaled_scalar

        raise ValueError(f"Encountered unknown {op=} when evaluation the scalar.")

    @functools.cache
    def repr_vector_by_basis(
        self, vector: vt.Vector, *, sympy_mode: bool = False
    ) -> str:
        """
        Express the :class:`Vector` object as the linear combination of
        the basis :class:`Vector` objects of the associated :class:`PEPContext`.

        This linear combination is expressed as a `str`.

        Args:
            vector (:class:`Vector`): The :class:`Vector` object which we want
                to express in terms of the basis :class:`Vector` objects.
            sympy_mode (bool): If true, then the input should be defined completely
                in terms of SymPy objects and should not mix Python numeric objects.
                Will raise an error if sympy_mode is `True` and the input contains a
                Python numeric object. By default `False`.

        Returns:
            str: The representation of `vector` in terms of the basis
            :class:`Vector` objects of the :class:`PEPContext` associated
            with this :class:`ExpressionManager`.
        """
        assert isinstance(vector, vt.Vector)
        evaluated_vector = self.eval_vector(vector, sympy_mode=sympy_mode)
        return self.repr_evaluated_vector_by_basis(evaluated_vector)

    def repr_evaluated_vector_by_basis(
        self, evaluated_vector: vt.EvaluatedVector
    ) -> str:
        """
        Express the :class:`EvaluatedVector` object as the linear combination of
        the basis :class:`Vector` objects of the associated :class:`PEPContext`.

        This linear combination is expressed as a `str`.

        Args:
            evaluated_vector (:class:`EvaluatedVector`): The
                :class:`EvaluatedVector` object which we want to express in
                terms of the basis :class:`Vector` objects.

        Returns:
            str: The representation of `evaluated_vector` in terms of
            the basis :class:`Vector` objects of the :class:`PEPContext`
            associated with this :class:`ExpressionManager`.
        """
        repr_str = ""
        for i, v in enumerate(evaluated_vector.coords):
            ith_tag = self.get_tag_of_basis_vector_index(i)
            repr_str += utils.tag_and_coef_to_str(ith_tag, v)

        # Post processing
        if repr_str == "":
            return "0"
        if repr_str.startswith("+ "):
            repr_str = repr_str[2:]
        if repr_str.startswith("- "):
            repr_str = "-" + repr_str[2:]
        return repr_str.strip()

    @functools.cache
    def repr_scalar_by_basis(
        self,
        scalar: sc.Scalar,
        *,
        greedy_square: bool = False,
        sympy_mode: bool = False,
    ) -> str:
        """Express the :class:`Scalar` object using the basis :class:`Vector`
        and :class:`Scalar` objects of the associated :class:`PEPContext`.

        A :class:`Scalar` can be formed by linear combinations of basis
        :class:`Scalar` objects. A :class:`Scalar` can also be formed through
        the inner product of two basis :class:`Vector` objects. This function
        returns the representation of this :class:`Scalar` object in terms of
        the basis :class:`Vector` and :class:`Scalar` objects as a `str`.

        Args:
            scalar (:class:`Scalar`): The :class:`Scalar` object which we want
                to express in terms of the basis :class:`Vector` and
                :class:`Scalar` objects.
            greedy_square (bool): If `greedy_square` is true, the function will
                try to return :math:`\\|a-b\\|^2` whenever possible. If not,
                the function will return
                :math:`\\|a\\|^2 - 2 * \\langle a, b \\rangle + \\|b\\|^2` instead.
                `True` by default.
            sympy_mode (bool): If true, then the input should be defined completely
                in terms of SymPy objects and should not mix Python numeric objects.
                Will raise an error if sympy_mode is `True` and the input contains a
                Python numeric object. By default `False`.

        Returns:
            str: The representation of `scalar` in terms of the basis :class:`Vector`
            and :class:`Scalar` objects of the :class:`PEPContext` associated with this
            :class:`ExpressionManager`.
        """
        assert isinstance(scalar, sc.Scalar)
        evaluated_scalar = self.eval_scalar(scalar, sympy_mode=sympy_mode)
        return self.repr_evaluated_scalar_by_basis(
            evaluated_scalar, greedy_square=greedy_square
        )

    def repr_evaluated_scalar_by_basis(
        self, evaluated_scalar: sc.EvaluatedScalar, greedy_square: bool = False
    ) -> str:
        """Express the :class:`EvaluatedScalar` object using the basis :class:`Vector`
        and :class:`Scalar` objects of the associated :class:`PEPContext`.

        A :class:`Scalar` can be formed by linear combinations of basis
        :class:`Scalar` objects. A :class:`Scalar` can also be formed through
        the inner product of two basis :class:`Vector` objects. This function
        returns the representation of this :class:`Scalar` object in terms of
        the basis :class:`Vector` and :class:`Scalar` objects as a `str`.

        Args:
            evaluated_scalar (:class:`EvaluatedScalar`): The
                :class:`EvaluatedScalar` object which we want to express in
                terms of the basis :class:`Vector` and :class:`Scalar` objects.
            greedy_square (bool): If `greedy_square` is true, the function will
                try to return :math:`\\|a-b\\|^2` whenever possible. If not,
                the function will return
                :math:`\\|a\\|^2 - 2 * \\langle a, b \\rangle + \\|b\\|^2` instead.
                `True` by default.

        Returns:
            str: The representation of `evaluated_scalar` in terms of
            the basis :class:`Vector` and :class:`Scalar` objects of the
            :class:`PEPContext` associated with this :class:`ExpressionManager`.
        """
        repr_str = ""
        if not math.isclose(evaluated_scalar.offset, 0, abs_tol=1e-5):
            repr_str += utils.numerical_str(evaluated_scalar.offset)

        for i, v in enumerate(evaluated_scalar.func_coords):
            # Note the tag is from scalar basis.
            ith_tag = self.get_tag_of_basis_scalar_index(i)
            repr_str += utils.tag_and_coef_to_str(ith_tag, v)

        if greedy_square:
            diag_elem = np.diag(evaluated_scalar.inner_prod_coords).copy()
            for i in range(evaluated_scalar.inner_prod_coords.shape[0]):
                ith_tag = self.get_tag_of_basis_vector_index(i)
                # j starts from i+1 since we want to handle the diag elem at last.
                for j in range(i + 1, evaluated_scalar.inner_prod_coords.shape[0]):
                    jth_tag = self.get_tag_of_basis_vector_index(j)
                    v = evaluated_scalar.inner_prod_coords[i, j]
                    # We want to minimize the diagonal elements to zero greedily.
                    if diag_elem[i] * v > 0:  # same sign with diagonal elem
                        diag_elem[i] -= v
                        diag_elem[j] -= v
                        repr_str += utils.tag_and_coef_to_str(
                            f"|{ith_tag}+{jth_tag}|^2", v
                        )
                    else:  # different sign
                        diag_elem[i] += v
                        diag_elem[j] += v
                        repr_str += utils.tag_and_coef_to_str(
                            f"|{ith_tag}-{jth_tag}|^2", -v
                        )
                # Handle the diagonal elements
                repr_str += utils.tag_and_coef_to_str(f"|{ith_tag}|^2", diag_elem[i])
        else:
            for i in range(evaluated_scalar.inner_prod_coords.shape[0]):
                ith_tag = self.get_tag_of_basis_vector_index(i)
                for j in range(i, evaluated_scalar.inner_prod_coords.shape[0]):
                    jth_tag = self.get_tag_of_basis_vector_index(j)
                    v = evaluated_scalar.inner_prod_coords[i, j]
                    if i == j:
                        repr_str += utils.tag_and_coef_to_str(f"|{ith_tag}|^2", v)
                    else:
                        repr_str += utils.tag_and_coef_to_str(
                            f"⟨{ith_tag}, {jth_tag}⟩", 2 * v
                        )

        # Post processing
        if repr_str == "":
            return "0"
        if repr_str.startswith("+ "):
            repr_str = repr_str[2:]
        if repr_str.startswith("- "):
            repr_str = "-" + repr_str[2:]
        return repr_str.strip()


def represent_matrix_by_basis(
    matrix: np.ndarray, ctx: pc.PEPContext, greedy_square: bool = False
) -> str:
    """Express the `matrix` in terms of the basis :class:`Vector` objects
    of the :class:`PEPContext`.

    The concrete representation of the inner product of two abstract
    basis :class:`Vector` objects is a matrix (the outer product of the
    basis vectors corresponding to the concrete representations of the abstract
    basis :class:`Vector` objects). The matrix can then be expressed
    as a linear combination of the inner products of abstract basis
    :class:`Vector` objects. This is provided as a `str`.

    Args:
        matrix (np.ndarray): The matrix which we want to express in terms of
            the basis :class:`Vector` objects of the :class:`PEPContext`.
        ctx (:class:`PEPContext`): The :class:`PEPContext` whose basis
            :class:`Vector` objects we consider.
        greedy_square (bool): If `greedy_square` is true, the function will
            try to return :math:`\\|a-b\\|^2` whenever possible. If not,
            the function will return
            :math:`\\|a\\|^2 - 2 * \\langle a, b \\rangle + \\|b\\|^2` instead.
            `True` by default.

    Returns:
        str: The representation of `matrix` in terms of the basis
        :class:`Vector` objects of `ctx`.

    Example:
        >>> x_1 = vt.Vector(is_basis=True, tags=["x_1"])
        >>> x_2 = vt.Vector(is_basis=True, tags=["x_2"])
        >>> x_3 = vt.Vector(is_basis=True, tags=["x_3"])
        >>> matrix = np.array([[0.5, 0.5, 0], [0.5, 2, 0], [0, 0, 3]])
        >>> exm.represent_matrix_by_basis(matrix, pep_context, greedy_square=True)
    """
    em = ExpressionManager(ctx)
    matrix_shape = (len(em._basis_vectors), len(em._basis_vectors))
    if matrix.shape != matrix_shape:
        raise ValueError(
            "The valid matrix for given context should have shape {matrix_shape}"
        )
    if not np.allclose(matrix, matrix.T):
        raise ValueError("Input matrix must be symmetric.")

    return em.repr_evaluated_scalar_by_basis(
        sc.EvaluatedScalar(
            func_coords=np.zeros(len(em._basis_scalars)),
            inner_prod_coords=matrix,
            offset=0.0,
        ),
        greedy_square=greedy_square,
    )
