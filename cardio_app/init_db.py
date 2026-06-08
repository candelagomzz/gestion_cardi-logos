"""
Script de inicialización de la base de datos.
Carga los ficheros JSON de la carpeta `data/` en MongoDB,
resolviendo las referencias entre colecciones (paciente_id, etc.)
de forma robusta mediante nombres en lugar de índices.

Uso:
    python init_db.py

Requiere MongoDB corriendo en localhost:27017.
"""

import json
import os
from pymongo import MongoClient
from pymongo.errors import ConnectionFailure

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, "data")

MONGO_URI = "mongodb://localhost:27017/"
DATABASE_NAME = "cardio_app"


def cargar_json(nombre_fichero: str) -> list:
    ruta = os.path.join(DATA_DIR, nombre_fichero)
    with open(ruta, encoding="utf-8") as f:
        return json.load(f)


def main():
    print("Conectando a MongoDB...")
    try:
        cliente = MongoClient(MONGO_URI, serverSelectionTimeoutMS=3000)
        cliente.admin.command("ping")
    except ConnectionFailure:
        print("ERROR: No se puede conectar a MongoDB en localhost:27017.")
        print("Asegúrate de que MongoDB esté corriendo antes de ejecutar este script.")
        return

    db = cliente[DATABASE_NAME]
    print(f"Base de datos: '{DATABASE_NAME}'")

    # ── Limpiar colecciones ──────────────────────────────────────────────
    for col in ["profesionales", "franjas", "pacientes", "consultas", "tensiones"]:
        db[col].drop()
        print(f"  ✓ Colección '{col}' limpiada.")

    # ── 1. Profesionales ─────────────────────────────────────────────────
    profesionales = cargar_json("profesionales.json")
    result = db["profesionales"].insert_many(profesionales)
    print(f"\n✔ Profesionales insertados: {len(result.inserted_ids)}")

    # ── 2. Franjas ───────────────────────────────────────────────────────
    franjas = cargar_json("franjas.json")
    result = db["franjas"].insert_many(franjas)
    print(f"✔ Franjas insertadas: {len(result.inserted_ids)}")

    # ── 3. Pacientes ─────────────────────────────────────────────────────
    pacientes_data = cargar_json("pacientes.json")
    result = db["pacientes"].insert_many(pacientes_data)
    pac_ids = result.inserted_ids
    print(f"✔ Pacientes insertados: {len(pac_ids)}")

    # Mapa nombre_completo → ObjectId para resolver referencias
    pac_nombre_a_id = {}
    for i, p in enumerate(pacientes_data):
        nombre_completo = f"{p['nombre']} {p['apellidos']}"
        pac_nombre_a_id[nombre_completo] = pac_ids[i]

    # ── 4. Consultas ─────────────────────────────────────────────────────
    consultas_data = cargar_json("consultas.json")

    # Resolver referencias de paciente por nombre (campo auxiliar en JSON)
    for c in consultas_data:
        ref = c.pop("_paciente_ref", None)  # campo auxiliar, no persiste
        if ref and ref in pac_nombre_a_id:
            c["paciente_id"] = str(pac_nombre_a_id[ref])
        elif "paciente_id" not in c:
            c["paciente_id"] = None

    result = db["consultas"].insert_many(consultas_data)
    print(f"✔ Consultas insertadas: {len(result.inserted_ids)}")

    # ── 5. Tensiones ─────────────────────────────────────────────────────
    tensiones_data = cargar_json("tensiones.json")

    # Resolver referencias de paciente por nombre (campo auxiliar en JSON)
    for t in tensiones_data:
        ref = t.pop("_paciente_ref", None)
        if ref and ref in pac_nombre_a_id:
            t["paciente_id"] = str(pac_nombre_a_id[ref])

    result = db["tensiones"].insert_many(tensiones_data)
    print(f"✔ Tensiones insertadas: {len(result.inserted_ids)}")

    # ── Resumen ───────────────────────────────────────────────────────────
    print("\n" + "=" * 55)
    print("  Base de datos inicializada correctamente.")
    print("=" * 55)
    print("  Credenciales de prueba:")
    print("    Administrador → DNI: 12345678A  /  Pass: Admin12ab")
    print("    Auxiliar      → DNI: 23456789B  /  Pass: Aux11iliar")
    print("    Médico 1      → DNI: 34567890C  /  Pass: Doctor12x")
    print("    Médico 2      → DNI: 45678901D  /  Pass: Medic12ab")
    print("=" * 55)

    cliente.close()


if __name__ == "__main__":
    main()
