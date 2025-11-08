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
    if total_pagado >= float(evento.monto_total):
        evento.adeuda = False
        flash("Se completo el pago del evento")

@ingresos_bp.route("/agregar_pago/<int:id_evento>", methods =["GET","POST"])
def agregar_pago(id_evento):
    evento = Evento.query.get_or_404(id_evento)
    if request.method == "POST":
        monto_pago = request.form.get("monto_pago")
        # Usuario logueado
        usuario_creacion = session.get("username")
        if monto_pago and float(monto_pago) > 0:
            # Registro de un pago
            pago = Pago(id_evento = id_evento,
                        monto_pago = float(monto_pago),
                        fecha = datetime.utcnow(),
                        usuario_creacion = usuario_creacion)
            db.session.add(pago)
    # Actualizar el estado de pago del evento
            db.session.commit()
        
        return redirect(url_for('ingresos.ingresos'))
    return render_template("agregar_pago.html", evento=evento)

def total_pagado(evento) -> float:
    total_pagado = 0
    for p in evento.pagos:
        total_pagado+=float(p.monto_pago)

    return total_pagado

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






# ---------------------Metodos que no sabemos si agregar todavia-----------------------------------


# CHEQUEAR!!! Logica de agregar un pago, desde que ruta hacerlo NO editarlo


# @main.route("/ingresos/eliminar/<int:id_pago>", methods = ["POST"])
# def eliminar_ingreso(id_pago):
#     try:
#         pago = Pago.query.get(id_pago)
#         if not pago:
#             flash("No se encontro el pago")
#             return redirect(url_for("ingresos.html"))

#         evento = Evento.query.get(pago.evento_id)
#         db.session.delete(pago)
#         db.session.commit()

#         # Actualizar estado del evento
#         actualizar_estado_evento(evento)

#         flash("Pago eliminado correctamente")
#         return redirect(url_for("main.ingresos"))

#     except Exception as e:
#         db.session.rollback()
#         flash(f"Error al eliminar pago: {str(e)}")
#         return redirect(url_for("ingresos.html"))