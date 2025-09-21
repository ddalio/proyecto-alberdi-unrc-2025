from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from datetime import datetime
from app.models import db, Evento, Cliente, ResponsableLlave, Pago

eventos_bp = Blueprint('eventos', __name__, url_prefix='/eventos')

# Listado de eventos
@eventos_bp.route("/", methods=["GET"])
def listar_eventos():
    try:
        # todos los eventos
        eventos = Evento.query.all()
        return render_template('eventos.html', eventos_list = eventos)
    except Exception as e:
        # si no hay eventos disponibles
        flash(f"Error al cargar eventos: {str(e)}")
        return render_template("eventos.html", eventos_list = [])

# DESACOPLAR !!!
# Crear un nuevo evento
# 
#
@eventos_bp.route("/agregar_evento", methods=["GET", "POST"])
def agregar_evento():
    if request.method == "POST":
        try:
            dni_cliente = request.form.get("dni")
            nombre_cliente = request.form.get("nombre")
            apellido_cliente = request.form.get("apellido")
            telefono_cliente = request.form.get("telefono")
            institucion_cliente = request.form.get("institucion")

            cliente = Cliente.query.get(dni_cliente)
            if not cliente:
                cliente = Cliente(
                    dni=dni_cliente,
                    nombre=nombre_cliente,
                    apellido=apellido_cliente,
                    telefono=telefono_cliente,
                    institucion=institucion_cliente
                )
                db.session.add(cliente)

            # Responsable apertura
            nombre_apertura = request.form.get("nombre_apertura")
            apellido_apertura = request.form.get("apellido_apertura")
            responsable_llave_apertura = None
            if nombre_apertura and apellido_apertura:
                responsable_llave_apertura = ResponsableLlave.query.filter_by(
                    nombre=nombre_apertura, apellido=apellido_apertura
                ).first()
            if not responsable_llave_apertura:
                responsable_llave_apertura = ResponsableLlave(
                    nombre=nombre_apertura, apellido=apellido_apertura
                )
                db.session.add(responsable_llave_apertura)
                db.session.flush()

            # Responsable cierre
            nombre_cierre = request.form.get("nombre_cierre")
            apellido_cierre = request.form.get("apellido_cierre")
            responsable_llave_cierre = None
            if nombre_cierre and apellido_cierre:
                responsable_llave_cierre = ResponsableLlave.query.filter_by(
                    nombre=nombre_cierre, apellido=apellido_cierre
                ).first()
            if not responsable_llave_cierre:
                responsable_llave_cierre = ResponsableLlave(
                    nombre=nombre_cierre, apellido=apellido_cierre
                )
                db.session.add(responsable_llave_cierre)
                db.session.flush()

            # Usuario logueado
            usuario_nombre = session.get("username")
            usuario = Cuenta.query.get(usuario_nombre)

            # Fechas
            fecha_inicio_str = request.form.get("fecha_inicio")
            hora_inicio_str = request.form.get("hora_inicio") or "00:00"
            fecha_inicio = datetime.strptime(f"{fecha_inicio_str} {hora_inicio_str}", "%Y-%m-%d %H:%M")

            fecha_fin_str = request.form.get("fecha_fin")
            hora_fin_str = request.form.get("hora_fin") or "00:00"
            fecha_fin = datetime.strptime(f"{fecha_fin_str} {hora_fin_str}", "%Y-%m-%d %H:%M")

            # Evento
            evento = Evento(
                descripcion=request.form.get("descripcion"),
                fecha_inicio=fecha_inicio,
                fecha_fin=fecha_fin,
                observaciones=request.form.get("observaciones"),
                monto_total=float(request.form.get("monto_total")),
                adeuda=True,
                nro_recibo=request.form.get("nro_recibo"),
                dni=cliente.dni,
                id_responsable_apertura=responsable_llave_apertura.id_responsable,
                id_responsable_cierre=responsable_llave_cierre.id_responsable,
                usuario_creacion=usuario.nombre_usuario
            )
            db.session.add(evento)
            db.session.commit()

            # Seña inicial
            monto_inicial = request.form.get("monto")
            if monto_inicial and float(monto_inicial) > 0:
                pago = Pago(
                    evento_id=evento.id_evento,  # ojo: id_evento, no id
                    monto_pago=float(monto_inicial),
                    fecha=datetime.utcnow(),
                    usuario_creacion=usuario.nombre_usuario
                )
                db.session.add(pago)
                db.session.commit()

            actualizar_pago_evento(evento)
            db.session.commit()

            flash("Evento creado correctamente")
            return redirect(url_for('eventos.listar_eventos'))

        except Exception as e:
            db.session.rollback()
            print(f"Error al crear el evento: {str(e)}", "error")
            return redirect(url_for('eventos.agregar_evento'))

    # Si es GET => mostrar formulario
    return render_template("agregar_evento.html")

    #ver nro_recibo. (HACER)

# Funcion para actualizar el estado de pago de un evento
def actualizar_pago_evento(evento):
    total_pagado = sum([float(p.monto_pago) for p in evento.pagos])

    if total_pagado >= float(evento.monto_total):
        evento.adeuda = False
        flash("Se completo el pago del evento")
# NOTA!!! Se usaria en el metodo donde este el listado de los eventos
def buscar_evento():
    return 0

@eventos_bp.route("/editar", methods =["POST"])
def editar_evento():
    return render_template("editar-evento.html")

@eventos_bp.route("/detalles/<int:id_evento>", methods=["GET"])
def detalles_evento(id_evento):
    # Buscar evento por ID
    evento = Evento.query.get_or_404(id_evento)  # 404 si no existe

    return render_template("detalles-evento.html", evento=evento)

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


