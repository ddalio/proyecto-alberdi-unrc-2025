# app/__init__.py
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from dotenv import load_dotenv
from flask_jwt_extended import JWTManager
import os

db = SQLAlchemy()
jwt = JWTManager()

def create_app():
    app = Flask(__name__)

    load_dotenv()

    app.config["JWT_SECRET_KEY"] = os.getenv("JWT_SECRET_KEY")

    app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///alberdi.db"
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    app.secret_key = "clave-secreta"
    db.init_app(app)
    jwt.init_app(app)

    from .routes import register_blueprints
    register_blueprints(app)

    return app
