"""
Modelos de dominio del sistema.
Clases de datos puras, sin dependencia de ninguna tecnología.
"""

from dataclasses import dataclass, field
from typing import Optional
from datetime import date, time


# ---------------------------------------------------------------------------
# Enumeraciones como constantes para evitar dependencias externas
# ---------------------------------------------------------------------------

class Rol:
    ADMINISTRADOR = "administrador"
    AUXILIAR = "auxiliar"
    MEDICO = "medico"
    VALORES = [ADMINISTRADOR, AUXILIAR, MEDICO]


class DiaSemana:
    LUNES = "lunes"
    MARTES = "martes"
    MIERCOLES = "miercoles"
    JUEVES = "jueves"
    VIERNES = "viernes"
    SABADO = "sabado"
    VALORES = [LUNES, MARTES, MIERCOLES, JUEVES, VIERNES, SABADO]


class EstadoConsulta:
    LIBRE = "libre"
    OCUPADA = "ocupada"
    ATENDIDA = "atendida"
    CANCELADA = "cancelada"
    ELIMINADA = "eliminada"
    VALORES = [LIBRE, OCUPADA, ATENDIDA, CANCELADA, ELIMINADA]


class GeneroFHIR:
    MALE = "male"
    FEMALE = "female"
    OTHER = "other"
    UNKNOWN = "unknown"
    VALORES = [MALE, FEMALE, OTHER, UNKNOWN]


class EstadoObservacionFHIR:
    REGISTERED = "registered"
    PRELIMINARY = "preliminary"
    FINAL = "final"
    AMENDED = "amended"
    CORRECTED = "corrected"
    CANCELLED = "cancelled"
    ENTERED_IN_ERROR = "entered-in-error"
    UNKNOWN = "unknown"
    VALORES = [REGISTERED, PRELIMINARY, FINAL, AMENDED, CORRECTED, CANCELLED, ENTERED_IN_ERROR, UNKNOWN]


class MetodoTension:
    AUSCULTATORIO = "auscultatorio"
    OSCILOMETRICO = "oscilometrico"
    VALORES = [AUSCULTATORIO, OSCILOMETRICO]


class SitioCuerpo:
    BRAZO_IZQUIERDO = "brazo_izquierdo"
    BRAZO_DERECHO = "brazo_derecho"
    MUNECA_IZQUIERDA = "muneca_izquierda"
    MUNECA_DERECHA = "muneca_derecha"
    VALORES = [BRAZO_IZQUIERDO, BRAZO_DERECHO, MUNECA_IZQUIERDA, MUNECA_DERECHA]


class TamanoBrazalete:
    PEQUENO = "pequeno"
    MEDIANO = "mediano"
    GRANDE = "grande"
    EXTRA_GRANDE = "extra_grande"
    VALORES = [PEQUENO, MEDIANO, GRANDE, EXTRA_GRANDE]


# ---------------------------------------------------------------------------
# Entidades de dominio
# ---------------------------------------------------------------------------

@dataclass
class Profesional:
    nombre: str
    apellidos: str
    dni: str
    rol: str
    contrasena: str
    activo: bool = True
    _id: Optional[str] = None

    def nombre_completo(self) -> str:
        return f"{self.nombre} {self.apellidos}"


@dataclass
class Franja:
    dia: str
    hora_inicial: str   # "HH:MM"
    hora_final: str     # "HH:MM"
    medico_dni: str
    _id: Optional[str] = None


@dataclass
class Paciente:
    nombre: str
    apellidos: str
    genero: str
    fecha_nacimiento: str   # ISO: "YYYY-MM-DD"
    activo: bool = True
    _id: Optional[str] = None

    def nombre_completo(self) -> str:
        return f"{self.nombre} {self.apellidos}"


@dataclass
class Consulta:
    dia: str            # "DD/MM/YYYY"
    hora_inicio: str    # "HH:MM"
    hora_fin: str       # "HH:MM"
    medico_dni: str
    estado: str = EstadoConsulta.LIBRE
    paciente_id: Optional[str] = None
    comentario: Optional[str] = None
    _id: Optional[str] = None


@dataclass
class TomaTension:
    paciente_id: str
    fecha: str                      # ISO "YYYY-MM-DD"
    sistolica: int
    diastolica: int
    metodo: str
    sitio_cuerpo: str
    tamano_brazalete: str
    dispositivo: str
    estado: str
    descripcion: Optional[str] = None
    en_rango: bool = False
    _id: Optional[str] = None
