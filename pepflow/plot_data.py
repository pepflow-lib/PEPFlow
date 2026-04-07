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

import attrs
import dash_bootstrap_components as dbc
import pandas as pd
import plotly
import plotly.express as px
import plotly.graph_objects as go
from dash import dcc, html

from pepflow import constants as const
from pepflow import utils

if TYPE_CHECKING:
    from pepflow.function import Function
    from pepflow.operator import Operator
    from pepflow.pep import PEPBuilder
    from pepflow.pep_result import PEPResult


plotly.io.renderers.default = "colab+vscode"
plotly.io.templates.default = "plotly_white"


def style_dual_value_table(table: dbc.Table) -> dbc.Table:
    """Apply centralized styling rules for dual-value tables.

    Current rules:
    - Shrink table width to content as much as possible.
    - Center-align table text.
    - Reduce cell padding (compact spacing).
    - Apply a subtle gray background to header cells and row-index cells.
    - Make row index cells (first body cell in each row) bold.

    Extend this function when additional table styling is needed.
    """

    # Normalize Dash children into a list so loops can stay uniform
    def as_list(node: object) -> list[object]:
        if node is None:
            return []
        if isinstance(node, (list, tuple)):
            return list(node)
        return [node]

    # Merge new style keys without dropping existing component styles
    def merge_style(component: object, extra_style: dict[str, str]) -> None:
        setattr(
            component,
            "style",
            {**(getattr(component, "style", None) or {}), **extra_style},
        )

    # Set base table layout/style in a type-checker-safe way
    setattr(
        table,
        "style",
        {
            "width": "auto",
            "maxWidth": "100%",
            "textAlign": "center",
            "marginBottom": "0",
        },
    )

    sections = as_list(getattr(table, "children", None))

    # Pass 1: shared styling for every cell
    for section in sections:
        for row in as_list(getattr(section, "children", None)):
            for cell in as_list(getattr(row, "children", None)):
                merge_style(
                    cell,
                    {
                        "textAlign": "center",
                        "padding": "0.35rem 0.55rem",
                        "verticalAlign": "middle",
                        "fontSize": f"{const.TABLE_CELL_FONT_REM:.2f}rem",
                    },
                )

    # Pass 2: highlight header cells (column labels)
    if sections:
        for row in as_list(getattr(sections[0], "children", None)):
            for cell in as_list(getattr(row, "children", None)):
                merge_style(cell, {"backgroundColor": "#f5f6f8"})

    # Pass 3: highlight row index cells (first cell in each body row)
    if len(sections) >= 2:
        for row in as_list(getattr(sections[1], "children", None)):
            cells = as_list(getattr(row, "children", None))
            if not cells:
                continue
            merge_style(
                cells[0],
                {
                    "fontWeight": "700",
                    "backgroundColor": "#f5f6f8",
                },
            )
    return table


