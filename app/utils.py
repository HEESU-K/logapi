import smtplib
from email.mime.text import MIMEText

import re
import sqlite3

def send_error_alert(error_count):
    if error_count > Config.ALERT_THRESHOLD:
        msg = MIMEText("Error count has exceeded the threshold.")
        msg["Subject"] = "Alert: High Error Rate"
        with smtplib.SMTP("smtp.example.com") as server:
            server.login("user@example.com", "password")
            server.sendmail("from@example.com", "admin@example.com", msg.as_string())