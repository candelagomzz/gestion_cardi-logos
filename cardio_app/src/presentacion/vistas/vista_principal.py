"""
Vista principal: contenedor que gestiona el cambio de pantallas.
Arquitectura MVC: esta vista no contiene lógica de negocio.
La navegación se delega siempre al controlador mediante controlador.navegar().
"""

import tkinter as tk
from src.presentacion.vistas.componentes import COLOR_FONDO, BarraSuperior
from src.presentacion.vistas.vista_login import VistaLogin
from src.presentacion.vistas.vista_inicio import VistaInicio
from src.presentacion.vistas.vista_profesionales import VistaProfesionales
from src.presentacion.vistas.vista_franjas import VistaFranjas
from src.presentacion.vistas.vista_pacientes import VistaPacientes
from src.presentacion.vistas.vista_consultas_auxiliar import VistaConsultasAuxiliar
from src.presentacion.vistas.vista_agenda import VistaAgenda
from src.presentacion.vistas.vista_consultas_medico import VistaConsultasMedico
from src.presentacion.vistas.vista_tensiones import VistaTensiones
from src.presentacion.vistas.vista_perfil import VistaPerfil

_MAPA_VISTAS = {
    "inicio": VistaInicio,
    "profesionales": VistaProfesionales,
    "franjas": VistaFranjas,
    "pacientes": VistaPacientes,
    "consultas_auxiliar": VistaConsultasAuxiliar,
    "agenda": VistaAgenda,
    "consultas_medico": VistaConsultasMedico,
    "tensiones": VistaTensiones,
    "perfil": VistaPerfil,
}


class VistaPrincipal:
    def __init__(self, root: tk.Tk, controlador):
        self._root = root
        self._controlador = controlador
        self._root.configure(bg=COLOR_FONDO)
        self._contenedor = tk.Frame(self._root, bg=COLOR_FONDO)
        self._contenedor.pack(fill=tk.BOTH, expand=True)

    def mostrar_pantalla(self, nombre: str, **kwargs) -> None:
        for widget in self._contenedor.winfo_children():
            widget.destroy()

        if nombre == "login":
            VistaLogin(self._contenedor, self._controlador).pack(
                fill=tk.BOTH, expand=True)
            return

        BarraSuperior(
            self._contenedor, self._controlador,
            "♥ Gestión de Consultas Cardiológicas"
        ).pack(fill=tk.X)

        area = tk.Frame(self._contenedor, bg=COLOR_FONDO)
        area.pack(fill=tk.BOTH, expand=True)

        self._crear_menu_lateral(area).pack(side=tk.LEFT, fill=tk.Y)
        tk.Frame(area, bg="#BDBDBD", width=1).pack(side=tk.LEFT, fill=tk.Y)

        contenido = tk.Frame(area, bg=COLOR_FONDO)
        contenido.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        clase_vista = _MAPA_VISTAS.get(nombre, VistaInicio)
        clase_vista(contenido, self._controlador, **kwargs).pack(
            fill=tk.BOTH, expand=True)

    def _crear_menu_lateral(self, parent) -> tk.Frame:
        ctrl = self._controlador
        panel = tk.Frame(parent, bg="#1A237E", width=200)
        panel.pack_propagate(False)

        def btn_menu(texto, pantalla):
            tk.Button(
                panel, text=texto, bg="#1A237E", fg="white",
                font=("Segoe UI", 10), relief=tk.FLAT,
                anchor=tk.W, padx=20, pady=8, cursor="hand2",
                activebackground="#283593", activeforeground="white",
                command=lambda p=pantalla: ctrl.navegar(p)
            ).pack(fill=tk.X)

        def seccion(texto):
            tk.Label(panel, text=texto, bg="#1A237E", fg="#9FA8DA",
                     font=("Segoe UI", 8)).pack(
                pady=(15, 3), padx=15, anchor=tk.W)

        seccion("MENÚ")
        btn_menu("🏠  Inicio", "inicio")
        btn_menu("👤  Mi perfil", "perfil")

        if ctrl.es_administrador():
            seccion("ADMINISTRACIÓN")
            btn_menu("👥  Profesionales", "profesionales")
            btn_menu("🕐  Franjas horarias", "franjas")

        if ctrl.es_auxiliar():
            seccion("AUXILIAR")
            btn_menu("📋  Agenda", "agenda")
            btn_menu("🗓️  Consultas", "consultas_auxiliar")
            btn_menu("🏥  Pacientes", "pacientes")

        if ctrl.es_medico():
            seccion("MÉDICO")
            btn_menu("📅  Mis consultas", "consultas_medico")
            btn_menu("💉  Tensiones", "tensiones")

        return panel
