from flask import Blueprint, render_template
from app.models import Cliente

main = Blueprint('main', __name__)

@main.route("/")
@main.route("/inicio")
def inicio():
    return render_template('inicio.html')

@main.route("/registro")
def registro():
    return render_template('registro.html')

@main.route("/eventos")
def eventos():
    return render_template('eventos.html'   )

@main.route("/clientes")
def clientes():
    clientes = Cliente.query.all()
    return render_template('clientes.html', clientes=clientes)

@main.route("/ingresos")
def ingresos():
    return render_template('ingresos.html')

@main.route("/cuentas")
def cuentas():
    return render_template('cuentas.html')

# esta es una función que ya tiene flask para los errores
@main.errorhandler(404)
def not_found(e):
  return render_template("404.html")


