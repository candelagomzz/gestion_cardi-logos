"""Repositorio MongoDB para Tomas de Tensión."""

from typing import List, Optional
from bson import ObjectId

from src.datos.repositorios.interfaces import IRepositorioTensiones
from src.datos.repositorios.base_mongo import RepositorioBaseMongo
from src.datos.modelos.entidades import TomaTension
from src.datos.config_db import COLECCION_TENSIONES


class RepositorioTensionesMongo(RepositorioBaseMongo, IRepositorioTensiones):

    def _col(self):
        return self._coleccion(COLECCION_TENSIONES)

    def _doc_a_toma(self, doc: dict) -> TomaTension:
        return TomaTension(
            paciente_id=doc["paciente_id"],
            fecha=doc["fecha"],
            sistolica=doc["sistolica"],
            diastolica=doc["diastolica"],
            metodo=doc["metodo"],
            sitio_cuerpo=doc["sitio_cuerpo"],
            tamano_brazalete=doc["tamano_brazalete"],
            dispositivo=doc["dispositivo"],
            estado=doc["estado"],
            descripcion=doc.get("descripcion"),
            en_rango=doc.get("en_rango", False),
            _id=str(doc["_id"]),
        )

    def obtener_todas(self) -> List[TomaTension]:
        return [self._doc_a_toma(d) for d in self._col().find()]

    def obtener_por_id(self, id_: str) -> Optional[TomaTension]:
        doc = self._col().find_one({"_id": ObjectId(id_)})
        return self._doc_a_toma(doc) if doc else None

    def obtener_por_paciente(self, paciente_id: str) -> List[TomaTension]:
        return [
            self._doc_a_toma(d)
            for d in self._col().find({"paciente_id": paciente_id}).sort("fecha", -1)
        ]

    def insertar(self, toma: TomaTension) -> str:
        doc = {
            "paciente_id": toma.paciente_id,
            "fecha": toma.fecha,
            "sistolica": toma.sistolica,
            "diastolica": toma.diastolica,
            "metodo": toma.metodo,
            "sitio_cuerpo": toma.sitio_cuerpo,
            "tamano_brazalete": toma.tamano_brazalete,
            "dispositivo": toma.dispositivo,
            "estado": toma.estado,
            "descripcion": toma.descripcion,
            "en_rango": toma.en_rango,
        }
        resultado = self._col().insert_one(doc)
        return str(resultado.inserted_id)

    def actualizar(self, id_: str, datos: dict) -> bool:
        resultado = self._col().update_one(
            {"_id": ObjectId(id_)}, {"$set": datos}
        )
        return resultado.modified_count > 0
