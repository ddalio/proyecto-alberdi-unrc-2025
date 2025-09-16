from .auth_routes import auth_bp
from .cuentas_routes import cuentas_bp
from .eventos_routes import eventos_bp
from .ingresos_routes import ingresos_bp

def register_blueprints(app):
    app.register_blueprint(auth_bp)
    app.register_blueprint(cuentas_bp)
    app.register_blueprint(eventos_bp)
    app.register_blueprint(ingresos_bp)
