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

import json
from collections.abc import Hashable
from typing import TYPE_CHECKING

import dash
import dash_bootstrap_components as dbc
import numpy as np
import pandas as pd
import plotly
import plotly.graph_objects as go
from dash import ALL, MATCH, Dash, Input, Output, State, ctx, dcc, html

from pepflow import pep_context as pc
from pepflow import registry as reg
from pepflow import utils
from pepflow.plot_data import PlotData

if TYPE_CHECKING:
    from pepflow.function import Function
    from pepflow.operator import Operator
    from pepflow.pep import PEPBuilder
    from pepflow.pep_context import PEPContext
    from pepflow.pep_result import PEPResult
    from pepflow.utils import NUMERICAL_TYPE


plotly.io.renderers.default = "colab+vscode"
plotly.io.templates.default = "plotly_white"


def solve_primal_prob_and_get_all_plot_data(
    pep_builder: PEPBuilder,
    context: pc.PEPContext,
    resolve_parameters: dict[str, utils.NUMERICAL_TYPE] | None = None,
) -> tuple[list[PlotData], PEPResult]:
    from pepflow.operator import LinearOperatorTranspose

    plot_data_list = []

    result = pep_builder.solve_primal(
        context=context, resolve_parameters=resolve_parameters
    )

    for func in context.func_to_triplets.keys():
        plot_data = PlotData.from_func_or_oper_pep_result_and_builder(
            func, result, pep_builder
        )
        plot_data_list.append(plot_data)

    for oper in context.oper_to_duplets.keys():
        # Skip LinearOperator objects because they should not have interpolation conditions implemented.
        if isinstance(oper, LinearOperatorTranspose):
            continue
        plot_data = PlotData.from_func_or_oper_pep_result_and_builder(
            oper, result, pep_builder
        )
        plot_data_list.append(plot_data)

    return plot_data_list, result


def get_all_plot_data_from_result_and_builder(
    pep_result: PEPResult, pep_builder: PEPBuilder
) -> list[PlotData]:
    from pepflow.operator import LinearOperatorTranspose

    plot_data_list = []

    for func in pep_result.context.func_to_triplets.keys():
        plot_data = PlotData.from_func_or_oper_pep_result_and_builder(
            func, pep_result, pep_builder
        )
        plot_data_list.append(plot_data)

    for oper in pep_result.context.oper_to_duplets.keys():
        # Skip LinearOperator objects because they should not have interpolation conditions implemented.
        if isinstance(oper, LinearOperatorTranspose):
            continue
        plot_data = PlotData.from_func_or_oper_pep_result_and_builder(
            oper, pep_result, pep_builder
        )
        plot_data_list.append(plot_data)

    return plot_data_list


def get_plot_data_from_func_or_oper_result_and_builder(
    func_or_oper: Function | Operator, pep_result: PEPResult, pep_builder: PEPBuilder
) -> PlotData:
    from pepflow.operator import LinearOperatorTranspose

    if isinstance(func_or_oper, LinearOperatorTranspose):
        raise ValueError(
            "There is no PlotData associated with LinearOperatorTranspose objects."
        )
    plot_data = PlotData.from_func_or_oper_pep_result_and_builder(
        func_or_oper, pep_result, pep_builder
    )
    return plot_data


