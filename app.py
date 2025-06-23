import os
from datetime import datetime
from flask import Flask, render_template, request, redirect, url_for, jsonify
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import func, case
from werkzeug.utils import secure_filename

app = Flask(__name__)

# Configuración de la base de datos (PostgreSQL si está en env, SQLite local si no)
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL') or 'sqlite:///components.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Carpeta para subir datasheets PDFs
UPLOAD_FOLDER = 'static/datasheets'
ALLOWED_EXTENSIONS = {'pdf'}
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

db = SQLAlchemy(app)

# Modelos

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

class StockItem(db.Model):
    __tablename__ = 'stock_items'
    id = db.Column(db.Integer, primary_key=True)
    material_description = db.Column(db.String, nullable=False)
    part_number = db.Column(db.String)
    hazards_identified = db.Column(db.String)
    date = db.Column(db.String)  # ISO 'YYYY-MM-DD'
    quantity = db.Column(db.Integer, default=0)
    after_open = db.Column(db.String)
    expiration_date = db.Column(db.String)
    due_date_match = db.Column(db.String)
    batch_number = db.Column(db.String)
    comments = db.Column(db.String)

# Funciones

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# Rutas

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/hexagonos')
def hexagonos():
    return render_template('index.html')

@app.route('/componentes')
def componentes():
    return render_template('componentes_menu.html')

@app.route('/insumos')
def insumos():
    return render_template('insumos_menu.html')

@app.route('/refrigerador_1')
def refrigerador_1():
    # Lista fija para demo, ideal cargar de DB si quieres
    resinas = [
        {"material": "Epoxy Adhesive", "part_number": "EA9390", "base": 100, "hardener": 56},
        {"material": "Epoxy Paste Adhesive", "part_number": "EA9396", "base": 100, "hardener": 30},
        {"material": "Epoxy Type of Product Structural Adhesive", "part_number": "EY3804", "base": 100, "hardener": 66},
        {"material": "Epoxy Paste", "part_number": "EA9394", "base": 100, "hardener": 17},
        {"material": "Thixotropic Paste Adhesive", "part_number": "EA934", "base": 100, "hardener": 33},
        {"material": "Thixotropic Paste Adhesive", "part_number": "52A", "base": 100, "hardener": 41},
        {"material": "Epoxy Paste Adhesive", "part_number": "EA956", "base": 100, "hardener": 58},
        {"material": "Epoxy Paste Adhesive", "part_number": "EA9309.3NA", "base": 100, "hardener": 22}
    ]
    stock_items = StockItem.query.all()
    return render_template('refrigerador_1.html', resinas=resinas, stock_items=stock_items)

@app.route('/upload_datasheet/<part_number>', methods=['GET', 'POST'])
def upload_datasheet(part_number):
    if request.method == 'POST':
        if 'pdf_file' not in request.files:
            return "No se subió ningún archivo"
        file = request.files['pdf_file']
        if file.filename == '':
            return "Nombre de archivo vacío"
        if file and allowed_file(file.filename):
            os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
            filename = secure_filename(f"{part_number}.pdf")
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            return redirect(url_for('refrigerador_1'))
    return render_template('upload_pdf.html', part_number=part_number)

@app.route('/existencias_stock', methods=['GET'])
def existencias_stock():
    materiales = StockItem.query.all()
    return render_template('existencias_stock.html', materiales=materiales)

@app.route('/update_stock_field', methods=['POST'])
def update_stock_field():
    data = request.json
    stock_id = data.get('id')
    field = data.get('field')
    value = data.get('value')

    item = StockItem.query.get(stock_id)
    if not item or field not in StockItem.__table__.columns.keys():
        return jsonify({'status': 'error', 'message': 'Elemento o campo inválido'}), 400

    setattr(item, field, value)
    db.session.commit()
    return jsonify({'status': 'success'})

@app.route('/update_component_field', methods=['POST'])
def update_component_field():
    data = request.json
    comp_id = data.get('id')
    field = data.get('field')
    value = data.get('value')

    component = Component.query.get(comp_id)
    if not component or field not in Component.__table__.columns.keys():
        return jsonify({'status': 'error', 'message': 'Elemento o campo inválido'}), 400

    setattr(component, field, value)
    db.session.commit()
    return jsonify({'status': 'success'})

# Rutas ejemplo para otras zonas de insumos (puedes completar o cambiar)
@app.route('/refrigerador_2')
def refrigerador_2():
    return "Vista para Refrigerador 2"

@app.route('/camara_frigorifica')
def camara_frigorifica():
    return "Vista para Cámara Frigorífica"

