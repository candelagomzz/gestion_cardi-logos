"""Vista de inicio / dashboard."""

import tkinter as tk
from datetime import date
from src.presentacion.vistas.componentes import (
    MarcoBase, COLOR_PRIMARIO, COLOR_FONDO, COLOR_SECUNDARIO,
    FUENTE_TITULO, FUENTE_SUBTITULO, FUENTE_NORMAL
)
from src.datos.modelos.entidades import Rol


class VistaInicio(MarcoBase):
    def __init__(self, parent, controlador, **kwargs):
        super().__init__(parent, controlador)
        usuario = controlador.usuario_actual

        tk.Label(
            self,
            text=f"Bienvenido/a, {usuario.nombre_completo()}",
            bg=COLOR_FONDO, fg=COLOR_PRIMARIO, font=FUENTE_TITULO
        ).pack(pady=(30, 5))

        tk.Label(
            self,
            text=f"Hoy es {date.today().strftime('%A, %d de %B de %Y')}",
            bg=COLOR_FONDO, fg="#757575", font=FUENTE_NORMAL
        ).pack()

        # Tarjetas de acceso rápido según rol
        panel = tk.Frame(self, bg=COLOR_FONDO)
        panel.pack(pady=30)

        if usuario.rol == Rol.ADMINISTRADOR:
            self._tarjeta(panel, "Gestionar\nProfesionales", "profesionales", 0)
            self._tarjeta(panel, "Gestionar\nFranjas", "franjas", 1)

        elif usuario.rol == Rol.AUXILIAR:
            self._tarjeta(panel, "Confeccionar\nAgenda", "agenda", 0)
            self._tarjeta(panel, "Gestionar\nConsultas", "consultas_auxiliar", 1)
            self._tarjeta(panel, "Gestionar\nPacientes", "pacientes", 2)

        elif usuario.rol == Rol.MEDICO:
            self._tarjeta(panel, "Mis\nConsultas", "consultas_medico", 0)
            self._tarjeta(panel, "Tensiones\nPacientes", "tensiones", 1)

    def _tarjeta(self, parent, texto: str, pantalla: str, col: int):
        marco = tk.Frame(parent, bg="white", relief=tk.RAISED, bd=1,
                         width=150, height=120, cursor="hand2")
        marco.grid(row=0, column=col, padx=15)
        marco.pack_propagate(False)
        marco.bind("<Button-1>", lambda e, p=pantalla: self.controlador._vista.mostrar_pantalla(p))

        lbl = tk.Label(marco, text=texto, bg="white", fg=COLOR_PRIMARIO,
                       font=FUENTE_SUBTITULO, justify=tk.CENTER)
        lbl.pack(expand=True)
        lbl.bind("<Button-1>", lambda e, p=pantalla: self.controlador._vista.mostrar_pantalla(p))