@attrs.frozen
class PlotData:
    func_or_oper: Function | Operator
    df_dict: dict[str, pd.DataFrame]
    fig_dict: dict[str, go.Figure]
    psd_dv_dict: dict[str, str]
    pep_type: utils.PEPType

    def dual_matrix_to_tab(self, name: str, df: pd.DataFrame) -> html.Div:
        table = dbc.Table.from_dataframe(  # ty: ignore
            utils.get_pivot_table_of_dual_value(df, num_decs=3),
            bordered=True,
            index=True,
        )
        table = style_dual_value_table(table)
        return html.Div(
            table,
            id={
                "type": "dual-value-display",
                "index": f"{self.func_or_oper.tag}-{name}",
            },
            style={"marginLeft": "36px"},
        )

    def make_list_of_scalar_constraint_tabs(self) -> list[dbc.Tab]:
        list_of_tabs = [
            dbc.Tab(
                html.Div(
                    [
                        html.P(
                            "Interactive Heat Map:",
                            style={
                                "marginTop": "10px",
                                "marginBottom": "-30px",
                                "fontWeight": "700",
                                "fontSize": f"{const.SECTION_LABEL_FONT_REM:.2f}rem",
                                "position": "relative",
                                "zIndex": "1",
                            },
                        ),
                        dcc.Graph(
                            id={
                                "type": "interactive-scatter",
                                "index": f"{self.func_or_oper.tag}-{name}",
                            },
                            figure=fig,
                            config={"displayModeBar": False},
                        ),
                        html.P(
                            "Dual Value Matrix:",
                            style={
                                "fontWeight": "700",
                                "fontSize": f"{const.SECTION_LABEL_FONT_REM:.2f}rem",
                            },
                        ),
                        self.dual_matrix_to_tab(name, df),
                    ]
                ),
                label=f"{name}",
                label_style={"fontSize": f"{const.TAB_LABEL_FONT_REM:.2f}rem"},
                tab_id=f"{self.func_or_oper.tag}-{name}-interactive-constraint-tab",
            )
            for (name, fig), (_, df) in zip(self.fig_dict.items(), self.df_dict.items())
        ]
        return list_of_tabs

    def make_list_of_psd_constraint_tabs(self) -> list[dbc.Tab]:
        list_of_tabs = [
            dbc.Tab(
                html.Div(
                    [
                        html.P(
                            "Dual Value Matrix:",
                            style={
                                "fontWeight": "700",
                                "fontSize": f"{const.SECTION_LABEL_FONT_REM:.2f}rem",
                            },
                        ),
                        html.Pre(
                            psd_dv,
                            id={
                                "type": "psd-display",
                                "index": f"{self.func_or_oper.tag}-{name}",
                            },
                        ),
                    ]
                ),
                label=f"{name}",
                label_style={"fontSize": f"{const.TAB_LABEL_FONT_REM:.2f}rem"},
                tab_id=f"{self.func_or_oper.tag}-{name}-interactive-constraint-tab",
            )
            for name, psd_dv in self.psd_dv_dict.items()
        ]
        return list_of_tabs

    def plot_data_to_tab(self) -> dbc.Tab:
        list_sc_tabs = self.make_list_of_scalar_constraint_tabs()
        list_psd_tabs = self.make_list_of_psd_constraint_tabs()
        if len(list_sc_tabs) + len(list_psd_tabs) > 1:
            tabs = dbc.Tab(
                children=[
                    dbc.Tabs(
                        [
                            *self.make_list_of_scalar_constraint_tabs(),
                            *self.make_list_of_psd_constraint_tabs(),
                        ],
                    )
                ],
                label=f"{self.func_or_oper.tag} Interpolation Conditions",
                label_style={"fontSize": f"{const.TAB_LABEL_FONT_REM:.2f}rem"},
            )
        else:
            tabs = dbc.Tab(
                children=[
                    html.Div(
                        [
                            *self.make_list_of_scalar_constraint_tabs(),
                            *self.make_list_of_psd_constraint_tabs(),
                        ],
                    )
                ],
                label=f"{self.func_or_oper.tag} Interpolation Conditions",
                label_style={"fontSize": f"{const.TAB_LABEL_FONT_REM:.2f}rem"},
            )
        return tabs

    def df_dict_to_dcc_store_list(self) -> list[dcc.Store]:
        dcc_store_list = []
        for name, df in self.df_dict.items():
            dcc_store_list.append(
                dcc.Store(
                    id={
                        "type": "dataframe-store",
                        "index": f"{self.func_or_oper.tag}-{name}",
                    },
                    data=(self.func_or_oper.tag, df.to_dict("records"), df.attrs),
                )
            )
        return dcc_store_list

    def psd_dv_dict_to_dcc_store_list(self) -> list[dcc.Store]:
        dcc_store_list = []
        for name, psd_dv in self.psd_dv_dict.items():
            dcc_store_list.append(
                dcc.Store(
                    id={
                        "type": "psd-dv-store",
                        "index": f"{self.func_or_oper.tag}-{name}",
                    },
                    data=(
                        self.func_or_oper.tag,
                        psd_dv,
                    ),
                )
            )
        return dcc_store_list

    @classmethod
    def from_func_or_oper_pep_result_and_builder(
        cls,
        func_or_oper: Function | Operator,
        pep_result: PEPResult,
        pep_builder: PEPBuilder,
    ) -> PlotData:
        constraint_data = pep_result.context.get_constraint_data(func_or_oper)
        pd_dict = constraint_data.process_scalar_constraint_with_result(pep_result)

        df_dict = {}
        fig_dict = {}
        for name, df in pd_dict.items():
            df["constraint"] = df.constraint_name.map(
                lambda x: "inactive"
                if x in pep_builder.relaxed_constraints
                else "active"
            )

            fig = px.scatter(
                df,
                x="col",
                y="row",
                color="dual_value",
                symbol="constraint",
                symbol_map={"inactive": "x-open", "active": "circle"},
                custom_data="constraint_name",
                color_continuous_scale="Viridis",
                range_color=[0, df["dual_value"].max()],
            )
            fig.update_layout(yaxis=dict(autorange="reversed"))
            fig.update_traces(marker=dict(size=15))
            fig.update_layout(
                coloraxis_colorbar=dict(
                    title_text="<b>Dual Value</b>",
                    yanchor="top",
                    y=1.06,
                    x=1.3,
                    ticks="outside",
                )
            )
            fig.update_xaxes(
                tickmode="array",
                tickvals=list(range(len(df.attrs["order_col"]))),
                ticktext=df.attrs["order_col"],
                tickfont=dict(size=const.GRAPH_FONT_SIZE),
                zeroline=False,
            )
            fig.update_yaxes(
                tickmode="array",
                tickvals=list(range(len(df.attrs["order_row"]))),
                ticktext=df.attrs["order_row"],
                tickfont=dict(size=const.GRAPH_FONT_SIZE),
                zeroline=False,
            )
            match pep_result.pep_type:
                case utils.PEPType.PRIMAL:
                    fig.update_layout(showlegend=True)
                case utils.PEPType.DUAL:
                    fig.update_layout(showlegend=False)
            fig.update_layout(
                font=dict(size=const.GRAPH_FONT_SIZE),
                legend_title_text="<b>Constraint</b>",
                legend_title_font=dict(size=const.LEGEND_TITLE_FONT_SIZE),
                legend=dict(yanchor="top", y=1.0),
                coloraxis_colorbar=dict(
                    title_text="<b>Dual Value</b>",
                    yanchor="top",
                    y=1.01,
                    x=1.3,
                    ticks="outside",
                    tickfont=dict(size=const.GRAPH_FONT_SIZE),
                    title_font=dict(size=const.LEGEND_TITLE_FONT_SIZE),
                ),
            )

            fig.for_each_xaxis(lambda x: x.update(title=""))
            fig.for_each_yaxis(lambda y: y.update(title=""))
            df_dict[name] = df
            fig_dict[name] = fig

        psd_dv_dict = {}
        for name, psd_dv in pep_result.get_matrix_constraint_dual_values(
            func_or_oper
        ).items():
            psd_dv_dict[name] = str(psd_dv)

        return cls(
            func_or_oper=func_or_oper,
            df_dict=df_dict,
            fig_dict=fig_dict,
            psd_dv_dict=psd_dv_dict,
            pep_type=pep_result.pep_type,
        )
