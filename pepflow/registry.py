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

if TYPE_CHECKING:
    from pepflow.function import Function
    from pepflow.operator import Operator

# Keep the track of all created functions and operators.
REGISTERED_FUNC_AND_OPER_DICT: dict[str, Function | Operator] = {}


def declare_func(func_class: type[Function], tag: str, **kwargs):
    """
    Declare a function.

    Args:
        func_class (type[:class:`Function`]): The type of function we want to
            declare. Examples include :class:`ConvexFunction` or
            :class:`SmoothConvexFunction`.
        tag (str): A tag that will be added to the :class:`Function`'s
            `tags` list. It can be used to identify the :class:`Function`
            object.
        **kwargs: The other parameters needed to declare the function. For
            example, :class:`SmoothConvexFunction` will require a
            smoothness parameter `L`.
    """
    func = func_class(is_basis=True, composition=None, tags=[tag], **kwargs)
    return func


def declare_oper(oper_class: type[Operator], tag: str, **kwargs):
    """
    Declare an operator.

    Args:
        oper_class (type[:class:`Operator`]): The type of operator we want to
            declare. Examples include :class:`LinearOperator`.
        tag (str): A tag that will be added to the :class:`Operator`'s
            `tags` list. It can be used to identify the :class:`Operator`
            object.
        **kwargs: The other parameters needed to declare the function. For
            example, :class:`LinearOperator` will require a
            operator norm parameter `M`.
    """
    oper = oper_class(is_basis=True, composition=None, tags=[tag], **kwargs)
    return oper


# TODO: Find a better way to declare the return type while keeping type checker happy.
def get_func_or_oper_by_tag(tag: str):
    """
    Return the :class:`Function` or :class:`Operator` object associated with
    the provided `tag`.

    Args:
        tag (str): The `tag` of the :class:`Function` or :class:`Object` object
            we want to retrieve.

    Returns:
        :class:`Function` | :class:`Operator`: The :class:`Function` or
        :class:`Operator` object associated with the `tag`.
    """
    if tag in REGISTERED_FUNC_AND_OPER_DICT:
        return REGISTERED_FUNC_AND_OPER_DICT[tag]
    raise ValueError("Cannot find the function or operator of given tag.")
