"""
Validadores de reglas de negocio.
Devuelven listas de mensajes de error (vacías si es válido).
"""

import re
from typing import List
from src.datos.modelos.entidades import (
    Profesional, Franja, Paciente, Consulta, TomaTension,
    Rol, DiaSemana, EstadoConsulta, GeneroFHIR, EstadoObservacionFHIR,
    MetodoTension, SitioCuerpo, TamanoBrazalete,
)


def validar_contrasena(contrasena: str) -> List[str]:
    errores = []
    if not (8 <= len(contrasena) <= 15):
        errores.append("La contraseña debe tener entre 8 y 15 caracteres.")
    if not contrasena[0].isalpha():
        errores.append("La contraseña debe comenzar por una letra.")
    if not re.fullmatch(r"[a-zA-Z0-9]+", contrasena):
        errores.append("La contraseña solo puede contener letras y dígitos.")
    digitos = sum(1 for c in contrasena if c.isdigit())
    if digitos < 2:
        errores.append("La contraseña debe contener al menos 2 dígitos.")
    return errores


def validar_profesional(profesional: Profesional) -> List[str]:
    errores = []
    if not profesional.nombre.strip():
        errores.append("El nombre es obligatorio.")
    if not profesional.apellidos.strip():
        errores.append("Los apellidos son obligatorios.")
    if not profesional.dni.strip():
        errores.append("El DNI es obligatorio.")
    if profesional.rol not in Rol.VALORES:
        errores.append(f"Rol inválido. Valores permitidos: {Rol.VALORES}")
    errores += validar_contrasena(profesional.contrasena)
    return errores


def validar_franja(franja: Franja) -> List[str]:
    errores = []
    if franja.dia not in DiaSemana.VALORES:
        errores.append(f"Día inválido. Valores permitidos: {DiaSemana.VALORES}")
    if not _hora_valida(franja.hora_inicial):
        errores.append("La hora inicial debe estar en punto o a la media hora (HH:00 o HH:30).")
    if not _hora_valida(franja.hora_final):
        errores.append("La hora final debe estar en punto o a la media hora.")
    if _hora_valida(franja.hora_inicial) and _hora_valida(franja.hora_final):
        if not _diferencia_media_hora(franja.hora_inicial, franja.hora_final):
            errores.append("La duración de la franja debe ser exactamente 30 minutos.")
    if not franja.medico_dni.strip():
        errores.append("El médico es obligatorio.")
    return errores


def validar_paciente(paciente: Paciente) -> List[str]:
    errores = []
    if not paciente.nombre.strip():
        errores.append("El nombre es obligatorio.")
    if not paciente.apellidos.strip():
        errores.append("Los apellidos son obligatorios.")
    if paciente.genero not in GeneroFHIR.VALORES:
        errores.append(f"Género inválido. Valores FHIR permitidos: {GeneroFHIR.VALORES}")
    if not paciente.fecha_nacimiento.strip():
        errores.append("La fecha de nacimiento es obligatoria.")
    return errores


def validar_toma_tension(toma: TomaTension) -> List[str]:
    errores = []
    if toma.sistolica <= 0:
        errores.append("La tensión sistólica debe ser un valor positivo.")
    if toma.diastolica <= 0:
        errores.append("La tensión diastólica debe ser un valor positivo.")
    if toma.metodo not in MetodoTension.VALORES:
        errores.append(f"Método inválido. Valores: {MetodoTension.VALORES}")
    if toma.sitio_cuerpo not in SitioCuerpo.VALORES:
        errores.append(f"Sitio del cuerpo inválido. Valores: {SitioCuerpo.VALORES}")
    if toma.tamano_brazalete not in TamanoBrazalete.VALORES:
        errores.append(f"Tamaño de brazalete inválido. Valores: {TamanoBrazalete.VALORES}")
    if toma.estado not in EstadoObservacionFHIR.VALORES:
        errores.append(f"Estado inválido. Valores FHIR: {EstadoObservacionFHIR.VALORES}")
    if not toma.dispositivo.strip():
        errores.append("El dispositivo es obligatorio.")
    if not toma.fecha.strip():
        errores.append("La fecha es obligatoria.")
    return errores


# ---------------------------------------------------------------------------
# Helpers privados
# ---------------------------------------------------------------------------

def _hora_valida(hora: str) -> bool:
    """Comprueba que la hora sea HH:MM con MM en {00, 30}."""
    partes = hora.split(":")
    if len(partes) != 2:
        return False
    try:
        hh, mm = int(partes[0]), int(partes[1])
        return 0 <= hh <= 23 and mm in (0, 30)
    except ValueError:
        return False


def _diferencia_media_hora(hora_ini: str, hora_fin: str) -> bool:
    """Comprueba que la diferencia entre dos horas es exactamente 30 minutos."""
    h1, m1 = map(int, hora_ini.split(":"))
    h2, m2 = map(int, hora_fin.split(":"))
    minutos_ini = h1 * 60 + m1
    minutos_fin = h2 * 60 + m2
    return (minutos_fin - minutos_ini) == 30
