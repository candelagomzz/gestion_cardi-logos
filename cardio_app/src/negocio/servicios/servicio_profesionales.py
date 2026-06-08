"""Servicio de negocio para Profesionales."""

from typing import List, Optional
from src.datos.repositorios.interfaces import IRepositorioProfesionales
from src.datos.modelos.entidades import Profesional
from src.negocio.validadores.validadores import validar_profesional, validar_contrasena


class ServicioProfesionales:
    def __init__(self, repo: IRepositorioProfesionales):
        self._repo = repo

    def listar(self) -> List[Profesional]:
        return self._repo.obtener_todos()

    def obtener(self, id_: str) -> Optional[Profesional]:
        return self._repo.obtener_por_id(id_)

    def obtener_por_dni(self, dni: str) -> Optional[Profesional]:
        return self._repo.obtener_por_dni(dni)

    def crear(self, profesional: Profesional) -> str:
        errores = validar_profesional(profesional)
        if self._repo.obtener_por_dni(profesional.dni):
            errores.append("Ya existe un profesional con ese DNI.")
        if errores:
            raise ValueError("\n".join(errores))
        return self._repo.insertar(profesional)

    def modificar(self, id_: str, datos: dict) -> bool:
        if "contrasena" in datos:
            errores = validar_contrasena(datos["contrasena"])
            if errores:
                raise ValueError("\n".join(errores))
        return self._repo.actualizar(id_, datos)

    def cambiar_contrasena(self, id_: str, nueva_contrasena: str) -> bool:
        errores = validar_contrasena(nueva_contrasena)
        if errores:
            raise ValueError("\n".join(errores))
        return self._repo.actualizar(id_, {"contrasena": nueva_contrasena})
