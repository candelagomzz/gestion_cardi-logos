"""Servicio de autenticación."""

from typing import Optional
from src.datos.repositorios.interfaces import IRepositorioProfesionales
from src.datos.modelos.entidades import Profesional


class ServicioAutenticacion:
    def __init__(self, repo_profesionales: IRepositorioProfesionales):
        self._repo = repo_profesionales

    def autenticar(self, dni: str, contrasena: str) -> Optional[Profesional]:
        """
        Devuelve el profesional si el DNI y contraseña coinciden y está activo.
        Devuelve None si la autenticación falla.
        """
        profesional = self._repo.obtener_por_dni(dni)
        if profesional and profesional.activo and profesional.contrasena == contrasena:
            return profesional
        return None