def launch_primal_interactive(
    pep_builder: PEPBuilder,
    context: PEPContext,
    resolve_parameters: dict[str, NUMERICAL_TYPE] | None = None,
    port: int = 8050,
    jupyter_mode: str | None = "external",
):
    """Launch the Primal PEP Interactive Dashboard.

    Attributes:
        pep_builder (:class:`PEPBuilder`): The :class:`PEPBuilder` object whose
            associated Primal PEP problem we consider.
        context (:class:`PEPContext`): The :class:`PEPContext` object associated
            with the Primal PEP problem.
        resolve_parameters (dict[str, :class:`NUMERICAL_TYPE`] | `None`): A dictionary
            that maps the name of parameters to the numerical values.
        port (int): The port where we host the Primal PEP Interactive Dashboard.
        jupyter_mode (str | None): A string to specify how to launch the PEP
            Interactive Dashboard. Default is "external". Other options are
            "tab", "jupyterlab", or `None`. If `None`, then the PEP Interactive
            Dashboard will launch inline.

    Example:
        >>> pf.launch_primal_interactive(pb, ctx, resolve_parameters={"L": 1})
    """
    app = Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])
    plot_data_list, result = solve_primal_prob_and_get_all_plot_data(
        pep_builder, context, resolve_parameters
    )
    display_row = dbc.Row(
        [
            # Column 1: The scatter plots of dual variables and buttons to relax or restore constraints.
            dbc.Col(
                [
                    dbc.Button(
                        "Relax All Constraints",
                        id="relax-all-constraints-button",
                        style={"margin-bottom": "5px", "margin-right": "5px"},
                    ),
                    dbc.Button(
                        "Restore All Constraints",
                        id="restore-all-constraints-button",
                        style={"margin-bottom": "5px"},
                        color="success",
                    ),
                    dbc.Tabs(
                        children=[
                            plot_data.plot_data_to_tab() for plot_data in plot_data_list
                        ],
                    ),
                ],
                width=5,
            ),
            # Column 2: The data display and area to add constraints to dual variables.
            dbc.Col(
                [
                    dbc.Button(
                        "Solve PEP Problem",
                        id="solve-button",
                        color="primary",
                        className="me-1",
                        style={"margin-bottom": "5px"},
                    ),
                    dcc.Loading(
                        dbc.Card(
                            id="result-card",
                            style={"height": "60vh", "overflow-y": "auto"},
                        )
                    ),
                ],
                width=7,
            ),
        ],
    )

    dcc_store_list = []
    for plot_data in plot_data_list:
        dcc_store_list.extend(plot_data.df_dict_to_dcc_store_list())
    for plot_data in plot_data_list:
        dcc_store_list.extend(plot_data.psd_dv_dict_to_dcc_store_list())

    # 3. Define the app layout.
    app.layout = html.Div(
        [
            html.H2("PEPFlow"),
            display_row,
            # For each function/operator interpolation group, store the corresponding
            # DataFrame/Dual Value Matrix as a dictionary in dcc.Store.
            *dcc_store_list,
        ]
    )

    @dash.callback(
        Output("result-card", "children"),
        Output({"type": "dual-value-display", "index": ALL}, "children"),
        Output({"type": "interactive-scatter", "index": ALL}, "figure"),
        Output({"type": "dataframe-store", "index": ALL}, "data"),
        Output({"type": "psd-dv-store", "index": ALL}, "data"),
        Input("solve-button", "n_clicks"),
    )
    def solve(_):
        plot_data_list, result = solve_primal_prob_and_get_all_plot_data(
            pep_builder, context, resolve_parameters
        )
        with np.printoptions(precision=3, linewidth=500, suppress=True):
            result_card = dbc.CardBody(
                [
                    html.H3(f"Optimal Value: {result.opt_value:.4g}"),
                    html.H3(f"Solver Status: {result.solver_status}"),
                    html.P("Relaxed Constraints:"),
                    html.Div(
                        style={
                            "display": "flex",
                            "gap": "10px",
                            "flexDirection": "row",
                        },
                        children=[
                            html.Pre(
                                json.dumps(pep_builder.relaxed_constraints, indent=2),
                                id="relaxed-constraints",
                            ),
                            dcc.Clipboard(
                                id="relaxed-constraint-copy",
                                target_id="relaxed-constraints",
                                style={
                                    "fontSize": 20,
                                },
                            ),
                        ],
                    ),
                ]
            )
        dual_value_displays = []
        for plot_data in plot_data_list:
            for df in plot_data.df_dict.values():
                dual_value_displays.append(
                    dbc.Table.from_dataframe(  # ty: ignore
                        utils.get_pivot_table_of_dual_value(
                            df, num_decs=3
                        ).reset_index(),
                        bordered=True,
                    )
                )
        # List that stores all the corresponding figures from the list of plot_data.
        figs: list[go.Figure] = []
        # List that stores all the corresponding information related to the dataframes from the list of plot_data.
        # Specifically, it stores tuples of the form (func_or_oper.tag, df.to_dict("records"), df.attrs).
        # The df.attrs stores the order of the row and column points as a dictionary. Specifically,
        # it is of the form {"order_row": order_row, "order_col": order_col}.
        df_data: list[
            tuple[str, list[dict[str, str]], dict[Hashable, list[str]]]
        ] = []  #
        # List that stores all the corresponding information related to psd constraint from the list of plot_data.
        # Specifically, it stores tuples of the form (func_or_oper.tag, psd_dv).
        psd_dv_data: list[tuple[str, str]] = []
        for plot_data in plot_data_list:
            for fig in plot_data.fig_dict.values():
                figs.append(fig)
            for df in plot_data.df_dict.values():
                df_data.append(
                    (plot_data.func_or_oper.tag, df.to_dict("records"), df.attrs)
                )
            for psd_dv in plot_data.psd_dv_dict.values():
                psd_dv_data.append((plot_data.func_or_oper.tag, psd_dv))
        return result_card, dual_value_displays, figs, df_data, psd_dv_data

    @dash.callback(
        Output(
            {"type": "interactive-scatter", "index": ALL},
            "figure",
            allow_duplicate=True,
        ),
        Output({"type": "dataframe-store", "index": ALL}, "data", allow_duplicate=True),
        Input("restore-all-constraints-button", "n_clicks"),
        prevent_initial_call=True,
    )
    def restore_all_constraints(_):
        nonlocal pep_builder
        pep_builder.relaxed_constraints = []
        updated_figs = []
        df_data = []
        plot_data_list = get_all_plot_data_from_result_and_builder(result, pep_builder)
        for plot_data in plot_data_list:
            updated_figs.extend(plot_data.fig_dict.values())
            df_data.extend(plot_data.df_dict_to_dcc_store_list())
        return updated_figs, df_data

    @dash.callback(
        Output(
            {"type": "interactive-scatter", "index": ALL},
            "figure",
            allow_duplicate=True,
        ),
        Output({"type": "dataframe-store", "index": ALL}, "data", allow_duplicate=True),
        Input("relax-all-constraints-button", "n_clicks"),
        State({"type": "dataframe-store", "index": ALL}, "data"),
        prevent_initial_call=True,
    )
    def relax_all_constraints(_, list_previous_df_tuples):
        nonlocal pep_builder
        pep_builder.relaxed_constraints = []
        for previous_df_tuple in list_previous_df_tuples:
            _, previous_df_as_dict, _ = previous_df_tuple
            pep_builder.relaxed_constraints.extend(
                pd.DataFrame(previous_df_as_dict)["constraint_name"].to_list()
            )
        updated_figs = []
        df_data = []
        plot_data_list = get_all_plot_data_from_result_and_builder(result, pep_builder)
        for plot_data in plot_data_list:
            updated_figs.extend(plot_data.fig_dict.values())
            df_data.extend(plot_data.df_dict_to_dcc_store_list())
        return updated_figs, df_data

    @dash.callback(
        Output(
            {"type": "interactive-scatter", "index": MATCH},
            "figure",
            allow_duplicate=True,
        ),
        Output(
            {"type": "dataframe-store", "index": MATCH}, "data", allow_duplicate=True
        ),
        Input({"type": "interactive-scatter", "index": MATCH}, "clickData"),
        prevent_initial_call=True,
    )
    def update_df_and_redraw(clickData):
        nonlocal pep_builder
        if not clickData["points"][0]["customdata"]:
            return dash.no_update, dash.no_update

        clicked_name = clickData["points"][0]["customdata"][0]
        if clicked_name not in pep_builder.relaxed_constraints:
            pep_builder.relaxed_constraints.append(clicked_name)
        else:
            pep_builder.relaxed_constraints.remove(clicked_name)

        func_or_oper_tag, constraint_group_name = ctx.triggered_id["index"].split("-")
        func_or_oper = reg.get_func_or_oper_by_tag(func_or_oper_tag)
        plot_data = get_plot_data_from_func_or_oper_result_and_builder(
            func_or_oper, result, pep_builder
        )

        new_fig = plot_data.fig_dict[constraint_group_name]
        new_df = plot_data.df_dict[constraint_group_name]

        return new_fig, (func_or_oper_tag, new_df.to_dict("records"), new_df.attrs)

    app.run(debug=True, port=port, jupyter_mode=jupyter_mode)  # ty: ignore
