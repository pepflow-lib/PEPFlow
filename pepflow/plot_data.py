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

from pepflow import utils

if TYPE_CHECKING:
    from pepflow.function import Function
    from pepflow.operator import Operator
    from pepflow.pep import PEPBuilder
    from pepflow.pep_result import PEPResult


plotly.io.renderers.default = "colab+vscode"
plotly.io.templates.default = "plotly_white"


@attrs.frozen
class PlotData:
    func_or_oper: Function | Operator
    df_dict: dict[str, pd.DataFrame]
    fig_dict: dict[str, go.Figure]
    psd_dv_dict: dict[str, str]
    pep_type: utils.PEPType

    def dual_matrix_to_tab(self, name: str, df: pd.DataFrame) -> html.Div:
        return html.Div(
            dbc.Table.from_dataframe(  # ty: ignore
                utils.get_pivot_table_of_dual_value(df, num_decs=3).reset_index(),
                bordered=True,
            ),
            id={
                "type": "dual-value-display",
                "index": f"{self.func_or_oper.tag}-{name}",
            },
        )

    def make_list_of_scalar_constraint_tabs(self) -> list[dbc.Tab]:
        list_of_tabs = [
            dbc.Tab(
                html.Div(
                    [
                        html.P("Interactive Heat Map:"),
                        dcc.Graph(
                            id={
                                "type": "interactive-scatter",
                                "index": f"{self.func_or_oper.tag}-{name}",
                            },
                            figure=fig,
                        ),
                        html.P("Dual Value Matrix:"),
                        self.dual_matrix_to_tab(name, df),
                    ]
                ),
                label=f"{name}",
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
                        html.P("Dual Value Matrix:"),
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
                x="row",
                y="col",
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
                    title_text="Dual Value", yanchor="top", y=1, x=1.3, ticks="outside"
                )
            )
            fig.update_xaxes(
                tickmode="array",
                tickvals=list(range(len(df.attrs["order_row"]))),
                ticktext=df.attrs["order_row"],
            )
            fig.update_yaxes(
                tickmode="array",
                tickvals=list(range(len(df.attrs["order_col"]))),
                ticktext=df.attrs["order_col"],
            )
            match pep_result.pep_type:
                case utils.PEPType.PRIMAL:
                    fig.update_layout(showlegend=True)
                case utils.PEPType.DUAL:
                    fig.update_layout(showlegend=False)

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
