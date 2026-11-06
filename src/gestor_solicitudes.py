import os
import datetime
from modelos.estudiante import Estudiante
from modelos.solicitud import Solicitud
from modelos.estado import Estado, EstadoInvalidoException, TransicionInvalidaException
from modelos.tipo_solicitud import TipoSolicitud
from modelos.prioridad import Prioridad
from persistencia.datos_sistema import DatosSistema
from persistencia.solicitud_repositorio import PersistenciaException, SolicitudRepositorio


# Clase principal del sistema
class GestorSolicitudes:

    def __init__(self, repositorio: SolicitudRepositorio):
        self.lst = []   # solicitudes
        self.ests = []  # estudiantes
        self.resp = []  # responsables
        self.repositorio = repositorio
        self.fin = False

    def iniciar(self):
        try:
            self.cargar()
        except PersistenciaException as e:
            print("Error: " + str(e) + ".")
            print("El sistema no puede iniciar sin sus datos. El archivo no se modifico.")
            return
        flag = True
        while flag:
            self.mostrar_menu()
            op = self.leer("Opcion: ")
            if self.fin:
                print("")
                op = "0"
            try:
                flag = self.procesar_opcion(op)
            except PersistenciaException as e:
                print("Error: " + str(e) + ". La operacion no se guardo.")
                # vuelve al ultimo estado guardado para no persistir despues un cambio que el usuario vio fallar
                self.cargar()
            print("")

    def mostrar_menu(self):
        print("==============================================")
        print(" SISTEMA DE GESTION DE SOLICITUDES ACADEMICAS")
        print("==============================================")
        print("1. Registrar solicitud")
        print("2. Cambiar estado de una solicitud")
        print("3. Asignar responsable")
        print("4. Buscar / filtrar solicitudes")
        print("5. Reporte basico")
        print("6. Listar todas las solicitudes")
        print("0. Salir")

    # lee una linea de la consola
    def leer(self, msg):
        try:
            return input(msg).strip()
        except EOFError:
            self.fin = True
            return ""

    def procesar_opcion(self, op):
        if op == "1":
            self.registrar()
        elif op == "2":
            print("--- Cambiar estado ---")
            id = self.leer("ID de la solicitud: ")
            s = self.buscar(id)
            if s == None:
                print("Error: no existe una solicitud con ID " + id + ".")
                return True
            print("Estado actual: " + s.get_estado())
            nuevo = self.leer("Nuevo estado (PENDIENTE, EN_REVISION, APROBADA, RECHAZADA, CERRADA): ")
            nuevo = nuevo.upper().replace(" ", "_")
            anterior = s.get_estado()
            try:
                r = self.cambiar_estado(id, nuevo)
            except EstadoInvalidoException:
                print("Error: estado invalido.")
                return True
            except TransicionInvalidaException as e:
                print("Error: " + str(e))
                return True
            if r == 1:
                print("Estado actualizado: " + anterior + " -> " + nuevo)
            elif r == 0:
                print("La solicitud ya se encuentra en estado " + nuevo + ".")
            else:
                print("Error: no existe una solicitud con ID " + id + ".")
        elif op == "3":
            print("--- Asignar responsable ---")
            id2 = self.leer("ID de la solicitud: ")
            s2 = self.buscar(id2)
            if s2 == None:
                print("Error: no existe una solicitud con ID " + id2 + ".")
                return True
            print("Responsables disponibles:")
            for i in range(len(self.resp)):
                print("  " + str(self.resp[i].id) + " - " + self.resp[i].nombre + " (" + self.resp[i].area + ")")
            idr = self.leer("ID del responsable: ")
            res = self.asignar_responsable(id2, idr)
            if res == 1:
                rr = s2.get_responsable()
                print("Responsable asignado: " + rr.nombre + " (" + rr.area + ") -> solicitud #" + str(s2.id))
            elif res == -2:
                print("Error: no existe un responsable con ID " + idr + ".")
            elif res == -3:
                print("Error: no se puede asignar responsable a una solicitud CERRADA.")
            else:
                print("Error: no se pudo asignar el responsable.")
        elif op == "4":
            print("--- Buscar / filtrar solicitudes ---")
            print("Filtrar por:")
            print("  1. Estado")
            print("  2. Tipo")
            print("  3. Prioridad")
            print("  4. Legajo")
            f = self.leer("Opcion: ")
            aux = None
            if f == "1":
                v = self.leer("Estado (PENDIENTE, EN_REVISION, APROBADA, RECHAZADA, CERRADA): ")
                aux = self.filtrar_por_estado(v)
            elif f == "2":
                v = self.leer("Tipo (CERTIFICADO, CAMBIO_COMISION, REVISION_NOTA, EQUIVALENCIA, OTRO): ")
                aux = self.filtrar_por_tipo(v)
            elif f == "3":
                v = self.leer("Prioridad (ALTA, MEDIA, BAJA): ")
                aux = self.filtrar_por_prioridad(v)
            elif f == "4":
                v = self.leer("Legajo: ")
                aux = self.filtrar_por_legajo(v)
            else:
                print("Opcion invalida.")
                return True
            if len(aux) == 0:
                print("No se encontraron solicitudes.")
            else:
                print("Se encontraron " + str(len(aux)) + " solicitud(es):")
                print("")
                for i in range(len(aux)):
                    self.mostrar(aux[i])
        elif op == "5":
            self.reporte()
        elif op == "6":
            print("--- Listado de solicitudes ---")
            if len(self.lst) == 0:
                print("No hay solicitudes registradas.")
                return True
            print("")
            for i in range(len(self.lst)):
                self.mostrar(self.lst[i])
            print("Total: " + str(len(self.lst)) + " solicitud(es).")
        elif op == "0":
            print("Saliendo del sistema...")
            return False
        else:
            print("Opcion invalida.")
        return True

    # registra una nueva solicitud pidiendo los datos por consola
    def registrar(self):
        print("--- Registrar solicitud ---")
        legajo = self.leer_y_validar_legajo()
        if legajo is None:
            return
        nombre, apellido, email, carrera = self.cargar_datos_estudiante(legajo)
        if nombre is None:
            return
        tipo = self.leer_y_mapear_tipo()
        if tipo is None:
            return
        descripcion = self.leer_y_validar_descripcion()
        if descripcion is None:
            return
        prioridad = self.leer_y_validar_prioridad(tipo)
        fecha = self.hoy()
        id = self.registrar_solicitud(legajo, nombre, apellido, email, carrera, tipo.value, descripcion, prioridad.value, fecha)
        self.mostrar_resultado_registro(id, legajo, apellido, nombre, tipo, prioridad, fecha)

    def leer_y_validar_legajo(self):
        legajo = self.leer("Legajo del estudiante: ")
        if legajo == "":
            print("Error: el legajo es obligatorio.")
            return None
        if not legajo.isdigit():
            print("Error: el legajo debe ser numerico.")
            return None
        return legajo

    def cargar_datos_estudiante(self, legajo):
        nombre = ""
        apellido = ""
        email = ""
        carrera = ""
        for i in range(len(self.ests)):
            if self.ests[i].legajo == legajo:
                nombre = self.ests[i].nombre
                apellido = self.ests[i].apellido
                email = self.ests[i].email
                carrera = self.ests[i].carrera
                print("Estudiante encontrado: " + apellido + ", " + nombre + " (" + carrera + ")")
                return nombre, apellido, email, carrera
        print("El estudiante no esta registrado. Ingrese sus datos.")
        nombre = self.leer("Nombre: ")
        apellido = self.leer("Apellido: ")
        if nombre == "" or apellido == "":
            print("Error: nombre y apellido son obligatorios.")
            return None, None, None, None
        email = self.leer("Email: ")
        if email.find("@") == -1:
            print("Error: email invalido.")
            return None, None, None, None
        carrera = self.leer("Carrera: ")
        return nombre, apellido, email, carrera

    def leer_y_mapear_tipo(self):
        print("Tipos de solicitud:")
        for i, t in enumerate(TipoSolicitud, start=1):
            print("  " + str(i) + ". " + t.value)
        op = self.leer("Tipo: ")
        try:
            return TipoSolicitud.from_opcion_menu(op)
        except ValueError:
            print("Error: tipo invalido.")
            return None

    def leer_y_validar_descripcion(self):
        descripcion = self.leer("Descripcion: ")
        if len(descripcion) == 0:
            print("Error: la descripcion no puede estar vacia.")
            return None
        return descripcion

    def leer_y_validar_prioridad(self, tipo):
        pd = tipo.prioridad_por_defecto()
        prioridad_texto = self.leer("Prioridad (ALTA/MEDIA/BAJA) [Enter = " + pd.value + "]: ")
        if prioridad_texto == "":
            return pd
        try:
            return Prioridad.from_str(prioridad_texto)
        except ValueError:
            print("Prioridad invalida, se usa la prioridad por defecto: " + pd.value)
            return pd

    def mostrar_resultado_registro(self, id, legajo, apellido, nombre, tipo, prioridad, fecha):
        print("")
        print("Solicitud #" + str(id) + " registrada correctamente.")
        print("  Estudiante: " + legajo + " - " + apellido + ", " + nombre)
        print("  Tipo: " + tipo.value)
        print("  Prioridad: " + prioridad.value)
        print("  Estado: PENDIENTE")
        print("  Fecha: " + fecha)

    def registrar_solicitud(self, legajo, nombre, apellido, email, carrera, tipo, descripcion, prioridad, fecha):
        est = None
        for i in range(len(self.ests)):
            if self.ests[i].legajo == legajo:
                est = self.ests[i]
        if est == None:
            est = Estudiante(legajo, nombre, apellido, email, carrera)
            self.ests.append(est)
        # calcula el proximo id
        aux = 0
        for i in range(len(self.lst)):
            if self.lst[i].id > aux:
                aux = self.lst[i].id
        s = Solicitud(aux + 1, est, tipo, descripcion, prioridad, "PENDIENTE", None, fecha, fecha)
        self.lst.append(s)
        self.guardar()
        return s.id

    # devuelve True si se pudo cambiar el estado
    def cambiar_estado(self, id, nuevo):
        s = self.buscar(id)
        if s == None:
            return -1
        nuevo_estado = Estado.from_str(nuevo)
        actual_estado = Estado.from_str(s.get_estado())
        if actual_estado == nuevo_estado:
            return 0
        if not actual_estado.puede_pasar_a(nuevo_estado):
            raise TransicionInvalidaException(
                "no se puede pasar de " + actual_estado.value + " a " + nuevo_estado.value + "."
            )
        s.set_estado(nuevo_estado.value)
        s.set_fecha_modificacion(self.hoy())
        self.guardar()
        return 1

    def asignar_responsable(self, id_solicitud, id_responsable):
        s = self.buscar(id_solicitud)
        if s == None:
            return -1
        x = None
        for i in range(len(self.resp)):
            if str(self.resp[i].id) == id_responsable:
                x = self.resp[i]
        if x == None:
            return -2
        if s.estado == "CERRADA":
            return -3
        s.set_responsable(x)
        s.set_fecha_modificacion(self.hoy())
        self.guardar()
        return 1

    def buscar(self, id):
        try:
            n = int(id)
        except:
            return None
        for i in range(len(self.lst)):
            if self.lst[i].id == n:
                return self.lst[i]
        return None

    def filtrar_por_estado(self, x):
        res = []
        x = x.upper().strip().replace(" ", "_")
        for i in range(len(self.lst)):
            if self.lst[i].estado.upper() == x:
                res.append(self.lst[i])
        return res

    def filtrar_por_tipo(self, x):
        res = []
        x = x.upper().strip().replace(" ", "_")
        for i in range(len(self.lst)):
            if self.lst[i].tipo.upper() == x:
                res.append(self.lst[i])
        return res

    def filtrar_por_prioridad(self, x):
        res = []
        x = x.upper().strip()
        for i in range(len(self.lst)):
            if self.lst[i].prioridad.upper() == x:
                res.append(self.lst[i])
        return res

    def filtrar_por_legajo(self, x):
        res = []
        x = x.strip()
        for i in range(len(self.lst)):
            if self.lst[i].estudiante.legajo == x:
                res.append(self.lst[i])
        return res

    def mostrar(self, s):
        r = "Sin asignar"
        if s.responsable != None:
            r = s.responsable.nombre + " (" + s.responsable.area + ")"
        dias = self.dias_desde_creacion(s)
        venc = ""
        if self.esta_vencida(s):
            venc = " (VENCIDA)"
        print("#" + str(s.id) + " [" + s.estado + "] " + s.tipo + " - Prioridad: " + s.prioridad)
        print("   Estudiante: " + s.estudiante.legajo + " - " + s.estudiante.apellido + ", " + s.estudiante.nombre)
        print("   Descripcion: " + s.descripcion)
        print("   Responsable: " + r)
        print("   Creada: " + s.fecha_creacion + " | Modificada: " + s.fecha_modificacion + " | Dias: " + str(dias) + venc)
        print("")

    def reporte(self):
        c1 = c2 = c3 = c4 = c5 = 0
        t1 = t2 = t3 = t4 = t5 = 0
        pa = 0
        v = 0
        # recorre la lista
        for i in range(len(self.lst)):
            x = self.lst[i]
            if x.estado == "PENDIENTE":
                c1 += 1
            elif x.estado == "EN_REVISION":
                c2 += 1
            elif x.estado == "APROBADA":
                c3 += 1
            elif x.estado == "RECHAZADA":
                c4 += 1
            elif x.estado == "CERRADA":
                c5 += 1
            if x.tipo == "CERTIFICADO":
                t1 += 1
            elif x.tipo == "CAMBIO_COMISION":
                t2 += 1
            elif x.tipo == "REVISION_NOTA":
                t3 += 1
            elif x.tipo == "EQUIVALENCIA":
                t4 += 1
            elif x.tipo == "OTRO":
                t5 += 1
            if x.estado[0:4] == "PEND" and x.prioridad.upper() == "ALTA":
                pa += 1
            if self.esta_vencida(x):
                v += 1
        print("============ REPORTE ============")
        print("Total de solicitudes: " + str(len(self.lst)))
        print("")
        print("Cantidad por estado:")
        print("  PENDIENTE: " + str(c1))
        print("  EN_REVISION: " + str(c2))
        print("  APROBADA: " + str(c3))
        print("  RECHAZADA: " + str(c4))
        print("  CERRADA: " + str(c5))
        print("")
        print("Cantidad por tipo:")
        print("  CERTIFICADO: " + str(t1))
        print("  CAMBIO_COMISION: " + str(t2))
        print("  REVISION_NOTA: " + str(t3))
        print("  EQUIVALENCIA: " + str(t4))
        print("  OTRO: " + str(t5))
        print("")
        print("Pendientes de prioridad ALTA: " + str(pa))
        print("Solicitudes vencidas: " + str(v))
        print("=================================")

    def dias_desde_creacion(self, s):
        p = s.get_fecha_creacion().split("-")
        h = self.hoy().split("-")
        f1 = datetime.date(int(p[0]), int(p[1]), int(p[2]))
        f2 = datetime.date(int(h[0]), int(h[1]), int(h[2]))
        return (f2 - f1).days

    def esta_vencida(self, s):
        if s.estado != "PENDIENTE" and s.estado != "EN_REVISION":
            return False
        d = self.dias_desde_creacion(s)
        if s.prioridad == "ALTA" and d > 3:
            return True
        if s.prioridad == "MEDIA" and d > 7:
            return True
        if s.prioridad == "BAJA" and d > 15:
            return True
        return False

    def hoy(self):
        if os.environ.get("FECHA_HOY"):
            return os.environ.get("FECHA_HOY")
        return datetime.date.today().strftime("%Y-%m-%d")

    def validar_email(self, email):
        if email == None or email == "":
            return False
        partes = email.split("@")
        if len(partes) != 2:
            return False
        if partes[1].find(".") == -1:
            return False
        return True

    # exporta las solicitudes a un csv para mandarle a alumnado
    def exportar_csv(self, ruta):
        txt = "id;legajo;tipo;prioridad;estado;fecha\n"
        for i in range(len(self.lst)):
            x = self.lst[i]
            txt += str(x.id) + ";" + x.estudiante.legajo + ";" + x.tipo + ";" + x.prioridad + ";" + x.estado + ";" + x.fecha_creacion + "\n"
        try:
            f = open(ruta, "w")
            f.write(txt)
            f.close()
        except:
            pass

    def cargar(self):
        datos = self.repositorio.cargar()
        self.ests = datos.estudiantes
        self.resp = datos.responsables
        self.lst = datos.solicitudes

    def guardar(self):
        self.repositorio.guardar(DatosSistema(self.ests, self.resp, self.lst))
