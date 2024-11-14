from dash import Dash, dcc, html
from run import logs_frequency
import plotly.express as px
import pandas as pd


df = logs_frequency()

app = Dash(__name__)

fig = px.line(df, x='date', y='count', title='Log Frequency')

app.layout = html.Div([
    html.H1("Log frequency by day"),
    dcc.Graph(id='line-plot', figure=fig)
])

if __name__ == "__main__":
    app.run_server(debug=True)