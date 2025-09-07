from app import db
from datetime import datetime

class Cliente(db.Model):
    __tablename__ = 'cliente'
    
    dni = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100), nullable=False)
    apellido = db.Column(db.String(100), nullable=False)
    telefono = db.Column(db.String(20))
    institucion = db.Column(db.String(40))
    #activo = db.Column(db.Boolean, default=True)
    
    def __repr__(self):
        return f'<Cliente {self.dni} {self.nombre} {self.apellido}>' 
    


