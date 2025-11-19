from app import create_app, db
from sqlalchemy import text

app = create_app()

with app.app_context():
    try:
        print("=== ACTUALIZANDO ESTRUCTURA DE CUENTA ===")
        
        # 1. Verificar columnas actuales
        from sqlalchemy import inspect
        inspector = inspect(db.engine)
        current_columns = [col['name'] for col in inspector.get_columns('cuenta')]
        print(f"Columnas actuales: {current_columns}")
        
        # 2. Agregar columnas faltantes
        if 'rol' not in current_columns:
            print("Agregando columna 'rol'...")
            db.session.execute(text("ALTER TABLE cuenta ADD COLUMN rol VARCHAR(20) NOT NULL DEFAULT 'usuario'"))
        
        if 'email_verificado' not in current_columns:
            print("Agregando columna 'email_verificado'...")
            db.session.execute(text("ALTER TABLE cuenta ADD COLUMN email_verificado BOOLEAN NOT NULL DEFAULT 0"))
        
        if 'fecha_verificacion' not in current_columns:
            print("Agregando columna 'fecha_verificacion'...")
            db.session.execute(text("ALTER TABLE cuenta ADD COLUMN fecha_verificacion DATETIME NULL"))
        
        # 3. Renombrar password a password_hash si es necesario
        if 'password' in current_columns and 'password_hash' not in current_columns:
            print("Renombrando 'password' a 'password_hash'...")
            db.session.execute(text("ALTER TABLE cuenta RENAME COLUMN password TO password_hash"))
        
        db.session.commit()
        print("=== ACTUALIZACIÓN COMPLETADA ===")
        
        # 4. Verificar resultado final
        final_columns = [col['name'] for col in inspector.get_columns('cuenta')]
        print(f"Columnas finales: {final_columns}")
        
    except Exception as e:
        print(f"Error durante la actualización: {e}")
        db.session.rollback()
