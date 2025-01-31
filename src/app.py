from dash import Dash, html, dcc, callback, Output, Input, State, page_container
import plotly.express as px
import pandas as pd
import dash_bootstrap_components as dbc
import numpy as np
import plotly.graph_objects as go
import re

# import dash_auth
# import dash_mantine_components as dmc

external_style = [
    "https://maxcdn.bootstrapcdn.com/font-awesome/4.7.0/css/font-awesome.min.css"
]

app = Dash(
    __name__,
    use_pages=True,
    suppress_callback_exceptions=True,
    external_stylesheets=[dbc.themes.COSMO, external_style],
)
app.title = "Center for Impact Case Study"
server = app.server

from pages.home import register_callbacks

# auth = dash_auth.BasicAuth(
#     app,
#     {'nimagna': 'uclacfi',
#      'nimagna2':'uclacfi2'}
# )

pd.options.mode.chained_assignment = None

app.layout = html.Div([page_container])  # This renders the layout of the current page

register_callbacks(app)


if __name__ == "__main__":
    app.run(debug=True, port=8000)
