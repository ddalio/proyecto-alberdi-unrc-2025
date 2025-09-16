from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from datetime import datetime
from app.models import db, Evento, Cliente, ResponsableLlave, Pago, Cuenta

eventos_bp = Blueprint('eventos', __name__, url_prefix='/eventos')

# Listado de eventos
@eventos_bp.route("/eventos", methods=["GET"])
def eventos():
    try:
        # todos los eventos
        eventos = Evento.query.all()
        return render_template('eventos.html', lista_eventos = eventos)
    except Exception as e:
        # si no hay eventos disponibles
        flash(f"Error al cargar eventos: {str(e)}")
        return render_template("eventos.html", eventos = [])

# DESACOPLAR !!!
# Crear un nuevo evento
# 
#
@eventos_bp.route("/agregar_evento ")
def agregar_evento():
    return render_template('agregar_evento.html')

@eventos_bp.route("/eventos/crear", methods =["POST"])
def crear_evento():
    try:
        # Validacion para campos obligatorios (HACER)

        # Datos responsable del alquiler
        dni_cliente = request.form.get("dni")
        nombre_cliente = request.form.get("nombre")
        apellido_cliente = request.form.get("apellido")
        telefono_cliente = request.form.get("telefono")
        institucion_cliente = request.form.get("institucion")

        # Busca en la base de datos si el cliente ya se encuentra.
        cliente = Cliente.query.get(dni_cliente)
        if not cliente:
                # si el cliente no esta entonces lo guardo
                cliente = Cliente(dni=dni_cliente, nombre=nombre_cliente, apellido = apellido_cliente, telefono= telefono_cliente, institucion=institucion_cliente)
                db.session.add(cliente)

        # Responsable de la llave
        nombre_apertura = request.form.get("nombre_apertura")
        apellido_apertura = request.form.get("apellido_apertura")
        nombre_cierre = request.form.get("nombre_cierre")
        apellido_cierre = request.form.get("apellido_cierre")


        responsable_llave_apertura = None
        responsable_llave_cierre = None

        if nombre_apertura and apellido_apertura:
            responsable_llave_apertura = ResponsableLlave.query.filter_by(
                nombre= nombre_apertura, apellido = apellido_apertura
                ).first()

        if not responsable_llave_apertura:
            #si no existe entonces lo creamos
            responsable_llave_apertura = ResponsableLlave(
                nombre=nombre_apertura,
                apellido=apellido_apertura
            )
            db.session.add(responsable_llave_apertura)
            db.session.flush() #genera id_responsable para usar en evento

        if nombre_cierre and apellido_cierre:
            responsable_llave_cierre = ResponsableLlave.query.filter_by(
                nombre=nombre_cierre,
                apellido=apellido_cierre
            ).first()

        if not responsable_llave_cierre:
            responsable_llave_cierre = ResponsableLlave(
                nombre=nombre_cierre,
                apellido=apellido_cierre
            )
            db.session.add(responsable_llave_cierre)
            db.session.flush()

        # Usuario logueado
        usuario_nombre = session.get("username")
        usuario = Cuenta.query.get(usuario_nombre)

        evento = Evento(
            descripcion = request.form.get("descripcion"),
            #esto no deberia ser horario? - cambiar en el modelo tipo
            fecha_inicio = datetime.strptime(request.form["fecha_inicio"], "%Y-%m-%d").date(),
            # esto no deberia ser horario? - cambiar en el modelo tipo
            fecha_fin = datetime.strptime(request.form["fecha_fin"], "%Y-%m-%d").date(),
            observaciones = request.form.get("observaciones"),
            monto_total = float(request.form.get("monto_total")),
            adeuda = True,
            nro_recibo = None,
            dni = cliente.dni,
            id_responsable_apertura = responsable_llave_apertura.id_responsable,
            id_responsable_cierre = responsable_llave_cierre.id_responsable,
            usuario_creacion = usuario.nombre_usuario
        )

        db.session.add(evento)
        db.session.commit()

        # Registro de un monto inicial (seña)
        monto_inicial = request.form.get("monto")
        if monto_inicial and float(monto_inicial) > 0:
            # Registro de un pago
            pago = Pago(evento_id = evento.id,
                        monto_pago = float(monto_inicial),
                        fecha = datetime.utcnow(),
                        usuario_creacion = usuario.nombre_usuario)
            db.session.add(pago)
            db.session.commit()

        # Actualizar el estado de pago del evento
        actualizar_pago_evento(evento)
        db.session.commit()
        flash("Evento creado correctamente")
        return redirect(url_for('eventos_bp.eventos'))

    except Exception as e:
        db.session.rollback()
        flash(f"Error al crear evento: {str(e)}")
        return redirect(url_for('eventos_bp.eventos'))

    #ver nro_recibo. (HACER)

# NOTA!!! Se usaria en el metodo donde este el listado de los eventos
def buscar_evento():
    return 0

@eventos_bp.route("/eventos/editar", methods =["POST"])
def editar_evento():
    return render_template("editar-evento.html")

# Funcion para actualizar el estado de pago de un evento
def actualizar_pago_evento(evento):
    total_pagado = sum([float(p.monto_pago) for p in evento.pagos])

    if total_pagado >= float(evento.monto_total):
        evento.adeuda = False
        flash("Se completo el pago del evento")

# DUDA!!! No se si se necesita una ruta aparte para esto
#@eventos_bp.route("/eventos/eliminar/<int:id_evento>", methods =["POST"])
def eliminar_evento():
    return render_template("eliminar-evento.html")


# ---------------------Metodos que no sabemos si agregar todavia-----------------------------------

# Esto es para debug nomas, en realidad no tenemos pensado poner una pagina solo para clientes/responsables de eventos
# Lo podriamos agregar si nos hace falta
@eventos_bp.route("/clientes")
def clientes():
    clientes = Cliente.query.all()
    return render_template('clientes.html', clientes=clientes)


