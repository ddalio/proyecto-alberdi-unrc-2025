from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class Cuenta(db.Model):
    __tablename__ = "cuenta"

    nombre_usuario = db.Column(db.String(10), primary_key=True, nullable=False)
    email = db.Column(db.String(50), unique=True, nullable=False)
    nombre = db.Column(db.String(20), nullable=False)
    apellido = db.Column(db.String(20), nullable=False)
    contraseña = db.Column(db.String(255), nullable=False)

    def __repr__(self):
        return f"<Cuenta {self.nombre_usuario}>"