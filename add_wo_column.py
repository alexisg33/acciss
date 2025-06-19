from app import db

with db.engine.connect() as conn:
    conn.execute('ALTER TABLE components ADD COLUMN wo_number TEXT')
    print("✅ Columna 'wo_number' agregada correctamente.")
