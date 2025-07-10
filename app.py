# app.py - Versión final corregida

import os
from datetime import datetime
from flask import Flask, render_template, request, redirect, url_for, jsonify
from flask_sqlalchemy import SQLAlchemy
from werkzeug.utils import secure_filename
from flask import redirect
from utils_qr import generar_qr


app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL') or 'sqlite:///components.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
UPLOAD_FOLDER = 'static/datasheets'
ALLOWED_EXTENSIONS = {'pdf'}
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

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

@app.route('/register_in', methods=['GET', 'POST'], endpoint='register_in')
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
        return redirect(url_for('inventory'))  # <- aquí usas el endpoint definido en la ruta /inventario
    return render_template('register_in.html')

@app.route('/inventario', methods=['GET'])
def inventory():
    search = request.args.get('search', '')
    selected_aircraft = request.args.get('aircraft_registration', '')

    query = db.session.query(Component)
    query = query.filter((Component.output_date == None) | (Component.output_date == ''))

    if selected_aircraft:
        query = query.filter_by(aircraft_registration=selected_aircraft)

    if search:
        search_pattern = f"%{search}%"
        query = query.filter(
            (Component.part_number.ilike(search_pattern)) |
            (Component.description.ilike(search_pattern)) |
            (Component.serial_number.ilike(search_pattern))
        )

    components = query.order_by(Component.entry_date.desc()).all()

    # Aquí el cambio corregido
    aircrafts = (
        db.session.query(Component.aircraft_registration)
        .filter((Component.output_date == None) | (Component.output_date == ''))
        .distinct()
        .all()
    )
    aircrafts = [a[0] for a in aircrafts if a[0]]

    return render_template('inventory.html', components=components, aircrafts=aircrafts, selected_aircraft=selected_aircraft)




class StockItem(db.Model):
    __tablename__ = 'stock_items'
    id = db.Column(db.Integer, primary_key=True)
    material_description = db.Column(db.String, nullable=False)
    part_number = db.Column(db.String)
    hazards_identified = db.Column(db.String)
    date = db.Column(db.String)
    quantity = db.Column(db.Float, default=0.0)
    after_open = db.Column(db.String)
    expiration_date = db.Column(db.String)
    due_date_match = db.Column(db.String)
    batch_number = db.Column(db.String)
    comments = db.Column(db.String)

class StockBaja(db.Model):
    __tablename__ = 'stock_bajas'
    id = db.Column(db.Integer, primary_key=True)
    stock_id = db.Column(db.Integer, db.ForeignKey('stock_items.id'))  # Asegúrate del nombre correcto
    employee_id = db.Column(db.String)
    date = db.Column(db.String)
    quantity = db.Column(db.Integer)
    comments = db.Column(db.String)

    stock = db.relationship("StockItem", backref="bajas")  # Aquí debe coincidir con tu modelo real

 


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
    stock_items = StockItem.query.filter(StockItem.quantity > 0).all()
    consumos = Consumo.query.order_by(Consumo.fecha.desc()).all()
    return render_template('refrigerador_1.html', resinas=resinas, stock_items=stock_items, consumos=consumos)

