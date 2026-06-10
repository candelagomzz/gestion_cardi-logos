"""Vista de confección de agenda (Auxiliar)."""

import tkinter as tk
from datetime import datetime
from src.presentacion.vistas.componentes import (
    MarcoBase, boton_primario, campo_form,
    COLOR_FONDO, FUENTE_TITULO, FUENTE_NORMAL, FUENTE_SUBTITULO, COLOR_PRIMARIO
)


class VistaAgenda(MarcoBase):
    def __init__(self, parent, controlador, **kwargs):
        super().__init__(parent, controlador)
        self._construir()

    def _construir(self):
        tk.Label(self, text="Confección de Agenda de Consultas",
                 fg=COLOR_PRIMARIO, bg=COLOR_FONDO,
                 font=FUENTE_TITULO).pack(anchor=tk.W, padx=15, pady=10)

        tk.Label(
            self,
            text=("Selecciona un médico y un período para generar las\n"
                  "consultas libres según sus franjas horarias registradas."),
            bg=COLOR_FONDO, fg="#555", font=FUENTE_NORMAL, justify=tk.LEFT
        ).pack(anchor=tk.W, padx=15, pady=(0, 15))

        form = tk.Frame(self, bg=COLOR_FONDO)
        form.pack(padx=20)

        # Médicos desde el controlador
        medicos = self.controlador.listar_medicos_activos()
        self._medicos_map = {
            f"{m.dni} – {m.nombre_completo()}": m.dni for m in medicos
        }
        self._var_medico = campo_form(
            form, "Médico", 0, valores=list(self._medicos_map.keys()))
        self._var_fecha_ini = campo_form(form, "Fecha inicio (DD/MM/YYYY)", 1)
        self._var_fecha_fin = campo_form(form, "Fecha fin (DD/MM/YYYY)", 2)

        boton_primario(self, "▶ Generar consultas",
                       self._generar).pack(anchor=tk.W, padx=20, pady=15)

        self._lbl_resultado = tk.Label(self, text="", bg=COLOR_FONDO,
                                       font=FUENTE_SUBTITULO)
        self._lbl_resultado.pack(pady=5)

    def _generar(self):
        medico_dni = self._medicos_map.get(self._var_medico.get(), "")
        try:
            fecha_ini = datetime.strptime(
                self._var_fecha_ini.get().strip(), "%d/%m/%Y").date()
            fecha_fin = datetime.strptime(
                self._var_fecha_fin.get().strip(), "%d/%m/%Y").date()
        except ValueError:
            self.mostrar_error("Formato de fecha incorrecto. Use DD/MM/YYYY.")
            return
        try:
            creadas = self.controlador.confeccionar_agenda(
                medico_dni, fecha_ini, fecha_fin)
            self._lbl_resultado.config(
                text=f"✅  Se han generado {creadas} nuevas consultas.",
                fg="#2E7D32")
        except ValueError as e:
            self._lbl_resultado.config(text=f"⚠️  {e}", fg="#C62828")
