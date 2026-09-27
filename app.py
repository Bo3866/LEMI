from flask import Flask, render_template

from safety.routes import safety_bp


app = Flask(__name__)


@app.route("/")
def index():
    return render_template(
        "map.html"
    )


app.register_blueprint(
    safety_bp
)


print("目前 Flask 路由：")

for rule in app.url_map.iter_rules():
    print(
        rule,
        "->",
        rule.endpoint
    )


if __name__ == "__main__":

    app.run(
        debug=True,
        host="127.0.0.1",
        port=5000,
        use_reloader=False
    )