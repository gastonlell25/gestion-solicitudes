import os


# Clase para manejar la base de datos
class ArchivoJSON:

    def __init__(self):
        self.ruta = os.environ.get("ARCHIVO_DATOS") or os.path.join(os.path.dirname(__file__), "..", "data", "solicitudes.json")

    def leer(self):
        try:
            f = open(self.ruta, "r", encoding="utf-8")
            txt = f.read()
            f.close()
            return txt
        except:
            return None

    def escribir(self, txt):
        with open(self.ruta, "w", encoding="utf-8") as f:
            f.write(txt)
