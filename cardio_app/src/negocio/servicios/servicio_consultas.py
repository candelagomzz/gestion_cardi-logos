"""Servicio de negocio para Consultas."""

from datetime import date, timedelta
from typing import List, Optional

from src.datos.repositorios.interfaces import (
    IRepositorioConsultas, IRepositorioFranjas, IRepositorioPacientes
)
from src.datos.modelos.entidades import Consulta, EstadoConsulta, DiaSemana


# Mapeo de nombre de día a número weekday (lunes=0)
_DIA_A_WEEKDAY = {
    DiaSemana.LUNES: 0,
    DiaSemana.MARTES: 1,
    DiaSemana.MIERCOLES: 2,
    DiaSemana.JUEVES: 3,
    DiaSemana.VIERNES: 4,
    DiaSemana.SABADO: 5,
}


class ServicioConsultas:
    def __init__(
        self,
        repo: IRepositorioConsultas,
        repo_franjas: IRepositorioFranjas,
        repo_pacientes: IRepositorioPacientes,
    ):
        self._repo = repo
        self._repo_franjas = repo_franjas
        self._repo_pacientes = repo_pacientes

    # ── Auxiliar ──────────────────────────────────────────────────────────

    def listar_todas(self) -> List[Consulta]:
        return self._repo.obtener_todas()

    def obtener(self, id_: str) -> Optional[Consulta]:
        return self._repo.obtener_por_id(id_)

    def confeccionar_agenda(
        self, medico_dni: str, fecha_ini: date, fecha_fin: date
    ) -> int:
        """
        Genera consultas libres para el médico en el período indicado
        basándose en sus franjas. Evita duplicados.
        No permite fechas pasadas.
        Devuelve el número de consultas nuevas creadas.
        """
        if not medico_dni:
            raise ValueError("Debes seleccionar un médico.")
        if fecha_ini > fecha_fin:
            raise ValueError("La fecha inicial no puede ser posterior a la final.")
        if fecha_ini < date.today():
            raise ValueError("La fecha inicial no puede ser una fecha pasada.")

        franjas = self._repo_franjas.obtener_por_medico(medico_dni)
        if not franjas:
            raise ValueError("El médico no tiene franjas horarias registradas.")

        nuevas: List[Consulta] = []
        dia_actual = fecha_ini
        while dia_actual <= fecha_fin:
            weekday = dia_actual.weekday()
            dia_str = dia_actual.strftime("%d/%m/%Y")
            for franja in franjas:
                if _DIA_A_WEEKDAY.get(franja.dia) == weekday:
                    if not self._repo.existe_consulta(
                        medico_dni, dia_str, franja.hora_inicial
                    ):
                        nuevas.append(Consulta(
                            dia=dia_str,
                            hora_inicio=franja.hora_inicial,
                            hora_fin=franja.hora_final,
                            medico_dni=medico_dni,
                            estado=EstadoConsulta.LIBRE,
                        ))
            dia_actual += timedelta(days=1)

        return self._repo.insertar_muchas(nuevas)

    def asignar_paciente(self, id_consulta: str, paciente_id: str) -> bool:
        """Vincula un paciente a una consulta libre → estado ocupada."""
        consulta = self._repo.obtener_por_id(id_consulta)
        if not consulta:
            raise ValueError("Consulta no encontrada.")
        if consulta.estado != EstadoConsulta.LIBRE:
            raise ValueError("Solo se puede asignar paciente a una consulta libre.")
        paciente = self._repo_pacientes.obtener_por_id(paciente_id)
        if not paciente or not paciente.activo:
            raise ValueError("Paciente no encontrado o no activo.")
        if self._repo.contar_consultas_paciente_dia(paciente_id, consulta.dia) >= 2:
            raise ValueError(
                "El paciente ya tiene 2 consultas reservadas ese día. "
                "No se permiten más de 2 reservas por paciente y día."
            )
        return self._repo.actualizar(id_consulta, {
            "estado": EstadoConsulta.OCUPADA,
            "paciente_id": paciente_id,
        })

    def modificar_estado_auxiliar(self, id_consulta: str, nuevo_estado: str) -> bool:
        """El auxiliar puede cambiar el estado a: libre, ocupada, cancelada, eliminada."""
        estados_permitidos = [
            EstadoConsulta.LIBRE,
            EstadoConsulta.OCUPADA,
            EstadoConsulta.CANCELADA,
            EstadoConsulta.ELIMINADA,
        ]
        if nuevo_estado not in estados_permitidos:
            raise ValueError(
                f"Estado no permitido para el auxiliar: {nuevo_estado}")
        datos = {"estado": nuevo_estado}
        if nuevo_estado == EstadoConsulta.LIBRE:
            datos["paciente_id"] = None
        return self._repo.actualizar(id_consulta, datos)

    # ── Médico ────────────────────────────────────────────────────────────

    def listar_por_medico(self, medico_dni: str) -> List[Consulta]:
        return self._repo.obtener_por_medico(medico_dni)

    def listar_atendidas_por_medico(self, medico_dni: str) -> List[Consulta]:
        return [
            c for c in self._repo.obtener_por_medico(medico_dni)
            if c.estado == EstadoConsulta.ATENDIDA
        ]

    def listar_consultas_paciente_de_medico(
        self, medico_dni: str, paciente_id: str
    ) -> List[Consulta]:
        """Consultas de un paciente concreto atendidas por este médico."""
        return [
            c for c in self._repo.obtener_por_medico(medico_dni)
            if c.paciente_id == paciente_id
        ]

    def listar_consultas_hoy(self, medico_dni: str) -> List[Consulta]:
        hoy = date.today().strftime("%d/%m/%Y")
        return [
            c for c in self._repo.obtener_por_medico(medico_dni)
            if c.dia == hoy
            and c.estado != EstadoConsulta.ELIMINADA
        ]

    def listar_pendientes(self, medico_dni: str) -> List[Consulta]:
        hoy = date.today()
        return [
            c for c in self._repo.obtener_por_medico(medico_dni)
            if _parse_dia(c.dia) > hoy
            and c.estado in (EstadoConsulta.LIBRE, EstadoConsulta.OCUPADA)
        ]

    def actualizar_estado_medico(self, id_consulta: str, nuevo_estado: str) -> bool:
        """El médico solo puede poner: atendida o cancelada."""
        if nuevo_estado not in (EstadoConsulta.ATENDIDA, EstadoConsulta.CANCELADA):
            raise ValueError(
                "El médico solo puede establecer estado 'atendida' o 'cancelada'.")
        return self._repo.actualizar(id_consulta, {"estado": nuevo_estado})

    def actualizar_comentario(self, id_consulta: str, comentario: str) -> bool:
        return self._repo.actualizar(id_consulta, {"comentario": comentario})


def _parse_dia(dia_str: str) -> date:
    """Convierte 'DD/MM/YYYY' a date."""
    d, m, y = map(int, dia_str.split("/"))
    return date(y, m, d)
