# blueprint/viewlog/route.py
from flask import Blueprint
from config import Config
from datetime import datetime

import sqlite3
import pandas as pd

viewlogs_bp = Blueprint('viewlogs', __name__, url_prefix='viewlogs')

# 일자별 로그 발생 빈도 분석 및 시각화
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

