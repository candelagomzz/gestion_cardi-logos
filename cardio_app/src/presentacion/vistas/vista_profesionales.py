"""Vista CRUD de Profesionales (Administrador).
No importa nada de la capa de datos: obtiene los valores permitidos
del controlador mediante controlador.roles_disponibles().
"""

import tkinter as tk
from src.presentacion.vistas.componentes import (
    MarcoBase, crear_tabla, boton_primario, boton_secundario,
    etiqueta_seccion, campo_form, COLOR_FONDO, FUENTE_TITULO
)


class VistaProfesionales(MarcoBase):
    def __init__(self, parent, controlador, **kwargs):
        super().__init__(parent, controlador)
        self._seleccionado_id = None
        self._construir()

    def _construir(self):
        tk.Label(self, text="Gestión de Profesionales", fg="#1565C0",
                 bg=COLOR_FONDO, font=FUENTE_TITULO).pack(
            anchor=tk.W, padx=15, pady=10)

        etiqueta_seccion(self, "Listado de profesionales")
        cols = [("Nombre", 150), ("Apellidos", 180), ("DNI", 110),
                ("Rol", 110), ("Activo", 70)]
        self._tabla = crear_tabla(self, cols, alto=12)
        self._tabla.bind("<<TreeviewSelect>>",
                         lambda e: self._al_seleccionar())
        self._cargar_tabla()

        bar = tk.Frame(self, bg=COLOR_FONDO)
        bar.pack(fill=tk.X, padx=10, pady=5)
        boton_primario(bar, "➕ Nuevo",
                       self._abrir_nuevo).pack(side=tk.LEFT, padx=3)
        boton_secundario(bar, "✏️ Editar",
                         self._abrir_editar).pack(side=tk.LEFT, padx=3)

    def _cargar_tabla(self):
        for item in self._tabla.get_children():
            self._tabla.delete(item)
        for p in self.controlador.listar_profesionales():
            self._tabla.insert("", tk.END, iid=p._id, values=(
                p.nombre, p.apellidos, p.dni, p.rol,
                "Sí" if p.activo else "No"
            ))

    def _al_seleccionar(self):
        sel = self._tabla.selection()
        self._seleccionado_id = sel[0] if sel else None

    def _abrir_nuevo(self):
        _FormularioProfesional(self, self.controlador, None,
                               self._cargar_tabla)

    def _abrir_editar(self):
        if not self._seleccionado_id:
            self.mostrar_info("Selecciona un profesional primero.")
            return
        p = self.controlador.obtener_profesional(self._seleccionado_id)
        _FormularioProfesional(self, self.controlador, p, self._cargar_tabla)


class _FormularioProfesional(tk.Toplevel):
    def __init__(self, parent, controlador, profesional, callback):
        super().__init__(parent)
        self._ctrl = controlador
        self._profesional = profesional
        self._es_nuevo = profesional is None
        self._callback = callback
        self.title("Nuevo profesional" if self._es_nuevo else "Editar profesional")
        self.resizable(False, False)
        self.configure(bg=COLOR_FONDO)
        self._construir()
        self.grab_set()

    def _construir(self):
        form = tk.Frame(self, bg=COLOR_FONDO)
        form.pack(padx=20, pady=15)

        # Los valores de rol los pide al controlador, no importa entidades
        self._var_nombre = campo_form(form, "Nombre", 0)
        self._var_apellidos = campo_form(form, "Apellidos", 1)
        self._var_dni = campo_form(form, "DNI", 2)
        self._var_rol = campo_form(form, "Rol", 3,
                                   valores=self._ctrl.roles_disponibles())
        self._var_contrasena = campo_form(form, "Contraseña", 4,
                                          es_password=True)
        self._var_activo = campo_form(form, "Activo", 5,
                                      valores=["True", "False"])

        if self._profesional:
            p = self._profesional
            self._var_nombre.set(p.nombre)
            self._var_apellidos.set(p.apellidos)
            self._var_dni.set(p.dni)
            self._var_rol.set(p.rol)
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
                self._ctrl.crear_profesional({
                    "nombre": self._var_nombre.get().strip(),
                    "apellidos": self._var_apellidos.get().strip(),
                    "dni": self._var_dni.get().strip(),
                    "rol": self._var_rol.get(),
                    "contrasena": self._var_contrasena.get(),
                })
            else:
                datos = {
                    "nombre": self._var_nombre.get().strip(),
                    "apellidos": self._var_apellidos.get().strip(),
                    "rol": self._var_rol.get(),
                    "activo": self._var_activo.get() == "True",
                }
                if self._var_contrasena.get():
                    datos["contrasena"] = self._var_contrasena.get()
                self._ctrl.modificar_profesional(
                    self._profesional._id, datos)
            self._callback()
            self.destroy()
        except ValueError as e:
            messagebox.showerror("Validación", str(e), parent=self)