@app.route('/rack_1')
def rack_1():
    return "Vista para Rack 1"

@app.route('/rack_2')
def rack_2():
    return "Vista para Rack 2"

@app.route('/rack_3')
def rack_3():
    return "Vista para Rack 3"

@app.route('/rack_4')
def rack_4():
    return "Vista para Rack 4"

@app.route('/gaveta_1')
def gaveta_1():
    return "Vista para Gaveta 1"

@app.route('/gaveta_2')
def gaveta_2():
    return "Vista para Gaveta 2"

@app.route('/gaveta_3')
def gaveta_3():
    return "Vista para Gaveta 3"

@app.route('/coordinacion_insumos')
def coordinacion_insumos():
    return "Vista para Coordinación de Insumos"

# Registro de componentes entrada
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

# Inventario filtrado y listado de componentes no salidos
@app.route('/inventory', methods=['GET'])
def inventory():
    selected_aircraft = request.args.get('aircraft_registration')
    search = request.args.get('search')

    query = Component.query.filter((Component.output_date == '') | (Component.output_date == None))

    if selected_aircraft:
        query = query.filter(Component.aircraft_registration == selected_aircraft)

    if search:
        query = query.filter(
            (Component.part_number.ilike(f'%{search}%')) |
            (Component.description.ilike(f'%{search}%')) |
            (Component.serial_number.ilike(f'%{search}%'))
        )

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

# Registro de salida componente
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

# Historial de salidas
@app.route('/historial_salidas')
def historial_salidas():
    search = request.args.get('search')
    query = Component.query.filter(Component.output_date != '')
    if search:
        query = query.filter(
            (Component.part_number.ilike(f'%{search}%')) |
            (Component.description.ilike(f'%{search}%')) |
            (Component.serial_number.ilike(f'%{search}%'))
        )
    salidas = query.order_by(Component.output_date.desc()).all()
    return render_template('historial_salidas.html', salidas=salidas)

# Gráfica entradas/salidas por matrícula
@app.route('/chart')
def chart():
    return render_template('chart.html')

@app.route('/chart_data')
def chart_data():
    data = (
        db.session.query(
            Component.aircraft_registration,
            func.count(case(((Component.output_date == '') | (Component.output_date == None), 1))).label('entradas'),
            func.count(case(((Component.output_date != '') & (Component.output_date != None), 1))).label('salidas')
        )
        .filter(Component.aircraft_registration.isnot(None))
        .filter(Component.aircraft_registration != '')
        .group_by(Component.aircraft_registration)
        .all()
    )

    return jsonify({
        'labels': [d[0] for d in data],
        'entradas': [d[1] for d in data],
        'salidas': [d[2] for d in data],
    })

# Rutas para registrar resina y baja stock con fecha automática
@app.route('/registrar_resina', methods=['POST'])
def registrar_resina():
    data = request.json
    nueva_resina = StockItem(
        material_description = data.get('material_description', ''),
        part_number = data.get('part_number', ''),
        hazards_identified = data.get('hazards_identified', ''),
        date = datetime.now().strftime('%Y-%m-%d'),  # fecha actual automática
        quantity = int(data.get('quantity', 0)),
        after_open = data.get('after_open', ''),
        expiration_date = data.get('expiration_date', ''),
        due_date_match = data.get('due_date_match', ''),
        batch_number = data.get('batch_number', ''),
        comments = data.get('comments', '')
    )
    db.session.add(nueva_resina)
    db.session.commit()
    return jsonify({'status': 'success'})

@app.route('/registrar_baja', methods=['POST'])
def registrar_baja():
    data = request.json
    baja = StockItem(
        material_description = 'BAJA',
        part_number = '',
        hazards_identified = '',
        date = datetime.now().strftime('%Y-%m-%d'),
        quantity = 0,
        after_open = '',
        expiration_date = '',
        due_date_match = data.get('due_date_match', ''),
        batch_number = data.get('batch_number', ''),
        comments = data.get('comments', '')
    )
    db.session.add(baja)
    db.session.commit()
    return jsonify({'status': 'success'})

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=True)

import os
from datetime import datetime
from flask import Flask, render_template, request, redirect, url_for, jsonify
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import func, case
from werkzeug.utils import secure_filename

app = Flask(__name__)

# Configuración de la base de datos
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL') or 'sqlite:///components.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Carpeta para subir datasheets PDFs
UPLOAD_FOLDER = 'static/datasheets'
ALLOWED_EXTENSIONS = {'pdf'}
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Inicialización de base de datos
db = SQLAlchemy(app)

# Modelos
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