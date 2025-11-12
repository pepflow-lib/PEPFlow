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

import warnings

import cvxpy
import numpy as np

from pepflow import constants
from pepflow import constraint as ctr
from pepflow import expression_manager as exm
from pepflow import pep_context as pc
from pepflow import scalar as sc
from pepflow import utils

warnings.filterwarnings(
    "ignore",
    message=".*compressed sparse column.*",
    category=UserWarning,
)


def evaled_scalar_to_cvx_express(
    eval_scalar: sc.EvaluatedScalar, vec_var: cvxpy.Variable, matrix_var: cvxpy.Variable
) -> cvxpy.Expression:
    return (
        vec_var @ eval_scalar.func_coords
        + cvxpy.trace(matrix_var @ eval_scalar.inner_prod_coords)
        + eval_scalar.offset
    )


class PrimalPEPDualVarManager:
    """
    A class to access the dual variables associated with the constraints
    of the Primal PEP.

    Should not be instantiated directly. Automatically
    generated as a member variable of the :class:`PEPResult` object
    returned when calling :py:func:`pepflow.PEPBuilder.solve_primal`.
    """

    # It is used in the primal PEP to get the dual variables.
    def __init__(self, named_constraints: list[tuple[str, cvxpy.Constraint]]):
        self.named_constraints = {}
        for name, c in named_constraints:
            self.add_constraint(name, c)

    def cvx_constraints(self) -> list[cvxpy.Constraint]:
        return list(self.named_constraints.values())

    def clear(self) -> None:
        self.named_constraints.clear()

    def add_constraint(self, name: str, constraint: cvxpy.Constraint) -> None:
        if name in self.named_constraints:
            raise KeyError(f"There is already a constraint named {name}")
        self.named_constraints[name] = constraint

    def dual_value(self, name: str) -> float | None:
        """
        Given the name of a :class:`Constraint` object representing a constraint in
        Primal PEP, return the value of its corresponding dual variable.

        Args:
            name (str): The name of the :class:`Constraint` object whose
                associated dual variable we want to retrieve.

        Returns:
            float: The value of the dual variable corresponding to the
            :class:`Constraint` object associated with the `name` argument.
        """
        if name not in self.named_constraints:
            return None  # Is this good choice?
        dual_value = self.named_constraints[name].dual_value
        if dual_value is None:
            return None
        return dual_value


class DualPEPDualVarManager:
    """
    A class to access the dual variables associated with the constraints
    of Primal PEP after solving Dual PEP.

    Should not be instantiated
    directly. Automatically generated as a member variable of the
    :class:`PEPResult` object returned when calling
    :py:func:`pepflow.PEPBuilder.solve_dual`.
    """

    # It is used in the dual PEP to get the dual variables.
    def __init__(self, named_variables: list[tuple[str, cvxpy.Variable]]):
        self.named_variables = {}
        for name, v in named_variables:
            self.add_variable(name, v)

    def cvx_variables(self) -> list[cvxpy.Variable]:
        return list(self.named_variables.values())

    def clear(self) -> None:
        self.named_variables.clear()

    def add_variable(self, name: str, variable: cvxpy.Variable) -> None:
        if name in self.named_variables:
            raise KeyError(f"There is already a variable named {name}")
        self.named_variables[name] = variable

    def get_variable(self, name: str) -> cvxpy.Variable:
        if name not in self.named_variables:
            raise KeyError(f"Cannot find a variable named {name}")
        return self.named_variables[name]

    def dual_value(self, name: str) -> float | None:
        """
        Given the name of a :class:`Constraint` object representing a constraint in the
        Primal PEP, return the value of its corresponding dual variable.

        Args:
            name (str): The name of the :class:`Constraint` object whose
                corresponding dual variable we want to retrieve.

        Returns:
            float: The value of the dual variable corresponding to the
            :class:`Constraint` object associated with the `name` argument.
        """
        if name not in self.named_variables:
            return None  # Is this good choice?
        dual_value = self.named_variables[name].value
        if dual_value is None:
            return None
        return dual_value


