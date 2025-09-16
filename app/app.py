from flask import Flask, render_template, request, redirect, url_for, flash
from sqlalchemy.exc import SQLAlchemyError
from models import db, Cuenta 

app = Flask(__name__)

#credenciales admi para produccion
# admin|admin@alberdi.com|admin|admin|1234

# las intacacias de la base de datos estan en instance/alberdi.db
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///alberdi.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db.init_app(app)


@app.route("/")
@app.route("/inicio ")
def inicio():
    return render_template('inicio.html')


app.secret_key = "clave-secreta"  # Necesaria para usar flash()


@app.route("/login", methods=["GET", "POST"])
def login():
    error = None
    if request.method == "POST":
        email = request.form.get("email")
        contraseña = request.form.get("contraseña")

        # Buscar cuenta por nombre de usuario
        cuenta = Cuenta.query.filter_by(email=email).first()

        if cuenta:
            if cuenta.password == contraseña:
                flash(f"Bienvenido {cuenta.nombre_usuario} ✅", "success")
                return redirect(url_for("inicio"))
            else:
                error = "Contraseña incorrecta ❌"
        else:
            error = "Email no encontrado ❌"

    return render_template("login.html", error=error)


@app.route("/eventos")
def eventos():
    return render_template('eventos.html')

@app.route("/ingresos")
def ingresos():
    return render_template('ingresos.html')

@app.route("/cuentas")
def cuentas():
    return render_template('cuentas.html')

# esta es una función que ya tiene flask para los errores
@app.errorhandler(404)
def not_found(e):
  return render_template("404.html")


if __name__ == "__main__":
    with app.app_context():
        db.create_all()   # crea las tablas si no existen
    app.run(host="0.0.0.0", port=5000)

