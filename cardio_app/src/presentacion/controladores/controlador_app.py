"""
Controlador principal de la aplicación.
Gestiona la sesión activa y delega a los controladores de cada módulo.
"""

from typing import Optional
from src.datos.modelos.entidades import Profesional, Rol


class ControladorApp:
    def __init__(self, servicios: dict):
        self._servicios = servicios
        self._vista = None
        self._usuario_actual: Optional[Profesional] = None

    def set_vista(self, vista):
        self._vista = vista

    @property
    def usuario_actual(self) -> Optional[Profesional]:
        return self._usuario_actual

    @property
    def servicios(self) -> dict:
        return self._servicios

    # ------------------------------------------------------------------
    # Acceso y sesión
    # ------------------------------------------------------------------

    def mostrar_login(self):
        self._usuario_actual = None
        self._vista.mostrar_pantalla("login")

    def autenticar(self, dni: str, contrasena: str) -> bool:
        profesional = self._servicios["autenticacion"].autenticar(dni, contrasena)
        if profesional:
            self._usuario_actual = profesional
            self._vista.mostrar_pantalla("inicio")
            return True
        return False

    def cerrar_sesion(self):
        self.mostrar_login()

    # ------------------------------------------------------------------
    # Navegación por rol
    # ------------------------------------------------------------------

    def puede_acceder(self, rol_requerido: str) -> bool:
        if not self._usuario_actual:
            return False
        return self._usuario_actual.rol == rol_requerido

    def es_administrador(self) -> bool:
        return self._usuario_actual and self._usuario_actual.rol == Rol.ADMINISTRADOR

    def es_auxiliar(self) -> bool:
        return self._usuario_actual and self._usuario_actual.rol == Rol.AUXILIAR

    def es_medico(self) -> bool:
        return self._usuario_actual and self._usuario_actual.rol == Rol.MEDICO