class CVXPrimalSolver:
    def __init__(
        self,
        perf_metric: sc.Scalar,
        constraints: list[ctr.Constraint],
        context: pc.PEPContext,
    ):
        self.perf_metric = perf_metric
        self.constraints = constraints
        self.dual_var_manager = PrimalPEPDualVarManager([])
        self.context = context

    def build_problem(
        self, resolve_parameters: dict[str, utils.NUMERICAL_TYPE] | None = None
    ) -> cvxpy.Problem:
        em = exm.ExpressionManager(self.context, resolve_parameters=resolve_parameters)
        f_var = cvxpy.Variable(em._num_basis_scalars)
        g_var = cvxpy.Variable(
            (em._num_basis_vectors, em._num_basis_vectors), symmetric=True
        )

        # Evaluate all points and scalars in advance to store it in cache.
        for vector in self.context.vectors:
            em.eval_vector(vector)
        for scalar in self.context.scalars:
            em.eval_scalar(scalar)

        self.dual_var_manager.clear()
        self.dual_var_manager.add_constraint(constants.PSD_CONSTRAINT, g_var >> 0)
        for c in self.constraints:
            if isinstance(c, ctr.ScalarConstraint):
                exp = evaled_scalar_to_cvx_express(
                    em.eval_scalar(c.lhs - c.rhs), f_var, g_var
                )
                if c.cmp == utils.Comparator.GE:
                    self.dual_var_manager.add_constraint(c.name, exp >= 0)
                elif c.cmp == utils.Comparator.LE:
                    self.dual_var_manager.add_constraint(c.name, exp <= 0)
                elif c.cmp == utils.Comparator.EQ:
                    self.dual_var_manager.add_constraint(c.name, exp == 0)
                else:
                    raise ValueError(f"Unknown comparator {c.cmp}")
            if isinstance(c, ctr.PSDConstraint):
                mat_of_scalars = c.lhs - c.rhs
                mat_of_cvx_constrs = np.empty(
                    mat_of_scalars.shape,  # ty: ignore
                    dtype=cvxpy.Expression,
                )
                for i, j in np.ndindex(mat_of_cvx_constrs.shape):
                    mat_of_cvx_constrs[i, j] = evaled_scalar_to_cvx_express(
                        em.eval_scalar(mat_of_scalars[i, j]),  # ty: ignore
                        f_var,
                        g_var,
                    )
                if c.cmp == utils.Comparator.SEQ:
                    self.dual_var_manager.add_constraint(
                        c.name, cvxpy.bmat(mat_of_cvx_constrs) >> 0
                    )
                elif c.cmp == utils.Comparator.PEQ:
                    self.dual_var_manager.add_constraint(
                        c.name, cvxpy.bmat(mat_of_cvx_constrs) << 0
                    )
                elif c.cmp == utils.Comparator.EQ:
                    self.dual_var_manager.add_constraint(
                        c.name, cvxpy.bmat(mat_of_cvx_constrs) == 0
                    )
                else:
                    raise ValueError(f"Unknown comparator {c.cmp}")
        obj = evaled_scalar_to_cvx_express(
            em.eval_scalar(self.perf_metric), f_var, g_var
        )

        return cvxpy.Problem(
            cvxpy.Maximize(obj), self.dual_var_manager.cvx_constraints()
        )

    def solve(self, **kwargs):
        problem = self.build_problem()
        result = problem.solve(**kwargs)
        return result


