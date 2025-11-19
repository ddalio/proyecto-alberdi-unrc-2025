from functools import wraps
from flask import flash, redirect, url_for, session
from app.models import Cuenta

def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'username' not in session:
            flash("Debe iniciar sesión para acceder a esta página", "error")
            return redirect(url_for('auth.login'))
        
        cuenta = Cuenta.query.get(session['username'])
        if not cuenta or not cuenta.es_administrador():
            flash("No tiene permisos de administrador", "error")
            return redirect(url_for('auth.inicio'))
        
        return f(*args, **kwargs)
    return decorated_function

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'username' not in session:
            flash("Debe iniciar sesión", "error")
            return redirect(url_for('auth.login'))
        return f(*args, **kwargs)
    return decorated_function