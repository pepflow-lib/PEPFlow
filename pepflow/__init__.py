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

# isort: skip_file
from .constants import PSD_CONSTRAINT as PSD_CONSTRAINT
from .constraint import ScalarConstraint as ScalarConstraint
from .constraint import PSDConstraint as PSDConstraint
from .expression_manager import ExpressionManager as ExpressionManager
from .expression_manager import represent_matrix_by_basis as represent_matrix_by_basis

# interactive_constraint
from .primal_interactive_constraint import (
    launch_primal_interactive as launch_primal_interactive,
)
from .dual_interactive_constraint import (
    launch_dual_interactive as launch_dual_interactive,
)

# pep_result
from .pep_result import PEPResult as PEPResult
from .pep_result import MatrixWithNames as MatrixWithNames

# pep
from .pep import PEPBuilder as PEPBuilder
from .pep_context import PEPContext as PEPContext
from .pep_context import get_current_context as get_current_context
from .pep_context import set_current_context as set_current_context

# Function and Operator Registry
from .registry import declare_func as declare_func
from .registry import declare_oper as declare_oper
from .registry import get_func_or_oper_by_tag as get_func_or_oper_by_tag

# Function, Operator, Vector, Scalar, Parameter
from .function import Function as Function
from .function import SmoothStronglyConvexFunction as SmoothStronglyConvexFunction
from .function import SmoothConvexFunction as SmoothConvexFunction
from .function import ConvexFunction as ConvexFunction
from .function import Triplet as Triplet
from .operator import Operator as Operator
from .operator import LinearOperator as LinearOperator
from .operator import Duplet as Duplet
from .parameter import Parameter as Parameter
from .scalar import EvaluatedScalar as EvaluatedScalar
from .scalar import Scalar as Scalar
from .vector import EvaluatedVector as EvaluatedVector
from .vector import Vector as Vector

# Solver
from .solver import CVXPrimalSolver as CVXPrimalSolver
from .solver import CVXDualSolver as CVXDualSolver
from .solver import PrimalPEPDualVarManager as PrimalPEPDualVarManager
from .solver import DualPEPDualVarManager as DualPEPDualVarManager

# Others
from .utils import SOP as SOP
from .utils import SOP_self as SOP_self
from .ipython_utils import pprint_str as pprint_str
from .ipython_utils import pprint_matrix as pprint_matrix
from .ipython_utils import pprint_labeled_vector as pprint_labeled_vector
from .ipython_utils import pprint_labeled_matrix as pprint_labeled_matrix

# Logging
from .logging import logger as logger
