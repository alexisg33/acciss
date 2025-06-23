import os
from datetime import datetime
from flask import Flask, render_template, request, redirect, url_for, jsonify
from flask_sqlalchemy import SQLAlchemy
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

# Ruta para la "baja" con el id, cantidad y número de empleado
@app.route('/registrar_baja', methods=['POST'])
def registrar_baja():
    data = request.json
    material_id = data.get('id')
    employee_id = data.get('employee_id')
    quantity = int(data.get('quantity'))

    material = StockItem.query.get(material_id)
    if not material:
        return jsonify({'status': 'error', 'message': 'Material no encontrado'}), 400

    # Restamos la cantidad y agregamos la baja
    material.quantity -= quantity
    db.session.commit()

    baja = StockItem(
        material_description=f"Baja - {material.material_description}",
        part_number=material.part_number,
        hazards_identified=material.hazards_identified,
        date=datetime.now().strftime('%Y-%m-%d'),
        quantity=-quantity,
        after_open=material.after_open,
        expiration_date=material.expiration_date,
        due_date_match=material.due_date_match,
        batch_number=material.batch_number,
        comments=f"Baja realizada por el empleado {employee_id}"
    )
    db.session.add(baja)
    db.session.commit()

    return jsonify({'status': 'success'})

# Rutas para otros refrigeradores
@app.route('/refrigerador_2')
def refrigerador_2():
    return "Vista para Refrigerador 2"

@app.route('/camara_frigorifica')
def camara_frigorifica():
    return "Vista para Cámara Frigorífica"

@app.route('/Rack_1')
def camara_frigorifica():
    return "Vista para Cámara Rack 1"

@app.route('/Rack_2')
def camara_frigorifica():
    return "Vista para Cámara Rack 2"

@app.route('/Rack_3')
def camara_frigorifica():
    return "Vista para Cámara Rack 3"

@app.route('/Rack_4')
def camara_frigorifica():
    return "Vista para Cámara Rack 4"

@app.route('/Gaveta_1')
def camara_frigorifica():
    return "Vista para Gaveta 1"

@app.route('/Gaveta_2')
def camara_frigorifica():
    return "Vista para Gaveta 2"

@app.route('/Gaveta_3')
def camara_frigorifica():
    return "Vista para Gaveta 3"

@app.route('/Coordinación_de_Insumos')
def camara_frigorifica():
    return "Coordinación de Insumos"

# Inicio de la aplicación
if __name__ == '__main__':
    with app.app_context():
        db.create_all()  # Crea todas las tablas en la base de datos
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=True)
