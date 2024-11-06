import sqlite3
from config import Config


def init_db():
    conn = sqlite3.connect(Config.DB_PATH)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT,
            level TEXT,
            message TEXT,
            source TEXT
        )
    ''')
    conn.commit()
    conn.close()



def init_access_log_db():
    conn = sqlite3.connect(Config.DB_PATH)
    cursor = conn.cursor()
    cursor.execute(
        '''
        CREATE TABLE IF NOT EXISTS access_log(
            id            INTEGER PRIMARY KEY AUTOINCREMENT,
            ip_address    VARCHAR(45),
            timestamp     TEXT,
            http_method   VARCHAR(10),
            url           TEXT,
            protocol      VARCHAR(10),
            status_code   INTEGER,
            response_size INTEGER,
            referer       TEXT,
            user_agent    TEXT
        )
        '''
    )

def init_error_log_db():
    conn = sqlite3.connect(Config.DB_PATH)
    cursor = conn.cursor()
    cursor.execute(
        '''
        CREATE TABLE IF NOT EXISTS error_log(
            id              INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp       TEXT,
            error_level     VARCHAR(10),
            client_ip       VARCHAR(45),
            error_message   TEXT,
            file_path       TEXT,
            referer         TEXT
        )
        '''
    )