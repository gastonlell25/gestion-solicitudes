from gestor_solicitudes import GestorSolicitudes
from persistencia.solicitud_repositorio_archivo import SolicitudRepositorioArchivo

if __name__ == "__main__":
    g = GestorSolicitudes(SolicitudRepositorioArchivo())
    g.iniciar()
