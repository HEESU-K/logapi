from flask import Flask
from app.models import init_db, init_access_log_db, init_error_log_db
from blueprint.getlogs import getlogs_bp
from blueprint.viewlogs import viewlogs_bp


# 데이터베이스 초기화
init_db()
init_access_log_db()
init_error_log_db()

app = Flask(__name__)

# 애플리케이션 실행
#app = create_app()
if __name__ == "__main__":
    app.run(debug=True)

