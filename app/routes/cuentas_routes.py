from flask import Blueprint, render_template, request, redirect, url_for, flash
from app.models import Cuenta, Administrador
from werkzeug.security import generate_password_hash, check_password_hash
from app import db



cuentas_bp = Blueprint('cuentas', __name__, url_prefix='/cuentas')

# NOTA!!! Toda esta seccion la verias si sos admin
# Listado de cuentas
@cuentas_bp.route("/")
def cuentas():
    return render_template('cuentas.html')

# NOTA!!! Se usaria en el metodo donde este el listado de las cuentas
def buscar_cuenta():
    return 0

@cuentas_bp.route("/crear", methods=['GET', 'POST'])
def crear_cuenta():
    
    if request.method == "POST":    
        nombre_usuario = request.form.get('usuario').strip()
        contraseña = request.form.get('password').strip()
        repetir_contraseña = request.form.get('password2').strip()
        nombre = request.form.get('nombre').strip()
        apellido = request.form.get('apellido').strip()
        email = request.form.get('email').strip()
        rol = request.form.get('rol').strip()

        # validacion para que los campos no sean vacio(hacer con frontend)
        if not all([nombre_usuario, contraseña, repetir_contraseña, nombre, apellido, email,rol]):
            flash("Todos los campos son obligatorios", "error")
            return render_template('agregar_usuario.html', form=request.form)

        # hacer estas validaciones con frontend
        if(contraseña != repetir_contraseña):
            flash("Las contraseñas no coinciden", "error")
            return render_template('agregar_usuario.html', form=request.form)
    
        if Cuenta.query.filter_by(nombre_usuario=nombre_usuario).first():
            flash("El nombre de usuario ya existe", "error")
            return render_template("agregar_usuario.html", form=request.form)


        # encriptar la contraseña
        hash_contraseña = generate_password_hash(contraseña)

        nueva_cuenta = Cuenta(nombre_usuario=nombre_usuario, email=email, nombre=nombre, apellido=apellido, password=hash_contraseña)
        db.session.add(nueva_cuenta)
        
        #guardo la cuenta en la tabla cuenta y ademas en administrador en caso de que el rol = admin
        if rol == "administrador":
            nuevo_admin = Administrador(nombre_usuario = nombre_usuario)
            db.session.add(nuevo_admin)

        db.session.commit()
        return redirect(url_for("cuentas.cuentas"))

    return render_template('agregar_usuario.html')



#se pondria el id de la cuenta a editar
@cuentas_bp.route("/editar")
def editar_cuenta():
    return render_template('editar-cuenta.html')

# DUDA!!! No se si se necesita una ruta aparte para esto, creo q no
#@main.route("/cuentas/eliminar")
def eliminar_cuenta():
    return render_template('cuentas.html')