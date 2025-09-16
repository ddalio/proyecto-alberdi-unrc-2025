from app import create_app, db

app = create_app()

with app.app_context():
    db.create_all()  # 🔹 crea todas las tablas definidas en models.py

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
