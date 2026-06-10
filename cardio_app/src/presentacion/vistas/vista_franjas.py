"""Vista CRUD de Franjas Horarias (Administrador)."""

import tkinter as tk
from src.presentacion.vistas.componentes import (
    MarcoBase, crear_tabla, boton_primario, boton_secundario, boton_peligro,
    etiqueta_seccion, campo_form, COLOR_FONDO, FUENTE_TITULO
)


class VistaFranjas(MarcoBase):
    def __init__(self, parent, controlador, **kwargs):
        super().__init__(parent, controlador)
        self._seleccionado_id = None
        self._construir()

    def _construir(self):
        tk.Label(self, text="Gestión de Franjas Horarias", fg="#1565C0",
                 bg=COLOR_FONDO, font=FUENTE_TITULO).pack(
            anchor=tk.W, padx=15, pady=10)

        etiqueta_seccion(self, "Franjas registradas")
        cols = [("Médico", 200), ("Día", 100),
                ("Hora inicio", 100), ("Hora fin", 100)]
        self._tabla = crear_tabla(self, cols, alto=14)
        self._tabla.bind("<<TreeviewSelect>>",
                         lambda e: self._al_seleccionar())
        self._cargar_tabla()

        bar = tk.Frame(self, bg=COLOR_FONDO)
        bar.pack(fill=tk.X, padx=10, pady=5)
        boton_primario(bar, "➕ Nueva", self._abrir_nuevo).pack(
            side=tk.LEFT, padx=3)
        boton_secundario(bar, "✏️ Editar", self._abrir_editar).pack(
            side=tk.LEFT, padx=3)
        boton_peligro(bar, "🗑️ Eliminar", self._eliminar).pack(
            side=tk.LEFT, padx=3)

    def _cargar_tabla(self):
        for item in self._tabla.get_children():
            self._tabla.delete(item)
        for f in self.controlador.listar_franjas():
            self._tabla.insert("", tk.END, iid=f._id, values=(
                f.medico_dni, f.dia, f.hora_inicial, f.hora_final
            ))

    def _al_seleccionar(self):
        sel = self._tabla.selection()
        self._seleccionado_id = sel[0] if sel else None

    def _abrir_nuevo(self):
        _FormularioFranja(self, self.controlador, None, self._cargar_tabla)

    def _abrir_editar(self):
        if not self._seleccionado_id:
            self.mostrar_info("Selecciona una franja.")
            return
        franja = self.controlador.obtener_franja(self._seleccionado_id)
        _FormularioFranja(self, self.controlador, franja, self._cargar_tabla)

    def _eliminar(self):
        if not self._seleccionado_id:
            self.mostrar_info("Selecciona una franja.")
            return
        if self.confirmar("¿Eliminar la franja seleccionada?"):
            self.controlador.eliminar_franja(self._seleccionado_id)
            self._cargar_tabla()


class _FormularioFranja(tk.Toplevel):
    def __init__(self, parent, controlador, franja, callback):
        super().__init__(parent)
        self._ctrl = controlador
        self._franja = franja
        self._es_nuevo = franja is None
        self._callback = callback
        self.title("Nueva franja" if self._es_nuevo else "Editar franja")
        self.resizable(False, False)
        self.configure(bg=COLOR_FONDO)
        self._construir()
        self.grab_set()

    def _construir(self):
        form = tk.Frame(self, bg=COLOR_FONDO)
        form.pack(padx=20, pady=15)

        # Médicos: los pide al controlador
        medicos = self._ctrl.listar_medicos_activos()
        self._medicos_map = {
            f"{m.dni} – {m.nombre_completo()}": m.dni for m in medicos
        }
        horas = [f"{h:02d}:{m:02d}" for h in range(8, 22) for m in (0, 30)]

        self._var_medico = campo_form(
            form, "Médico", 0, valores=list(self._medicos_map.keys()))
        self._var_dia = campo_form(
            form, "Día", 1, valores=self._ctrl.dias_semana())
        self._var_hora_ini = campo_form(form, "Hora inicio", 2, valores=horas)
        self._var_hora_fin = campo_form(form, "Hora fin", 3, valores=horas)

        if self._franja:
            f = self._franja
            for k, v in self._medicos_map.items():
                if v == f.medico_dni:
                    self._var_medico.set(k)
                    break
            self._var_dia.set(f.dia)
            self._var_hora_ini.set(f.hora_inicial)
            self._var_hora_fin.set(f.hora_final)

        bar = tk.Frame(self, bg=COLOR_FONDO)
        bar.pack(pady=10)
        boton_primario(bar, "Guardar", self._guardar).pack(
            side=tk.LEFT, padx=5)
        boton_secundario(bar, "Cancelar", self.destroy).pack(
            side=tk.LEFT, padx=5)

    def _guardar(self):
        from tkinter import messagebox
        try:
            medico_dni = self._medicos_map.get(self._var_medico.get(), "")
            datos = {
                "dia": self._var_dia.get(),
                "hora_inicial": self._var_hora_ini.get(),
                "hora_final": self._var_hora_fin.get(),
                "medico_dni": medico_dni,
            }
            if self._es_nuevo:
                self._ctrl.crear_franja(datos)
            else:
                self._ctrl.modificar_franja(self._franja._id, datos)
            self._callback()
            self.destroy()
        except ValueError as e:
            messagebox.showerror("Validación", str(e), parent=self)
