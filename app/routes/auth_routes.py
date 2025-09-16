from flask import Blueprint, render_template, request, redirect, url_for, session, flash
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from app.models import Evento, Cliente, ResponsableLlave, Pago, Cuenta, db

auth_bp = Blueprint('auth', __name__)

   

@app.route("/")
@app.route("/inicio ")
def inicio():
    if 'username' not in session:
        return redirect(url_for('main.ingresar'))
    return render_template('inicio.html')   


# Login
@app.route("/login", methods=["GET", "POST"])
def login():
    error = None
    if request.method == "POST":
        email = request.form.get("email")
        contraseña = request.form.get("contraseña")

        # Buscar cuenta por nombre de usuario
        cuenta = Cuenta.query.filter_by(email=email).first()

        if cuenta:
            if cuenta.contraseña == contraseña:
                flash(f"Bienvenido {cuenta.nombre_usuario} ✅", "success")
                return redirect(url_for("inicio"))
            else:
                error = "Contraseña incorrecta ❌"
        else:
            error = "Email no encontrado ❌"

    return render_template("login.html", error=error)

#cerrar sesion
def salir():
    return 0

# Funcion que ya tiene flask para los errores

@auth_bp.errorhandler(404)
def not_found(e):
  return render_template("404.html")