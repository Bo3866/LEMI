from flask import Flask, render_template, request, jsonify

from safety.routes import safety_bp

from data_fetch.geocoding import geocode_address

app = Flask(__name__)


@app.route("/")
def index():
    return render_template(
        "map.html"
    )


app.register_blueprint(
    safety_bp
)

@app.route('/api/geocode', methods=['POST'])
def handle_geocode():
    data = request.get_json() or {}
    address = data.get('address', '').strip()
    
    if not address:
        return jsonify({"status": "error", "message": "請輸入地址或地點！"}), 400

    result = geocode_address(address)
    
    if result:
        # 【關鍵】包裝成前端想要的 { status: 'success', data: { ... } } 格式
        return jsonify({
            "status": "success",
            "data": result
        }), 200
    else:
        return jsonify({
            "status": "error",
            "message": f"找不到地址：{address}"
        }), 400

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
        use_reloader=False)