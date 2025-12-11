from flask import Blueprint, render_template, request, redirect, url_for, flash, session, jsonify
from datetime import datetime, timedelta
from app.models import db, Evento, Cliente, ResponsableLlave, Pago, Cuenta
from flask import Blueprint, make_response
from reportlab.pdfgen import canvas
from io import BytesIO
import locale


eventos_bp = Blueprint('eventos_bp', __name__, url_prefix='/eventos')

@eventos_bp.route("/pdf", methods=["GET"])
def eventos_pdf():
    campo = request.args.get("campo")
    valor = request.args.get("valor")

    try:
        eventos = busqueda_por_campo(campo, valor)
    except Exception as e:
        flash(f"Error al descargar eventos: {str(e)}")
        return render_template("eventos.html", mensaje="Error al descargar eventos")

    buffer = BytesIO()
    p = canvas.Canvas(buffer)
    
    # --- CONFIGURACIÓN DE ESPACIOS ---
    MARGEN_IZQUIERDO = 50
    UMBRAL_NUEVA_PAGINA = 80  # Si 'y' está por debajo de 80, salta de página.
    SALTO_LINEA = 15          # Espacio vertical entre líneas del mismo evento
    ESPACIO_ENTRE_EVENTOS = 20 # Espacio vertical entre eventos diferentes
    SALTO_TOTAL_EVENTO = SALTO_LINEA + ESPACIO_ENTRE_EVENTOS # 35
    # ---------------------------------

    p.setFont("Helvetica-Bold", 14)
    p.drawString(MARGEN_IZQUIERDO, 820, f"Listado de eventos")

    p.setFont("Helvetica", 12)
    y = 790 # Comienza el contenido aquí

    for e in eventos:
        
        # 1. VERIFICAR SALTO DE PÁGINA ANTES DE DIBUJAR
        # Se asegura de que haya espacio suficiente para las dos líneas del evento.
        if y < UMBRAL_NUEVA_PAGINA: 
            p.showPage()
            p.setFont("Helvetica-Bold", 14)
            p.drawString(MARGEN_IZQUIERDO, 820, f"Listado de eventos (Continuación)")
            p.setFont("Helvetica", 12)
            y = 790

        # --- LÍNEA 1 (Información principal) ---
        # Separamos la información más extensa en la primera línea.
        texto1 = (
            f"Descripción: {e.descripcion} | "
            f"Vecino: {e.cliente.nombre} {e.cliente.apellido}"
        )
        
        p.drawString(MARGEN_IZQUIERDO, y, texto1)

        # Mover la posición Y para la segunda línea
        y -= SALTO_LINEA

        # --- LÍNEA 2 (Detalles de tiempo y monto) ---
        texto2 = (
            f"Fecha: {e.fecha_inicio.strftime('%d-%m-%Y')} | "
            f'Hora: {e.fecha_inicio.strftime("%H:%M")} a {e.fecha_fin.strftime("%H:%M")} | '
            f'Monto: ${e.monto_total}' # Asumiendo que existe el campo monto_total
        )

        p.drawString(MARGEN_IZQUIERDO, y, texto2)

        # Mover la posición Y para el ESPACIO entre este evento y el siguiente
        y -= ESPACIO_ENTRE_EVENTOS

    p.showPage()
    p.save()

    buffer.seek(0)
    response = make_response(buffer.read())
    response.headers["Content-Type"] = "application/pdf"
    response.headers["Content-Disposition"] = "attachment; filename=eventos.pdf"

    return response

# Listado de eventos
@eventos_bp.route("/", methods=["GET"])
def eventos():
    try:
        # todos los eventos
        eventos = Evento.query.all()
        return render_template('eventos.html', eventos = eventos)
    except Exception as e:
        # si no hay eventos disponibles
        print(f"Error al cargar eventos: {str(e)}")
        return render_template("eventos.html", mensaje="Error al cargar eventos")

