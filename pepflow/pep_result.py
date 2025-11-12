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

from typing import TYPE_CHECKING, Any

import attrs
import natsort
import numpy as np
import pandas as pd

from pepflow import ipython_utils
from pepflow import pep_context as pc
from pepflow import utils
from pepflow.constants import PSD_CONSTRAINT
from pepflow.solver import DualPEPDualVarManager, PrimalPEPDualVarManager

if TYPE_CHECKING:
    from pepflow.function import Function
    from pepflow.operator import Operator


@attrs.define
class MatrixWithNames:
    """A data class that stores a matrix along with the names of its rows and columns.

    You can access a specific element by providing its row and column labels.

    Attributes:
        matrix (np.ndarray): A matrix.
        row_names (list[str]): A list of the names of the rows of the matrix.
        col_names (list[str]): A list of the names of the columns of the matrix.
    """

    matrix: np.ndarray
    row_names: list[str]
    col_names: list[str]

    def __attrs_post_init__(self):
        if self.matrix.shape != (len(self.row_names), len(self.col_names)):
            raise ValueError(
                "The shape of the matrix does not match the length of row_names and col_names."
            )

    def to_dataframe(self) -> pd.DataFrame:
        """Convert the matrix to a pandas DataFrame with row and column names."""
        return pd.DataFrame(
            self.matrix,
            index=self.row_names,
            columns=self.col_names,
        )

    def __call__(self, tag1: str, tag2: str) -> Any:
        """Access a matrix element by its row and column names."""
        i, j = self.row_names.index(tag1), self.col_names.index(tag2)
        return self.matrix[i, j]

    def pprint(self) -> None:
        """Prints a matrix with corresponding row and column labels."""
        ipython_utils.pprint_labeled_matrix(self)


@attrs.frozen
class PEPResult:
    """
    A data class object that contains the results of solving the PEP.

    Attributes:
        opt_value (float): The objective value of the solved Primal or Dual PEP.
        dual_var_manager (:class:`PrimalPEPDualVarManager` or :class:`DualPEPDualVarManager`):
            A manager object which provides access to the dual variables associated with the
            constraints of the Primal PEP or the dual variables that correspond to the
            constraints of the Dual PEP.
        pep_type (:class:`PEPType`): The type of the solved PEP, either "primal" or "dual".
        solver_status (Any): States whether the solver managed to solve the Primal/Dual PEP successfully.
        context (:class:`PEPContext`): The :class:`PEPContext` object used to solve the PEP.

    Example:
        >>> result = ctx.solve(resolve_parameters={"L": 1})
        >>> opt_value = result.opt_value
    """

    opt_value: float
    dual_var_manager: PrimalPEPDualVarManager | DualPEPDualVarManager
    pep_type: utils.PEPType
    solver_status: Any
    context: pc.PEPContext

    def __attrs_post_init__(self):
        match self.pep_type:
            case utils.PEPType.PRIMAL:
                if not isinstance(self.dual_var_manager, PrimalPEPDualVarManager):
                    raise TypeError(
                        "The dual_var_manager must be a PrimalPEPDualVarManager for Primal PEPResult."
                    )
            case utils.PEPType.DUAL:
                if not isinstance(self.dual_var_manager, DualPEPDualVarManager):
                    raise TypeError(
                        "The dual_var_manager must be a DualPEPDualVarManager for Dual PEPResult."
                    )

    def get_gram_dual_matrix(self) -> MatrixWithNames:
        """
        Return the Gram dual variable matrix associated with the constraint
        that the Primal PEP decision variable :math:`G` is PSD.

        Returns:
            MatrixWithNames: The PSD dual variable matrix associated with the
            constraint that the Primal PEP decision variable :math:`G` is PSD.
        """
        # Note the raw matrix is defined based on the order of basis scalars in the context.
        # Should we consider sorting them through natsort as well scalar one?
        names = [c.__repr__() for c in self.context.basis_vectors()]
        return MatrixWithNames(
            np.array(self.dual_var_manager.dual_value(PSD_CONSTRAINT)),
            row_names=names,
            col_names=names,
        )

    def get_dual_value(self, name: str) -> float | None:
        return self.dual_var_manager.dual_value(name)

    def get_scalar_constraint_dual_value_in_pandas(
        self, func_or_oper: Function | Operator
    ) -> dict[str, pd.DataFrame] | pd.DataFrame:
        """
        Return a dictionary that maps the names of the scalar constraints
        to their corresponding dual variables.

        Args:
            func_or_oper (:class:`Function` | :class:`Operator`): The
                :class:`Function` or :class:`Operator` object whose scalar
                constraints' dual variables we want to retrieve.

        Returns:
            dict[str, pd.dataframe]: A dictionary that maps the names of the
            scalar constraints to their corresponding dual variable matrices
            stored in a DataFrame.
        """
        constraint_data = self.context.get_constraint_data(func_or_oper)
        pd_dict = constraint_data.process_scalar_constraint_with_result(self)
        if len(pd_dict) == 1:
            return pd_dict.popitem()[1]
        return pd_dict

    def get_scalar_constraint_dual_value_in_numpy(
        self, func_or_oper: Function | Operator
    ) -> dict[str, MatrixWithNames] | MatrixWithNames:
        """
        Return a dictionary that maps the names of the scalar constraints
        to their corresponding dual variables.

        Args:
            func_or_oper (:class:`Function` | :class:`Operator`): The
                :class:`Function` or :class:`Operator` object whose scalar
                constraints' dual variables we want to retrieve.

        Returns:
            dict[str, MatrixWithNames]: A dictionary that maps the names of the
            scalar constraints to their corresponding dual variable matrices
            stored in a :class:`MatrixWithNames`.
        """
        data_frame_dict = self.get_scalar_constraint_dual_value_in_pandas(func_or_oper)
        if isinstance(data_frame_dict, pd.DataFrame):
            # Single constraint case
            order_col = natsort.natsorted(
                list(set(data_frame_dict["col_point"].tolist()))
            )
            order_row = natsort.natsorted(
                list(set(data_frame_dict["row_point"].tolist()))
            )
            return MatrixWithNames(
                utils.get_matrix_of_dual_value(data_frame_dict),
                row_names=order_row,
                col_names=order_col,
            )
        return_dict: dict[str, MatrixWithNames] = {}
        for name, df in data_frame_dict.items():
            order_col = natsort.natsorted(df["col_point"].unique())
            order_row = natsort.natsorted(df["row_point"].unique())
            return_dict[name] = MatrixWithNames(
                utils.get_matrix_of_dual_value(df),
                row_names=order_row,
                col_names=order_col,
            )
        return return_dict

    def get_matrix_constraint_dual_values(
        self, func_or_oper: Function | Operator
    ) -> dict[str, np.ndarray]:
        """
        Return a dictionary that maps the names of the PSD constraints
        to their corresponding dual variable matrices.

        Args:
            func_or_oper (:class:`Function` | :class:`Operator`): The
                :class:`Function` or :class:`Operator` object whose PSD
                constraints' dual variables we want to retrieve.

        Returns:
            dict[str, np.ndarray]: A dictionary that maps the names of the
            PSD constraints to their corresponding dual variable matrices.
        """
        constraint_data = self.context.get_constraint_data(func_or_oper)
        psd_dual_dict = {}
        for type_name, psd_constraint in constraint_data.psd_dict.items():
            dual_value = self.dual_var_manager.dual_value(psd_constraint.name)
            # TODO: we do not which column name should be tagged here.
            psd_dual_dict[type_name] = np.array(dual_value)
        return psd_dual_dict
