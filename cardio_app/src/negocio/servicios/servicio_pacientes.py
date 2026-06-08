"""Servicio de negocio para Pacientes."""

from typing import List, Optional
from src.datos.repositorios.interfaces import IRepositorioPacientes
from src.datos.modelos.entidades import Paciente
from src.negocio.validadores.validadores import validar_paciente


class ServicioPacientes:
    def __init__(self, repo: IRepositorioPacientes):
        self._repo = repo

    def listar(self) -> List[Paciente]:
        return self._repo.obtener_todos()

    def obtener(self, id_: str) -> Optional[Paciente]:
        return self._repo.obtener_por_id(id_)

    def crear(self, paciente: Paciente) -> str:
        errores = validar_paciente(paciente)
        if errores:
            raise ValueError("\n".join(errores))
        return self._repo.insertar(paciente)

    def modificar(self, id_: str, datos: dict) -> bool:
        return self._repo.actualizar(id_, datos)
