from flask import Blueprint, render_template
from flask import Flask, render_template, request, redirect, url_for, session, flash
from werkzeug.security import generate_password_hash, check_password_hash
from app.models import Cuenta, Cliente

main = Blueprint('main', __name__)

@main.route("/")
@main.route("/inicio")
def inicio():
    return render_template('inicio.html')

@main.route("/registro", methods = ["GET", "POST"])
def registro():
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")

        # Buscar usuario en la base de datos
        user = Cuenta.query.filter_by(nombre_usuario=username).first()

        # Si el usuario existe y la contraseña es correcta, iniciar sesión
        if user and check_password_hash(user.contrasenia, password):
            session['username'] = user.nombre_usuario
            return redirect(url_for('main.inicio'))
        else:
            flash("Usuario o contraseña incorrectos"), 401
            return redirect(url_for('main.registro'))

    return render_template('registro.html')


@main.route("/eventos")
def eventos():
    try:
        # eventos ordenados por fecha
        eventos = Evento.query.order_by(Evento.fecha_inicio.des()).all()
        return render_template('eventos_lista.html', eventos = eventos)
    except Exception as e:
        # si no hay eventos disponibles
        flash(f"Error al cargar eventos: {str(e)}")
        return render_template("eventos_lista.html", eventos = [])

@main.route("/eventos/crear", methods =["POST"])
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
        if not usuario:
            flash("Usuario no encontrado en sesión")
            return redirect(url_for("main.crear"))

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
        flash("Evento creado correctamente")
        return redirect(url_for("main.lista_eventos"))

    except Exception as e:
        db.session.rollback()
        flash(f"Error al crear evento: {str(e)}")
        return redirect(url_for("main.crear"))

    #ver la logica de pago para actualizar adeuda y nro_recibo

@main.route("/ingresos")
def ingresos():
    try:
        # Trae todos los pagos 
        pagos = Pago.query.order_by(Pago.fecha.desc()).all()
        return render_template("lista_ingresos.html", pagos = pagos)
    except Exception as e:
        flash(f"Error al cargar ingresos: {str(e)}")
        return render_template('lista_ingresos.html', pagos = [])


@main.route("/ingresos/editar/<int:id_pago>", methods=["GET"])
def editar_ingreso(id_pago):
    pago = Pago.query.get_or_404(id_pago)
    return render_template("editar_pago.html", pago=pago)


# Funcion para actualizar el estado de pago de un evento
def actualizar_estado_evento(evento):
    total_pagado = sum([float(p.monto_pago) for p in evento.pagos])
    
    if total_pagado >= float(evento.monto_total):
        evento.adeuda = False
        evento.nro_recibo = evento.pagos[-1].id_pago if evento.pagos else None
    else:
        evento.adeuda = True
        evento.nro_recibo = None

    db.session.commit()

@main.route("/ingresos/editar/<int:id_pago>", methods=["POST"])
def actualizar_pago(id_pago):
    try:
        pago = Pago.query.get_or_404(id_pago)
        pago.monto_pago = float(request.form.get("monto_pago"))
        pago.fecha = datetime.strptime(request.form.get("fecha"), "%Y-%m-%d")
        db.session.commit()

        # Actualizar estado del evento relacionado
        actualizar_estado_evento(pago.evento)

        flash("Pago actualizado correctamente")
        return redirect(url_for("main.ingresos"))
    except Exception as e:
        db.session.rollback()
        flash(f"Error al actualizar pago: {str(e)}")
        return redirect(url_for("main.editar_pago", id_pago=id_pago))



@main.route("/ingresos/eliminar/<int:id_pago>")
def eliminar_ingreso(id_pago):
    try:
        pago = Pago.query.get_or_404(id_pago)
        evento = pago.evento
        db.session.delete(pago)
        db.session.commit()

        # Actualizar estado del evento
        actualizar_estado_evento(evento)

        flash("Pago eliminado correctamente")
        return redirect(url_for("main.ingresos"))

    except Exception as e:
        db.session.rollback()
        flash(f"Error al eliminar pago: {str(e)}")
        return redirect(url_for("main.ingresos"))


# esta es una función que ya tiene flask para los errores
@main.errorhandler(404)
def not_found(e):
  return render_template("404.html")



@main.route("/cuentas")
def cuentas():
    return render_template('cuentas.html')

@main.route("/clientes")
def clientes():
    clientes = Cliente.query.all()
    return render_template('clientes.html', clientes=clientes)
