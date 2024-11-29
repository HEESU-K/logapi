from flask import Flask
from .getlogs.route import getlogs_bp
from .viewlogs.route import viewlogs_bp, error_log_graph, show_logs, error_distribution_chart
from .db.models import init_db, init_access_log_db, init_error_log_db


def create_app():
    app = Flask(__name__)

    # 데이터베이스 초기화
    init_db()
    init_access_log_db()
    init_error_log_db()

    # 대시보드
    error_log_graph(app)
    show_logs(app)
    error_distribution_chart(app)

    # getlogs, viewlogs 블루 프린트 등록
    app.register_blueprint(getlogs_bp)
    app.register_blueprint(viewlogs_bp)

    return app

