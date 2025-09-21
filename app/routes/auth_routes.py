from flask import Blueprint, render_template, request, redirect, url_for, session, flash
from werkzeug.security import check_password_hash
from app.models import Cuenta

auth_bp = Blueprint('auth', __name__)
   

@auth_bp.route("/")
@auth_bp.route("/inicio ")
def inicio():
    if 'username' not in session:
        return redirect(url_for('auth.login'))
    return render_template('inicio.html')

@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    error = None
    if request.method == "POST":
        email = request.form.get("email")
        contraseña = request.form.get("contraseña")

        # Buscar cuenta por email
        cuenta = Cuenta.query.filter_by(email=email).first()

        if cuenta:
            # Comparar hash de contraseña
            if check_password_hash(cuenta.contrasenia, contraseña):
                session['username'] = cuenta.nombre_usuario
                return redirect(url_for("auth.inicio"))
            else:
                error = "Contraseña incorrecta ❌"
        else:
            error = "Email no encontrado ❌"

    return render_template("login.html", error=error)


# Cerrar sesión
@auth_bp.route("/logout")
def salir():
    session.pop('username', None)  # elimina la sesión si existe
    flash("Has cerrado sesión correctamente", "success")
    return redirect(url_for("auth.login"))

# Funcion que ya tiene flask para los errores

@auth_bp.errorhandler(404)
def not_found(e):
  return render_template("404.html")