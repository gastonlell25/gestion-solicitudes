import os
from servicios.solicitud_service import SolicitudService
from servicios.reporte_service import ReporteService
from modelos.estado import EstadoInvalidoException, TransicionInvalidaException
from modelos.tipo_solicitud import TipoSolicitud
from modelos.prioridad import Prioridad
from modelos.datos_solicitud import DatosSolicitud
from modelos.excepciones import (
    OperacionRechazadaException,
    ResponsableNoEncontradoException,
    SolicitudCerradaException,
    SolicitudNoEncontradaException,
)
from persistencia.solicitud_repositorio import PersistenciaException, SolicitudRepositorio


class GestorSolicitudes:
    """Coordinador de UI y servicio de lógica de negocio."""

    def __init__(self, repositorio: SolicitudRepositorio):
        self.servicio = SolicitudService(repositorio)
        self.fin = False

    def iniciar(self):
        """Punto de entrada: carga datos e inicia el menú interactivo."""
        try:
            self.servicio.cargar()
        except PersistenciaException as e:
            print("Error: " + str(e) + ".")
            print("El sistema no puede iniciar sin sus datos. El archivo no se modifico.")
            return
        flag = True
        while flag:
            self.mostrar_menu()
            opcion = self.leer("Opcion: ")
            if self.fin:
                print("")
                opcion = "0"
            try:
                flag = self.procesar_opcion(opcion)
            except PersistenciaException as e:
                print("Error: " + str(e) + ". La operacion no se guardo.")
                self.servicio.cargar()
            print("")

    def mostrar_menu(self):
        """Muestra el menú principal."""
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

    def leer(self, msg):
        """Lee una línea de consola."""
        try:
            return input(msg).strip()
        except EOFError:
            self.fin = True
            return ""

    def procesar_opcion(self, opcion):
        """Procesa la opción del menú seleccionada."""
        if opcion == "1":
            self.registrar()
        elif opcion == "2":
            self._opcion_cambiar_estado()
        elif opcion == "3":
            self._opcion_asignar_responsable()
        elif opcion == "4":
            self._opcion_filtrar()
        elif opcion == "5":
            self.reporte()
        elif opcion == "6":
            self._opcion_listar()
        elif opcion == "0":
            print("Saliendo del sistema...")
            return False
        else:
            print("Opcion invalida.")
        return True

    def _opcion_cambiar_estado(self):
        """Maneja la opción de cambiar estado."""
        print("--- Cambiar estado ---")
        id_solicitud = self.leer("ID de la solicitud: ")
        solicitud = self.servicio.buscar(id_solicitud)
        if solicitud == None:
            print("Error: no existe una solicitud con ID " + id_solicitud + ".")
            return
        print("Estado actual: " + solicitud.get_estado())
        nuevo = self.leer("Nuevo estado (PENDIENTE, EN_REVISION, APROBADA, RECHAZADA, CERRADA): ")
        nuevo = nuevo.upper().replace(" ", "_")
        anterior = solicitud.get_estado()
        try:
            cambio = self.servicio.cambiar_estado(id_solicitud, nuevo)
        except EstadoInvalidoException:
            print("Error: estado invalido.")
            return
        except (OperacionRechazadaException, TransicionInvalidaException) as e:
            print("Error: " + str(e))
            return
        if cambio:
            print("Estado actualizado: " + anterior + " -> " + nuevo)
        else:
            print("La solicitud ya se encuentra en estado " + nuevo + ".")

    def _opcion_asignar_responsable(self):
        """Maneja la opción de asignar responsable."""
        print("--- Asignar responsable ---")
        id_solicitud = self.leer("ID de la solicitud: ")
        solicitud = self.servicio.buscar(id_solicitud)
        if solicitud == None:
            print("Error: no existe una solicitud con ID " + id_solicitud + ".")
            return
        print("Responsables disponibles:")
        for i in range(len(self.servicio.responsables)):
            print("  " + str(self.servicio.responsables[i].id) + " - " + self.servicio.responsables[i].nombre + " (" + self.servicio.responsables[i].area + ")")
        id_responsable = self.leer("ID del responsable: ")
        try:
            self.servicio.asignar_responsable(id_solicitud, id_responsable)
        except OperacionRechazadaException as e:
            print("Error: " + str(e))
            return
        responsable = solicitud.get_responsable()
        print("Responsable asignado: " + responsable.nombre + " (" + responsable.area + ") -> solicitud #" + str(solicitud.id))

    def _opcion_filtrar(self):
        """Maneja la opción de filtrar."""
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
            resultado_filtro = self.servicio.filtrar_por_estado(valor_filtro)
        elif opcion_filtro == "2":
            valor_filtro = self.leer("Tipo (CERTIFICADO, CAMBIO_COMISION, REVISION_NOTA, EQUIVALENCIA, OTRO): ")
            resultado_filtro = self.servicio.filtrar_por_tipo(valor_filtro)
        elif opcion_filtro == "3":
            valor_filtro = self.leer("Prioridad (ALTA, MEDIA, BAJA): ")
            resultado_filtro = self.servicio.filtrar_por_prioridad(valor_filtro)
        elif opcion_filtro == "4":
            valor_filtro = self.leer("Legajo: ")
            resultado_filtro = self.servicio.filtrar_por_legajo(valor_filtro)
        else:
            print("Opcion invalida.")
            return
        if len(resultado_filtro) == 0:
            print("No se encontraron solicitudes.")
        else:
            print("Se encontraron " + str(len(resultado_filtro)) + " solicitud(es):")
            print("")
            for i in range(len(resultado_filtro)):
                self.mostrar(resultado_filtro[i])

    def _opcion_listar(self):
        """Maneja la opción de listar todas las solicitudes."""
        print("--- Listado de solicitudes ---")
        if len(self.servicio.solicitudes) == 0:
            print("No hay solicitudes registradas.")
            return
        print("")
        for i in range(len(self.servicio.solicitudes)):
            self.mostrar(self.servicio.solicitudes[i])
        print("Total: " + str(len(self.servicio.solicitudes)) + " solicitud(es).")

    def registrar(self):
        """Flujo de registro de una nueva solicitud."""
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
        fecha = self.servicio._hoy()
        datos = DatosSolicitud(legajo, nombre, apellido, email, carrera, tipo.value, descripcion, prioridad.value, fecha)
        id_solicitud = self.servicio.registrar_solicitud(datos)
        self.mostrar_resultado_registro(id_solicitud, legajo, apellido, nombre, tipo, prioridad, fecha)

    def leer_y_validar_legajo(self):
        """Lee y valida un legajo."""
        legajo = self.leer("Legajo del estudiante: ")
        if legajo == "":
            print("Error: el legajo es obligatorio.")
            return None
        if not legajo.isdigit():
            print("Error: el legajo debe ser numerico.")
            return None
        return legajo

    def cargar_datos_estudiante(self, legajo):
        """Carga datos de un estudiante existente o pide datos nuevos."""
        nombre = ""
        apellido = ""
        email = ""
        carrera = ""
        for i in range(len(self.servicio.estudiantes)):
            if self.servicio.estudiantes[i].legajo == legajo:
                nombre = self.servicio.estudiantes[i].nombre
                apellido = self.servicio.estudiantes[i].apellido
                email = self.servicio.estudiantes[i].email
                carrera = self.servicio.estudiantes[i].carrera
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
        """Lee el tipo de solicitud desde el menú."""
        print("Tipos de solicitud:")
        for i, t in enumerate(TipoSolicitud, start=1):
            print("  " + str(i) + ". " + t.value)
        opcion = self.leer("Tipo: ")
        try:
            return TipoSolicitud.from_opcion_menu(opcion)
        except ValueError:
            print("Error: tipo invalido.")
            return None

    def leer_y_validar_descripcion(self):
        """Lee y valida la descripción."""
        descripcion = self.leer("Descripcion: ")
        if len(descripcion) == 0:
            print("Error: la descripcion no puede estar vacia.")
            return None
        return descripcion

    def leer_y_validar_prioridad(self, tipo):
        """Lee y valida la prioridad, con defecto según tipo."""
        prioridad_defecto = tipo.prioridad_por_defecto()
        prioridad_texto = self.leer("Prioridad (ALTA/MEDIA/BAJA) [Enter = " + prioridad_defecto.value + "]: ")
        if prioridad_texto == "":
            return prioridad_defecto
        try:
            return Prioridad.from_str(prioridad_texto)
        except ValueError:
            print("Prioridad invalida, se usa la prioridad por defecto: " + prioridad_defecto.value)
            return prioridad_defecto

    def mostrar_resultado_registro(self, id_solicitud, legajo, apellido, nombre, tipo, prioridad, fecha):
        """Muestra el resultado del registro."""
        print("")
        print("Solicitud #" + str(id_solicitud) + " registrada correctamente.")
        print("  Estudiante: " + legajo + " - " + apellido + ", " + nombre)
        print("  Tipo: " + tipo.value)
        print("  Prioridad: " + prioridad.value)
        print("  Estado: PENDIENTE")
        print("  Fecha: " + fecha)

    def mostrar(self, solicitud):
        """Muestra los detalles de una solicitud."""
        responsable_texto = "Sin asignar"
        if solicitud.responsable != None:
            responsable_texto = solicitud.responsable.nombre + " (" + solicitud.responsable.area + ")"
        dias = solicitud.dias_desde_creacion(self.servicio._hoy())
        vencimiento = ""
        if solicitud.esta_vencida(self.servicio._hoy()):
            vencimiento = " (VENCIDA)"
        print("#" + str(solicitud.id) + " [" + solicitud.estado + "] " + solicitud.tipo + " - Prioridad: " + solicitud.prioridad)
        print("   Estudiante: " + solicitud.estudiante.legajo + " - " + solicitud.estudiante.apellido + ", " + solicitud.estudiante.nombre)
        print("   Descripcion: " + solicitud.descripcion)
        print("   Responsable: " + responsable_texto)
        print("   Creada: " + solicitud.fecha_creacion + " | Modificada: " + solicitud.fecha_modificacion + " | Dias: " + str(dias) + vencimiento)
        print("")

    def reporte(self):
        """Muestra el reporte básico."""
        print(ReporteService.generar(self.servicio.solicitudes, self.servicio._hoy()))

    def cargar(self):
        """Delegado: carga datos desde el repositorio."""
        self.servicio.cargar()

    def guardar(self):
        """Delegado: guarda datos en el repositorio."""
        self.servicio.guardar()

    def buscar(self, id):
        """Delegado: busca una solicitud por ID."""
        return self.servicio.buscar(id)
