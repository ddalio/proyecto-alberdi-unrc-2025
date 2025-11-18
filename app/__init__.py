# app/__init__.py
from flask import Flask, session
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

def create_app():
    app = Flask(__name__)
    app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///alberdi.db"
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    app.secret_key = "clave-secreta"
    db.init_app(app)

    #Hace que current_user esté disponible en todos los templates
    @app.context_processor
    def inject_user():
        from app.models import Cuenta
        
        current_user = None
        if 'username' in session:
            current_user = Cuenta.query.get(session['username'])
        
        return dict(current_user=current_user)

    from .routes import register_blueprints
    register_blueprints(app)

    return app
