# blueprint/getlogs/route.py
from flask import Blueprint, request
from config import Config

import sqlite3
import subprocess
import os
import re

getlogs_bp = Blueprint('getlogs', __name__, url_prefix='/getlogs')

# 로그 데이터 가져오기
def read_logs(file_path):
    process = subprocess.Popen(['tail', '-f', file_path], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    for line in iter(process.stdout.readlines, b''):
        yield line.decode('utf-8').strip()

# txt 파일 초기화
def initialize_log_file(): 
    with open("access_log.txt", "w") as access_file, open("error_log.txt", "w") as error_file:
        access_file.write("")
        error_file.write("")

# 로그 데이터 텍스트 파일에 저장
def save_to_txt(file_name, log_data):
    with open(file_name, "a") as file:
        file.write(log_data + "\n")

# 에러 로그와 접근 로그를 분류 후 저장
def classify_and_save_logs(log_line):
    if re.search(r' (2\d{2}|3\d{2}) ', log_line):
        save_to_txt("access_log.txt", log_line)
        insert_db()
        initialize_log_file()
    elif any(keyword in log_line.lower() for keyword in ["alert", "crit", "debug", "emerg", "error", "info", "notice", "warn"]):
        save_to_txt("error_log.txt", log_line)
        insert_db_error()
        initialize_log_file()

@getlogs_bp.route('/read_logs')
def process_logs():
    log_file_path = "//" # 로그 파일 경로 지정 필요
    initialize_log_file()
    try:
        for log_line in read_logs(log_file_path):
            classify_and_save_logs(log_line)
    except KeyboardInterrupt:
        print("로그 수집 중단")


@getlogs_bp.route('/writedb')
def insert_db():
    conn = sqlite3.connect(Config.DB_PATH)
    cursor = conn.cursor()

    with open('access_log.txt', 'r') as log:
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

# error log DB에 저장
@getlogs_bp.route('/writedb_error')
def insert_db_error():
    conn = sqlite3.connect(Config.DB_PATH)
    cursor = conn.cursor()

    with open('error_log.txt', 'r') as log:
        content = log.readlines()

    for line in content:
        timestamp = line[1:27]
        error_level = line[32:line.index(']', 32)]
        client_ip_start = line.index("[client ") + len("[client ")
        client_ip_end = line.index("]", client_ip_start)
        client_ip = line[client_ip_start:client_ip_end]
        message = line[client_ip_end + 2:]

        query = "INSERT INTO error_log (timestamp, error_level, client_ip, error_message) VALUES (?, ?, ?, ?)"

        cursor.execute(query, (timestamp, error_level, client_ip, message)
        )

    conn.commit()
    conn.close()


# 로그 전체 검색
@getlogs_bp.route('/')
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


@getlogs_bp.route('/filter')
def get_logs_filter():
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


