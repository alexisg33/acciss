from app import db
from sqlalchemy import text

with db.engine.connect() as conn:
    try:
        conn.execute(text("ALTER TABLE components ADD COLUMN wo_number TEXT"))
        print("✅ Columna 'wo_number' agregada correctamente.")
    except Exception as e:
        print(f"⚠️ Ya existe o hubo error: {e}")
