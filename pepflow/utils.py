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

import enum
import math
import numbers
from collections import defaultdict
from typing import TYPE_CHECKING, Any, TypeAlias

import numpy as np
import pandas as pd
import sympy as sp

from pepflow import constants as const

if TYPE_CHECKING:
    from pepflow.parameter import Parameter
    from pepflow.scalar import Scalar
    from pepflow.vector import Vector


NUMERICAL_TYPE: TypeAlias = numbers.Number | sp.Number


def SOP(v, w, sympy_mode: bool = False) -> np.ndarray:
    """Symmetric Outer Product."""
    coef = sp.S(1) / 2 if sympy_mode else 1 / 2
    return coef * (np.outer(v, w) + np.outer(w, v))


def SOP_self(v, sympy_mode: bool = False) -> np.ndarray:
    return SOP(v, v, sympy_mode=sympy_mode)


class PEPType(enum.Enum):
    """
    An enum to representing either Primal or Dual PEP.

    Attributes:
        PRIMAL: Represents Primal PEP.
        DUAL: Represents Dual PEP.
    """

    PRIMAL = "primal"
    DUAL = "dual"


class Op(enum.Enum):
    ADD = "add"
    SUB = "sub"
    MUL = "mul"
    DIV = "div"
    POW = "pow"


class Comparator(enum.Enum):
    """
    An enum to representing comparators of relations.

    Attributes:
        GE: Greater than or equal.
        LE: Less than or equal.
        EQ: Equal to.
        PEQ: Preceq.
        SEQ: Succeq.
    """

    GE = "GE"
    LE = "LE"
    EQ = "EQ"
    PEQ = "PEQ"
    SEQ = "SEQ"

    def from_str(op: str) -> Comparator:
        if op in ["le", "lt", "<=", "<"]:
            cmp = Comparator.LE
        elif op in ["ge", "gt", ">=", ">"]:
            cmp = Comparator.GE
        elif op == "eq" or op == "==":
            cmp = Comparator.EQ
        elif op in ["peq", "<<"]:
            cmp = Comparator.PEQ
        elif op in ["seq", ">>"]:
            cmp = Comparator.SEQ
        else:
            raise ValueError(
                f"op must be one of `le`, `ge`, `lt`, `gt`, `eq`, `peq`, `seq`, `<=`, `>=`, `<`, `>`, `==`, `<<`, `>>`,  but got {op}"
            )
        return cmp


def is_numerical(val: Any) -> bool:
    return isinstance(val, numbers.Number) or is_sympy_real(val)


def is_parameter(val: Any) -> bool:
    from pepflow import parameter as param

    return isinstance(val, param.Parameter)


def is_numerical_or_parameter(val: Any) -> bool:
    return is_numerical(val) or is_parameter(val)


def is_sympy_expr(val: Any) -> bool:
    return isinstance(val, sp.Basic)


def is_sympy_real(val: Any) -> bool:
    val_is_sp_real = False
    if is_sympy_expr(val):
        val_is_sp_real = val.is_real
    return val_is_sp_real


def simplify_if_param_or_sympy_expr(
    val: NUMERICAL_TYPE | Parameter | sp.Basic,
) -> NUMERICAL_TYPE | Parameter | sp.Basic:
    if not is_numerical_or_parameter(val):
        raise TypeError(
            f"Expected a numerical value, Parameter, or SymPy expression, got {type(val)}"
        )
    # Both Parameter and SymPy expressions have a simplify() method
    if is_parameter(val) or is_sympy_expr(val):
        return val.simplify()  # type: ignore
    return val


def num_or_param_or_sympy_expr_is_zero(
    val: NUMERICAL_TYPE | Parameter | sp.Basic,
) -> bool:
    if is_parameter(val):
        from pepflow.parameter import ParameterByDictRepresentation

        # Parameter objects have an eval_expression attribute.
        expression = val.eval_expression  # type: ignore
        if isinstance(expression, ParameterByDictRepresentation):
            return expression.is_zero()
        return False
    elif is_sympy_expr(val):
        # Both SymPy expressions has a equals method
        return val.equals(0)  # type: ignore
    return val == 0


def simplify_dict(
    old_dict: defaultdict[Any, Any],
) -> defaultdict[Any, Any]:
    """
    Return a new defaultdict(int) whose values are simplified.
    Entries whose simplified value is zero are removed.
    """
    return defaultdict(
        int,
        {
            key: simplified_val
            for key, val in old_dict.items()
            if not num_or_param_or_sympy_expr_is_zero(
                simplified_val := simplify_if_param_or_sympy_expr(val)
            )
        },
    )


def numerical_str(val: Any) -> str:
    from pepflow import parameter as param

    if not is_numerical_or_parameter(val):
        raise ValueError(
            "Cannot call numerical_str for {val} since it is not numerical."
        )
    if isinstance(val, param.Parameter):
        return str(val)
    return str(val) if is_sympy_real(val) else f"{val:.4g}"


