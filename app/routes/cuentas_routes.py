from flask import Blueprint, render_template

cuentas_bp = Blueprint('cuentas', __name__, url_prefix='/cuentas')

# NOTA!!! Toda esta seccion la verias si sos admin
# Listado de cuentas
@cuentas_bp.route("/cuentas")
def cuentas():
    return render_template('cuentas.html')

# NOTA!!! Se usaria en el metodo donde este el listado de las cuentas
def buscar_cuenta():
    return 0

@cuentas_bp.route("/cuentas/crear")
def crear_cuenta():
    return render_template('agregar_usuario.html')

#se pondria el id de la cuenta a editar
@cuentas_bp.route("/cuentas/editar")
def editar_cuenta():
    return render_template('editar-cuenta.html')

# DUDA!!! No se si se necesita una ruta aparte para esto, creo q no
#@main.route("/cuentas/eliminar")
def eliminar_cuenta():
    return render_template('cuentas.html')