"""Repositorio MongoDB para Profesionales."""

from typing import List, Optional
from bson import ObjectId

from src.datos.repositorios.interfaces import IRepositorioProfesionales
from src.datos.repositorios.base_mongo import RepositorioBaseMongo
from src.datos.modelos.entidades import Profesional
from src.datos.config_db import COLECCION_PROFESIONALES


class RepositorioProfesionalesMongo(RepositorioBaseMongo, IRepositorioProfesionales):

    def _col(self):
        return self._coleccion(COLECCION_PROFESIONALES)

    def _doc_a_profesional(self, doc: dict) -> Profesional:
        return Profesional(
            nombre=doc["nombre"],
            apellidos=doc["apellidos"],
            dni=doc["dni"],
            rol=doc["rol"],
            contrasena=doc["contrasena"],
            activo=doc.get("activo", True),
            _id=str(doc["_id"]),
        )

    def obtener_todos(self) -> List[Profesional]:
        return [self._doc_a_profesional(d) for d in self._col().find()]

    def obtener_por_id(self, id_: str) -> Optional[Profesional]:
        doc = self._col().find_one({"_id": ObjectId(id_)})
        return self._doc_a_profesional(doc) if doc else None

    def obtener_por_dni(self, dni: str) -> Optional[Profesional]:
        doc = self._col().find_one({"dni": dni})
        return self._doc_a_profesional(doc) if doc else None

    def insertar(self, profesional: Profesional) -> str:
        doc = {
            "nombre": profesional.nombre,
            "apellidos": profesional.apellidos,
            "dni": profesional.dni,
            "rol": profesional.rol,
            "contrasena": profesional.contrasena,
            "activo": profesional.activo,
        }
        resultado = self._col().insert_one(doc)
        return str(resultado.inserted_id)

    def actualizar(self, id_: str, datos: dict) -> bool:
        resultado = self._col().update_one(
            {"_id": ObjectId(id_)}, {"$set": datos}
        )
        return resultado.modified_count > 0
