from flask import Flask, render_template

app = Flask(__name__)

@app.route("/")
@app.route("/inicio")
def inicio():
    return render_template('inicio.html')

@app.route("/registro")
def registrar():
    return render_template('registro.html')

@app.route("/eventos")
def eventos():
    return render_template('eventos.html')

@app.route("/ingresos")
def ingresos():
    return render_template('ingresos.html')

@app.route("/cuentas")
def cuentas():
    return render_template('cuentas.html')

# esta es una función que ya tiene flask para los errores
@app.errorhandler(404)
def not_found(e):
  return render_template("404.html")


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)

