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
import types

import numpy as np
import sympy as sp
from IPython.display import Math, display
from sympy import Matrix

from pepflow import pep_result, utils


def pprint_str(string: str) -> None:
    """Pretty-print the string in LaTeX format.

    Args:
        string (str): The string to be printed.

    Example:
        >>> pprint_str("x_0")
    """
    display(Math(utils.str_to_latex(string)))


def pprint_matrix(mat: np.ndarray, precision: int = 3) -> None:
    """Pretty-print the matrix in LaTeX format.

    Args:
        mat (np.ndarray): The matrix to be printed.
        precision (int): Number of decimal places to display for each value. Defaults to 3.

    Example:
        >>> mat = np.array([[0.0, 0.5], [0.0, 0.0]])
        >>> pprint_matrix(mat)
    """
    if precision:
        mat = np.round(np.array(mat, dtype=float), precision)
    display(sp.Matrix(mat))


def pprint_labeled_vector(
    vec: np.ndarray | types.FunctionType,
    labels: list[str],
    precision: int = 3,
    print_label: bool = True,
    return_vector: bool = False,
) -> np.ndarray | None:
    """Prints a vector with corresponding labels.

    This function displays a vector (typically coefficients of function values)
    using a list of strings as labels. The matrix can be provided either directly
    as a NumPy array or as a function mapping labels to values.
    Optionally, the printed values can be formatted to a given precision.

    Args:
        mat (np.ndarray | types.FunctionType): A vector, a function that returns
            vector values given labels.
        labels (list[str]): List of strings to use as labels.
        precision (int): Number of decimal places to display for each value. Defaults to 3.
        print_label (bool): Whether to display the labels. Defaults to `True`.
        return_vector (bool): If `True`, returns the constructed vector as a NumPy array.
            Defaults to `False`.

    Returns:
        np.ndarray | None: The vector as a NumPy array if `return_vector=True`, otherwise `None`.

    Example:
        >>> vec = np.array([0.5, 0.125])
        >>> tags = ["f(x_0)", "f(x_1)"]
        >>> pprint_labeled_vector(vec, tags)
    """
    # If vec is callable, create a NumPy array from it
    length = len(labels)
    if isinstance(vec, types.FunctionType):
        m = np.zeros((length,))
        for tag in labels:
            m[labels.index(tag)] = vec(tag)
        raw_vec = m
    else:
        raw_vec = vec

    assert isinstance(vec, np.ndarray)
    if raw_vec.shape != (length,):
        raise ValueError("The shape of the vector does not match the length of labels.")

    if precision:
        vector = np.round(np.array(raw_vec, dtype=float), precision)
    else:
        vector = raw_vec

    if print_label:
        col_def = "c" * length
        head = " & ".join(tag for tag in labels) + r" \\"
        row = " & ".join(str(v) for v in vector)
        latex_str = rf"""
        \begin{{array}}{{{col_def}}}
        {head}
        \hline
        {row}
        \end{{array}}
        """

        latex_str = utils.str_to_latex(latex_str)
        display(Math(latex_str))
    else:
        display(Matrix(vector))

    if return_vector:
        return raw_vec


def pprint_labeled_matrix(
    mat: np.ndarray | types.FunctionType | pep_result.MatrixWithNames,
    row_labels: list[str] | None = None,
    column_labels: list[str] | None = None,
    precision: int = 3,
    print_label: bool = True,
    return_matrix: bool = False,
) -> np.ndarray | None:
    """Prints a matrix with corresponding row and column labels.

    This function displays a matrix (typically representing dual variables),
    using a list of strings (mostly tags) as labels for rows and columns. The matrix
    can be provided either directly as a NumPy array or as a function mapping index
    pairs to values. Optionally, the printed values can be formatted to a given precision.

    Args:
        mat (np.ndarray | types.FunctionType | :class:`MatrixWithNames`): A matrix,
            a function that returns matrix values given row and column labels,
            or a `MatrixWithNames` object.
        row_labels (list[str] | None): List of strings to use as row labels. When `None`,
            the function works only mat is a :class:`MatrixWithNames` object
        column_labels (list[str] | None): List of strings to use as column labels. When `None`,
            the function works only for square matrices with equal row and column labels.
        precision (int): Number of decimal places to display for each value. Defaults to `3`.
        print_label (bool): Whether to display the labels. Defaults to `True`.
        return_matrix (bool): If `True`, returns the constructed matrix as a NumPy array.
            Defaults to False.

    Returns:
        np.ndarray | None: The matrix as a NumPy array if `return_matrix=True`, otherwise `None`.

    Example:
        >>> mat = np.array([[0.0, 0.5], [0.0, 0.0]])
        >>> tags = ["x1", "x2"]
        >>> pprint_labeled_matrix(mat, tags)
    """
    if not isinstance(mat, pep_result.MatrixWithNames):
        if row_labels is None:
            raise ValueError("row_labels is missing")

    if column_labels is None:
        column_labels = row_labels
        if isinstance(mat, np.ndarray):
            if (
                mat.shape[0] != mat.shape[1]
            ):  # if column_labels is None, the matrix should be square
                raise ValueError(f"Array is not square: {mat.shape[0]}x{mat.shape[1]}")

    if isinstance(mat, pep_result.MatrixWithNames):
        row_labels = mat.row_names
        column_labels = mat.col_names

    # To make typecheck happy
    assert isinstance(row_labels, list) and all(isinstance(x, str) for x in row_labels)
    assert isinstance(column_labels, list) and all(
        isinstance(x, str) for x in column_labels
    )

    # If mat is callable, create a NumPy array from it
    row_length = len(row_labels)
    column_length = len(column_labels)
    if isinstance(mat, types.FunctionType) or isinstance(
        mat, pep_result.MatrixWithNames
    ):
        m = np.zeros((row_length, column_length))
        for tag1, tag2 in itertools.product(row_labels, column_labels):
            m[row_labels.index(tag1), column_labels.index(tag2)] = mat(tag1, tag2)
        raw_matrix = m
    else:
        raw_matrix = mat

    assert isinstance(raw_matrix, np.ndarray)
    if raw_matrix.shape != (len(row_labels), len(column_labels)):
        raise ValueError(
            "The shape of the matrix does not match the length of row_labels and column_labels."
        )

    if precision:
        matrix = np.round(np.array(raw_matrix, dtype=float), precision)
    else:
        matrix = raw_matrix

    if print_label:
        col_def = "c|" + "c" * column_length
        head = " & " + " & ".join(tag for tag in column_labels) + r" \\"
        rows = ""
        for i in range(row_length):
            rows += (
                row_labels[i] + " & " + " & ".join(str(v) for v in matrix[i]) + r" \\"
            )
        latex_str = rf"""
        \begin{{array}}{{{col_def}}}
        {head}
        \hline
        {rows}
        \end{{array}}
        """

        latex_str = utils.str_to_latex(latex_str)
        latex_str = latex_str.replace(r"\|", "|")
        display(Math(latex_str))
    else:
        display(Matrix(matrix))

    if return_matrix:
        return raw_matrix
