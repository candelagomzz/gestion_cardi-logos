"""Repositorio MongoDB para Franjas horarias."""

from typing import List, Optional
from bson import ObjectId

from src.datos.repositorios.interfaces import IRepositorioFranjas
from src.datos.repositorios.base_mongo import RepositorioBaseMongo
from src.datos.modelos.entidades import Franja
from src.datos.config_db import COLECCION_FRANJAS


class RepositorioFranjasMongo(RepositorioBaseMongo, IRepositorioFranjas):

    def _col(self):
        return self._coleccion(COLECCION_FRANJAS)

    def _doc_a_franja(self, doc: dict) -> Franja:
        return Franja(
            dia=doc["dia"],
            hora_inicial=doc["hora_inicial"],
            hora_final=doc["hora_final"],
            medico_dni=doc["medico_dni"],
            _id=str(doc["_id"]),
        )

    def obtener_todas(self) -> List[Franja]:
        return [self._doc_a_franja(d) for d in self._col().find()]

    def obtener_por_id(self, id_: str) -> Optional[Franja]:
        doc = self._col().find_one({"_id": ObjectId(id_)})
        return self._doc_a_franja(doc) if doc else None

    def obtener_por_medico(self, medico_dni: str) -> List[Franja]:
        return [self._doc_a_franja(d) for d in self._col().find({"medico_dni": medico_dni})]

    def insertar(self, franja: Franja) -> str:
        doc = {
            "dia": franja.dia,
            "hora_inicial": franja.hora_inicial,
            "hora_final": franja.hora_final,
            "medico_dni": franja.medico_dni,
        }
        resultado = self._col().insert_one(doc)
        return str(resultado.inserted_id)

    def actualizar(self, id_: str, datos: dict) -> bool:
        resultado = self._col().update_one(
            {"_id": ObjectId(id_)}, {"$set": datos}
        )
        return resultado.modified_count > 0

    def eliminar(self, id_: str) -> bool:
        resultado = self._col().delete_one({"_id": ObjectId(id_)})
        return resultado.deleted_count > 0

    def existe_duplicado(self, franja: Franja, excluir_id: Optional[str] = None) -> bool:
        filtro = {
            "dia": franja.dia,
            "hora_inicial": franja.hora_inicial,
            "hora_final": franja.hora_final,
            "medico_dni": franja.medico_dni,
        }
        if excluir_id:
            filtro["_id"] = {"$ne": ObjectId(excluir_id)}
        return self._col().count_documents(filtro) > 0
