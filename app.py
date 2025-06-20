import os
from datetime import datetime
from flask import Flask, render_template, request, redirect, url_for, jsonify
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import func, case
from sqlalchemy.exc import ProgrammingError

app = Flask(__name__)

# Configuración para PostgreSQL usando variable de entorno, o SQLite por defecto
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL') or 'sqlite:///components.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

class Component(db.Model):
    __tablename__ = 'components'
    id = db.Column(db.Integer, primary_key=True)
    part_number = db.Column(db.String)
    description = db.Column(db.String)
    serial_number = db.Column(db.String)
    entry_date = db.Column(db.String, default=lambda: datetime.now().strftime('%Y-%m-%d'))
    location = db.Column(db.String)
    status = db.Column(db.String)
    technician = db.Column(db.String)
    aircraft_registration = db.Column(db.String)
    wo_number = db.Column(db.String)
    output_location = db.Column(db.String)
    output_technician = db.Column(db.String)
    output_destination = db.Column(db.String)
    output_date = db.Column(db.String)

# Función para agregar columna wo_number si no existe (ejecutar una vez y comentar)
def add_wo_number_column():
    try:
        with db.engine.connect() as con:
            con.execute('ALTER TABLE components ADD COLUMN wo_number VARCHAR;')
        print("Columna 'wo_number' agregada correctamente.")
    except ProgrammingError as e:
        print("La columna 'wo_number' ya existe o error:", e)

# add_wo_number_column()  # Ejecutar una vez y comentar

@app.route('/')
def index():
    return render_template('index.html')  # Página con hexágonos

@app.route('/hexagonos')
def hexagonos():
    return render_template('index.html')  # O puedes usar otra plantilla si quieres

@app.route('/componentes')
def componentes():
    # Aquí puedes mostrar un menú con botones para componentes
    return render_template('componentes_menu.html')

@app.route('/insumos')
def insumos():
    # Por ahora solo "Work in progress"
    return render_template('insumos_menu.html')

# --- Rutas ya existentes de registro e inventario componentes ---

@app.route('/register_in', methods=['GET', 'POST'])
def register_in():
    if request.method == 'POST':
        component = Component(
            part_number=request.form['part_number'],
            description=request.form['description'],
            serial_number=request.form['serial_number'],
            location=request.form['location'],
            status=request.form['status'],
            technician=request.form['technician'],
            aircraft_registration=request.form['aircraft_registration'],
            wo_number=request.form.get('wo_number') or '',
            output_location='',
            output_technician='',
            output_destination='',
            output_date=''
        )
        db.session.add(component)
        db.session.commit()
        return redirect('/inventory')
    return render_template('register_in.html')

@app.route('/inventory', methods=['GET'])
def inventory():
    selected_aircraft = request.args.get('aircraft_registration', None)

    query = Component.query.filter((Component.output_date == '') | (Component.output_date == None))

    if selected_aircraft:
        query = query.filter(Component.aircraft_registration == selected_aircraft)

    components = query.all()

    aircrafts = (
        db.session.query(Component.aircraft_registration)
        .filter((Component.output_date == '') | (Component.output_date == None))
        .filter(Component.aircraft_registration.isnot(None))
        .filter(Component.aircraft_registration != '')
        .distinct()
        .all()
    )
    aircrafts = [a[0] for a in aircrafts]

    return render_template('inventory.html', components=components, aircrafts=aircrafts, selected_aircraft=selected_aircraft)

@app.route('/register_out/<int:id>', methods=['POST'])
def register_out(id):
    component = Component.query.get(id)
    if component:
        component.output_location = request.form['output_location']
        component.output_technician = request.form['output_technician']
        component.output_destination = request.form['output_destination']
        component.output_date = datetime.now().strftime('%Y-%m-%d')
        db.session.commit()
    return redirect(url_for('inventory'))

@app.route('/historial_salidas')
def historial_salidas():
    salidas = Component.query.filter(Component.output_date != '').order_by(Component.output_date.desc()).all()
    return render_template('historial_salidas.html', salidas=salidas)

@app.route('/chart')
def chart():
    return render_template('chart.html')

@app.route('/chart_data')
def chart_data():
    data = (
        db.session.query(
            Component.aircraft_registration,
            func.count(case(
                ( (Component.output_date == '') | (Component.output_date == None), 1 )
            )).label('entradas'),
            func.count(case(
                ( (Component.output_date != '') & (Component.output_date != None), 1 )
            )).label('salidas')
        )
        .filter(Component.aircraft_registration.isnot(None))
        .filter(Component.aircraft_registration != '')
        .group_by(Component.aircraft_registration)
        .all()
    )
@app.route('/')
def index():
    return render_template('index.html')

    return jsonify({
        'labels': [d[0] for d in data],
        'entradas': [d[1] for d in data],
        'salidas': [d[2] for d in data],
    })

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port, debug=True)
