from flask import Flask
from flask_sqlalchemy import SQLAlchemy


def create_app():
    app = Flask(__name__)

    #credenciales admi para produccion
    # admin|admin@alberdi.com|admin|admin|1234

    # las intacacias de la base de datos estan en instance/alberdi.db
    app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///alberdi.db"
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

    db.init_app(app)


    app.secret_key = "clave-secreta"  # Necesaria para usar flash()


    
    # Importa y registra las rutas
    app.register_blueprints(app)
    
    return app
