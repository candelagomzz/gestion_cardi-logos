"""Clase base para repositorios MongoDB con conexión compartida."""

from pymongo import MongoClient
from src.datos.config_db import MONGO_URI, DATABASE_NAME


class RepositorioBaseMongo:
    _cliente: MongoClient = None
    _db = None

    @classmethod
    def _obtener_db(cls):
        if cls._cliente is None:
            cls._cliente = MongoClient(MONGO_URI)
            cls._db = cls._cliente[DATABASE_NAME]
        return cls._db

    def _coleccion(self, nombre: str):
        return self._obtener_db()[nombre]

    @staticmethod
    def _doc_a_str_id(doc: dict) -> dict:
        """Convierte ObjectId a str para desacoplar del driver."""
        if doc and "_id" in doc:
            doc["_id"] = str(doc["_id"])
        return doc
