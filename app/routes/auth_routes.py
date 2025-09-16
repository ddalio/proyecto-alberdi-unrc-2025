from flask import Blueprint, render_template, request, redirect, url_for, session, flash
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from app.models import Evento, Cliente, ResponsableLlave, Pago, Cuenta, db

auth_bp = Blueprint('auth', __name__)

# Aca estaria el calendario, y los botones para Ingresar y Consultar un evento
@auth_bp.route("/") # DUDA!!! Capaz seria mejor poner esto en iniciar sesion, asi primero ingresas
@auth_bp.route("/inicio")
def inicio():
    if 'username' not in session:
        return redirect(url_for('main.ingresar'))
    return render_template('inicio.html')

# Login
@auth_bp.route("/ingresar", methods = ["GET", "POST"])
def ingresar():
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")

        # Buscar usuario en la base de datos
        user = Cuenta.query.filter_by(nombre_usuario=username).first()

        # Si el usuario existe y la contraseña es correcta, iniciar sesión
        if user and check_password_hash(user.contrasenia, password):
            session['username'] = user.nombre_usuario
            return redirect(url_for('main.inicio'))
        else:
            flash("Usuario o contraseña incorrectos"), 401
            return redirect(url_for('main.ingresar'))

    return render_template('login.html')

#cerrar sesion
def salir():
    return 0

# Funcion que ya tiene flask para los errores

@auth_bp.errorhandler(404)
def not_found(e):
  return render_template("404.html")