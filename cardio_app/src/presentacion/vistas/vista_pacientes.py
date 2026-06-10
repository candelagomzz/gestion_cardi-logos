"""Vista CRUD de Pacientes (Auxiliar)."""

import tkinter as tk
from src.presentacion.vistas.componentes import (
    MarcoBase, crear_tabla, boton_primario, boton_secundario,
    etiqueta_seccion, campo_form, COLOR_FONDO, FUENTE_TITULO
)


class VistaPacientes(MarcoBase):
    def __init__(self, parent, controlador, **kwargs):
        super().__init__(parent, controlador)
        self._seleccionado_id = None
        self._construir()

    def _construir(self):
        tk.Label(self, text="Gestión de Pacientes", fg="#1565C0",
                 bg=COLOR_FONDO, font=FUENTE_TITULO).pack(
            anchor=tk.W, padx=15, pady=10)

        etiqueta_seccion(self, "Listado de pacientes")
        cols = [("Nombre", 140), ("Apellidos", 180), ("Género", 90),
                ("F. Nacimiento", 110), ("Activo", 70)]
        self._tabla = crear_tabla(self, cols, alto=14)
        self._tabla.bind("<<TreeviewSelect>>",
                         lambda e: self._al_seleccionar())
        self._cargar_tabla()

        bar = tk.Frame(self, bg=COLOR_FONDO)
        bar.pack(fill=tk.X, padx=10, pady=5)
        boton_primario(bar, "➕ Nuevo", self._abrir_nuevo).pack(
            side=tk.LEFT, padx=3)
        boton_secundario(bar, "✏️ Editar", self._abrir_editar).pack(
            side=tk.LEFT, padx=3)

    def _cargar_tabla(self):
        for item in self._tabla.get_children():
            self._tabla.delete(item)
        for p in self.controlador.listar_pacientes():
            self._tabla.insert("", tk.END, iid=p._id, values=(
                p.nombre, p.apellidos, p.genero,
                p.fecha_nacimiento, "Sí" if p.activo else "No"
            ))

    def _al_seleccionar(self):
        sel = self._tabla.selection()
        self._seleccionado_id = sel[0] if sel else None

    def _abrir_nuevo(self):
        _FormularioPaciente(self, self.controlador, None, self._cargar_tabla)

    def _abrir_editar(self):
        if not self._seleccionado_id:
            self.mostrar_info("Selecciona un paciente.")
            return
        p = self.controlador.obtener_paciente(self._seleccionado_id)
        _FormularioPaciente(self, self.controlador, p, self._cargar_tabla)


class _FormularioPaciente(tk.Toplevel):
    def __init__(self, parent, controlador, paciente, callback):
        super().__init__(parent)
        self._ctrl = controlador
        self._paciente = paciente
        self._es_nuevo = paciente is None
        self._callback = callback
        self.title("Nuevo paciente" if self._es_nuevo else "Editar paciente")
        self.resizable(False, False)
        self.configure(bg=COLOR_FONDO)
        self._construir()
        self.grab_set()

    def _construir(self):
        form = tk.Frame(self, bg=COLOR_FONDO)
        form.pack(padx=20, pady=15)

        self._var_nombre = campo_form(form, "Nombre", 0)
        self._var_apellidos = campo_form(form, "Apellidos", 1)
        # Géneros desde el controlador, no desde entidades
        self._var_genero = campo_form(
            form, "Género (FHIR)", 2, valores=self._ctrl.generos_fhir())
        self._var_nacimiento = campo_form(
            form, "F. nacimiento (YYYY-MM-DD)", 3)
        self._var_activo = campo_form(
            form, "Activo", 4, valores=["True", "False"])

        if self._paciente:
            p = self._paciente
            self._var_nombre.set(p.nombre)
            self._var_apellidos.set(p.apellidos)
            self._var_genero.set(p.genero)
            self._var_nacimiento.set(p.fecha_nacimiento)
            self._var_activo.set(str(p.activo))

        bar = tk.Frame(self, bg=COLOR_FONDO)
        bar.pack(pady=10)
        boton_primario(bar, "Guardar", self._guardar).pack(
            side=tk.LEFT, padx=5)
        boton_secundario(bar, "Cancelar", self.destroy).pack(
            side=tk.LEFT, padx=5)

    def _guardar(self):
        from tkinter import messagebox
        try:
            if self._es_nuevo:
                self._ctrl.crear_paciente({
                    "nombre": self._var_nombre.get().strip(),
                    "apellidos": self._var_apellidos.get().strip(),
                    "genero": self._var_genero.get(),
                    "fecha_nacimiento": self._var_nacimiento.get().strip(),
                })
            else:
                self._ctrl.modificar_paciente(self._paciente._id, {
                    "nombre": self._var_nombre.get().strip(),
                    "apellidos": self._var_apellidos.get().strip(),
                    "genero": self._var_genero.get(),
                    "fecha_nacimiento": self._var_nacimiento.get().strip(),
                    "activo": self._var_activo.get() == "True",
                })
            self._callback()
            self.destroy()
        except ValueError as e:
            messagebox.showerror("Validación", str(e), parent=self)
