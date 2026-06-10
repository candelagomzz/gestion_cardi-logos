"""
Controlador principal de la aplicación — arquitectura MVC.

Es el único intermediario entre la capa de Presentación y la capa de Negocio.
Las vistas NUNCA acceden directamente a los servicios ni a las entidades
de la capa de datos. Solo llaman a métodos de este controlador.

Responsabilidades:
  - Gestionar la sesión activa (usuario logueado, rol, permisos)
  - Exponer operaciones de negocio como métodos propios
  - Gestionar la navegación entre pantallas
  - Traducir los resultados de los servicios a estructuras simples para las vistas
"""

from datetime import date
from typing import Optional, List, Dict, Any

from src.datos.modelos.entidades import Profesional, Rol


class ControladorApp:

    def __init__(self, servicios: dict):
        self._servicios = servicios
        self._vista = None
        self._usuario_actual: Optional[Profesional] = None

    def set_vista(self, vista) -> None:
        self._vista = vista

    # ── Navegación ────────────────────────────────────────────────────────

    def navegar(self, pantalla: str, **kwargs) -> None:
        """Único punto de navegación. Las vistas llaman a este método."""
        self._vista.mostrar_pantalla(pantalla, **kwargs)

    def mostrar_login(self) -> None:
        self._usuario_actual = None
        self._vista.mostrar_pantalla("login")

    def cerrar_sesion(self) -> None:
        self.mostrar_login()

    # ── Sesión y permisos ─────────────────────────────────────────────────

    @property
    def usuario_actual(self) -> Optional[Profesional]:
        return self._usuario_actual

    def es_administrador(self) -> bool:
        return bool(self._usuario_actual and
                    self._usuario_actual.rol == Rol.ADMINISTRADOR)

    def es_auxiliar(self) -> bool:
        return bool(self._usuario_actual and
                    self._usuario_actual.rol == Rol.AUXILIAR)

    def es_medico(self) -> bool:
        return bool(self._usuario_actual and
                    self._usuario_actual.rol == Rol.MEDICO)

    # ── Autenticación ─────────────────────────────────────────────────────

    def autenticar(self, dni: str, contrasena: str) -> bool:
        profesional = self._servicios["autenticacion"].autenticar(dni, contrasena)
        if profesional:
            self._usuario_actual = profesional
            self._vista.mostrar_pantalla("inicio")
            return True
        return False

    # ── Profesionales ─────────────────────────────────────────────────────

    def listar_profesionales(self) -> list:
        return self._servicios["profesionales"].listar()

    def obtener_profesional(self, id_: str):
        return self._servicios["profesionales"].obtener(id_)

    def crear_profesional(self, datos: dict) -> None:
        from src.datos.modelos.entidades import Profesional
        p = Profesional(
            nombre=datos["nombre"],
            apellidos=datos["apellidos"],
            dni=datos["dni"],
            rol=datos["rol"],
            contrasena=datos["contrasena"],
            activo=True,
        )
        self._servicios["profesionales"].crear(p)

    def modificar_profesional(self, id_: str, datos: dict) -> None:
        self._servicios["profesionales"].modificar(id_, datos)

    def cambiar_contrasena_perfil(self, nueva_contrasena: str) -> None:
        self._servicios["profesionales"].cambiar_contrasena(
            self._usuario_actual._id, nueva_contrasena
        )

    def listar_medicos_activos(self) -> list:
        """Devuelve solo los profesionales con rol médico y activos."""
        return [
            p for p in self._servicios["profesionales"].listar()
            if p.rol == Rol.MEDICO and p.activo
        ]

    # ── Franjas ───────────────────────────────────────────────────────────

    def listar_franjas(self) -> list:
        return self._servicios["franjas"].listar()

    def obtener_franja(self, id_: str):
        return self._servicios["franjas"].obtener(id_)

    def crear_franja(self, datos: dict) -> None:
        from src.datos.modelos.entidades import Franja
        f = Franja(
            dia=datos["dia"],
            hora_inicial=datos["hora_inicial"],
            hora_final=datos["hora_final"],
            medico_dni=datos["medico_dni"],
        )
        self._servicios["franjas"].crear(f)

    def modificar_franja(self, id_: str, datos: dict) -> None:
        from src.datos.modelos.entidades import Franja
        f = Franja(
            dia=datos["dia"],
            hora_inicial=datos["hora_inicial"],
            hora_final=datos["hora_final"],
            medico_dni=datos["medico_dni"],
            _id=id_,
        )
        self._servicios["franjas"].modificar(id_, f)

    def eliminar_franja(self, id_: str) -> None:
        self._servicios["franjas"].eliminar(id_)

    # ── Pacientes ─────────────────────────────────────────────────────────

    def listar_pacientes(self) -> list:
        return self._servicios["pacientes"].listar()

    def obtener_paciente(self, id_: str):
        return self._servicios["pacientes"].obtener(id_)

    def crear_paciente(self, datos: dict) -> None:
        from src.datos.modelos.entidades import Paciente
        p = Paciente(
            nombre=datos["nombre"],
            apellidos=datos["apellidos"],
            genero=datos["genero"],
            fecha_nacimiento=datos["fecha_nacimiento"],
            activo=True,
        )
        self._servicios["pacientes"].crear(p)

    def modificar_paciente(self, id_: str, datos: dict) -> None:
        self._servicios["pacientes"].modificar(id_, datos)

    # ── Consultas (Auxiliar) ──────────────────────────────────────────────

    def listar_consultas(self) -> list:
        return self._servicios["consultas"].listar_todas()

    def obtener_consulta(self, id_: str):
        return self._servicios["consultas"].obtener(id_)

    def confeccionar_agenda(self, medico_dni: str,
                            fecha_ini: date, fecha_fin: date) -> int:
        return self._servicios["consultas"].confeccionar_agenda(
            medico_dni, fecha_ini, fecha_fin)

    def asignar_paciente_consulta(self, id_consulta: str,
                                  paciente_id: str) -> None:
        self._servicios["consultas"].asignar_paciente(id_consulta, paciente_id)

    def modificar_estado_consulta_auxiliar(self, id_consulta: str,
                                           nuevo_estado: str) -> None:
        self._servicios["consultas"].modificar_estado_auxiliar(
            id_consulta, nuevo_estado)

    # ── Consultas (Médico) ────────────────────────────────────────────────

    def listar_mis_consultas(self) -> list:
        return self._servicios["consultas"].listar_por_medico(
            self._usuario_actual.dni)

    def listar_mis_consultas_hoy(self) -> list:
        return self._servicios["consultas"].listar_consultas_hoy(
            self._usuario_actual.dni)

    def listar_mis_consultas_pendientes(self) -> list:
        return self._servicios["consultas"].listar_pendientes(
            self._usuario_actual.dni)

    def listar_mis_consultas_atendidas(self) -> list:
        return self._servicios["consultas"].listar_atendidas_por_medico(
            self._usuario_actual.dni)

    def listar_consultas_de_paciente(self, paciente_id: str) -> list:
        return self._servicios["consultas"].listar_consultas_paciente_de_medico(
            self._usuario_actual.dni, paciente_id)

    def actualizar_estado_consulta_medico(self, id_consulta: str,
                                          nuevo_estado: str) -> None:
        self._servicios["consultas"].actualizar_estado_medico(
            id_consulta, nuevo_estado)

    def actualizar_comentario_consulta(self, id_consulta: str,
                                       comentario: str) -> None:
        self._servicios["consultas"].actualizar_comentario(
            id_consulta, comentario)

    # ── Tensiones ─────────────────────────────────────────────────────────

    def listar_tensiones_paciente(self, paciente_id: str) -> list:
        return self._servicios["tensiones"].listar_por_paciente(paciente_id)

    def obtener_tension(self, id_: str):
        return self._servicios["tensiones"].obtener(id_)

    def registrar_tension(self, datos: dict) -> None:
        from src.datos.modelos.entidades import TomaTension
        t = TomaTension(
            paciente_id=datos["paciente_id"],
            fecha=datos["fecha"],
            sistolica=datos["sistolica"],
            diastolica=datos["diastolica"],
            metodo=datos["metodo"],
            sitio_cuerpo=datos["sitio_cuerpo"],
            tamano_brazalete=datos["tamano_brazalete"],
            dispositivo=datos["dispositivo"],
            estado=datos["estado"],
            descripcion=datos.get("descripcion"),
        )
        self._servicios["tensiones"].registrar(t)

    def modificar_tension(self, id_: str, datos: dict) -> None:
        self._servicios["tensiones"].modificar(id_, datos)

    def media_tensiones(self, paciente_id: str,
                        ultimas_n: Optional[int] = None) -> dict:
        return self._servicios["tensiones"].media_tensiones(
            paciente_id, ultimas_n)

    def filtrar_tensiones(self, paciente_id: str, metodo: Optional[str] = None,
                          sitio_cuerpo: Optional[str] = None,
                          tamano_brazalete: Optional[str] = None,
                          dispositivo: Optional[str] = None) -> list:
        return self._servicios["tensiones"].filtrar(
            paciente_id, metodo=metodo, sitio_cuerpo=sitio_cuerpo,
            tamano_brazalete=tamano_brazalete, dispositivo=dispositivo)

    def listar_pacientes_del_medico(self) -> list:
        """Devuelve los pacientes que tienen consultas con el médico activo."""
        consultas = self._servicios["consultas"].listar_por_medico(
            self._usuario_actual.dni)
        pac_ids = list({c.paciente_id for c in consultas if c.paciente_id})
        pacientes = [self._servicios["pacientes"].obtener(pid) for pid in pac_ids]
        return [p for p in pacientes if p]

    # ── Constantes de dominio para las vistas ────────────────────────────
    # Las vistas obtienen los valores permitidos desde aquí,
    # sin importar nada de la capa de datos directamente.

    def roles_disponibles(self) -> list:
        return Rol.VALORES

    def dias_semana(self) -> list:
        from src.datos.modelos.entidades import DiaSemana
        return DiaSemana.VALORES

    def estados_consulta_auxiliar(self) -> list:
        from src.datos.modelos.entidades import EstadoConsulta
        return [EstadoConsulta.LIBRE, EstadoConsulta.OCUPADA,
                EstadoConsulta.CANCELADA, EstadoConsulta.ELIMINADA]

    def estados_consulta_medico(self) -> list:
        from src.datos.modelos.entidades import EstadoConsulta
        return [EstadoConsulta.ATENDIDA, EstadoConsulta.CANCELADA]

    def generos_fhir(self) -> list:
        from src.datos.modelos.entidades import GeneroFHIR
        return GeneroFHIR.VALORES

    def metodos_tension(self) -> list:
        from src.datos.modelos.entidades import MetodoTension
        return MetodoTension.VALORES

    def sitios_cuerpo(self) -> list:
        from src.datos.modelos.entidades import SitioCuerpo
        return SitioCuerpo.VALORES

    def tamanos_brazalete(self) -> list:
        from src.datos.modelos.entidades import TamanoBrazalete
        return TamanoBrazalete.VALORES

    def estados_observacion_fhir(self) -> list:
        from src.datos.modelos.entidades import EstadoObservacionFHIR
        return EstadoObservacionFHIR.VALORES
