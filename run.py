from flask import Flask
from app.models import init_db, init_access_log_db, init_error_log_db
from blueprint.getlogs.route import getlogs_bp
from blueprint.viewlogs.route import viewlogs_bp


# 데이터베이스 초기화
init_db()
init_access_log_db()
init_error_log_db()

app = Flask(__name__)
app.register_blueprint(getlogs_bp)
app.register_blueprint(viewlogs_bp)

# 애플리케이션 실행
#app = create_app()
if __name__ == "__main__":
    app.run(debug=True)

