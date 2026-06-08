"""Repositorio MongoDB para Pacientes."""

from typing import List, Optional
from bson import ObjectId

from src.datos.repositorios.interfaces import IRepositorioPacientes
from src.datos.repositorios.base_mongo import RepositorioBaseMongo
from src.datos.modelos.entidades import Paciente
from src.datos.config_db import COLECCION_PACIENTES


class RepositorioPacientesMongo(RepositorioBaseMongo, IRepositorioPacientes):

    def _col(self):
        return self._coleccion(COLECCION_PACIENTES)

    def _doc_a_paciente(self, doc: dict) -> Paciente:
        return Paciente(
            nombre=doc["nombre"],
            apellidos=doc["apellidos"],
            genero=doc["genero"],
            fecha_nacimiento=doc["fecha_nacimiento"],
            activo=doc.get("activo", True),
            _id=str(doc["_id"]),
        )

    def obtener_todos(self) -> List[Paciente]:
        return [self._doc_a_paciente(d) for d in self._col().find()]

    def obtener_por_id(self, id_: str) -> Optional[Paciente]:
        doc = self._col().find_one({"_id": ObjectId(id_)})
        return self._doc_a_paciente(doc) if doc else None

    def insertar(self, paciente: Paciente) -> str:
        doc = {
            "nombre": paciente.nombre,
            "apellidos": paciente.apellidos,
            "genero": paciente.genero,
            "fecha_nacimiento": paciente.fecha_nacimiento,
            "activo": paciente.activo,
        }
        resultado = self._col().insert_one(doc)
        return str(resultado.inserted_id)

    def actualizar(self, id_: str, datos: dict) -> bool:
        resultado = self._col().update_one(
            {"_id": ObjectId(id_)}, {"$set": datos}
        )
        return resultado.modified_count > 0
