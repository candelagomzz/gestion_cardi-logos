"""Servicio de negocio para Franjas horarias."""

from typing import List, Optional
from src.datos.repositorios.interfaces import IRepositorioFranjas, IRepositorioProfesionales
from src.datos.modelos.entidades import Franja, Rol
from src.negocio.validadores.validadores import validar_franja


class ServicioFranjas:
    def __init__(self, repo: IRepositorioFranjas, repo_profesionales: IRepositorioProfesionales):
        self._repo = repo
        self._repo_prof = repo_profesionales

    def listar(self) -> List[Franja]:
        return self._repo.obtener_todas()

    def obtener(self, id_: str) -> Optional[Franja]:
        return self._repo.obtener_por_id(id_)

    def listar_por_medico(self, medico_dni: str) -> List[Franja]:
        return self._repo.obtener_por_medico(medico_dni)

    def crear(self, franja: Franja) -> str:
        errores = validar_franja(franja)
        medico = self._repo_prof.obtener_por_dni(franja.medico_dni)
        if not medico:
            errores.append("El médico indicado no existe en el sistema.")
        elif medico.rol != Rol.MEDICO:
            errores.append("El profesional indicado no tiene el rol de médico.")
        if self._repo.existe_duplicado(franja):
            errores.append("Ya existe una franja idéntica para este médico.")
        if errores:
            raise ValueError("\n".join(errores))
        return self._repo.insertar(franja)

    def modificar(self, id_: str, franja_actualizada: Franja) -> bool:
        errores = validar_franja(franja_actualizada)
        if self._repo.existe_duplicado(franja_actualizada, excluir_id=id_):
            errores.append("Ya existe una franja idéntica para este médico.")
        if errores:
            raise ValueError("\n".join(errores))
        datos = {
            "dia": franja_actualizada.dia,
            "hora_inicial": franja_actualizada.hora_inicial,
            "hora_final": franja_actualizada.hora_final,
            "medico_dni": franja_actualizada.medico_dni,
        }
        return self._repo.actualizar(id_, datos)

    def eliminar(self, id_: str) -> bool:
        return self._repo.eliminar(id_)
