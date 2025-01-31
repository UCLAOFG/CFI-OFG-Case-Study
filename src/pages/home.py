from dash import Dash, html, dcc, callback, Output, Input, State, register_page
import plotly.express as px
import pandas as pd
import dash_bootstrap_components as dbc
import numpy as np
import plotly.graph_objects as go
import re
import pathlib

from data import df, dfnz2
from pages.tab1 import *
from pages.tab2 import *


# import dash_auth
# import dash_mantine_components as dmc

register_page(__name__, title="Data Simulation", path="/")

layout = html.Div(
    [
        dbc.Row([dbc.Col(navbar)], className="mb-4"),
        dcc.Tabs(
            id="tabs-styled-with-props",
            value="tab-1",
            children=[
                dcc.Tab(
                    label="Environmental Disclosure and Performance Metrics",
                    value="tab-1",
                ),
                dcc.Tab(label="Climate Strategy Index", value="tab-2"),
            ],
            colors={"border": "white", "primary": "#FDE900", "background": "#FDE900"},
        ),
        html.Div(id="tabs-content-props"),
    ]
)


def register_callbacks(app):
    register_tab1_callbacks(app)
    register_tab2_callbacks(app)

    @app.callback(
        Output("tabs-content-props", "children"),
        Input("tabs-styled-with-props", "value"),
    )
    def render_content(tab):
        if tab == "tab-1":
            return tab1
        elif tab == "tab-2":
            return tab2
