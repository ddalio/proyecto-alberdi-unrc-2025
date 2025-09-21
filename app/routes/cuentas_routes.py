from flask import request, flash, redirect, url_for, render_template, Blueprint
from werkzeug.security import generate_password_hash
from app.models import Cuenta, Administrador, db

cuentas_bp = Blueprint('cuentas', __name__, url_prefix='/cuentas')

# NOTA!!! Toda esta seccion la verias si sos admin
# Listado de cuentas
@cuentas_bp.route("/")
def cuentas():
    try:
        # todas las cuentas
        cuentas = Cuenta.query.all()
        return render_template('cuentas.html', cuentas_list = cuentas)
    except Exception as e:
        # si no hay eventos disponibles
        print(f"Error al cargar cuentas: {str(e)}")
        return render_template("cuentas.html", cuentas_list = [])

# NOTA!!! Se usaria en el metodo donde este el listado de las cuentas
def buscar_cuenta():
    return 0

@cuentas_bp.route("/crear", methods=["GET", "POST"])
def crear_cuenta():
    if request.method == "POST":
        # Obtener datos del formulario
        nombre_usuario = request.form.get("usuario")
        rol = request.form.get("rol")
        nombre = request.form.get("nombre")
        apellido = request.form.get("apellido")
        email = request.form.get("email")
        password = request.form.get("password")
        password2 = request.form.get("password2")

        # Validaciones básicas
        if not nombre_usuario or not rol or not nombre or not apellido or not email or not password:
            print("Todos los campos obligatorios deben completarse", "error")
            return redirect(url_for("cuentas.crear_cuenta"))

        if password != password2:
            print("Las contraseñas no coinciden", "error")
            return redirect(url_for("cuentas.crear_cuenta"))

        # Verificar que usuario y email no existan
        if Cuenta.query.get(nombre_usuario):
            print("El nombre de usuario ya existe", "error")
            return redirect(url_for("cuentas.crear_cuenta"))

        if Cuenta.query.filter_by(email=email).first():
            print("El email ya está registrado", "error")
            return redirect(url_for("cuentas.crear_cuenta"))

        try:
            # Crear cuenta
            nueva_cuenta = Cuenta(
                nombre_usuario=nombre_usuario,
                nombre=nombre,
                apellido=apellido,
                email=email,
                contrasenia=generate_password_hash(password)
            )
            db.session.add(nueva_cuenta)
            db.session.flush()  # Para tener el nombre_usuario antes del commit

            # Si el rol es administrador, crear también la tupla en Administrador
            if rol.lower() == "administrador":
                admin = Administrador(nombre_usuario=nombre_usuario)
                db.session.add(admin)

            db.session.commit()
            print("Usuario creado correctamente", "success")
            return redirect(url_for("cuentas.cuentas"))  
        except Exception as e:
            db.session.rollback()
            print(f"Error al crear usuario: {str(e)}", "error")
            return redirect(url_for("cuentas.crear_cuenta"))

    # Si es GET => mostrar formulario
    return render_template("agregar_cuenta.html")



#se pondria el id de la cuenta a editar
@cuentas_bp.route("/editar")
def editar_cuenta():
    return render_template('editar_cuenta.html')

# DUDA!!! No se si se necesita una ruta aparte para esto, creo q no
#@main.route("/cuentas/eliminar")
def eliminar_cuenta():
    return render_template('eliminar_cuenta.html')