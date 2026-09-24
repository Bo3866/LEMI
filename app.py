from flask import Flask, render_template

from safety.accident.routes import (
    accident_bp
)


app = Flask(__name__)


# ==============================
# 首頁
# ==============================

@app.route("/")
def index():

    return render_template(
        "map.html"
    )


# ==============================
# 註冊安全資料 API
# ==============================

app.register_blueprint(
    accident_bp
)


# ==============================
# 啟動 Flask
# ==============================

if __name__ == "__main__":

    app.run(
        debug=True,
        host="127.0.0.1",
        port=5000,
        use_reloader=False
    )