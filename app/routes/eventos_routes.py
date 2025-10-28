from flask import Blueprint, render_template, request, redirect, url_for, flash, session, jsonify
from datetime import datetime, timedelta
from app.models import db, Evento, Cliente, ResponsableLlave, Pago, Cuenta

eventos_bp = Blueprint('eventos_bp', __name__, url_prefix='/eventos')

#Listado de eventos
@eventos_bp.route("/consultar", methods = ["GET"])
def consultar():
    try:
        eventos = Evento.query.all()
        return render_template("eventos.html", eventos_list = eventos)
    except Exception as e:
        # Log del error para debugging
        print(f"Error al consultar eventos: {str(e)}")
        return render_template("eventos.html", mensaje="Error al cargar los eventos")

# Listado de eventos
@eventos_bp.route("/eventos", methods=["GET"])
def eventos():
    try:
        # todos los eventos
        eventos = Evento.query.all()
        return render_template('eventos.html', eventos_list = eventos)
    except Exception as e:
        # si no hay eventos disponibles
        print(f"Error al cargar eventos: {str(e)}")
        return render_template("eventos.html", mensaje="Error al cargar eventos")


# DESACOPLAR !!!
# Crear un nuevo evento
# 
#
@eventos_bp.route("/agregar_evento", methods =["POST"])
def crear_evento():
    try:
        # Datos responsable del alquiler
        dni_cliente = request.form.get("dni")
        nombre_cliente = request.form.get("nombre")
        apellido_cliente = request.form.get("apellido")
        telefono_cliente = request.form.get("telefono")
        institucion_cliente = request.form.get("institucion")

        # Busca en la base de datos si el cliente ya se encuentra.
        cliente = Cliente.query.get(dni_cliente)

        if not cliente:
                # si el cliente no existe entonces lo guardo
                cliente = Cliente(dni=dni_cliente, nombre=nombre_cliente, apellido = apellido_cliente, telefono= telefono_cliente, institucion=institucion_cliente)
                db.session.add(cliente)
                db.session.commit();

        # Responsable de la llave
        nombre_apertura = request.form.get("nombre_apertura")
        apellido_apertura = request.form.get("apellido_apertura")
        nombre_cierre = request.form.get("nombre_cierre")
        apellido_cierre = request.form.get("apellido_cierre")

        responsable_llave_apertura = None
        responsable_llave_cierre = None

        #Verificamos si existe el nombre en la tabla 
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
            db.session.commit() #genera id_responsable para usar en evento

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
            db.session.commit()

        # Usuario logueado
        usuario_nombre = session.get("username")
        usuario = Cuenta.query.get(usuario_nombre)

        # Fechas
        fecha_inicio = combinar_fecha_hora(request, "fecha_inicio", "hora_inicio")
        fecha_fin = combinar_fecha_hora(request, "fecha_fin", "hora_fin")


        evento = Evento(
            descripcion = request.form.get("descripcion"),
            #esto no deberia ser horario? - cambiar en el modelo tipo
            fecha_inicio = fecha_inicio,
            # esto no deberia ser horario? - cambiar en el modelo tipo
            fecha_fin = fecha_fin,
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
        db.session.flush()

        # Registro de un monto inicial (seña)
        monto_inicial = request.form.get("monto")
        if monto_inicial and float(monto_inicial) > 0:
            # Registro de un pago
            pago = Pago(id_evento = evento.id_evento,
                        monto_pago = float(monto_inicial),
                        fecha = datetime.utcnow(),
                        usuario_creacion = usuario.nombre_usuario)
            db.session.add(pago)

        # Actualizar el estado de pago del evento
        actualizar_pago_evento(evento)
        db.session.commit()
        
        flash("Evento creado correctamente")
        return redirect(url_for('eventos_bp.eventos'))

    except Exception as e:
        db.session.rollback()
        flash(f"Error al crear evento: {str(e)}")
        return redirect(url_for('eventos_bp.nuevo_evento'))


    #ver nro_recibo. (HACER)

#Combina los valores de fecha y hora obtenidos del formulario en un objeto datetime.
def combinar_fecha_hora(request, campo_fecha: str, campo_hora: str = None) -> datetime:
    fecha_str = request.form.get(campo_fecha)
    hora_str = request.form.get(campo_hora) if campo_hora else None
    hora_str = hora_str or "00:00"


@eventos_bp.route("/nuevo_evento", methods=["GET"])
def nuevo_evento():
    return render_template("agegar_evento.html")

# NOTA!!! Se usaria en el metodo donde este el listado de los eventos
    #Los criterios de búsqueda pueden ser:@eventos_bp.route("/editar/<int:id_evento>", methods=["GET", "POST"])
@eventos_bp.route("/editar_evento/<int:id_evento>", methods=["GET", "POST"])
def editar_evento(id_evento):
    evento = Evento.query.get_or_404(id_evento)

    if request.method == "POST":
        try:
             # --- Fechas ---
            fecha_inicio = combinar_fecha_hora(request, "fecha_inicio", "hora_inicio")
            fecha_fin = combinar_fecha_hora(request, "fecha_fin", "hora_fin")

            # Actualizar datos del evento
            evento.descripcion = request.form.get("descripcion")
            evento.monto_total = request.form.get("monto_total")
            evento.fecha_inicio = fecha_inicio
            evento.fecha_fin = fecha_fin
            evento.nro_recibo = request.form.get("nro_recibo") or None
            evento.observaciones = request.form.get("observaciones")

            # Datos del cliente asociado
            evento.cliente.nombre = request.form.get("nombre")
            evento.cliente.apellido = request.form.get("apellido")
            evento.cliente.dni = request.form.get("dni")
            evento.cliente.telefono = request.form.get("telefono")
            evento.cliente.institucion = request.form.get("institucion") or None

            db.session.commit()
            flash("Evento actualizado correctamente ✅")
            return redirect(url_for('eventos.listar_eventos'))
        except Exception as e:
            db.session.rollback()
            flash(f"Error al editar el evento: {str(e)}", "error")

    # Cuando entras por GET → renderiza el formulario
    return render_template("editar_evento.html", evento=evento)

@eventos_bp.route("/detalles/<int:id_evento>", methods=["GET"])
def detalles_evento(id_evento):
    evento = Evento.query.get_or_404(id_evento)  

    return render_template("detalles_evento.html", evento=evento)



# NOTA!!! Se usaria en el metodo donde este el listado de los eventos
#Los criterios de búsqueda pueden ser:
#i. Por DNI del cliente
#ii. Por Nombre del cliente
#iii. Por Descripción del Evento
#iv. Por ID del evento
@eventos_bp.route("/buscar", methods =["GET","POST"])
def buscar_evento_campo():
    try:
        #recibimos parametro desde el frontend
        campo = request.form.get("campo")
        valor = request.form.get("valor")

        evento = Evento.query

        if campo in ["dni", "nombre", "descripcion"] and valor:
            columna = getattr(Evento, campo) # equivale a Evento.dni, Evento.nombre, Evento.descripcion.
            evento = evento.filter(columna.ilike(f"%{valor}%"))
            resultados = evento.all()
            return render_template("eventos.html", eventos_list=resultados)
    except Exception as e:   
        flash(f"Error al crear evento: {str(e)}")
        return redirect(url_for('eventos_bp.consultar'))
        
@eventos_bp.route("/eliminar/<int:id_evento>", methods=["POST"])
def eliminar_evento(id_evento):
    try:
        evento = Evento.query.get_or_404(id_evento)
        db.session.delete(evento)
        db.session.commit()
        flash("Evento eliminado correctamente ✅")
        return redirect(url_for("eventos_bp.consultar"))
    except Exception as e:
        db.session.rollback()
        flash(f"Error al eliminar el evento: {str(e)}", "error")
        return redirect(url_for("eventos_bp.consultar"))

# Funcion para actualizar el estado de pago de un evento
def actualizar_pago_evento(evento):
    total_pagado = sum([float(p.monto_pago) for p in evento.pagos])

    if total_pagado >= float(evento.monto_total):
        evento.adeuda = False
        flash("Se completo el pago del evento")


@eventos_bp.route("/events-json", methods=["GET"])
def eventos_json():
    eventos = Evento.query.all()

    return jsonify([
        {
            "title": e.descripcion,
            "start": e.fecha_inicio.strftime("%Y-%m-%d"),
            "end": (e.fecha_fin + timedelta(days=1)).strftime("%Y-%m-%d"),
            "allDay": True,
            "extendedProps": {
                "observaciones": e.observaciones or "",
                "monto_total": float(e.monto_total) if e.monto_total else 0.0,
                "adeuda": e.adeuda,
                "dni": e.dni,
                "responsable_apertura": f"{e.responsable_apertura.nombre} {e.responsable_apertura.apellido}" if e.responsable_apertura else "",
                "responsable_cierre": f"{e.responsable_cierre.nombre} {e.responsable_cierre.apellido}" if e.responsable_cierre else ""
            }
        }
        for e in eventos
        ])



# ---------------------Metodos que no sabemos si agregar todavia-----------------------------------

# Esto es para debug nomas, en realidad no tenemos pensado poner una pagina solo para clientes/responsables de eventos
# Lo podriamos agregar si nos hace falta
@eventos_bp.route("/clientes")
def clientes():
    clientes = Cliente.query.all()
    return render_template('clientes.html', clientes=clientes)


