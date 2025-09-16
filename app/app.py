from flask import Flask, render_template
from models import db
from routes import register_blueprints

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///alberdi.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.secret_key = "clave-secreta"

db.init_app(app)

@app.route("/")
@app.route("/inicio")
def inicio():
    return render_template("inicio.html")

@app.errorhandler(404)
def not_found(e):
    return render_template("404.html")

register_blueprints(app)

if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    app.run(host="0.0.0.0", port=5000)
