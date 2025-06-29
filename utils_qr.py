import qrcode

def generar_qr(texto, destino_io):
    img = qrcode.make(texto)
    img.save(destino_io, format="PNG")
