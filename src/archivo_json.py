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
        try:
            f = open(self.ruta, "w", encoding="utf-8")
            f.write(txt)
            f.close()
            return True
        except Exception as e:
            print("Error: " + str(e))
            return False
