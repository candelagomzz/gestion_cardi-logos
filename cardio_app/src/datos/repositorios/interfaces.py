"""
Interfaces abstractas de repositorios.
Definen el contrato sin acoplarse a ninguna tecnología de persistencia.
"""

from abc import ABC, abstractmethod
from typing import List, Optional
from src.datos.modelos.entidades import (
    Profesional, Franja, Paciente, Consulta, TomaTension
)


class IRepositorioProfesionales(ABC):
    @abstractmethod
    def obtener_todos(self) -> List[Profesional]: ...

    @abstractmethod
    def obtener_por_id(self, id_: str) -> Optional[Profesional]: ...

    @abstractmethod
    def obtener_por_dni(self, dni: str) -> Optional[Profesional]: ...

    @abstractmethod
    def insertar(self, profesional: Profesional) -> str: ...

    @abstractmethod
    def actualizar(self, id_: str, datos: dict) -> bool: ...


class IRepositorioFranjas(ABC):
    @abstractmethod
    def obtener_todas(self) -> List[Franja]: ...

    @abstractmethod
    def obtener_por_id(self, id_: str) -> Optional[Franja]: ...

    @abstractmethod
    def obtener_por_medico(self, medico_dni: str) -> List[Franja]: ...

    @abstractmethod
    def insertar(self, franja: Franja) -> str: ...

    @abstractmethod
    def actualizar(self, id_: str, datos: dict) -> bool: ...

    @abstractmethod
    def eliminar(self, id_: str) -> bool: ...

    @abstractmethod
    def existe_duplicado(self, franja: Franja, excluir_id: Optional[str] = None) -> bool: ...


class IRepositorioPacientes(ABC):
    @abstractmethod
    def obtener_todos(self) -> List[Paciente]: ...

    @abstractmethod
    def obtener_por_id(self, id_: str) -> Optional[Paciente]: ...

    @abstractmethod
    def insertar(self, paciente: Paciente) -> str: ...

    @abstractmethod
    def actualizar(self, id_: str, datos: dict) -> bool: ...


class IRepositorioConsultas(ABC):
    @abstractmethod
    def obtener_todas(self) -> List[Consulta]: ...

    @abstractmethod
    def obtener_por_id(self, id_: str) -> Optional[Consulta]: ...

    @abstractmethod
    def obtener_por_medico(self, medico_dni: str) -> List[Consulta]: ...

    @abstractmethod
    def obtener_por_paciente(self, paciente_id: str) -> List[Consulta]: ...

    @abstractmethod
    def insertar(self, consulta: Consulta) -> str: ...

    @abstractmethod
    def insertar_muchas(self, consultas: List[Consulta]) -> int: ...

    @abstractmethod
    def actualizar(self, id_: str, datos: dict) -> bool: ...

    @abstractmethod
    def existe_consulta(self, medico_dni: str, dia: str, hora_inicio: str) -> bool: ...

    @abstractmethod
    def contar_consultas_paciente_dia(self, paciente_id: str, dia: str) -> int: ...


class IRepositorioTensiones(ABC):
    @abstractmethod
    def obtener_todas(self) -> List[TomaTension]: ...

    @abstractmethod
    def obtener_por_id(self, id_: str) -> Optional[TomaTension]: ...

    @abstractmethod
    def obtener_por_paciente(self, paciente_id: str) -> List[TomaTension]: ...

    @abstractmethod
    def insertar(self, toma: TomaTension) -> str: ...

    @abstractmethod
    def actualizar(self, id_: str, datos: dict) -> bool: ...
