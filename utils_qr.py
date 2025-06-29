# utils_qr.py

import qrcode
import os

def generar_qr(datos: str, nombre_archivo: str):
    os.makedirs(os.path.dirname(nombre_archivo), exist_ok=True)
    qr = qrcode.make(datos)
    qr.save(nombre_archivo)
