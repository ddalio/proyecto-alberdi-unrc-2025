from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
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
    password_hash = db.Column(db.String(255), nullable=False)
    email_verificado = db.Column(db.Boolean, default=False)


    fecha_creacion = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    ultimo_acceso = db.Column(db.DateTime, nullable=True)

    # Relación con eventos y pagos creados por el usuario
    eventos = db.relationship('Evento', back_populates='usuario', cascade="all, delete-orphan")
    pagos = db.relationship('Pago', back_populates='usuario', cascade="all, delete-orphan")

    # Relación con administrador
    administrador = db.relationship('Administrador', back_populates='cuenta', uselist=False)

    def __repr__(self):
        return f'<Cuenta {self.nombre_usuario}>'
  
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def es_administrador(self):
        return Administrador.query.filter_by(nombre_usuario=self.nombre_usuario).first() is not None

    def obtener_rol(self):
        return "Administrador" if self.es_administrador() else "Usuario"

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
    
    @property
    def monto_deuda(self):
        return float(self.monto_total) - sum(float(p.monto_pago) for p in self.pagos)
    
    @property
    def adeuda(self):   
        adeuda = self.total_pagado < self.monto_total
        return adeuda

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
    
    email_verificado = db.Column(db.Boolean, nullable=False, default=False)
    fecha_verificacion = db.Column(db.DateTime, nullable=True)

    # Relaciones
    pago = db.relationship('Pago', back_populates='auditorias_pago')
    usuario = db.relationship('Cuenta')

    def __repr__(self):
        return f'<AuditoriaPago Pago {self.id_pago} - Usuario {self.nombre_usuario}>'


# ==============================
# 9. LIBRO
# ==============================

class Libro(db.Model):
    __tablename__ = "libro"

    #Restricciones para la tabla libro
    __table_args__ = (
        db.UniqueConstraint("isbn", name="uq_isbn_libro"), 
        db.CheckConstraint("length(trim(titulo)) > 0", name="ck_libro_titulo"), 
        db.CheckConstraint("length(trim(autor)) > 0", name="ck_libro_autor"), 
        db.CheckConstraint("cantidad_paginas IS NULL OR cantidad_paginas > 0", name="libro_paginas", ), 
        db.CheckConstraint("cantidad_copias >= 0", name="ck_libro_copias"), {"mysql_engine": "InnoDB"},
    )

    id_libro = db.Column( db.Integer, primary_key=True, autoincrement=True)
    isbn = db.Column(db.String(13), nullable=True)
    titulo = db.Column(db.String(255), nullable=False)
    subtitulo = db.Column(db.String(255), nullable=True)
    autor = db.Column(db.String(255), nullable=False)
    genero = db.Column(db.String(100), nullable=True)
    idioma = db.Column(db.String(50), nullable=True)
    cantidad_paginas = db.Column(db.Integer, nullable=True)
    cantidad_copias = db.Column(db.Integer, nullable=False)

    prestamos = db.relationship( "Prestamo", back_populates="libro_prestado", )

    #Obtenemos si un libro en especifico figura xomo prestado; si no posee pecha de devolucion significa que se encuentra en prestamo
    @property
    def cantidad_prestamos_activos(self):
        return sum(
            1
            for prestamo in self.prestamos
            if prestamo.fecha_devolucion is None
        )
    #Consulta si hay copias disponibles para prestar.
    @property
    def cantidad_disponible(self):
        return self.cantidad_copias - self.cantidad_prestamos_activos
    #Calcula el estado de prestamo de un libro.
    @property
    def estado(self):
        if self.cantidad_copias == 0:
            return "sin_existencias"

        if self.cantidad_disponible > 0:
            return "disponible"

        return "sin_disponibilidad"

# ==============================
# 10. BIBLIOTECARIO
# ==============================

class Bibliotecario(db.Model):
    __tablename__ = "bibliotecario"

    nombre_usuario = db.Column( db.String(10), db.ForeignKey( "administrador.nombre_usuario", name="fk_bibliotecario_administrador", ondelete="RESTRICT",), primary_key=True,)
    nombre = db.Column(db.String(20), nullable=False)


# ==============================
# 11. PRESTAMO
# ==============================
class Prestamo(db.Model):
    __tablename__ = 'prestamo'
    id_prestamo = db.Column(db.Integer, primary_key=True)
    fecha_prestamo = db.Column(db.Date, nullable=False)
    fecha_devolucion = db.Column(db.Date, nullable=True) 
    tiempo_prestamo = db.Column(db.Integer, nullable=False) #corroborar si no va Date
    dni = db.Column(db.String(20), db.ForeignKey('cliente.dni'))
    id_libro = db.Column(db.Integer, db.ForeignKey('libro.id_libro')) 
    nombre_usuario = db.Column(db.String(20), db.ForeignKey('bibliotecario.nombre_usuario'))

    #Relaciones entre las tablas, es para facilitar la navegación
    deudor = db.relationship('Cliente', backref='prestamos')
    libro_prestado = db.relationship('Libro', backref='prestamo')
    # como es una relación N a 1, no hace falta nueva tabla
    # en compensación se registra esto para facilitar la navegación 
    gestor_prestamo = db.relationship('Bibliotecario', backref='gestor')

#### ###

# Agregar estos campos después de password_hash en la clase Cuenta
   # rol = db.Column(db.String(20), nullable=False, default='usuario')
    email_verificado = db.Column(db.Boolean, nullable=False, default=False)
    fecha_verificacion = db.Column(db.DateTime, nullable=True)

# Agregar estos métodos después de la función obtener_rol() en la clase Cuenta
    def set_password(self, password):
        from werkzeug.security import generate_password_hash
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        from werkzeug.security import check_password_hash
        return check_password_hash(self.password_hash, password)

# Agregar estos métodos después de la función obtener_rol() en la clase Cuenta
    def set_password(self, password):
        from werkzeug.security import generate_password_hash
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        from werkzeug.security import check_password_hash
        return check_password_hash(self.password_hash, password)
