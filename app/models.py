from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
from app import db

# ==============================
# 1. CLIENTE
# ==============================
class Cliente(db.Model):
    __tablename__ = 'cliente'
    
    dni = db.Column(db.String(20), primary_key=True)
    nombre = db.Column(db.String(20), nullable=False)
    apellido = db.Column(db.String(20), nullable=False)
    telefono = db.Column(db.String(15), nullable=False)
    institucion = db.Column(db.String(40), nullable=True)

    # Relación con Evento (1 cliente -> muchos eventos)
    eventos = db.relationship('Evento', back_populates='cliente', cascade="all, delete-orphan")

    def __repr__(self):
        return f'<Cliente {self.dni} {self.nombre} {self.apellido}>'


# ==============================
# 2. RESPONSABLE LLAVE
# ==============================
class ResponsableLlave(db.Model):
    __tablename__ = 'responsable_llave'

    id_responsable = db.Column(db.Integer, primary_key=True, autoincrement=True)
    nombre = db.Column(db.String(20))
    apellido = db.Column(db.String(20))

    # Relación con Evento (1 responsable -> muchos eventos donde abre/cierra)
    eventos_apertura = db.relationship('Evento', foreign_keys='Evento.id_responsable_apertura', back_populates='responsable_apertura')
    eventos_cierre = db.relationship('Evento', foreign_keys='Evento.id_responsable_cierre', back_populates='responsable_cierre')

    def __repr__(self):
        return f'<ResponsableLlave {self.id_responsable} {self.nombre} {self.apellido}>'


# ==============================
# 3. CUENTA
# ==============================
class Cuenta(db.Model):
    __tablename__ = 'cuenta'

    nombre_usuario = db.Column(db.String(10), primary_key=True)
    email = db.Column(db.String(50), unique=True, nullable=False)
    nombre = db.Column(db.String(20), nullable=False)
    apellido = db.Column(db.String(20), nullable=False)
    password = db.Column(db.String(255), nullable=False) # ENCRIPTAR ESTO!!!

    # Relación con eventos y pagos creados por el usuario
    eventos = db.relationship('Evento', back_populates='usuario', cascade="all, delete-orphan")
    pagos = db.relationship('Pago', back_populates='usuario', cascade="all, delete-orphan")

    # Relación con administrador
    administrador = db.relationship('Administrador', back_populates='cuenta', uselist=False)

    def __repr__(self):
        return f'<Cuenta {self.nombre_usuario}>'


# ==============================
# 4. EVENTO
# ==============================
class Evento(db.Model):
    __tablename__ = 'evento'

    id_evento = db.Column(db.Integer, primary_key=True, autoincrement=True)
    descripcion = db.Column(db.String(100))
    fecha_inicio = db.Column(db.DateTime, nullable=False)
    fecha_fin = db.Column(db.DateTime, nullable=False)
    observaciones = db.Column(db.String(100))
    monto_total = db.Column(db.Numeric(10, 2), nullable=False)
    adeuda = db.Column(db.Boolean, default=True) #esto se actualiza cuando todos los pagos == monto total
    nro_recibo = db.Column(db.Integer) #esto se actualiza cuando todos los pagos == monto total
    @property
    def total_pagado(self):
        return sum(float(p.monto_pago) for p in self.pagos)

    # FKs
    dni = db.Column(db.String(20), db.ForeignKey('cliente.dni'), nullable=False)
    id_responsable_apertura = db.Column(db.Integer, db.ForeignKey('responsable_llave.id_responsable'))
    id_responsable_cierre = db.Column(db.Integer, db.ForeignKey('responsable_llave.id_responsable'))
    usuario_creacion = db.Column(db.String(10), db.ForeignKey('cuenta.nombre_usuario'), nullable=False)

    # Relaciones
    cliente = db.relationship('Cliente', back_populates='eventos')
    responsable_apertura = db.relationship('ResponsableLlave', foreign_keys=[id_responsable_apertura], back_populates='eventos_apertura')
    responsable_cierre = db.relationship('ResponsableLlave', foreign_keys=[id_responsable_cierre], back_populates='eventos_cierre')
    usuario = db.relationship('Cuenta', back_populates='eventos')

    pagos = db.relationship('Pago', back_populates='evento', cascade="all, delete-orphan")
    auditorias_evento = db.relationship('AuditoriaEvento', back_populates='evento', cascade="all, delete-orphan")

    def __repr__(self):
        return f'<Evento {self.id_evento} - {self.descripcion}>'


# ==============================
# 5. PAGO
# ==============================
class Pago(db.Model):
    __tablename__ = 'pago'

    id_pago = db.Column(db.Integer, primary_key=True, autoincrement=True)
    id_evento = db.Column(db.Integer, db.ForeignKey('evento.id_evento'), nullable=False)
    monto_pago = db.Column(db.Numeric(10, 2), nullable=False)
    fecha = db.Column(db.Date, nullable=False)
    usuario_creacion = db.Column(db.String(10), db.ForeignKey('cuenta.nombre_usuario'), nullable=False)

    # Relaciones
    evento = db.relationship('Evento', back_populates='pagos')
    usuario = db.relationship('Cuenta', back_populates='pagos')

    auditorias_pago = db.relationship('AuditoriaPago', back_populates='pago', cascade="all, delete-orphan")

    def __repr__(self):
        return f'<Pago {self.id_pago} - Evento {self.id_evento}>'


# ==============================
# 6. ADMINISTRADOR
# ==============================
class Administrador(db.Model):
    __tablename__ = 'administrador'

    nombre_usuario = db.Column(db.String(10), db.ForeignKey('cuenta.nombre_usuario'), primary_key=True)

    cuenta = db.relationship('Cuenta', back_populates='administrador')

    def __repr__(self):
        return f'<Administrador {self.nombre_usuario}>'


# ==============================
# 7. AUDITORÍA EVENTO
# ==============================
class AuditoriaEvento(db.Model):
    __tablename__ = 'auditoria_evento'

    id_evento = db.Column(db.Integer, db.ForeignKey('evento.id_evento'), primary_key=True)
    nombre_usuario = db.Column(db.String(10), db.ForeignKey('cuenta.nombre_usuario'), primary_key=True)
    fecha_auditoria = db.Column(db.DateTime, default=datetime.utcnow)

    # Relaciones
    evento = db.relationship('Evento', back_populates='auditorias_evento')
    usuario = db.relationship('Cuenta')

    def __repr__(self):
        return f'<AuditoriaEvento Evento {self.id_evento} - Usuario {self.nombre_usuario}>'


# ==============================
# 8. AUDITORÍA PAGO
# ==============================
class AuditoriaPago(db.Model):
    __tablename__ = 'auditoria_pago'

    id_pago = db.Column(db.Integer, db.ForeignKey('pago.id_pago'), primary_key=True)
    nombre_usuario = db.Column(db.String(10), db.ForeignKey('cuenta.nombre_usuario'), primary_key=True)
    fecha_auditoria = db.Column(db.DateTime, default=datetime.utcnow)

    # Relaciones
    pago = db.relationship('Pago', back_populates='auditorias_pago')
    usuario = db.relationship('Cuenta')

    def __repr__(self):
        return f'<AuditoriaPago Pago {self.id_pago} - Usuario {self.nombre_usuario}>'
