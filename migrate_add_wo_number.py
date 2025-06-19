import psycopg2
import os

DATABASE_URL = os.environ.get('DATABASE_URL')

conn = psycopg2.connect(DATABASE_URL)
cur = conn.cursor()

cur.execute("""
ALTER TABLE components
ADD COLUMN IF NOT EXISTS wo_number VARCHAR(100);
""")

conn.commit()
cur.close()
conn.close()

print("Columna wo_number agregada correctamente.")
