import json

from archivo_json import ArchivoJSON
from modelos.estado import Estado
from modelos.estudiante import Estudiante
from modelos.prioridad import Prioridad
from modelos.responsable import Responsable
from modelos.solicitud import Solicitud
from persistencia.datos_sistema import DatosSistema


class SolicitudRepositorioArchivo:
    """Guarda y recupera estudiantes, responsables y solicitudes en un archivo JSON."""

    def __init__(self, archivo=None):
        self.archivo = archivo or ArchivoJSON()

    def cargar(self):
        data2 = None
        txt = self.archivo.leer()
        if txt != None:
            try:
                data2 = json.loads(txt)
            except:
                pass
        if data2 == None:
            datos = self.proc(self.datos_ejemplo())
            self.guardar(datos)
            return datos
        return self.proc(data2)

    # procesa los datos
    def proc(self, data2):
        ests = []
        resp = []
        lst = []
        for e in data2["estudiantes"]:
            ests.append(Estudiante(e["legajo"], e["nombre"], e["apellido"], e["email"], e["carrera"]))
        for r in data2["responsables"]:
            resp.append(Responsable(r["id"], r["nombre"], r["area"]))
        for x in data2["solicitudes"]:
            # los datos pueden venir con variantes de mayusculas/minusculas; Estado y
            # Prioridad las normalizan, y si no reconocen el valor lo dejan como esta
            try:
                est = Estado.from_str(x["estado"]).value
            except ValueError:
                est = x["estado"]
            try:
                pri = Prioridad.from_str(x["prioridad"]).value
            except ValueError:
                pri = x["prioridad"]
            e = x["estudiante"]
            aux = Estudiante(e["legajo"], e["nombre"], e["apellido"], e["email"], e["carrera"])
            rr = None
            if x["responsable"] != None:
                rr = Responsable(x["responsable"]["id"], x["responsable"]["nombre"], x["responsable"]["area"])
            lst.append(Solicitud(x["id"], aux, x["tipo"], x["descripcion"], pri, est, rr, x["fecha_creacion"], x["fecha_modificacion"]))
        return DatosSistema(ests, resp, lst)

    # guarda los datos en la base de datos
    def guardar(self, datos):
        data2 = {
            "estudiantes": datos.estudiantes,
            "responsables": datos.responsables,
            "solicitudes": datos.solicitudes
        }
        txt = json.dumps(data2, default=lambda o: o.__dict__, indent=2, ensure_ascii=False)
        return self.archivo.escribir(txt + "\n")

    def datos_ejemplo(self):
        e = [
            {"legajo": "10001", "nombre": "Lucia", "apellido": "Benitez", "email": "lucia.benitez@alumnos.ejemplo.edu", "carrera": "Tecnicatura Universitaria en Programacion"},
            {"legajo": "10002", "nombre": "Tomas", "apellido": "Aguirre", "email": "tomas.aguirre@alumnos.ejemplo.edu", "carrera": "Tecnicatura Universitaria en Programacion"},
            {"legajo": "10003", "nombre": "Camila", "apellido": "Rios", "email": "camila.rios@alumnos.ejemplo.edu", "carrera": "Ingenieria en Sistemas de Informacion"},
            {"legajo": "10004", "nombre": "Joaquin", "apellido": "Medina", "email": "joaquin.medina@alumnos.ejemplo.edu", "carrera": "Tecnicatura Universitaria en Programacion"},
            {"legajo": "10005", "nombre": "Sofia", "apellido": "Navarro", "email": "sofia.navarro@alumnos.ejemplo.edu", "carrera": "Ingenieria en Sistemas de Informacion"}
        ]
        r = [
            {"id": 1, "nombre": "Laura Quiroga", "area": "Alumnado"},
            {"id": 2, "nombre": "Martin Ferreyra", "area": "Secretaria Academica"},
            {"id": 3, "nombre": "Paula Dominguez", "area": "Bedelia"}
        ]
        s = [
            {"id": 1, "estudiante": e[0], "tipo": "CERTIFICADO", "descripcion": "Certificado de alumno regular para presentar en el trabajo", "prioridad": "BAJA", "estado": "PENDIENTE", "responsable": None, "fecha_creacion": "2026-10-20", "fecha_modificacion": "2026-10-20"},
            {"id": 2, "estudiante": e[1], "tipo": "CAMBIO_COMISION", "descripcion": "Cambio de comision de Programacion II por superposicion horaria", "prioridad": "ALTA", "estado": "EN_REVISION", "responsable": r[1], "fecha_creacion": "2026-10-22", "fecha_modificacion": "2026-10-24"},
            {"id": 3, "estudiante": e[2], "tipo": "REVISION_NOTA", "descripcion": "Revision de nota del segundo parcial de Matematica", "prioridad": "ALTA", "estado": "pendiente", "responsable": None, "fecha_creacion": "2026-10-28", "fecha_modificacion": "2026-10-28"},
            {"id": 4, "estudiante": e[3], "tipo": "EQUIVALENCIA", "descripcion": "Equivalencia de Algebra aprobada en otra universidad", "prioridad": "MEDIA", "estado": "APROBADA", "responsable": r[1], "fecha_creacion": "2026-09-15", "fecha_modificacion": "2026-10-05"},
            {"id": 5, "estudiante": e[4], "tipo": "CERTIFICADO", "descripcion": "Certificado analitico parcial", "prioridad": "BAJA", "estado": "CERRADA", "responsable": r[0], "fecha_creacion": "2026-09-01", "fecha_modificacion": "2026-09-10"},
            {"id": 6, "estudiante": e[0], "tipo": "REVISION_NOTA", "descripcion": "Revision de nota del trabajo practico de Bases de Datos", "prioridad": "Alta", "estado": "PENDIENTE", "responsable": None, "fecha_creacion": "2026-10-21", "fecha_modificacion": "2026-10-21"},
            {"id": 7, "estudiante": e[1], "tipo": "OTRO", "descripcion": "Constancia de examen para presentar en el trabajo", "prioridad": "BAJA", "estado": "RECHAZADA", "responsable": r[2], "fecha_creacion": "2026-10-01", "fecha_modificacion": "2026-10-03"},
            {"id": 8, "estudiante": e[2], "tipo": "CAMBIO_COMISION", "descripcion": "Cambio de comision de Ingles I al turno noche", "prioridad": "ALTA", "estado": "PENDIENTE", "responsable": r[2], "fecha_creacion": "2026-10-29", "fecha_modificacion": "2026-10-29"},
            {"id": 9, "estudiante": e[3], "tipo": "EQUIVALENCIA", "descripcion": "Equivalencia de Programacion I por titulo terciario", "prioridad": "MEDIA", "estado": "EN_REVISION", "responsable": r[1], "fecha_creacion": "2026-10-10", "fecha_modificacion": "2026-10-15"},
            {"id": 10, "estudiante": e[4], "tipo": "CERTIFICADO", "descripcion": "Certificado de examen final rendido", "prioridad": "media", "estado": "PENDIENTE", "responsable": None, "fecha_creacion": "2026-10-26", "fecha_modificacion": "2026-10-26"}
        ]
        return {"estudiantes": e, "responsables": r, "solicitudes": s}
