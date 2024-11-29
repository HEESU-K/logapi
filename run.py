from blueprint import create_app

# 애플리케이션 실행
#app = create_app()
if __name__ == "__main__":
    app = create_app()
    app.run(debug=True)
