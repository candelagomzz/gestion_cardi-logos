"""Servicio de negocio para Tomas de Tensión."""

from typing import List, Optional
from src.datos.repositorios.interfaces import IRepositorioTensiones, IRepositorioPacientes
from src.datos.modelos.entidades import TomaTension
from src.negocio.validadores.validadores import validar_toma_tension


class ServicioTensiones:
    def __init__(
        self,
        repo: IRepositorioTensiones,
        repo_pacientes: IRepositorioPacientes,
    ):
        self._repo = repo
        self._repo_pacientes = repo_pacientes

    def registrar(self, toma: TomaTension) -> str:
        errores = validar_toma_tension(toma)
        if not self._repo_pacientes.obtener_por_id(toma.paciente_id):
            errores.append("El paciente no existe.")
        if errores:
            raise ValueError("\n".join(errores))
        toma.en_rango = (toma.sistolica < 140 and toma.diastolica < 90)
        return self._repo.insertar(toma)

    def modificar(self, id_: str, datos: dict) -> bool:
        # Recalcular en_rango si se modifican sistólica o diastólica
        toma = self._repo.obtener_por_id(id_)
        if not toma:
            raise ValueError("Toma de tensión no encontrada.")
        sistolica = datos.get("sistolica", toma.sistolica)
        diastolica = datos.get("diastolica", toma.diastolica)
        datos["en_rango"] = (sistolica < 140 and diastolica < 90)
        return self._repo.actualizar(id_, datos)

    def listar_por_paciente(self, paciente_id: str) -> List[TomaTension]:
        return self._repo.obtener_por_paciente(paciente_id)

    def obtener(self, id_: str) -> Optional[TomaTension]:
        return self._repo.obtener_por_id(id_)

    def media_tensiones(
        self, paciente_id: str, ultimas_n: Optional[int] = None
    ) -> dict:
        """Calcula media de tensiones. Si ultimas_n es None, usa todas."""
        tomas = self._repo.obtener_por_paciente(paciente_id)
        if ultimas_n:
            tomas = tomas[:ultimas_n]
        if not tomas:
            return {"sistolica": None, "diastolica": None, "total": 0}
        media_s = sum(t.sistolica for t in tomas) / len(tomas)
        media_d = sum(t.diastolica for t in tomas) / len(tomas)
        return {"sistolica": round(media_s, 1), "diastolica": round(media_d, 1), "total": len(tomas)}

    def filtrar(
        self,
        paciente_id: str,
        metodo: Optional[str] = None,
        sitio_cuerpo: Optional[str] = None,
        tamano_brazalete: Optional[str] = None,
        dispositivo: Optional[str] = None,
    ) -> List[TomaTension]:
        tomas = self._repo.obtener_por_paciente(paciente_id)
        if metodo:
            tomas = [t for t in tomas if t.metodo == metodo]
        if sitio_cuerpo:
            tomas = [t for t in tomas if t.sitio_cuerpo == sitio_cuerpo]
        if tamano_brazalete:
            tomas = [t for t in tomas if t.tamano_brazalete == tamano_brazalete]
        if dispositivo:
            dispositivo_lower = dispositivo.lower()
            tomas = [t for t in tomas if dispositivo_lower in t.dispositivo.lower()]
        return tomas