# Crear un nuevo evento
@eventos_bp.route("/agregar_evento", methods =["GET","POST"])
def agregar_evento():
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
                raise Exception("Horario de inicio NO puede ser mayor a horario de finalización")

            if float(request.form.get("monto_total")) < 0:
                raise Exception("El monto inicial NO pude ser negativo")

            # Checkeo de solapamiento
            una_hora = timedelta(hours=1)
            rango_inicio_con_buffer = fecha_inicio - una_hora
            rango_fin_con_buffer = fecha_fin + una_hora

            # 2. Consultar si existe algún evento que se solape con el rango (incluyendo el buffer de 1h)
            evento_solapado = Evento.query.filter(
                Evento.fecha_fin > rango_inicio_con_buffer,
                Evento.fecha_inicio < rango_fin_con_buffer
            ).first()

            if evento_solapado:
                raise Exception("El evento se solapa con otro evento existente o no cumple con la separación mínima de 1 hora.")

            evento = Evento(
                descripcion = request.form.get("descripcion"),
                fecha_inicio = fecha_inicio,
                fecha_fin = fecha_fin,
                observaciones = request.form.get("observaciones"),
                monto_total = float(request.form.get("monto_total")),
                nro_recibo = None,
                dni = cliente.dni,
                id_responsable_apertura = responsable_llave_apertura.id_responsable,
                id_responsable_cierre = responsable_llave_cierre.id_responsable,
                usuario_creacion = usuario.nombre_usuario
            )

            db.session.add(evento)
            db.session.flush()
            db.session.commit()

            flash("Evento creado correctamente")
            return redirect(url_for('eventos_bp.eventos'))

        except Exception as e:
            db.session.rollback()
            flash(f"Error al crear evento: {str(e)}")
            return redirect(url_for('eventos_bp.agregar_evento'))
    return render_template("agregar_evento.html")


def agregar_cliente(form) -> Cliente:
    dni_cliente = form.get("dni")
    nombre_cliente = form.get("nombre")
    apellido_cliente = form.get("apellido")
    telefono_cliente = form.get("telefono")
    institucion_cliente = form.get("institucion")

    if not dni_cliente:
        raise ValueError("El campo DNI del cliente es obligatorio.")
    if not dni_valido(dni_cliente):
        raise ValueError("El DNI debe tener al menos 8 dígitos y contener solo números.")
    if not nombre_cliente or not apellido_cliente:
        raise ValueError("El nombre y apellido del cliente son obligatorios.")
    
    cliente = Cliente.query.get(dni_cliente)

    if not cliente:
        cliente = Cliente(
            dni=dni_cliente,
            nombre=nombre_cliente,
            apellido=apellido_cliente,
            telefono=telefono_cliente,
            institucion=institucion_cliente,
        )
        db.session.add(cliente)

    return cliente


def dni_valido(dni: str) -> bool:
    return dni.isdigit() and len(dni) >= 8

def editar_cliente(cliente, nombre, apellido, telefono, institucion) -> Cliente:
    if not cliente:
        raise flash("Cliente no encontrado.")
    
    cliente.nombre = nombre
    cliente.apellido = apellido
    cliente.telefono = telefono
    cliente.institucion = institucion

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
        db.session.commit() 

    return responsable_llave

# Edita el responsable de la llave, puede NO tener campos validos
def editar_responsable_llave(responsable_llave, nombre_form, apellido_form) -> ResponsableLlave:
    if not responsable_llave:
        #si no existe, agrego uno nuevo
        responsable_llave = agregar_responsable_llave(nombre_form, apellido_form)
    else:
        #si sí existe, edito los campos
        responsable_llave.nombre=nombre_form
        responsable_llave.apellido=apellido_form
        db.session.commit() 
    
    return responsable_llave


