import sqlite3
from app import app, db, Component

def migrate():
    conn_sqlite = sqlite3.connect('components.db')
    cursor = conn_sqlite.cursor()
    cursor.execute("SELECT * FROM components")
    rows = cursor.fetchall()

    with app.app_context():
        for row in rows:
            component = Component(
                part_number=row[1],
                description=row[2],
                serial_number=row[3],
                entry_date=row[4] or '',
                location=row[5],
                status=row[6],
                technician=row[7],
                aircraft_registration=row[8],
                output_location=row[9] or '',
                output_technician=row[10] or '',
                output_destination=row[11] or '',
                output_date=row[12] or ''
            )
            db.session.add(component)
        db.session.commit()
    conn_sqlite.close()
    print("✅ Migración completada")

if __name__ == '__main__':
    migrate()
