from flask import Blueprint, render_template, request, redirect, url_for, session, flash
from datetime import datetime
from app.models import Evento, Cliente, ResponsableLlave, Pago, Cuenta, db

ingresos_bp = Blueprint('ingresos', __name__, url_prefix='/ingresos')

# Listado de ingresos de TODOS los eventos, SOLO CONSULTA
# id evento | total a pagar | total pagado (sum pagos)
@ingresos_bp.route("/ingresos", methods = ["GET"])
def ingresos():
    return render_template('ingresos.html')




# ---------------------Metodos que no sabemos si agregar todavia-----------------------------------


# CHEQUEAR!!! Logica de agregar un pago, desde que ruta hacerlo NO editarlo
# @main.route("/ingresos/editar/<int:id_pago>", methods=["POST"])
# def actualizar_pago(id_pago):
#     # Usuario logueado
#     usuario_nombre = session.get("username")
#     usuario = Cuenta.query.get(usuario_nombre)

#     #verificar si el usuario tiene permisos(HACER)

#     try:
#         pago = Pago.query.get_or_404(id_pago)
#         pago.monto_pago = float(request.form.get("monto_pago"))
#         pago.fecha = datetime.utcnow()
#         pago.usuario_creacion = usuario.nombre_usuario

#         # Actualizar estado del evento al que pertenece el pago
#         actualizar_estado_evento(pago.evento)
#         flash("Se actualizo correctamente")
#         db.session.commit()


#         flash("Pago actualizado correctamente")
#         return redirect(url_for("ingresos"))
#     except Exception as e:
#         db.session.rollback()
#         flash(f"Error al actualizar pago: {str(e)}")
#         return redirect(url_for("INGRESOS", id_pago=id_pago))


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