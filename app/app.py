from dash import Dash, Input, Output, html, dcc
import plotly.express as px
import pandas as pd
from morpc.census import api
app = Dash()

# assume you have a "long-form" data frame
# see https://plotly.com/python/px-arguments/ for more options

app.layout = html.Div([
    html.H1(children='Census Data Tool'),

    html.Div([
        dcc.Dropdown(
            options=api.ALL_AVAIL_ENDPOINTS,
            value=None,
            id='survey_table_dropdown'
        ),

        dcc.Dropdown(
            id='vintage_dropdown',
            value=None,
        )
    ]),
])

@app.callback(
    Output('vintage_dropdown', 'options'),
    Input('survey_table_dropdown','value'))
def set_vintage_options(selected_survey_table):
    return [api.AVAIL_VINTAGES[selected_survey_table]]

if __name__ == '__main__':
    app.run(debug=True)