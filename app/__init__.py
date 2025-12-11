from flask import Flask, render_template, session
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_mail import Mail
from werkzeug.security import generate_password_hash
from datetime import datetime
from flask import make_response
from reportlab.pdfgen import canvas
from io import BytesIO
import os


db = SQLAlchemy()
migrate = Migrate()
mail = Mail()

def create_app():
    app = Flask(__name__)
    
    # Configuración general
    app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///alberdi.db"
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    app.secret_key = os.getenv("SECRET_KEY")
    
    # Config de mail
    app.config["MAIL_SERVER"] = "smtp.gmail.com"
    app.config["MAIL_PORT"] = 587
    app.config["MAIL_USE_TLS"] = True
    app.config["MAIL_USERNAME"] = os.getenv("MAIL_USERNAME")
    app.config["MAIL_PASSWORD"] = os.getenv("MAIL_PASSWORD")

    db.init_app(app)
    migrate.init_app(app, db)
    mail.init_app(app)

    @app.context_processor
    def inject_user():
        from app.models import Cuenta

        current_user = None
        es_admin = False

        if 'username' in session:
            current_user = Cuenta.query.get(session['username'])
            if current_user:
                es_admin = current_user.es_administrador()

        return dict(current_user=current_user, es_admin=es_admin)

    with app.app_context():
        from .routes import register_blueprints
        register_blueprints(app)

        db.create_all()

        from app.models import Cuenta, Administrador

        cuenta = Cuenta.query.filter_by(nombre_usuario='admin1').first()
        admin_password ='Admin1231!'

        
        if not cuenta:
            try:
                cuenta_admin = Cuenta(
                    nombre_usuario='admin1',
                    email='admin1@alberdi.com',
                    nombre='Administrador',
                    apellido='Sistema',
                    password_hash=generate_password_hash(admin_password),
                    fecha_creacion=datetime.utcnow(),
                    email_verificado=True
                )
                db.session.add(cuenta_admin)

                admin = Administrador(nombre_usuario='admin')
                db.session.add(admin)

                db.session.commit()
            except Exception:
                db.session.rollback()
                
    @app.errorhandler(404)
    def page_not_found(e):
        return render_template('404.html'), 404
    
    return app