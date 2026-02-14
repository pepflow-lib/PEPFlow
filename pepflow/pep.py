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

from collections import defaultdict
from typing import TYPE_CHECKING

from pepflow import pep_context as pc
from pepflow import pep_result as pr
from pepflow import scalar as sc
from pepflow import solver as ps
from pepflow import utils
from pepflow import vector as vt
from pepflow.constraint import Constraint, PSDConstraint, ScalarConstraint

if TYPE_CHECKING:
    from pepflow.pep_context import PEPContext
    from pepflow.utils import NUMERICAL_TYPE


class PEPBuilder:
    """The main class for Primal and Dual PEP formulation.

    Attributes:
        ctx (:class:`PEPContext`): The :class:`PEPContext` associated
            with this :class:`PEPBuilder` object.
        init_conditions (list[:class:`PSDConstraint` | :class:`ScalarConstraint`]): A
            list of all the initial conditions associated with this PEP.
        performance_metric (:class:`Scalar`): The performance metric for this
            PEP.
        relaxed_constraints (list[str]): A list of names of the constraints
            that will be ignored when the Primal or Dual PEP is constructed.
        dual_val_constraint (dict[str, list[tuple[str, float]]]): A dictionary
            of the form `{constraint_name: [(op, val)]}`. The `constraint_name`
            is the name of the constraint the dual variable is associated with.
            The `op` is a string for the type of relation, i.e., `le`, `ge`,
            `eq`, `<=`, `>=`, or `==`. The `val` is the value for the
            other side of the constraint. For example, consider
            `{"f:x_1,x_0", [("eq", 0)]}`. Denote the associated dual variable
            as :math:`\\lambda_{1,0}`. Then, this means to add a constraint
            of the form :math:`\\lambda_{1,0} = 0` to the Dual PEP.
            Because it is hard to judge if the constraint associated
            with `constraint_name` is active, we suggest to not add dual
            variable constraints manually but instead use the interactive
            dashboard.

    Example:
        >>> pep_builder = pf.PEPBuilder(ctx)
    """

    def __init__(self, pep_context: pc.PEPContext):
        self.ctx: pc.PEPContext = pep_context
        self.init_conditions: list[PSDConstraint | ScalarConstraint] = []
        self.performance_metric: sc.Scalar | None = None

        # Contain the name for the constraints that should be removed.
        # We should think about a better choice like manager.
        self.relaxed_constraints: list[str] = []

        # `dual_val_constraint` has the data structure: {constraint_name: [op, val]}.
        # Because it is hard to judge if the dual_val_constraint is applied or not,
        # we recommend to not use this object directly but through the interactive dashboard.
        self.dual_val_constraint: dict[str, list[tuple[str, float]]] = defaultdict(list)

    def clear_setup(self):
        """Resets the :class:`PEPBuilder` object. Does not reset the `ctx` attribute."""
        self.init_conditions.clear()
        self.performance_metric = None
        self.relaxed_constraints.clear()
        self.dual_val_constraint.clear()

    def add_init_point(self, tag: str) -> vt.Vector:
        point = vt.Vector(is_basis=True)
        point.add_tag(tag)
        return point

    def add_initial_constraint(self, constraint: PSDConstraint | ScalarConstraint):
        """
        Add an initial condition.

        Args:
            constraint (:class:`PSDConstraint` | :class:`ScalarConstraint`): A
                :class:`PSDConstraint` or :class:`ScalarConstraint` object that
                represents the desired initial condition.

        Example:
            >>> import pepflow as pf
            >>> f = pf.SmoothConvexFunction(is_basis=True, tags=["f"], L=1)
            >>> ctx = pf.PEPContext("ctx").set_as_current()
            >>> x = pf.Vector(is_basis=True, tags=["x_0"])
            >>> x_star = f.set_stationary_point("x_star")
            >>> pb = pf.PEPBuilder(ctx)
            >>> pb.add_initial_constraint(
            ...     ((x_0 - x_star) ** 2).le(R**2, name="initial_condition")
            ... )
        """
        # TODO: Add unit test.
        if isinstance(constraint, ScalarConstraint):
            for init_constr in self.init_conditions:
                if init_constr.name == constraint.name:
                    raise ValueError(
                        f"An initial constraint with the same name as {constraint.name} already exists."
                    )
            self.init_conditions.append(constraint)
        else:
            raise ValueError("The passed constraint is not a ScalarConstraint.")

    def set_performance_metric(self, metric: sc.Scalar):
        """
        Set the performance metric.

        Args:
            metric (:class:`Scalar`): A :class:`Scalar` object that
                represents the desired performance metric.

        Example:
            >>> pb.set_performance_metric(f(x_N) - f(x_star))
        """
        self.performance_metric = metric

    def set_relaxed_constraints(self, relaxed_constraints: list[str]):
        """
        Set the constraints that will be ignored.

        Args:
            relaxed_constraints (list[str]): A list of names of constraints
                that will be ignored.
        """
        self.relaxed_constraints.extend(relaxed_constraints)

    def add_dual_val_constraint(
        self, constraint_name: str, op: str, val: float
    ) -> None:
        if op not in ["le", "ge", "lt", "gt", "eq", "<=", ">=", "<", ">", "=="]:
            raise ValueError(
                f"op must be one of `le`, `ge`, `lt`, `gt`, `eq`, `<=`, `>=`, `<`, `>`, or `==` but got {op}."
            )
        if not utils.is_numerical(val):
            raise ValueError("Value must be some numerical value.")

        self.dual_val_constraint[constraint_name].append((op, val))

    def solve(
        self,
        context: PEPContext | None = None,
        resolve_parameters: dict[str, NUMERICAL_TYPE] | None = None,
    ):
        return self.solve_primal(context, resolve_parameters=resolve_parameters)

    def solve_primal(
        self,
        context: PEPContext | None = None,
        resolve_parameters: dict[str, NUMERICAL_TYPE] | None = None,
    ):
        """
        Solve the Primal PEP associated with this :class:`PEPBuilder` object
        using the given :class:`PEPContext` object.

        Args:
            context (:class:`PEPContext`): The :class:`PEPContext` object used
                to solve the Primal PEP associated with this
                :class:`PEPBuilder` object. `None` if we consider the current
                global :class:`PEPContext` object.
            resolve_parameters (dict[str, :data:`NUMERICAL_TYPE`] | `None`): A
                dictionary that maps the name of parameters to the numerical
                values.

        Returns:
            :class:`PEPResult`: A :class:`PEPResult` object that contains the
            information obtained after solving the Primal PEP associated with
            this :class:`PEPBuilder` object.
        """
        from pepflow.operator import LinearOperatorTranspose

        if context is None:
            context = pc.get_current_context()
        if context is None:
            raise RuntimeError("Did you forget to create a context?")

        all_constraints: list[Constraint] = [*self.init_conditions]
        for f in self.ctx.func_to_triplets.keys():
            all_constraints.extend(f.get_interpolation_constraints(context))

        for op in self.ctx.oper_to_duplets.keys():
            # Skip LinearOperator objects because they should not have interpolation conditions implemented.
            if isinstance(op, LinearOperatorTranspose):
                continue
            all_constraints.extend(op.get_interpolation_constraints(context))

        constraints = []
        for c in all_constraints:
            if not isinstance(c, ScalarConstraint) and not isinstance(c, PSDConstraint):
                raise ValueError(
                    "A constraint is not a ScalarConstraint or a PSDConstraint."
                )
            if c.name not in self.relaxed_constraints:
                constraints.append(c)
        # For now, we heavily rely on CVX. We can make a wrapper class to avoid
        # direct dependencies in the future.
        if isinstance(self.performance_metric, sc.Scalar):
            solver = ps.CVXPrimalSolver(
                perf_metric=self.performance_metric,
                constraints=constraints,
                context=context,
            )
            problem = solver.build_problem(resolve_parameters=resolve_parameters)
            result = problem.solve()

            return pr.PEPResult(
                opt_value=result,
                dual_var_manager=solver.dual_var_manager,
                pep_type=utils.PEPType.PRIMAL,
                solver_status=problem.status,
                context=context,
            )
        raise ValueError("The performance metric has not yet been initialized.")

    def solve_dual(
        self,
        context: PEPContext | None = None,
        resolve_parameters: dict[str, NUMERICAL_TYPE] | None = None,
    ):
        """
        Solve the Dual PEP associated with this :class:`PEPBuilder` object
        using the given :class:`PEPContext` object.

        Args:
            context (:class:`PEPContext`): The :class:`PEPContext` object used
                to solve the Dual PEP associated with this :class:`PEPBuilder`
                object. `None` if we consider the current global
                :class:`PEPContext` object.
            resolve_parameters (dict[str, :data:`NUMERICAL_TYPE`] | `None`): A
                dictionary that maps the name of parameters to the numerical values.

        Returns:
            :class:`PEPResult`: A :class:`PEPResult` object that
            contains the information obtained after solving the Dual PEP
            associated with this :class:`PEPBuilder` object.
        """
        from pepflow.operator import LinearOperatorTranspose

        if context is None:
            context = pc.get_current_context()
        if context is None:
            raise RuntimeError("Did you forget to create a context?")

        all_constraints: list[Constraint] = [*self.init_conditions]
        for f in self.ctx.func_to_triplets.keys():
            all_constraints.extend(f.get_interpolation_constraints(context))

        for op in self.ctx.oper_to_duplets.keys():
            # Skip LinearOperator objects because they should not have interpolation conditions implemented.
            if isinstance(op, LinearOperatorTranspose):
                continue
            all_constraints.extend(op.get_interpolation_constraints(context))

        # TODO: Consider a better API and interface to adding constraint for dual
        # variable in dual problem. We can add `extra_dual_val_constraints` to add
        # more constraints on dual var in dual PEP.
        constraints = []
        for c in all_constraints:
            if not isinstance(c, ScalarConstraint) and not isinstance(c, PSDConstraint):
                raise ValueError(
                    "A constraint is not a ScalarConstraint or a PSDConstraint."
                )
            if c.name in self.relaxed_constraints:
                continue

            if isinstance(c, ScalarConstraint):
                for op, val in self.dual_val_constraint[c.name]:
                    if op in ["le", "lt", "<=", "<"]:
                        c.dual_le(val)
                    elif op in ["ge", "gt", ">=", ">"]:
                        c.dual_ge(val)
                    elif op == "eq" or op == "==":
                        c.dual_eq(val)
                    else:
                        raise ValueError(f"Unknown op when construct the {c}")
                constraints.append(c)

            if isinstance(c, PSDConstraint):
                for op, val in self.dual_val_constraint[c.name]:
                    if op in ["peq", "<<"]:
                        c.dual_peq(val)
                    elif op in ["seq", ">>"]:
                        c.dual_seq(val)
                    elif op == "eq" or op == "==":
                        c.dual_eq(val)
                    else:
                        raise ValueError(f"Unknown op when construct the {c}")
                constraints.append(c)

        if isinstance(self.performance_metric, sc.Scalar):
            dual_solver = ps.CVXDualSolver(
                perf_metric=self.performance_metric,
                constraints=constraints,
                context=context,
            )
            problem = dual_solver.build_problem(resolve_parameters=resolve_parameters)
            result = problem.solve()

            return pr.PEPResult(
                opt_value=result,
                dual_var_manager=dual_solver.dual_var_manager,
                pep_type=utils.PEPType.DUAL,
                solver_status=problem.status,
                context=context,
            )

        raise ValueError("The performance metric has not yet been initialized.")
