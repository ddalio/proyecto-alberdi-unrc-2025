from flask import Blueprint, render_template, request, redirect, url_for, session, flash
from werkzeug.security import check_password_hash
import re
from app.models import Cuenta
from app.decorators import admin_required, login_required
from datetime import datetime
from app import db 

auth_bp = Blueprint('auth', __name__)

# Configuración de seguridad
MIN_PASSWORD_LENGTH = 8

@auth_bp.route("/")
@auth_bp.route("/inicio")
def inicio():
    if 'username' not in session:
        return redirect(url_for('auth.login'))
    return render_template('inicio.html')

@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form.get("email")
        contraseña = request.form.get("contraseña")
        
        cuenta = Cuenta.query.filter(
            (Cuenta.email == email) | (Cuenta.nombre_usuario == email)
        ).first()

        if cuenta and cuenta.email_verificado:
            # Verificar contraseña
            if check_password_hash(cuenta.password_hash, contraseña):
                cuenta.ultimo_acceso = datetime.utcnow()
                db.session.commit()
                
                session['username'] = cuenta.nombre_usuario
                session['es_admin'] = cuenta.es_administrador()
                return redirect(url_for("auth.inicio"))
            else:
                print("❌ Contraseña incorrecta")
                flash("Contraseña incorrecta", "error")
        else:
            print("❌ Cuenta no encontrada")
            flash("Email o usuario no encontrado", "error")

    return render_template("login.html")

# Cerrar sesión
@auth_bp.route("/logout")
def salir():
    session.clear()
    flash("Has cerrado sesión correctamente", "success")
    return redirect(url_for("auth.login"))

# Manejo de errores
@auth_bp.errorhandler(404)
def not_found(e):
    return render_template("404.html")