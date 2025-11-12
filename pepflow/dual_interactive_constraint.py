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
from typing import TYPE_CHECKING

import dash
import dash_bootstrap_components as dbc
import numpy as np
import plotly
from dash import ALL, Dash, Input, Output, State, dcc, html

from pepflow import utils
from pepflow.plot_data import PlotData

if TYPE_CHECKING:
    from pepflow.pep import PEPBuilder
    from pepflow.pep_context import PEPContext
    from pepflow.pep_result import PEPResult


plotly.io.renderers.default = "colab+vscode"
plotly.io.templates.default = "plotly_white"


def solve_dual_prob_and_get_all_plot_data(
    pep_builder: PEPBuilder,
    context: PEPContext,
    resolve_parameters: dict[str, utils.NUMERICAL_TYPE] | None = None,
) -> tuple[list[PlotData], PEPResult]:
    from pepflow.operator import LinearOperatorTranspose

    plot_data_list = []

    result = pep_builder.solve_dual(
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


def generate_dual_constraint_list_cardbody(data: list[str]) -> dbc.CardBody:
    def generate_dual_constraint_html_div(
        constraint_dict: dict[str, str | float],
    ) -> html.Div:
        constraint_name = constraint_dict["constraint_name"]
        op = constraint_dict["relation"]
        value = constraint_dict["value"]
        return html.Div(
            f"Constraint Name: {constraint_name}, Relation: {op}, Value: {value}",
            style={
                "border": "2px solid black",
                "padding": "2px",
                "margin": "2px",
                "text-align": "center",
                "width": "600px",
            },
        )

    def generate_remove_constraint_html_div(index: int) -> html.Div:
        return html.Div(
            dbc.Button(
                "Remove Constraint",
                id={
                    "type": "remove-specific-dual-constraint-button",
                    "index": index,
                },
                color="primary",
                className="me-1",
                style={"margin-bottom": "5px"},
            )
        )

    return dbc.CardBody(
        [
            html.Div(
                style={
                    "display": "flex",
                    "gap": "10px",
                    "flexDirection": "row",
                    "alignItems": "center",
                },
                children=[
                    generate_dual_constraint_html_div(json.loads(constraint_dict)),
                    generate_remove_constraint_html_div(index),
                ],
            )
            for index, constraint_dict in enumerate(data)
        ]
    )


def launch_dual_interactive(
    pep_builder: PEPBuilder,
    context: PEPContext,
    port: int = 9050,
    resolve_parameters: dict[str, utils.NUMERICAL_TYPE] | None = None,
):
    """Launch the Dual PEP Interactive Dashboard.

    Attributes:
        pep_builder (:class:`PEPBuilder`): The :class:`PEPBuilder` object whose
            associated Dual PEP problem we consider.
        context (:class:`PEPContext`): The :class:`PEPContext` object associated
            with the Dual PEP problem.
        resolve_parameters (dict[str, :class:`NUMERICAL_TYPE`]): A dictionary that
            maps the name of parameters to the numerical values.
        port (int): The port where we host the Dual PEP Interactive Dashboard.

    Example:
        >>> pf.launch_dual_interactive(pb, ctx, resolve_parameters={"L": 1})
    """
    app = Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])
    plot_data_list, result = solve_dual_prob_and_get_all_plot_data(
        pep_builder, context, resolve_parameters
    )

    solve_dual_button = dbc.Button(
        "Solve Dual PEP Problem",
        id="solve-button",
        color="primary",
        className="me-1",
        style={"margin-bottom": "5px"},
    )
    associated_constraint_div = html.Div(
        children="Associated Constraint",
        id="constraint-name-output-div",
        style={
            "border": "2px solid black",
            "padding": "2px",
            "margin": "2px",
            "text-align": "center",
            "width": "200px",
        },
    )
    relation_dropdown = html.Div(
        dcc.Dropdown(
            id="relation-dropdown",
            options=[
                {"label": "le", "value": "le"},
                {"label": "ge", "value": "ge"},
                {"label": "eq", "value": "eq"},
                {"label": "lt", "value": "lt"},
                {"label": "gt", "value": "gt"},
            ],
            value=None,
            placeholder="Relation",
            style={"width": "100px"},
        )
    )
    float_input = dcc.Input(
        id="float-input",
        type="number",
        placeholder="Enter a float",
        debounce=True,
        value=None,
        style={"width": "125px"},
    )
    add_constraint_button = dbc.Button(
        "Add Constraint",
        id="add-dual-constraint-button",
        color="primary",
        className="me-1",
        style={"margin-bottom": "5px"},
    )
    remove_all_constraint_button = dbc.Button(
        "Remove All Constraints",
        id="remove-dual-constraint-button",
        color="primary",
        className="me-1",
        style={"margin-bottom": "5px"},
    )
    display_row = dbc.Row(
        [
            # Column 1: The scatter plots of dual variables.
            dbc.Col(
                [
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
                    solve_dual_button,
                    dbc.Row(html.H3("Add Constraint to Dual Variable:")),
                    dbc.Row(
                        html.Div(
                            style={
                                "display": "flex",
                                "gap": "10px",
                                "flexDirection": "row",
                                "alignItems": "center",
                            },
                            children=[
                                associated_constraint_div,
                                relation_dropdown,
                                float_input,
                                add_constraint_button,
                                remove_all_constraint_button,
                            ],
                        )
                    ),
                    dbc.Row(html.H3("Constraints on Dual Variables:")),
                    dcc.Loading(
                        dbc.Card(
                            id="dual-constraint-card",
                            style={"overflow-x": "auto", "overflow-y": "auto"},
                        )
                    ),
                    dcc.Loading(
                        dbc.Card(
                            id="result-card",
                            style={"height": "15vh", "overflow-y": "auto"},
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
            # For each function, store the corresponding DataFrame as a dictionary in dcc.Store.
            *dcc_store_list,
            dcc.Store(id="list-of-constraints-on-dual", data=[]),
            dcc.Store(id="old-clickData", data=[]),
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
    def solve_dual(_):
        plot_data_list, result = solve_dual_prob_and_get_all_plot_data(
            pep_builder, context, resolve_parameters
        )
        with np.printoptions(precision=3, linewidth=500, suppress=True):
            result_card = dbc.CardBody(
                [
                    html.H3(f"Optimal Value: {result.opt_value:.4g}"),
                    html.H3(f"Solver Status: {result.solver_status}"),
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
        figs = []
        df_data = []
        psd_dv_data = []

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
        Output("constraint-name-output-div", "children"),
        Output("old-clickData", "data"),
        Input({"type": "interactive-scatter", "index": ALL}, "clickData"),
        Input("constraint-name-output-div", "children"),
        State("old-clickData", "data"),
        prevent_initial_call=True,
    )
    def update_constraint_name_output_div(clickData, prev_constraint, prev_clickData):
        for index in clickData:
            if index is not None and index not in prev_clickData:
                return index["points"][0]["customdata"][0], clickData
        return dash.no_update, dash.no_update

    @dash.callback(
        Output("dual-constraint-card", "children", allow_duplicate=True),
        Output("list-of-constraints-on-dual", "data", allow_duplicate=True),
        Input("add-dual-constraint-button", "n_clicks"),
        State("constraint-name-output-div", "children"),
        State("relation-dropdown", "value"),
        State("float-input", "value"),
        State("list-of-constraints-on-dual", "data"),
        prevent_initial_call=True,
    )
    def add_constraints_dual_vars(n_clicks, constraint_name, op, val, data):
        if op is None:
            return dash.no_update
        if val is None:
            return dash.no_update
        if constraint_name == "Associated Constraint":
            return dash.no_update
        pep_builder.add_dual_val_constraint(constraint_name, op, float(val))
        data.append(
            json.dumps(
                {
                    "constraint_name": constraint_name,
                    "relation": op,
                    "value": float(val),
                }
            )
        )
        dual_constraint_card = generate_dual_constraint_list_cardbody(data)

        return dual_constraint_card, data

    @dash.callback(
        Output("dual-constraint-card", "children", allow_duplicate=True),
        Output("list-of-constraints-on-dual", "data", allow_duplicate=True),
        Input("remove-dual-constraint-button", "n_clicks"),
        State("list-of-constraints-on-dual", "data"),
        prevent_initial_call=True,
    )
    def remove_all_constraints_dual_vars(n_clicks, data):
        pep_builder.dual_val_constraint.clear()
        data = []
        dual_constraint_card = generate_dual_constraint_list_cardbody(data)

        return dual_constraint_card, data

    @dash.callback(
        Output("dual-constraint-card", "children", allow_duplicate=True),
        Output("list-of-constraints-on-dual", "data", allow_duplicate=True),
        Input(
            {"type": "remove-specific-dual-constraint-button", "index": ALL}, "n_clicks"
        ),
        State("list-of-constraints-on-dual", "data"),
        prevent_initial_call=True,
    )
    def remove_one_constraint_dual_vars(n_clicks_list, data):
        for index, n_clicks in enumerate(n_clicks_list):
            if n_clicks is not None:
                constraint_dict = json.loads(data[index])
                constraint_name = constraint_dict["constraint_name"]
                op = constraint_dict["relation"]
                value = constraint_dict["value"]
                pep_builder.dual_val_constraint[constraint_name].remove((op, value))
                data.remove(data[index])
                dual_constraint_card = generate_dual_constraint_list_cardbody(data)
                return dual_constraint_card, data

        return dash.no_update, dash.no_update

    app.run(debug=True, port=port)