def combinar_fecha_hora(request, campo_fecha: str, campo_hora: str = None) -> datetime:
    fecha_str = request.form.get(campo_fecha)
    hora_str = request.form.get(campo_hora) if campo_hora else None
    hora_str = hora_str or "00:00"

    if not fecha_str:
        raise ValueError(f"El campo '{campo_fecha}' es obligatorio.")

    try:
        return datetime.strptime(f"{fecha_str} {hora_str}", "%Y-%m-%d %H:%M")
    except ValueError:
        raise ValueError(f"La fecha u hora ingresada en '{campo_fecha}' no tiene el formato correcto.")

@eventos_bp.route("/editar_evento/<int:id_evento>", methods=["GET", "POST"])
def editar_evento(id_evento):
    evento = Evento.query.get_or_404(id_evento)

    if request.method == "POST":
        try:
            # --- Fechas ---
            fecha_inicio = combinar_fecha_hora(request, "fecha_inicio", "hora_inicio")
            fecha_fin = combinar_fecha_hora(request, "fecha_fin", "hora_fin")

            if fecha_inicio >= fecha_fin:
                raise Exception("Horario de inicio NO puede ser mayor a horario de finalización")
            
            if float(request.form.get("monto_total")) < 0:
                raise Exception("El monto inicial NO pude ser negativo")
    
            # Actualizar datos del evento
            evento.descripcion = request.form.get("descripcion")
            evento.monto_total = request.form.get("monto_total")
            evento.fecha_inicio = fecha_inicio
            evento.fecha_fin = fecha_fin
            evento.observaciones = request.form.get("observaciones")
            db.session.commit()

            # Datos del cliente asociado
            cliente = evento.cliente
            evento.cliente = editar_cliente(cliente, request.form.get("nombre"),
                                            request.form.get("apellido"),
                                            request.form.get("telefono"),
                                            request.form.get("institucion"))

            # Datos de los responsables de la llave
            responsable_apertura = evento.responsable_apertura
            evento.responsable_apertura = editar_responsable_llave(responsable_apertura, 
                                                                         request.form.get("nombre_apertura"),
                                                                         request.form.get("apellido_apertura"))
            responsable_cierre = evento.responsable_cierre
            evento.responsable_cierre = editar_responsable_llave(responsable_cierre, 
                                                                       request.form.get("nombre_cierre"), 
                                                                       request.form.get("apellido_cierre"))

            flash("Evento actualizado correctamente ")
            return redirect(url_for('eventos_bp.eventos'))
        except Exception as e:
            db.session.rollback()
            flash(f"Error al editar el evento: {str(e)}", "error")
            return render_template("editar_evento.html", evento=evento)

    return render_template("editar_evento.html", evento=evento)

# Muestra los detalles de un evento
@eventos_bp.route("/detalles/<int:id_evento>", methods=["GET"])
def detalles_evento(id_evento):
    evento = Evento.query.get_or_404(id_evento)  

    # 2. Inicializar la hora de fin de limpieza
    hora_fin_limpieza_str = None
    
    # 3. Calcular la hora de fin con la limpieza (si existe fecha de fin)
    if evento.fecha_fin:
        # Asumiendo que evento.fecha_fin es un objeto datetime.
        # Sumamos una hora (60 minutos) de limpieza.
        fecha_fin_con_limpieza = evento.fecha_fin + timedelta(hours=1)
        
        # Formateamos solo la hora para pasarla a la plantilla
        hora_fin_limpieza_str = fecha_fin_con_limpieza.strftime('%H:%M') 
        # Si quisieras la fecha completa, usa: fecha_fin_con_limpieza.strftime('%d/%m/%Y %H:%M')

    return render_template("detalles_evento.html", 
                         evento=evento,
                         start_dt=evento.fecha_inicio,
                         end_dt=evento.fecha_fin,
                         hora_fin_limpieza_str=hora_fin_limpieza_str)