class CVXDualSolver:
    def __init__(
        self,
        perf_metric: sc.Scalar,
        constraints: list[ctr.Constraint],
        context: pc.PEPContext,
    ):
        self.perf_metric = perf_metric
        self.constraints = constraints
        self.dual_var_manager = DualPEPDualVarManager([])
        self.context = context

    def build_problem(
        self, resolve_parameters: dict[str, utils.NUMERICAL_TYPE] | None = None
    ) -> cvxpy.Problem:
        # The primal problem is always the following form:
        #
        # max_{F, G}:  <perf.vec, F> + Tr(G perf.Mat) + perf.const
        # s.t.         <constraint.vec, F> + Tr(G constraint.Mat) + constraint.const <= 0
        #              [scalar_{m, n}]_[M, N] >= 0 (PSD constraint)
        #              G >= 0
        # Caveat: we use max instead of min in primal problem.
        # Note the PSD constraint can be converted in terms of F and G when expanding scalar_{m, n}.
        # We use tensor and Einstein notation here:
        # Suppose scalar_{m, n} = F_i Vec^i_{m, n} + G_{i, j} Mat^{i, j}_{m, n} + C
        # where Vec is a rank-3 tensor and DM is a rank-4 tensor
        # TMat^{i, j}_{m, n} is the (i, j)-th element of inner_prod_matrix of (m, n) scalar.abs
        # TVec^{i}_{m, n} is the (i)-th element of func_coord of (m, n) scalar.
        # Then [scalar_{m, n}]_[M, N] = F_i TVec^i + G_{i, j} TMat^{i, j} + TC
        #
        # So the canonical form is
        # max_{F, G}:  <perf.vec, F> + Tr(G perf.Mat) + perf.const
        # s.t.         <constraint.vec, F> + Tr(G constraint.Mat) + constraint.const <= 0
        #              F_i TVec^i_{m, n} + G_{i, j} TMat^{i, j}_{m, n} + TC >= 0 (PSD constraint)
        #              G >= 0
        # Dual prob = min_{l, S, P} [max_{F, G} (<perf.vec, F> + Tr(G perf.Mat) - l * (constraint) + Tr(S*G))
        #                         + Tr(P * (F_i TVec^i_{m, n} + G_{i, j} TMat^{i, j}_{m, n} + TC))]
        # Note the sign above.
        # Because F is unbounded and the Lagrangian w.r.t. F is linear, the coefficients of F must be 0.
        # Similarly, the Lagrangian w.r.t. G is linear and G is PSD, the coefficients of G must << 0.
        dual_constraints = []
        lambd_constraints = []
        em = exm.ExpressionManager(self.context, resolve_parameters=resolve_parameters)
        # The one corresponding to G >= 0
        S = cvxpy.Variable((em._num_basis_vectors, em._num_basis_vectors), PSD=True)
        self.dual_var_manager.add_variable(constants.PSD_CONSTRAINT, S)
        evaled_perf_metric_scalar = em.eval_scalar(self.perf_metric)

        extra_constraints = []
        obj = evaled_perf_metric_scalar.offset
        F_coef_vec = 0
        G_coef_mat = 0
        F_coef_vec_PSD = 0
        G_coef_mat_PSD = 0
        # l * (Tr(G*eval_s.Matrix) + <F, eval_s.vec> + eval_s.const)
        for c in self.constraints:
            if isinstance(c, ctr.ScalarConstraint):
                lambd = cvxpy.Variable()
                self.dual_var_manager.add_variable(c.name, lambd)
                evaled_scalar = em.eval_scalar(c.lhs - c.rhs)
                if c.cmp == utils.Comparator.GE:
                    sign = 1
                    lambd_constraints.append(lambd >= 0)
                elif c.cmp == utils.Comparator.LE:
                    sign = -1  # We flip f(x) <=0  into -f(x) >= 0
                    lambd_constraints.append(lambd >= 0)
                elif c.cmp == utils.Comparator.EQ:
                    sign = 1
                else:
                    raise RuntimeError(
                        f"Unknown comparator in constraint {c.name}: get {c.cmp=}"
                    )
                G_coef_mat += sign * lambd * evaled_scalar.inner_prod_coords
                F_coef_vec += sign * lambd * evaled_scalar.func_coords
                obj += sign * lambd * evaled_scalar.offset

                # We can add extra constraints to directly manipulate the dual variables in dual PEP.
                for cmp, val in c.associated_dual_var_constraints:
                    if cmp == utils.Comparator.GE:
                        extra_constraints.append(lambd >= val)
                    elif cmp == utils.Comparator.LE:
                        extra_constraints.append(lambd <= val)
                    elif cmp == utils.Comparator.EQ:
                        extra_constraints.append(lambd == val)
                    else:
                        raise RuntimeError(
                            f"Unknown comparator in constraint {c.name} associated dual one:"
                            f"get {cmp=}"
                        )

            if isinstance(c, ctr.PSDConstraint):
                # TODO: Check the performance in the future.
                mat_of_scalars = c.lhs - c.rhs
                P = cvxpy.Variable(mat_of_scalars.shape, PSD=True)  # ty: ignore
                self.dual_var_manager.add_variable(c.name, P)
                mat_of_eval_scalars = np.empty(
                    mat_of_scalars.shape,  # ty: ignore
                    dtype=sc.EvaluatedScalar,
                )
                for i, j in np.ndindex(mat_of_scalars.shape):  # ty: ignore
                    mat_of_eval_scalars[i, j] = em.eval_scalar(mat_of_scalars[i, j])  # ty: ignore
                c_F_mat = np.empty(em._num_basis_scalars, dtype=cvxpy.Expression)
                for i in range(c_F_mat.size):
                    block_matrix = np.zeros(mat_of_scalars.shape)  # ty: ignore
                    for r_idx, c_idx in np.ndindex(block_matrix.shape):
                        block_matrix[r_idx, c_idx] = mat_of_eval_scalars[
                            r_idx, c_idx
                        ].func_coords[i]
                    c_F_mat[i] = cvxpy.trace(P @ block_matrix)
                c_G_mat = np.empty(
                    (em._num_basis_vectors, em._num_basis_vectors),
                    dtype=cvxpy.Expression,
                )
                for i, j in np.ndindex(c_G_mat.shape):
                    block_matrix = np.zeros(mat_of_scalars.shape)  # ty: ignore
                    for r_idx, c_idx in np.ndindex(block_matrix.shape):
                        block_matrix[r_idx, c_idx] = mat_of_eval_scalars[
                            r_idx, c_idx
                        ].inner_prod_coords[i, j]
                    c_G_mat[i, j] = cvxpy.trace(P @ block_matrix)

                block_matrix = np.zeros(mat_of_scalars.shape)  # ty: ignore
                for i, j in np.ndindex(block_matrix.shape):
                    block_matrix[i, j] = mat_of_eval_scalars[i, j].offset
                c_offset = cvxpy.trace(P @ block_matrix)

                if c.cmp == utils.Comparator.SEQ:
                    sign = 1
                elif c.cmp == utils.Comparator.PEQ:
                    sign = -1  # We flip f(x) <=0  into -f(x) >= 0
                elif c.cmp == utils.Comparator.EQ:
                    sign = 1
                else:
                    raise RuntimeError(
                        f"Unknown comparator in constraint {c.name}: get {c.cmp=}"
                    )
                G_coef_mat_PSD += sign * cvxpy.bmat(c_G_mat)
                F_coef_vec_PSD += sign * cvxpy.hstack(c_F_mat)
                obj += sign * c_offset

                # We can add extra constraints to directly manipulate the dual variables in dual PEP.
                for cmp, val in c.associated_dual_var_constraints:
                    if cmp == utils.Comparator.SEQ:
                        extra_constraints.append(P >> val)
                    elif cmp == utils.Comparator.PEQ:
                        extra_constraints.append(P << val)
                    elif cmp == utils.Comparator.EQ:
                        extra_constraints.append(P == val)
                    else:
                        raise RuntimeError(
                            f"Unknown comparator in constraint {c.name} associated dual one:"
                            f"get {cmp=}"
                        )

        dual_constraints.append(
            F_coef_vec + F_coef_vec_PSD + evaled_perf_metric_scalar.func_coords == 0
        )
        dual_constraints.append(
            S
            + evaled_perf_metric_scalar.inner_prod_coords
            + G_coef_mat
            + G_coef_mat_PSD
            == 0
        )

        return cvxpy.Problem(
            cvxpy.Minimize(obj),
            dual_constraints + lambd_constraints + extra_constraints,
        )

    def solve(self, **kwargs):
        problem = self.build_problem()
        result = problem.solve(**kwargs)
        return result
