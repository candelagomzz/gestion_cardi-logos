"""
Punto de entrada de la aplicación de gestión de consultas cardiológicas.
Agnóstico respecto a tecnologías: solo inicializa el contenedor de dependencias
y arranca la capa de presentación.
"""

from src.datos.repositorios.repositorio_profesionales import RepositorioProfesionalesMongo
from src.datos.repositorios.repositorio_franjas import RepositorioFranjasMongo
from src.datos.repositorios.repositorio_pacientes import RepositorioPacientesMongo
from src.datos.repositorios.repositorio_consultas import RepositorioConsultasMongo
from src.datos.repositorios.repositorio_tensiones import RepositorioTensionesMongo

from src.negocio.servicios.servicio_profesionales import ServicioProfesionales
from src.negocio.servicios.servicio_franjas import ServicioFranjas
from src.negocio.servicios.servicio_pacientes import ServicioPacientes
from src.negocio.servicios.servicio_consultas import ServicioConsultas
from src.negocio.servicios.servicio_tensiones import ServicioTensiones
from src.negocio.servicios.servicio_autenticacion import ServicioAutenticacion

from src.presentacion.controladores.controlador_app import ControladorApp
from src.presentacion.vistas.vista_principal import VistaPrincipal

import tkinter as tk


def construir_contenedor():
    """Construye y conecta todas las dependencias (inyección de dependencias)."""
    # Capa de datos
    repo_profesionales = RepositorioProfesionalesMongo()
    repo_franjas = RepositorioFranjasMongo()
    repo_pacientes = RepositorioPacientesMongo()
    repo_consultas = RepositorioConsultasMongo()
    repo_tensiones = RepositorioTensionesMongo()

    # Capa de negocio
    svc_auth = ServicioAutenticacion(repo_profesionales)
    svc_profesionales = ServicioProfesionales(repo_profesionales)
    svc_franjas = ServicioFranjas(repo_franjas, repo_profesionales)
    svc_pacientes = ServicioPacientes(repo_pacientes)
    svc_consultas = ServicioConsultas(repo_consultas, repo_franjas, repo_pacientes)
    svc_tensiones = ServicioTensiones(repo_tensiones, repo_pacientes)

    servicios = {
        "autenticacion": svc_auth,
        "profesionales": svc_profesionales,
        "franjas": svc_franjas,
        "pacientes": svc_pacientes,
        "consultas": svc_consultas,
        "tensiones": svc_tensiones,
    }
    return servicios


def main():
    root = tk.Tk()
    root.title("Gestión de Consultas Cardiológicas")
    root.geometry("1100x700")
    root.minsize(900, 600)

    servicios = construir_contenedor()
    controlador = ControladorApp(servicios)
    vista = VistaPrincipal(root, controlador)
    controlador.set_vista(vista)
    controlador.mostrar_login()

    root.mainloop()


if __name__ == "__main__":
    main()
