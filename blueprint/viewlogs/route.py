# blueprint/viewlog/route.py
from flask import Blueprint, Flask, jsonify, render_template
from config import Config
from datetime import datetime

import sqlite3
import pandas as pd

import plotly.graph_objs as go
import plotly.io as pio
import plotly.express as px


viewlogs_bp = Blueprint('viewlogs', __name__, url_prefix='/viewlogs')

# 일자별 로그 발생 빈도 분석 (access_log)
@viewlogs_bp.route('/')
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
            title = "Log Frequency",
            xaxis_title = "Date",
            yaxis_title = "Log Count",
            template ="plotly_white",
            xaxis_tickangle = 45
        )

        graph_html = pio.to_html(fig, full_html=False)
        return render_template("log_frequency.html", graph_html=graph_html)
    except Exception as e:
        return f"Error {e}", 500


# 에러 레벨 분포 분석 (error_log)
@viewlogs_bp.route('/error_distribution')
def get_error_distribution():
    conn = sqlite3.connect(Config.DB_PATH)
    cursor = conn.cursor()
    query = '''
        SELECT error_level, COUNT(*) AS COUNT 
        FROM error_log 
        GROUP BY error_level
        ORDER BY count DESC;
        '''
    
    cursor.execute(query)
    result = cursor.fetchall()
    conn.close()

    return [{"error_level": error_level, "count": count} for error_level, count in result]

# 에러 레벨 분포 시각화
@viewlogs_bp.route('/templates//error_distribution_chart', methods=['GET'])
def error_distribution_chart():
    try:
        data = get_error_distribution()
        error_levels = [item["error_level"] for item in data]
        counts = [item["count"] for item in data]

        fig = go.Figure(data=[
            go.Bar(x=error_levels, y=counts, marker_color=px.colors.qualitative.Plotly)
        ])
        fig.update_layout(
            title = "Error Level Distribution",
            xaxis_title = "Log Level",
            yaxis_title = "Count",
            template = "plotly_white"
        )

        graph_html = pio.to_html(fig, full_html=False)
        return render_template("/templates/error_distribution_chart.html", graph_html=graph_html)
    except Exception as e:
        return jsonify({"status": "error", "meessage": str(e)}), 500