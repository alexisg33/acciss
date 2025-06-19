import csv
import os
from flask_sqlalchemy import SQLAlchemy
from app import app, db, Component

with app.app_context():
    with open('components_export.csv', 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            component = Component(
                part_number=row['part_number'],
                description=row['description'],
                serial_number=row['serial_number'],
                entry_date=row['entry_date'],
                location=row['location'],
                status=row['status'],
                technician=row['technician'],
                aircraft_registration=row['aircraft_registration'],
                wo_number=row.get('wo_number'),
                output_location=row.get('output_location'),
                output_technician=row.get('output_technician'),
                output_destination=row.get('output_destination'),
                output_date=row.get('output_date')
            )
            db.session.add(component)
        db.session.commit()

print("✅ Datos importados a PostgreSQL con éxito.")
