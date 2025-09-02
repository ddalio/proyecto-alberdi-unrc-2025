from flask import Flask, render_template

app = Flask(__name__)

@app.route("/")
@app.route("/inicio")
def inicio():
    #el active_page sirve para los estilos en el nav
    return render_template('inicio.html', active_page='inicio')

@app.route("/registro")
def registrar():
    return render_template('registro.html')

@app.route("/eventos")
def eventos():
    return render_template('eventos.html')

@app.route("/ingresos")
def ingresos():
    #el active_page sirve para los estilos en el nav
    return render_template('ingresos.html', active_page='ingresos')

@app.route("/cuentas")
def cuentas():
    #el active_page sirve para los estilos en el nav
    return render_template('cuentas.html', active_page='cuentas')

# esta es una función que ya tiene flask para los errores
@app.errorhandler(404)
def not_found(e):
  return render_template("404.html")


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)

