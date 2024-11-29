# blueprint/viewlog/route.py
from flask import Blueprint, Flask, jsonify, render_template, render_template_string, request
from config import Config
from datetime import datetime
import dash
from dash import dash_table
from dash import dcc, html, Input, Output
import sqlite3
import pandas as pd
import json

import plotly.graph_objs as go
import plotly.io as pio
import plotly.express as px
import plotly.utils

import os, sys
sys.path.append(os.path.dirname(os.path.abspath(os.path.dirname(__file__))))

viewlogs_bp = Blueprint('viewlogs', __name__, url_prefix='/viewlogs')
conn = sqlite3.connect(Config.DB_PATH, check_same_thread=False)

# 일자별 로그 발생 빈도 분석
@viewlogs_bp.route('/log_frequency')
def logs_frequency():
    conn = sqlite3.connect(Config.DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute("SELECT timestamp FROM access_log")
    rows = cursor.fetchall()
    conn.close()

    dates = [datetime.strptime(row[0], "%d/%b/%Y:%H:%M:%S").date() for row in rows]
    date_counts = pd.Series(dates).value_counts().sort_index()

    df = pd.DataFrame(date_counts, columns = ["count"]).reset_index()
    df.columns = ["date", "count"]
    return df

# 일자별 로그 발생 빈도 시각화
@viewlogs_bp.route('/log_frequency_chart')
def logs_frequency_chart():
    try:
        df = logs_frequency()
        dates = df["date"].astype(str)
        counts = df["count"]

        fig = go.Figure(date=[
            go.Bar(x=dates, y=counts, marker_color="royalblue")
        ])
        fig.update_layout(
            title="Log Frequency",
            xaxis_title="Date",
            yaxis_title="Log Count",
            template="plotly_white",
            xaxis_tickangle=45
        )

        graph_html = pio.to_html(fig, full_html=False)
        return render_template("log_frequency.html", graph_html=graph_html)
    except Exception as e:
        return f"Error {e}", 500


# 에러 레벨 분포 분석
def get_error_distribution():
    query = '''
        SELECT error_level, COUNT(*) AS count
        FROM error_log 
        GROUP BY error_level
        ORDER BY count DESC;
    '''
    df = pd.read_sql_query(query, conn)
    return df
    

# 에러 레벨 분포 시각화
def error_distribution_chart(app):
    dash_app = dash.Dash(__name__, server=app, url_base_pathname="/viewlogs/error_distribution_chart/")

    df = get_error_distribution()
    
    fig = px.bar(
        df,
        x="error_level",
        y="count",
        title="Error Levels Count",
        labels={"error_level": "Error Level", "count": "Count"},
        color="error_level",
    )

    dash_app.layout = html.Div([
        html.H1("Error Log Dashboard", style={'textAlign': 'center'}),
        dcc.Graph(figure=fig),
    ])
    


def load_error_logs():
    query = "SELECT * FROM error_log"
    df = pd.read_sql_query(query, conn)
    
    try:
        df['timestamp'] = pd.to_datetime(
            df['timestamp'], 
            format='%a %b %d %H:%M:%S.%f',
            errors='coerce'
            )
    except Exception as e:
        print("포멧 변경 실패", e)
        df['timestamp'] = pd.NaT

    df = df.dropna(subset=['timestamp'])

    return df


def error_log_graph(app):
    # 대시보드 레이아웃
    dash_app_main  = dash.Dash(__name__, server=app, url_base_pathname="/viewlogs/error_log_graph/")
    dash_app_main.layout = html.Div([
        html.H1("Error Log Dashboard", style={'text-align': 'center'}),
        html.Label("Select Error Level"),
        dcc.Dropdown(
            id='error-level-filter',
            options=[
                {'label': 'All', 'value': 'All'},
                {'label': 'alert', 'value': 'alert'},
                {'label': 'crit', 'value': 'crit'},
                {'label': 'debug', 'value': 'debug'},
                {'label': 'emerg', 'value': 'emerg'},
                {'label': 'error', 'value': 'error'},
                {'label': 'info', 'value': 'info'},
                {'label': 'notice', 'value': 'notice'},
                {'label': 'warn', 'value': 'warn'},
            ],
            value='All',
            clearable=False
        ),
        # 시간대별 정렬 슬라이더
        html.Label("Select Time Range (Hourly)"),
        dcc.RangeSlider(
            id="time-range-slider",
            min=0,
            max=23,
            step=1,
            marks={i: f"{i}:00" for i in range(24)},
            value=[0, 23]
        ),
        dcc.Graph(id='error-log-graph')
    ])

    # 사용자 입력에 따라 그래픽 업데이트
    @dash_app_main.callback(
        Output('error-log-graph', 'figure'),
        [Input('error-level-filter', 'value'),
         Input('time-range-slider', 'value')]
    )
    def update_graph(selected_level, selected_time_range):
        df = load_error_logs()

        if selected_level != "All":
            df = df[df['error_level'] == selected_level]

        df['hour'] = df['timestamp'].dt.hour
        df = df[(df['hour'] >= selected_time_range[0]) & (df['hour'] <= selected_time_range[1])]

        fig=px.histogram(
            df,
            x='hour',
            color='error_level',
            title='Error Logs by Hour and Level',
            labels={'hour': 'Hour of the Day', 'count': 'Error Count'},
            barmode='group',
            template="plotly_white",
            text_auto=True
        )
        return fig

def load_logs(query):
    df = pd.read_sql_query(query, conn)
    return df

def show_logs(app):
    dash_app  = dash.Dash(__name__, server=app, url_base_pathname="/viewlogs/show_logs/")
    dash_app.layout = html.Div([
        html.H1("Log Dashboard", style={'text-align': 'center'}),
        html.Div([
            html.Button("Access Logs", id="access-log-btn", n_clicks=0),
            html.Button("Error Logs", id="error-log-btn", n_clicks=0),
        ], style={'text-align': 'center'}),
        html.Div(id='selected-log-type', style={'text-align': 'center'}),
        dash_table.DataTable(
            id='log-table',
            columns=[],
            data=[],
            style_table={'overflowX': 'auto'},
            style_cell={'text-align': 'left', 'padding': '10px'},
            style_header={'fontWeight': 'bold'},
        )
    ])

    @dash_app.callback(
        [Output('selected-log-type', 'children'),
        Output('log-table', 'columns'),
        Output('log-table', 'data')],
        [Input('access-log-btn', 'n_clicks'),
        Input('error-log-btn', 'n_clicks')]
    )
    def update_log_table(access_log_clicks, error_log_clicks):
        ctx = dash.callback_context
        if not ctx.triggered:
            triggered_button = None
        else:
            triggered_button = ctx.triggered[0]['prop_id'].split('.')[0]

        if triggered_button == "access-log-btn":
            query = "SELECT * FROM access_log"
            df = load_logs(query)
            selected_log_type = "Access Logs"
        elif triggered_button == "error-log-btn":
            query = "SELECT * FROM error_log"
            df = load_logs(query)
            selected_log_type = "Error Logs"
        else:
            df = pd.DataFrame()
            selected_log_type = "No logs selected"

        # 테이블의 컬럼과 데이터 설정
        columns = [{"name": col, "id": col} for col in df.columns] if not df.empty else []
        data = df.to_dict('records') if not df.empty else []

        return selected_log_type, columns, data


        
