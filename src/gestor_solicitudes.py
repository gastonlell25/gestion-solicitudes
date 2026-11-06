import os
import datetime
from modelos.estudiante import Estudiante
from modelos.solicitud import Solicitud
from modelos.estado import Estado, EstadoInvalidoException, TransicionInvalidaException
from modelos.tipo_solicitud import TipoSolicitud
from modelos.prioridad import Prioridad
from modelos.excepciones import (
    OperacionRechazadaException,
    ResponsableNoEncontradoException,
    SolicitudCerradaException,
    SolicitudNoEncontradaException,
)
from persistencia.datos_sistema import DatosSistema
from persistencia.solicitud_repositorio import PersistenciaException, SolicitudRepositorio
from servicios.reporte_service import ReporteService


# Clase principal del sistema
class GestorSolicitudes:

    def __init__(self, repositorio: SolicitudRepositorio):
        self.solicitudes = []
        self.estudiantes = []
        self.responsables = []
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
                cambio = self.cambiar_estado(id, nuevo)
            except EstadoInvalidoException:
                print("Error: estado invalido.")
                return True
            except (OperacionRechazadaException, TransicionInvalidaException) as e:
                print("Error: " + str(e))
                return True
            if cambio:
                print("Estado actualizado: " + anterior + " -> " + nuevo)
            else:
                print("La solicitud ya se encuentra en estado " + nuevo + ".")
        elif op == "3":
            print("--- Asignar responsable ---")
            id_solicitud = self.leer("ID de la solicitud: ")
            solicitud = self.buscar(id_solicitud)
            if solicitud == None:
                print("Error: no existe una solicitud con ID " + id_solicitud + ".")
                return True
            print("Responsables disponibles:")
            for i in range(len(self.responsables)):
                print("  " + str(self.responsables[i].id) + " - " + self.responsables[i].nombre + " (" + self.responsables[i].area + ")")
            id_responsable = self.leer("ID del responsable: ")
            try:
                self.asignar_responsable(id_solicitud, id_responsable)
            except OperacionRechazadaException as e:
                print("Error: " + str(e))
                return True
            responsable = solicitud.get_responsable()
            print("Responsable asignado: " + responsable.nombre + " (" + responsable.area + ") -> solicitud #" + str(solicitud.id))
        elif op == "4":
            print("--- Buscar / filtrar solicitudes ---")
            print("Filtrar por:")
            print("  1. Estado")
            print("  2. Tipo")
            print("  3. Prioridad")
            print("  4. Legajo")
            opcion_filtro = self.leer("Opcion: ")
            resultado_filtro = None
            if opcion_filtro == "1":
                valor_filtro = self.leer("Estado (PENDIENTE, EN_REVISION, APROBADA, RECHAZADA, CERRADA): ")
                resultado_filtro = self.filtrar_por_estado(valor_filtro)
            elif opcion_filtro == "2":
                valor_filtro = self.leer("Tipo (CERTIFICADO, CAMBIO_COMISION, REVISION_NOTA, EQUIVALENCIA, OTRO): ")
                resultado_filtro = self.filtrar_por_tipo(valor_filtro)
            elif opcion_filtro == "3":
                valor_filtro = self.leer("Prioridad (ALTA, MEDIA, BAJA): ")
                resultado_filtro = self.filtrar_por_prioridad(valor_filtro)
            elif opcion_filtro == "4":
                valor_filtro = self.leer("Legajo: ")
                resultado_filtro = self.filtrar_por_legajo(valor_filtro)
            else:
                print("Opcion invalida.")
                return True
            if len(resultado_filtro) == 0:
                print("No se encontraron solicitudes.")
            else:
                print("Se encontraron " + str(len(resultado_filtro)) + " solicitud(es):")
                print("")
                for i in range(len(resultado_filtro)):
                    self.mostrar(resultado_filtro[i])
        elif op == "5":
            self.reporte()
        elif op == "6":
            print("--- Listado de solicitudes ---")
            if len(self.solicitudes) == 0:
                print("No hay solicitudes registradas.")
                return True
            print("")
            for i in range(len(self.solicitudes)):
                self.mostrar(self.solicitudes[i])
            print("Total: " + str(len(self.solicitudes)) + " solicitud(es).")
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
        for i in range(len(self.estudiantes)):
            if self.estudiantes[i].legajo == legajo:
                nombre = self.estudiantes[i].nombre
                apellido = self.estudiantes[i].apellido
                email = self.estudiantes[i].email
                carrera = self.estudiantes[i].carrera
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
        estudiante = None
        for i in range(len(self.estudiantes)):
            if self.estudiantes[i].legajo == legajo:
                estudiante = self.estudiantes[i]
        if estudiante == None:
            estudiante = Estudiante(legajo, nombre, apellido, email, carrera)
            self.estudiantes.append(estudiante)
        proximo_id = 0
        for i in range(len(self.solicitudes)):
            if self.solicitudes[i].id > proximo_id:
                proximo_id = self.solicitudes[i].id
        solicitud = Solicitud(proximo_id + 1, estudiante, tipo, descripcion, prioridad, "PENDIENTE", None, fecha, fecha)
        self.solicitudes.append(solicitud)
        self.guardar()
        return solicitud.id

    # devuelve False si la solicitud ya estaba en ese estado (no es un error)
    def cambiar_estado(self, id, nuevo):
        s = self.buscar_existente(id)
        nuevo_estado = Estado.from_str(nuevo)
        actual_estado = Estado.from_str(s.get_estado())
        if actual_estado == nuevo_estado:
            return False
        if not actual_estado.puede_pasar_a(nuevo_estado):
            raise TransicionInvalidaException(
                "no se puede pasar de " + actual_estado.value + " a " + nuevo_estado.value + "."
            )
        s.set_estado(nuevo_estado.value)
        s.set_fecha_modificacion(self.hoy())
        self.guardar()
        return True

    def asignar_responsable(self, id_solicitud, id_responsable):
        solicitud = self.buscar_existente(id_solicitud)
        responsable_encontrado = None
        for i in range(len(self.responsables)):
            if str(self.responsables[i].id) == id_responsable:
                responsable_encontrado = self.responsables[i]
        if responsable_encontrado == None:
            raise ResponsableNoEncontradoException(id_responsable)
        if solicitud.estado == "CERRADA":
            raise SolicitudCerradaException()
        solicitud.set_responsable(responsable_encontrado)
        solicitud.set_fecha_modificacion(self.hoy())
        self.guardar()

    def buscar_existente(self, id):
        s = self.buscar(id)
        if s is None:
            raise SolicitudNoEncontradaException(id)
        return s

    def buscar(self, id):
        try:
            n = int(id)
        except ValueError:
            return None
        for i in range(len(self.solicitudes)):
            if self.solicitudes[i].id == n:
                return self.solicitudes[i]
        return None

    def _filtrar(self, obtener_valor, valor):
        """Recorrido único; cada función pública conserva la semántica original."""
        return [solicitud for solicitud in self.solicitudes
                if obtener_valor(solicitud) == valor]

    def filtrar_por_estado(self, x):
        return self._filtrar(lambda s: s.estado.upper(), x.upper().strip().replace(" ", "_"))

    def filtrar_por_tipo(self, x):
        return self._filtrar(lambda s: s.tipo.upper(), x.upper().strip().replace(" ", "_"))

    def filtrar_por_prioridad(self, x):
        return self._filtrar(lambda s: s.prioridad.upper(), x.upper().strip())

    def filtrar_por_legajo(self, x):
        # El legajo mantiene comparación exacta, sin normalizar mayúsculas.
        return self._filtrar(lambda s: s.estudiante.legajo, x.strip())

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
        print(ReporteService.generar(self.solicitudes, self.hoy()))

    def dias_desde_creacion(self, s):
        # Puente para mantener las llamadas de la consola durante la refactorización.
        return s.dias_desde_creacion(self.hoy())

    def esta_vencida(self, s):
        return s.esta_vencida(self.hoy())

    def hoy(self):
        if os.environ.get("FECHA_HOY"):
            return os.environ.get("FECHA_HOY")
        return datetime.date.today().strftime("%Y-%m-%d")

    def cargar(self):
        datos = self.repositorio.cargar()
        self.estudiantes = datos.estudiantes
        self.responsables = datos.responsables
        self.solicitudes = datos.solicitudes

    def guardar(self):
        self.repositorio.guardar(DatosSistema(self.estudiantes, self.responsables, self.solicitudes))
