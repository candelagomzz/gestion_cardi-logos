"""Vista de confección de agenda (Auxiliar)."""

import tkinter as tk
from src.presentacion.vistas.componentes import (
    MarcoBase, boton_primario, boton_secundario, campo_form,
    COLOR_FONDO, FUENTE_TITULO, FUENTE_NORMAL, FUENTE_SUBTITULO, COLOR_PRIMARIO
)
from src.datos.modelos.entidades import Rol
from datetime import datetime


class VistaAgenda(MarcoBase):
    def __init__(self, parent, controlador, **kwargs):
        super().__init__(parent, controlador)
        self._servicio = controlador.servicios["consultas"]
        self._servicio_prof = controlador.servicios["profesionales"]
        self._construir()

    def _construir(self):
        tk.Label(self, text="Confección de Agenda de Consultas", fg=COLOR_PRIMARIO,
                 bg=COLOR_FONDO, font=FUENTE_TITULO).pack(anchor=tk.W, padx=15, pady=10)

        tk.Label(
            self,
            text=(
                "Selecciona un médico y un período para generar automáticamente\n"
                "las consultas libres según sus franjas horarias registradas."
            ),
            bg=COLOR_FONDO, fg="#555", font=FUENTE_NORMAL, justify=tk.LEFT
        ).pack(anchor=tk.W, padx=15, pady=(0, 15))

        form = tk.Frame(self, bg=COLOR_FONDO)
        form.pack(padx=20)

        medicos = [p for p in self._servicio_prof.listar() if p.rol == Rol.MEDICO and p.activo]
        self._medicos_map = {f"{m.dni} – {m.nombre_completo()}": m.dni for m in medicos}
        medico_valores = list(self._medicos_map.keys())

        self._var_medico = campo_form(form, "Médico", 0, valores=medico_valores)
        self._var_fecha_ini = campo_form(form, "Fecha inicio (DD/MM/YYYY)", 1)
        self._var_fecha_fin = campo_form(form, "Fecha fin (DD/MM/YYYY)", 2)

        bar = tk.Frame(self, bg=COLOR_FONDO)
        bar.pack(pady=15)
        boton_primario(bar, "▶ Generar consultas", self._generar).pack(side=tk.LEFT, padx=5)

        self._lbl_resultado = tk.Label(self, text="", bg=COLOR_FONDO, font=FUENTE_SUBTITULO)
        self._lbl_resultado.pack(pady=10)

    def _generar(self):
        medico_key = self._var_medico.get()
        medico_dni = self._medicos_map.get(medico_key, "")
        fecha_ini_str = self._var_fecha_ini.get().strip()
        fecha_fin_str = self._var_fecha_fin.get().strip()

        try:
            fecha_ini = datetime.strptime(fecha_ini_str, "%d/%m/%Y").date()
            fecha_fin = datetime.strptime(fecha_fin_str, "%d/%m/%Y").date()
        except ValueError:
            self.mostrar_error("Formato de fecha incorrecto. Use DD/MM/YYYY.")
            return

        try:
            creadas = self._servicio.confeccionar_agenda(medico_dni, fecha_ini, fecha_fin)
            self._lbl_resultado.config(
                text=f"✅  Se han generado {creadas} nuevas consultas.",
                fg="#2E7D32"
            )
        except ValueError as e:
            self._lbl_resultado.config(text=f"⚠️  {e}", fg="#C62828")