# Listado de eventos Desde: fecha - Hasta: fecha
@eventos_bp.route("/filtrar", methods=["GET"])
def rango_eventos_por_fecha():
    try:
        # Obtener los parámetros desde el formulario
        desde_str = request.args.get("desde")
        hasta_str = request.args.get("hasta")

        # Si no se ingresó ninguna fecha, mostrar todos
        if not desde_str and not hasta_str:
            eventos = Evento.query.all()
            return render_template("eventos.html", eventos=eventos)

        # Parsear las fechas
        desde = datetime.strptime(desde_str, "%Y-%m-%d") if desde_str else None
        hasta = datetime.strptime(hasta_str, "%Y-%m-%d") if hasta_str else None

        # Validación de rango
        if desde and hasta and desde > hasta:
            raise Exception(" La fecha 'Desde' no puede ser mayor que la fecha 'Hasta'.")

        # Construir la query dinámicamente
        query = Evento.query
        if desde:
            query = query.filter(Evento.fecha_inicio >= desde)
        if hasta:
            query = query.filter(Evento.fecha_fin <= hasta)

        eventos = query.all()

        if not eventos:
            flash("No se encontraron eventos en ese rango de fechas.", "info")

        return render_template("eventos.html", eventos=eventos)

    except ValueError:
        flash("Formato de fecha inválido. Usa el formato YYYY-MM-DD.", "danger")
        return redirect(url_for("eventos_bp.eventos"))
    except Exception as e:
        flash(f"Error al filtrar eventos: {str(e)}", "danger")
        return redirect(url_for("eventos_bp.eventos"))

#Los criterios de búsqueda pueden ser:
#i. Por DNI del cliente
#ii. Por Nombre del cliente 
#iii. Por Descripción del Evento 
#iv. Por ID del evento
@eventos_bp.route("/buscar", methods=["GET", "POST"])
def buscar_evento_campo():
    try:
        campo = request.form.get("campo")
        valor = request.form.get("valor")

        resultados = busqueda_por_campo(campo, valor)

        if not resultados:
            flash("No se encontraron eventos con esos criterios.", "info")

        return render_template("eventos.html", eventos=resultados, campo=campo, valor=valor)

    except Exception as e:
        flash(f" Error al buscar eventos: {str(e)}", "danger")
        return redirect(url_for("eventos_bp.eventos"))
    
def busqueda_por_campo(campo, valor):
    query = Evento.query

    if not campo or not valor:
        raise Exception("Por favor, completá un campo y un valor de búsqueda.")

    if campo == "nombre":
        query = query.join(Cliente)
    # --- Filtros según el campo elegido ---
    if campo == "dni":
        query = query.filter(Evento.dni.ilike(f"%{valor}%"))

    elif campo == "descripcion":
        query = query.filter(Evento.descripcion.ilike(f"%{valor}%"))

    elif campo == "nombre":
        query = query.filter(Cliente.nombre.ilike(f"%{valor}%"))

    elif campo == "id_evento":
        # Si se ingresa un ID, buscamos por coincidencia exacta
        query = query.filter(Evento.id_evento == valor)
    elif not campo:
        query = query
    else:
        raise Exception("Campo de búsqueda no válido.")
     
    return query.all()
        
@eventos_bp.route("/eliminar/<int:id_evento>", methods=["POST"])
def eliminar_evento(id_evento):
    try:
        evento = Evento.query.get_or_404(id_evento)
        db.session.delete(evento)
        db.session.commit()
        flash("Evento eliminado correctamente")
        return redirect(url_for("eventos_bp.eventos"))
    except Exception as e:
        db.session.rollback()
        flash(f"Error al eliminar el evento: {str(e)}", "error")
        return redirect(url_for("eventos_bp.eventos"))

@eventos_bp.route("/events-json", methods=["GET"])
def eventos_json():
    eventos = Evento.query.all()

    return jsonify([
        {
            "title": e.descripcion,
            "start": e.fecha_inicio.isoformat(),  # → incluye fecha y hora
            "end": e.fecha_fin.isoformat(),       # → incluye fecha y hora
            "allDay": False,  
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
