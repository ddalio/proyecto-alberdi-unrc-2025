from flask import Blueprint, render_template, request, redirect, url_for, session, flash
from datetime import datetime
from flask_jwt_extended import create_access_token
from app.models import Cuenta
from dotenv import load_dotenv
from datetime import timedelta

import os

auth_bp = Blueprint('auth', __name__)

   

@auth_bp.route("/")
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

        cuenta = Cuenta.query.filter_by(email=email).first()
        
        if not cuenta or cuenta.password != contraseña:
            error: "email o contraseña incorrecta"
            return render_template("login.html", error=error)

        access_token = create_access_token(
            identity=cuenta.nombre_usuario,
            expires_delta=timedelta(hours=1)
        )

        # Guardamos el token en la sesión temporal
        session["access_token"] = access_token
        session["username"] = cuenta.nombre_usuario 
        
        return redirect(url_for("auth.inicio"))

    return render_template("login.html")

#cerrar sesion
def salir():
    return 0

# Funcion que ya tiene flask para los errores

@auth_bp.errorhandler(404)
def not_found(e):
  return render_template("404.html")