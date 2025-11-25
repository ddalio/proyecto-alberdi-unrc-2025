from flask import Blueprint, render_template, request, redirect, url_for, session, flash
from datetime import datetime
from app.models import Evento, Cliente, ResponsableLlave, Pago, Cuenta, db

ingresos_bp = Blueprint('ingresos', __name__, url_prefix='/ingresos')

# Listado de ingresos de TODOS los eventos, SOLO CONSULTA
# id evento | total a pagar | total pagado (sum pagos)
@ingresos_bp.route("/", methods = ["GET"])
def ingresos():
    try:
        eventos = Evento.query.all()
        return render_template('ingresos.html', eventos=eventos)
    except Exception as e:
        print(f"Error al cargar los ingresos eventos: {str(e)}")
        return render_template("ingresos.html", mensaje="Error al cargar ingresos")

# Funcion para actualizar el estado de pago de un evento
def actualizar_pago_evento(evento):
    if evento.total_pagado >= float(evento.monto_total):
        evento.adeuda = False
        flash("Se completo el pago del evento")

# Listado de eventos Desde: fecha - Hasta: fecha
@ingresos_bp.route("/filtrar", methods=["GET"])
def rango_eventos_por_fecha():
    try:
        # Obtener los parámetros desde el formulario
        desde_str = request.args.get("desde")
        hasta_str = request.args.get("hasta")

        # Si no se ingresó ninguna fecha, mostrar todos
        if not desde_str and not hasta_str:
            eventos = Evento.query.all()
            return render_template("eventos.html", eventos_list=eventos)

        # Parsear las fechas
        desde = datetime.strptime(desde_str, "%Y-%m-%d") if desde_str else None
        hasta = datetime.strptime(hasta_str, "%Y-%m-%d") if hasta_str else None

        # Validación de rango
        if desde and hasta and desde > hasta:
            flash("La fecha 'Desde' no puede ser mayor que 'Hasta'.", "warning")
            return redirect(url_for("eventos_bp.eventos"))

        # Construir la query dinámicamente
        query = Evento.query
        if desde:
            query = query.filter(Evento.fecha_inicio >= desde)
        if hasta:
            query = query.filter(Evento.fecha_fin <= hasta)

        eventos = query.all()

        if not eventos:
            flash("No se encontraron eventos en ese rango de fechas.", "info")

        return render_template("ingresos.html", eventos=eventos)

    except ValueError:
        flash("⚠️ Formato de fecha inválido. Usa el formato YYYY-MM-DD.", "danger")
        return redirect(url_for("ingresos.ingresos"))
    except Exception as e:
        flash(f"⚠️ Error al filtrar eventos: {str(e)}", "danger")
        return redirect(url_for("ingresos.ingresos"))

@ingresos_bp.route("/agregar_pago/<int:id_evento>", methods =["GET","POST"])
def agregar_pago(id_evento):
    evento = Evento.query.get_or_404(id_evento)
    if request.method == "POST":
        try:
            if evento.total_pagado == evento.monto_total:
                raise ValueError("El monto total ya es el correcto, NO se reciben más pagos")
            
            monto_pago = request.form.get("monto_pago")

            # Usuario logueado
            usuario_creacion = session.get("username")
            
            if float(monto_pago) < 0:
                raise ValueError("El monto debe ser positivo")
            
            
            if float(monto_pago) > evento.monto_total or float(monto_pago) + evento.total_pagado > evento.monto_total:
                raise ValueError("El monto es mayor a lo necesario")
            
            if monto_pago:
                # Registro de un pago
                pago = Pago(id_evento = id_evento,
                            monto_pago = float(monto_pago),
                            fecha = datetime.utcnow(),
                            usuario_creacion = usuario_creacion)
                db.session.add(pago)
                # Actualizar el estado de pago del evento
                actualizar_pago_evento(evento)
                db.session.commit()
            return redirect(url_for('ingresos.ingresos'))
        except ValueError as e:
            flash(f"Error al agregar pago: {str(e)}")
            return redirect(url_for("ingresos.ingresos"))
    return render_template("agregar_pago.html", evento=evento)

@ingresos_bp.route("pagos/<int:id_evento>")
def pagos(id_evento):
    try:
        # todos los eventos
        evento = Evento.query.get(id_evento)
        if not evento:
            raise ValueError("No se encontró el evento buscado")
        pagos = evento.pagos
        return render_template('pagos.html', pagos = pagos, id_evento = id_evento)
    except Exception as e:
        # si no hay eventos disponibles
        return render_template("pagos.html", mensaje=f"Error al cargar eventos {str(e)}")


@ingresos_bp.route("/pagos/eliminar/<int:id_pago>", methods=["GET","POST"])
def eliminar_pago(id_pago):
    try:
        # Solo seleccionar columnas existentes
        pago = db.session.query(
            Pago.id_pago,
            Pago.id_evento,
            Pago.monto_pago,
            Pago.fecha,
            Pago.usuario_creacion
        ).filter(Pago.id_pago == id_pago).first()

        if not pago:
            flash("No se encontró el pago")
            return redirect(url_for("ingresos.ingresos"))

        # Para borrar, necesitamos un objeto 'Pago' real, así que:
        pago_obj = Pago.query.get(id_pago)
        if pago_obj:
            db.session.delete(pago_obj)
            db.session.commit()
            flash("Pago eliminado correctamente")
        else:
            flash("No se pudo eliminar el pago")

        return redirect(url_for("ingresos.ingresos"))

    except Exception as e:
        db.session.rollback()
        flash(f"Error al eliminar pago: {str(e)}")
        return redirect(url_for("ingresos.ingresos"))
