"""Repositorio MongoDB para Consultas."""

from typing import List, Optional
from bson import ObjectId

from src.datos.repositorios.interfaces import IRepositorioConsultas
from src.datos.repositorios.base_mongo import RepositorioBaseMongo
from src.datos.modelos.entidades import Consulta
from src.datos.config_db import COLECCION_CONSULTAS


class RepositorioConsultasMongo(RepositorioBaseMongo, IRepositorioConsultas):

    def _col(self):
        return self._coleccion(COLECCION_CONSULTAS)

    def _doc_a_consulta(self, doc: dict) -> Consulta:
        return Consulta(
            dia=doc["dia"],
            hora_inicio=doc["hora_inicio"],
            hora_fin=doc["hora_fin"],
            medico_dni=doc["medico_dni"],
            estado=doc["estado"],
            paciente_id=doc.get("paciente_id"),
            comentario=doc.get("comentario"),
            _id=str(doc["_id"]),
        )

    def obtener_todas(self) -> List[Consulta]:
        return [self._doc_a_consulta(d) for d in self._col().find()]

    def obtener_por_id(self, id_: str) -> Optional[Consulta]:
        doc = self._col().find_one({"_id": ObjectId(id_)})
        return self._doc_a_consulta(doc) if doc else None

    def obtener_por_medico(self, medico_dni: str) -> List[Consulta]:
        return [self._doc_a_consulta(d) for d in self._col().find({"medico_dni": medico_dni})]

    def obtener_por_paciente(self, paciente_id: str) -> List[Consulta]:
        return [self._doc_a_consulta(d) for d in self._col().find({"paciente_id": paciente_id})]

    def insertar(self, consulta: Consulta) -> str:
        doc = self._consulta_a_doc(consulta)
        resultado = self._col().insert_one(doc)
        return str(resultado.inserted_id)

    def insertar_muchas(self, consultas: List[Consulta]) -> int:
        if not consultas:
            return 0
        docs = [self._consulta_a_doc(c) for c in consultas]
        resultado = self._col().insert_many(docs)
        return len(resultado.inserted_ids)

    def actualizar(self, id_: str, datos: dict) -> bool:
        resultado = self._col().update_one(
            {"_id": ObjectId(id_)}, {"$set": datos}
        )
        return resultado.modified_count > 0

    def existe_consulta(self, medico_dni: str, dia: str, hora_inicio: str) -> bool:
        return self._col().count_documents({
            "medico_dni": medico_dni,
            "dia": dia,
            "hora_inicio": hora_inicio,
        }) > 0

    def contar_consultas_paciente_dia(self, paciente_id: str, dia: str) -> int:
        return self._col().count_documents({
            "paciente_id": paciente_id,
            "dia": dia,
            "estado": {"$in": ["libre", "ocupada"]},
        })

    @staticmethod
    def _consulta_a_doc(consulta: Consulta) -> dict:
        return {
            "dia": consulta.dia,
            "hora_inicio": consulta.hora_inicio,
            "hora_fin": consulta.hora_fin,
            "medico_dni": consulta.medico_dni,
            "estado": consulta.estado,
            "paciente_id": consulta.paciente_id,
            "comentario": consulta.comentario,
        }