def coef_times_term_to_str(
    term_repr: str, val: NUMERICAL_TYPE | Parameter | sp.Basic
) -> str:
    """Returns a string representation with coefficient and term."""

    # TODO: Check performance
    if isinstance(val, sp.Basic):
        val = val.simplify()

    if is_numerical(val):
        sign = "+" if val >= 0 else "-"
        if math.isclose(abs(val), 1):
            return f"{sign} {term_repr} "
        elif math.isclose(val, 0, abs_tol=1e-5):
            return ""
        if isinstance(val, numbers.Number):
            coef = numerical_str(abs(val))
            return f"{sign} {coef}*{term_repr} "

    if is_sympy_expr(val) and not isinstance(val, sp.Rational):
        coef = sp.latex(val)  # We want LaTeX form (\pi), not plain text (pi)
    else:
        coef = str(val)
    coef = coef.strip()

    parenthesize_coef = parenthesize_repr(val).strip()
    if parenthesize_coef != coef:
        return f"+ {parenthesize_coef}*{term_repr} "

    if coef.startswith("-"):
        coef = coef[1:].lstrip()
        sign = "-"
    else:
        sign = "+"
    return f"{sign} {coef}*{term_repr} "


def parenthesize_tag(val: Vector | Scalar) -> str:
    tmp_repr = val.__repr__()
    if not val.is_basis:
        if op := getattr(val.eval_expression, "op", None):
            if op in (Op.ADD, Op.SUB):
                tmp_repr = f"({val.__repr__()})"
    return tmp_repr


def parenthesize_repr(
    val: Parameter | NUMERICAL_TYPE | sp.Basic, pow_base=False, pow_exponent=False
) -> str:
    # TODO: this function needs to write it properly.
    from pepflow.parameter import Parameter

    if is_sympy_expr(val) and not isinstance(val, sp.Rational):
        tmp_repr = sp.latex(val)  # We want LaTeX form (\pi), not plain text (pi)
    else:
        tmp_repr = str(val)

    if isinstance(val, sp.Basic):
        if val.is_Add:
            return f"({tmp_repr})"
        if pow_base:
            if val.is_Mul or val.is_Pow:
                return f"({tmp_repr})"
        return tmp_repr

    if isinstance(val, numbers.Number):
        return f"{val:.4g}"

    if pow_exponent:
        return f"{{{tmp_repr}}}"

    if isinstance(val, Parameter):
        if op := getattr(val.eval_expression, "op", None):
            if pow_base or op in (Op.ADD, Op.SUB):
                tmp_repr = f"({tmp_repr})"
        return tmp_repr

    raise ValueError(
        "parenthesize_repr only supports Parameter, numerical types, or sympy expressions."
    )


def grad_tag(base_tag: str) -> str:
    """Make a gradient tag for the base_tag (the func value typically)."""
    return f"{const.GRADIENT}_{base_tag}"


def triplet_tag(point: Vector, func_val: Scalar, grad: Vector) -> str:
    return f"{point.__repr__()}_{func_val.__repr__()}_{grad.__repr__()}"


def str_to_latex(s: str) -> str:
    """Convert string into latex style."""
    s = s.replace("star", r"\star")
    s = s.replace(f"{const.GRADIENT}_", r"\nabla ")
    s = s.replace("⟨", r"\left\langle ")
    s = s.replace("⟩", r" \right\rangle")
    s = s.replace("|", r"\|")
    s = s.replace("**", "^")

    def _replace_parenthesized_after_token(expr: str, token: str) -> str:
        """Replace `token(...)` with `token{...}` while preserving nesting."""
        if not token:
            return expr

        def _find_matching_paren(open_idx: int) -> int:
            depth = 1
            i = open_idx + 1
            while i < len(expr) and depth:
                if expr[i] == "(":
                    depth += 1
                elif expr[i] == ")":
                    depth -= 1
                i += 1
            return i if depth == 0 else -1

        out: list[str] = []
        i = 0
        while (k := expr.find(token, i)) >= 0:
            out.append(expr[i:k])
            j = k + len(token)
            if j >= len(expr) or expr[j] != "(":
                out.append(token)
                i = j
                continue
            end = _find_matching_paren(j)
            if end < 0:
                out.append(expr[k:])
                return "".join(out)
            inner = _replace_parenthesized_after_token(expr[j + 1 : end - 1], token)
            out.append(f"{token}{{{inner}}}")
            i = end

        out.append(expr[i:])
        return "".join(out)

    s = _replace_parenthesized_after_token(s, "^")
    s = _replace_parenthesized_after_token(s, r"\sqrt")
    return rf"$\displaystyle {s}$"


def get_matrix_of_dual_value(
    df: pd.DataFrame, value_col_name: str = "dual_value"
) -> np.ndarray:
    """The dataframe `df` has the columns "constraint_name",
    "col_point", "row_point", "row", "col", "constraint", and "dual_value".
    """
    # Check if we need to update the order.
    return get_pivot_table_of_dual_value(df, value_col_name).to_numpy()


def get_pivot_table_of_dual_value(
    df: pd.DataFrame, value_col_name: str = "dual_value", num_decs: int | None = None
) -> pd.DataFrame:
    """The dataframe `df` has the columns "constraint_name",
    "col_point", "row_point", "row", "col", "constraint", and "dual_value".
    """
    pivot_table = (
        pd.pivot_table(
            df,
            values=value_col_name,
            index="row_point",
            columns="col_point",
            dropna=False,
        )
        .fillna(0.0)
        .rename_axis("", axis=0)
    )
    if num_decs is not None:
        pivot_table = pivot_table.round(num_decs)
    return pivot_table


def name_to_vector_tuple(c_name: str) -> list[str]:
    """Take a constraint name and return the tag of the two corresponding points."""
    _, vectors = c_name.split(":")
    return vectors.split(",")
