import qrcode
import os

def generar_qr(texto, ruta_salida):
    os.makedirs(os.path.dirname(ruta_salida), exist_ok=True)
    qr = qrcode.make(texto)
    qr.save(ruta_salida)

