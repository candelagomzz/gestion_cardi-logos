"""Vista CRUD de Profesionales (Administrador)."""

import tkinter as tk
from tkinter import ttk
from src.presentacion.vistas.componentes import (
    MarcoBase, crear_tabla, boton_primario, boton_secundario, boton_peligro,
    etiqueta_seccion, campo_form, COLOR_FONDO, FUENTE_TITULO, FUENTE_NORMAL
)
from src.datos.modelos.entidades import Profesional, Rol


class VistaProfesionales(MarcoBase):
    def __init__(self, parent, controlador, **kwargs):
        super().__init__(parent, controlador)
        self._servicio = controlador.servicios["profesionales"]
        self._seleccionado_id = None
        self._construir()

    def _construir(self):
        # Título
        tk.Label(self, text="Gestión de Profesionales", bg="white" if False else "#F5F5F5",
                 fg="#1565C0", font=FUENTE_TITULO).pack(anchor=tk.W, padx=15, pady=10)

        # Tabla
        etiqueta_seccion(self, "Listado de profesionales")
        cols = [("Nombre", 150), ("Apellidos", 180), ("DNI", 110),
                ("Rol", 110), ("Activo", 70)]
        self._tabla = crear_tabla(self, cols, alto=12)
        self._tabla.bind("<<TreeviewSelect>>", self._al_seleccionar)
        self._cargar_tabla()

        # Botones de acción sobre listado
        bar = tk.Frame(self, bg="#F5F5F5")
        bar.pack(fill=tk.X, padx=10, pady=5)
        boton_primario(bar, "➕ Nuevo", self._abrir_formulario_nuevo).pack(side=tk.LEFT, padx=3)
        boton_secundario(bar, "✏️ Editar", self._abrir_formulario_editar).pack(side=tk.LEFT, padx=3)

    def _cargar_tabla(self):
        for item in self._tabla.get_children():
            self._tabla.delete(item)
        for p in self._servicio.listar():
            self._tabla.insert("", tk.END, iid=p._id, values=(
                p.nombre, p.apellidos, p.dni, p.rol,
                "Sí" if p.activo else "No"
            ))

    def _al_seleccionar(self, _event):
        sel = self._tabla.selection()
        self._seleccionado_id = sel[0] if sel else None

    def _abrir_formulario_nuevo(self):
        _FormularioProfesional(self, self.controlador, self._servicio, None, self._cargar_tabla)

    def _abrir_formulario_editar(self):
        if not self._seleccionado_id:
            self.mostrar_info("Selecciona un profesional primero.")
            return
        profesional = self._servicio.obtener(self._seleccionado_id)
        _FormularioProfesional(self, self.controlador, self._servicio,
                               profesional, self._cargar_tabla)


class _FormularioProfesional(tk.Toplevel):
    def __init__(self, parent, controlador, servicio, profesional: Profesional | None, callback):
        super().__init__(parent)
        self._servicio = servicio
        self._profesional = profesional
        self._callback = callback
        self._es_nuevo = profesional is None
        self.title("Nuevo profesional" if self._es_nuevo else "Editar profesional")
        self.resizable(False, False)
        self.configure(bg="#F5F5F5")
        self._construir()
        self.grab_set()

    def _construir(self):
        form = tk.Frame(self, bg="#F5F5F5")
        form.pack(padx=20, pady=15)

        self._var_nombre = campo_form(form, "Nombre", 0)
        self._var_apellidos = campo_form(form, "Apellidos", 1)
        self._var_dni = campo_form(form, "DNI", 2)
        self._var_rol = campo_form(form, "Rol", 3, valores=Rol.VALORES)
        self._var_contrasena = campo_form(form, "Contraseña", 4, es_password=True)
        self._var_activo = campo_form(form, "Activo", 5, valores=["True", "False"])

        if self._profesional:
            self._var_nombre.set(self._profesional.nombre)
            self._var_apellidos.set(self._profesional.apellidos)
            self._var_dni.set(self._profesional.dni)
            self._var_rol.set(self._profesional.rol)
            self._var_activo.set(str(self._profesional.activo))

        bar = tk.Frame(self, bg="#F5F5F5")
        bar.pack(pady=10)
        boton_primario(bar, "Guardar", self._guardar).pack(side=tk.LEFT, padx=5)
        boton_secundario(bar, "Cancelar", self.destroy).pack(side=tk.LEFT, padx=5)

    def _guardar(self):
        try:
            if self._es_nuevo:
                p = Profesional(
                    nombre=self._var_nombre.get().strip(),
                    apellidos=self._var_apellidos.get().strip(),
                    dni=self._var_dni.get().strip(),
                    rol=self._var_rol.get(),
                    contrasena=self._var_contrasena.get(),
                    activo=True,
                )
                self._servicio.crear(p)
            else:
                datos = {
                    "nombre": self._var_nombre.get().strip(),
                    "apellidos": self._var_apellidos.get().strip(),
                    "rol": self._var_rol.get(),
                    "activo": self._var_activo.get() == "True",
                }
                if self._var_contrasena.get():
                    datos["contrasena"] = self._var_contrasena.get()
                self._servicio.modificar(self._profesional._id, datos)
            self._callback()
            self.destroy()
        except ValueError as e:
            from tkinter import messagebox
            messagebox.showerror("Validación", str(e), parent=self)
