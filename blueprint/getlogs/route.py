# blueprint/getlogs/route.py
from flask import Blueprint, request
from config import Config

import sqlite3

getlogs_bp = Blueprint('getlogs', __name__, url_prefix='/getlogs')

@getlogs_bp.route('/writedb', method=['GET'])
def insert_db():
    conn = sqlite3.connect(Config.DB_PATH)
    cursor = conn.cursor()

    with open('../../log.txt', 'r') as log:
        content = log.readlines()

    for line in content:
        logs = line.split(' ')
        date = logs[3]
        http_method = logs[5]
        protocol = logs[7]

        query = "INSERT INTO access_log (ip_address, timestamp, http_method, url, protocol, status_code, response_size) VALUES (?, ?, ?, ?, ?, ?, ?)"

        cursor.execute(query, (logs[0], date[1:], http_method[1:], logs[6], protocol[:-1], logs[8], logs[9])
        )

    conn.commit()
    conn.close()

'''
로그 검색 및 필터링
- 날짜/시간 |  키워드, 오류 메시지  |  ERROR 레벨의 로그 중 특정 ip  |  특정 범위 지정

테이터 분석 및 통계
 로그 빈도(시간대별, 일자별 로그 발생 패턴) |  로그 레벨별 분포(INFO, WARN ERROR 로그 비율 파악)
'''


# 로그 전체 검색
@getlogs_bp.route('/', methods=['GET'])
def get_logs():
    status_code = request.args.get('status_code')
    ip_address = request.args.get('ip_address')

    conn = sqlite3.connect(Config.DB_PATH)
    cursor = conn.cursor()

    query = "SELECT id, ip_address, timestamp, http_method, url, protocol, status_code, response_size FROM access_log"
    conditions = []
    params = []

    if status_code:
        conditions.append("status_code = ?")
        params.append(status_code)
    if ip_address:
        conditions.append("ip_address = ?")
        params.append(ip_address)

    if conditions:
        query += " WHERE " + " AND ".join(conditions)

    cursor.execute(query, params)
    logs = cursor.fetchall()

    log_list = [
        {
            "id": log[0],
            "ip_address": log[1],
            "timestamp": log[2],
            "http_method": log[3],
            "url": log[4],
            "protocol": log[5],
            "status_code": log[6],
            "response_size": log[7],
        }
        for log in logs
    ]
    conn.close()
    return log_list


