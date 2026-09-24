@app.route("/")
def index():
    return render_template("map.html")