ALLOWED_EXTENSIONS = {'pdf'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@app.route('/upload_datasheet/<part_number>', methods=['GET', 'POST'])
def upload_datasheet(part_number):
    if request.method == 'POST':
        if 'file' not in request.files:
            return 'No file part'
        file = request.files['file']
        if file.filename == '':
            return 'No selected file'
        if file and allowed_file(file.filename):
            filename = secure_filename(f"{part_number}.pdf")
            file.save(os.path.join(app.static_folder, 'datasheets', filename))
            return redirect(url_for('refrigerador_1'))
    return render_template('upload_datasheet.html', part_number=part_number)


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

@app.route('/get_material_info/<int:id>', methods=['GET'])
def get_material_info(id):
    material = StockItem.query.get(id)
    if material:
        return jsonify({
            'material_description': material.material_description,
            'part_number': material.part_number,
            'due_date_match': material.due_date_match,
            'batch_number': material.batch_number
        })
    return jsonify(None), 404

@app.route('/registrar_resina', methods=['POST'])
def registrar_resina():
    data = request.json
    nueva = StockItem(
        material_description=data['material_description'],
        part_number=data['part_number'],
        hazards_identified=data['hazards_identified'],
        date=datetime.now().strftime('%Y-%m-%d'),
        quantity=int(data['quantity']),
        after_open=data['after_open'],
        expiration_date=data['expiration_date'],
        due_date_match=data['due_date_match'],
        batch_number=data['batch_number'],
        comments=data['comments']
    )
    db.session.add(nueva)
    db.session.commit()
    return jsonify({'status': 'success'})

@app.route('/registrar_baja', methods=['POST'])
def registrar_baja():
    data = request.json
    material_id = int(data['id'])
    employee_id = data['employee_id']
    cantidad = int(data['quantity'])

    item = StockItem.query.get(material_id)
    if not item:
        return jsonify({'status': 'error', 'message': 'No encontrado'}), 404

    if item.quantity < cantidad:
        return jsonify({'status': 'error', 'message': 'Cantidad insuficiente'}), 400

    item.quantity -= cantidad
    db.session.commit()

    baja = StockBaja(
        stock_id=item.id,
        employee_id=employee_id,
        date=datetime.now().strftime('%Y-%m-%d'),
        quantity=cantidad,
        comments=f"Baja realizada por el empleado {employee_id}"
    )
    db.session.add(baja)
    db.session.commit()

    return jsonify({'status': 'success'})

@app.route('/get_bajas')
def get_bajas():
    bajas = StockBaja.query.all()
    return jsonify([{
        'id': b.id,
        'stock_id': b.stock_id,
        'employee_id': b.employee_id,
        'date': b.date,
        'quantity': b.quantity,
        'comments': b.comments
    } for b in bajas])

@app.route('/refrigerador_2')
def refrigerador_2():
    return "<h1>Refrigerador 2 - En construcción</h1>"


@app.route('/rack_1')
def rack_1():
    return render_template('rack_1.html')

@app.route('/rack_2')
def rack_2():
    return render_template('rack_2.html')

@app.route('/rack_3')
def rack_3():
    return render_template('rack_3.html')

@app.route('/rack_4')
def rack_4():
    return render_template('rack_4.html')

@app.route('/gaveta_1')
def gaveta_1():
    return render_template('gaveta_1.html')

@app.route('/gaveta_2')
def gaveta_2():
    return render_template('gaveta_2.html')

@app.route('/gaveta_3')
def gaveta_3():
    return render_template('gaveta_3.html')


@app.route('/camara_frigorifica')
def camara_frigorifica():
    return render_template('camara_frigorifica.html')

class Consumo(db.Model):
    __tablename__ = 'consumo'
    id = db.Column(db.Integer, primary_key=True)  # <- ESTA LÍNEA ES FUNDAMENTAL
    stock_id = db.Column(db.Integer)
    empleado = db.Column(db.String)
    fecha = db.Column(db.String, default=lambda: datetime.now().strftime('%Y-%m-%d'))
    cantidad = db.Column(db.Float)
    descripcion = db.Column(db.String)
    part_number = db.Column(db.String)
    coincide = db.Column(db.String)
    lote = db.Column(db.String)
    comentarios = db.Column(db.String)



@app.route('/registrar_consumo', methods=['POST'])
def registrar_consumo():
    data = request.json
    item = StockItem.query.get(data['id'])  # o Consumo, según corresponda

    nuevo = Consumo(
        stock_id = item.id,
        empleado = data['employee_id'],
        cantidad = data['quantity'],
        descripcion    = item.material_description,
        part_number    = item.part_number,
        coincide       = item.due_date_match,
        lote           = item.batch_number,
        comentarios    = f"Consumo registrado por empleado {data['employee_id']}"
    )
    db.session.add(nuevo)
    db.session.commit()
    return jsonify({'status': 'success'})



@app.route('/chart')
def chart():
    return render_template('chart.html')

@app.route('/chart_data')
def chart_data():
    components = Component.query.all()
    entradas = {}
    salidas = {}

    for c in components:
        reg = c.aircraft_registration or 'Sin Matrícula'

        # Solo contamos la entrada si el componente sigue en inventario (sin salida)
        if not c.output_date:
            entradas[reg] = entradas.get(reg, 0) + 1
        else:
            salidas[reg] = salidas.get(reg, 0) + 1

    # Solo mostramos las matrículas que tienen al menos un componente activo
    labels = [reg for reg in entradas.keys() if entradas[reg] > 0]
    entradas_data = [entradas[reg] for reg in labels]
    salidas_data = [salidas.get(reg, 0) for reg in labels]  # Puede no haber salidas, por eso .get()

    return jsonify({
        'labels': labels,
        'entradas': entradas_data,
        'salidas': salidas_data
    })


@app.route('/historial_salidas')
def historial_salidas():
    salidas = Component.query.filter(Component.output_date != None).order_by(Component.output_date.desc()).all()
    return render_template('historial_salidas.html', salidas=salidas)

@app.route('/register_out/<int:id>', methods=['POST'])
def register_out(id):
    component = Component.query.get_or_404(id)
    component.output_date = datetime.now().strftime('%Y-%m-%d')
    
    # Aquí cambias esas tres líneas por las que te doy abajo:
    component.output_technician = request.form.get('output_technician', '')
    component.output_destination = request.form.get('output_destination', '')
    component.output_location = request.form.get('output_location', '')
    
    db.session.commit()
    return redirect(url_for('inventory'))

from sqlalchemy.orm import joinedload

@app.route('/coordinacion_insumos')
def coordinacion_insumos():
     # lógica nueva con joins
    bajas = db.session.query(StockBaja).options(joinedload(StockBaja.stock)).order_by(StockBaja.date.desc()).all()
    return render_template('coordinacion_insumos.html', bajas=bajas)
class StockMaterial(db.Model):
    __tablename__ = 'stock_materials'
    id = db.Column(db.Integer, primary_key=True)
    material_description = db.Column(db.String)
    part_number = db.Column(db.String)
    # otros campos...


@app.route('/get_material/<int:stock_id>')
def get_material(stock_id):
    material = Component.query.get(stock_id)
    if material:
        return jsonify({
            'descripcion': material.description,
            'part_number': material.part_number
        })
    return jsonify({'error': 'Material no encontrado'}), 404


@app.route('/qr/<int:id>')
def generar_qr_componente(id):
    componente = Component.query.get(id)
    if not componente:
        return "Componente no encontrado", 404

    texto_qr = f"""
ID: {componente.id}
PN: {componente.part_number}
SN: {componente.serial_number}
WO: {componente.wo_number or ''}
Estado: {componente.status}
Descripción: {componente.description}
Entrada: {componente.entry_date}
""".strip()



    ruta_qr = f"static/qrs/componente_{componente.id}.png"
    generar_qr(texto_qr, ruta_qr)

    return redirect('/' + ruta_qr)


@app.route('/qr_img/<int:id>')
def mostrar_qr_en_tabla(id):
    ruta_qr = f"static/qrs/componente_{id}.png"
    if not os.path.exists(ruta_qr):
        return "QR no encontrado", 404
    return f'<img src="/{ruta_qr}" alt="QR" width="80">'


import os

@app.route('/upload_datasheet/<part_number>', methods=['GET', 'POST'])
def upload_datasheet(part_number):
    if request.method == 'POST':
        if 'file' not in request.files:
            return 'No file part'
        file = request.files['file']
        if file.filename == '':
            return 'No selected file'
        if file and allowed_file(file.filename):
            filename = secure_filename(f"{part_number}.pdf")
            # Crear la carpeta si no existe
            folder = os.path.join(app.static_folder, 'datasheets')
            os.makedirs(folder, exist_ok=True)
            file.save(os.path.join(folder, filename))
            return redirect(url_for('refrigerador_1'))

    return render_template('upload_datasheet.html', part_number=part_number)



if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=True)
