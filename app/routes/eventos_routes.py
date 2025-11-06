from flask import Blueprint, render_template, request, redirect, url_for, flash, session, jsonify
from datetime import datetime, timedelta
from app.models import db, Evento, Cliente, ResponsableLlave, Pago, Cuenta
#from app.routes import ingresos_bp

eventos_bp = Blueprint('eventos_bp', __name__, url_prefix='/eventos')

# Listado de eventos
@eventos_bp.route("/", methods=["GET"])
def eventos():
    try:
        # todos los eventos
        eventos = Evento.query.all()
        return render_template('eventos.html', eventos_list = eventos)
    except Exception as e:
        # si no hay eventos disponibles
        print(f"Error al cargar eventos: {str(e)}")
        return render_template("eventos.html", mensaje="Error al cargar eventos")



# Crear un nuevo evento
@eventos_bp.route("/agregar_evento", methods =["GET","POST"])
def crear_evento():
    if request.method == "POST":
        try:
            # Ingresar cliente
            # Datos responsable del alquiler
            cliente = agregar_cliente(request.form)

            # Responsable de la llave
            responsable_llave_apertura = agregar_responsable_llave(request.form.get("nombre_apertura"), request.form.get("apellido_apertura"))
            responsable_llave_cierre = agregar_responsable_llave(request.form.get("nombre_cierre"), request.form.get("apellido_cierre"))

            # Usuario logueado
            usuario_nombre = session.get("username")
            usuario = Cuenta.query.get(usuario_nombre)

            # Fechas
            fecha_inicio = combinar_fecha_hora(request, "fecha_inicio", "hora_inicio")
            fecha_fin = combinar_fecha_hora(request, "fecha_fin", "hora_fin")

            if fecha_inicio >= fecha_fin:
                return

            evento = Evento(
                descripcion = request.form.get("descripcion"),
                fecha_inicio = fecha_inicio,
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
            agregar_pago(request.form.get("monto"))
            
            flash("Evento creado correctamente")
            return redirect(url_for('eventos_bp.eventos'))

        except Exception as e:
            db.session.rollback()
            flash(f"Error al crear evento: {str(e)}")
            return redirect(url_for('eventos_bp.crear_evento'))
    return render_template("agegar_evento.html")

    #ver nro_recibo. (HACER)

def agregar_pago(monto):
    monto_inicial = monto
    if monto_inicial and float(monto_inicial) > 0:
        # Registro de un pago
        pago = Pago(id_evento = evento.id_evento,
                    monto_pago = float(monto_inicial),
                    fecha = datetime.utcnow(),
                    usuario_creacion = usuario.nombre_usuario)
        db.session.add(pago)

    # Actualizar el estado de pago del evento
    db.session.commit()


def agregar_cliente(form) -> Cliente:
    dni_cliente = form.get("dni_cliente")
    nombre_cliente = form.get("nombre_cliente")
    apellido_cliente = form.get("apellido_cliente")
    telefono_cliente = form.get("telefono_cliente")
    institucion_cliente = form.get("institucion_cliente")

    if not dni_cliente:
        raise ValidationError("El campo DNI del cliente es obligatorio.")
    if not dni_valido(dni_cliente):
        raise ValidationError("El DNI debe tener al menos 8 dígitos y contener solo números.")
    if not nombre_cliente or not apellido_cliente:
        raise ValidationError("El nombre y apellido del cliente son obligatorios.")

    cliente = Cliente(
        dni=dni_cliente,
        nombre=nombre_cliente,
        apellido=apellido_cliente,
        telefono=telefono_cliente,
        institucion=institucion_cliente,
    )

    db.session.add(cliente)
    return cliente


def dni_valido(dni) -> bool:
    return dni >= 8 

def editar_cliente(form) -> Cliente:
    # Busca en la base de datos si el cliente ya se encuentra.
    dni_cliente = form.get("dni")
    cliente = Cliente.query.get(dni_cliente)

    if not cliente:
        raise ValidationError("Cliente no encontrado.")
    
    # Datos responsable del alquiler
    if not dni_valido(dni_cliente):
        raise ValidationError("El DNI debe tener al menos 8 dígitos y contener solo números.")
    
    cliente.nombre_cliente = form.get("nombre")
    cliente.apellido_cliente = form.get("apellido")
    cliente.telefono_cliente = form.get("telefono")
    cliente.institucion_cliente = form.get("institucion")

    db.session.commit()
    return cliente

def agregar_responsable_llave(nombre_form, apellido_form) -> ResponsableLlave:
     #Verificamos si existe el nombre en la tabla 
    responsable_llave = None
    if nombre_form and apellido_form:
        responsable_llave = ResponsableLlave.query.filter_by(
            nombre= nombre_form, apellido = apellido_form
            ).first()

    if not responsable_llave:
        #si no existe entonces lo creamos
        responsable_llave = ResponsableLlave(
            nombre=nombre_form,
            apellido=apellido_form
        )
        db.session.add(responsable_llave)
        db.session.commit() #genera id_responsable para usar en evento
    return responsable_llave

# Edita el responsable de la llave, puede NO tener campos validos
def editar_responsable_llave(responsable_id, nombre_form, apellido_form) -> ResponsableLlave:
    #Verificamos si existe el nombre en la tabla 
    responsable_llave = None
    if nombre_form and apellido_form:
        responsable_llave = ResponsableLlave.query.get(responsable_id)

    if not responsable_llave:
        #si no existe entonces lo creamos
        responsable_llave = ResponsableLlave(
            nombre=nombre_form,
            apellido=apellido_form
        )
        db.session.add(responsable_llave)
    else:
        #si sí existe, edito los campos
        responsable_llave.nombre=nombre_form
        responsable_llave.apellido=apellido_form
    
    db.session.commit() 
    return responsable_llave


#Combina los valores de fecha y hora obtenidos del formulario en un objeto datetime.
def combinar_fecha_hora(request, campo_fecha: str, campo_hora: str = None) -> datetime:
    fecha_str = request.form.get(campo_fecha)
    hora_str = request.form.get(campo_hora) if campo_hora else None
    hora_str = hora_str or "00:00"

    if not fecha_str:
        raise ValueError(f"El campo '{campo_fecha}' es obligatorio.")

    try:
        return datetime.strptime(f"{fecha_str} {hora_str}", "%Y-%m-%d %H:%M")
    except ValueError:
        raise ValidationError(f"La fecha u hora ingresada en '{campo_fecha}' no tiene el formato correcto.")

@eventos_bp.route("/editar_evento/<int:id_evento>", methods=["GET", "POST"])
def editar_evento(id_evento):
    evento = Evento.query.get_or_404(id_evento)

    if request.method == "POST":
        try:
            # --- Fechas ---
            fecha_inicio = combinar_fecha_hora(request, "fecha_inicio", "hora_inicio")
            fecha_fin = combinar_fecha_hora(request, "fecha_fin", "hora_fin")

            if fecha_inicio >= fecha_fin:
                raise ValidationError("La fecha de inicio debe ser anterior a la fecha de fin.")
    
            # Actualizar datos del evento
            evento.descripcion = request.form.get("descripcion")
            evento.monto_total = request.form.get("monto_total")
            evento.fecha_inicio = fecha_inicio
            evento.fecha_fin = fecha_fin
            evento.observaciones = request.form.get("observaciones")

            # Datos del cliente asociado
            evento.cliente = agregar_cliente(request.form)

            # Datos de los responsables de la llave
            id_apertura = evento.responsable_llave_apertura.id 
            evento.responsable_llave_apertura = editar_responsable_llave(id_apertura, 
                                                                         request.form.get("nombre_apertura"),
                                                                         request.form.get("apellido_apertura"))
            id_cierre = evento.responsable_llave_cierre.id 
            evento.responsable_llave_cierre = editar_responsable_llave(id_cierre, 
                                                                       request.form.get("nombre_cierre"), 
                                                                       request.form.get("apellido_cierre"))

            db.session.commit()
            flash("Evento actualizado correctamente ✅")
            return redirect(url_for('eventos_bp.eventos'))
        except Exception as e:
            db.session.rollback()
            flash(f"Error al editar el evento: {str(e)}", "error")

    return render_template("editar_evento.html", evento=evento)

# Muestra los detalles de un evento
@eventos_bp.route("/detalles/<int:id_evento>", methods=["GET"])
def detalles_evento(id_evento):
    evento = Evento.query.get_or_404(id_evento)  

    return render_template("detalles_evento.html", evento=evento)

# Listado de eventos Desde: fecha - Hasta: fecha
def rango_eventos_por_fecha():
    return 0


# NOTA!!! Se usaria en el metodo donde este el listado de los eventos
#Los criterios de búsqueda pueden ser:
#i. Por DNI del cliente
#ii. Por Nombre del cliente - ARREGLAR ESTE
#iii. Por Descripción del Evento - chequear que ande
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
        return redirect(url_for('eventos_bp.eventos'))
        
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
# def actualizar_pago_evento(evento):
#     ingresos_bp.actualizar_pago_evento(evento)




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

class ValidationError(Exception):
    """Excepción para errores de validación de datos."""
    pass




# ---------------------Metodos que no sabemos si agregar todavia-----------------------------------

# Esto es para debug nomas, en realidad no tenemos pensado poner una pagina solo para clientes/responsables de eventos
# Lo podriamos agregar si nos hace falta
@eventos_bp.route("/clientes")
def clientes():
    clientes = Cliente.query.all()
    return render_template('clientes.html', clientes=clientes)


