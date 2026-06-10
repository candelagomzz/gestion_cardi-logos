"""Vista de gestión de consultas del Médico."""

import tkinter as tk
from tkinter import ttk
from src.presentacion.vistas.componentes import (
    MarcoBase, crear_tabla, boton_primario, boton_secundario,
    campo_form, COLOR_FONDO, FUENTE_TITULO, FUENTE_NORMAL
)


class VistaConsultasMedico(MarcoBase):
    def __init__(self, parent, controlador, **kwargs):
        super().__init__(parent, controlador)
        self._seleccionado_id = None
        self._todas_las_tablas = []
        self._construir()

    def _construir(self):
        tk.Label(self, text="Mis Consultas", fg="#1565C0",
                 bg=COLOR_FONDO, font=FUENTE_TITULO).pack(
            anchor=tk.W, padx=15, pady=10)

        notebook = ttk.Notebook(self)
        notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)

        cols = [("Día", 100), ("H. Inicio", 75), ("H. Fin", 75),
                ("Estado", 90), ("Paciente", 175), ("Comentario", 180)]

        tab_hoy = tk.Frame(notebook, bg=COLOR_FONDO)
        notebook.add(tab_hoy, text="📅  Hoy")
        self._tabla_hoy = self._tab_simple(
            tab_hoy, cols, self.controlador.listar_mis_consultas_hoy)

        tab_pend = tk.Frame(notebook, bg=COLOR_FONDO)
        notebook.add(tab_pend, text="⏳  Pendientes")
        self._tabla_pend = self._tab_simple(
            tab_pend, cols, self.controlador.listar_mis_consultas_pendientes)

        tab_aten = tk.Frame(notebook, bg=COLOR_FONDO)
        notebook.add(tab_aten, text="✅  Atendidas")
        self._tabla_aten = self._tab_simple(
            tab_aten, cols, self.controlador.listar_mis_consultas_atendidas)

        tab_todas = tk.Frame(notebook, bg=COLOR_FONDO)
        notebook.add(tab_todas, text="📋  Todas")
        self._tabla_todas = self._tab_simple(
            tab_todas, cols, self.controlador.listar_mis_consultas)

        tab_pac = tk.Frame(notebook, bg=COLOR_FONDO)
        notebook.add(tab_pac, text="🔍  Por paciente")
        self._tabla_pac = self._tab_por_paciente(tab_pac, cols)

        self._todas_las_tablas = [
            self._tabla_hoy, self._tabla_pend,
            self._tabla_aten, self._tabla_todas, self._tabla_pac
        ]

        bar = tk.Frame(self, bg=COLOR_FONDO)
        bar.pack(fill=tk.X, padx=10, pady=5)
        boton_primario(bar, "✏️ Gestionar seleccionada",
                       self._abrir_gestion).pack(side=tk.LEFT, padx=3)
        boton_secundario(bar, "🔄 Refrescar todo",
                         self._refrescar_todas).pack(side=tk.LEFT, padx=3)

    def _tab_simple(self, parent, cols, funcion) -> ttk.Treeview:
        tabla = crear_tabla(parent, cols, alto=10)
        tabla.bind("<<TreeviewSelect>>",
                   lambda e, t=tabla: self._al_seleccionar(t))
        self._poblar(tabla, funcion())
        return tabla

    def _tab_por_paciente(self, parent, cols) -> ttk.Treeview:
        pacientes = self.controlador.listar_pacientes_del_medico()
        pac_map = {p.nombre_completo(): p._id for p in pacientes}

        barra = tk.Frame(parent, bg=COLOR_FONDO)
        barra.pack(fill=tk.X, padx=10, pady=8)
        tk.Label(barra, text="Paciente:", bg=COLOR_FONDO,
                 font=FUENTE_NORMAL).pack(side=tk.LEFT, padx=5)
        var = tk.StringVar()
        cb = ttk.Combobox(barra, textvariable=var,
                          values=list(pac_map.keys()),
                          state="readonly", width=38, font=FUENTE_NORMAL)
        cb.pack(side=tk.LEFT, padx=5)

        tabla = crear_tabla(parent, cols, alto=9)
        tabla.bind("<<TreeviewSelect>>",
                   lambda e, t=tabla: self._al_seleccionar(t))

        def buscar():
            pac_id = pac_map.get(var.get())
            if pac_id:
                self._poblar(tabla,
                             self.controlador.listar_consultas_de_paciente(
                                 pac_id))

        boton_primario(barra, "Buscar", buscar).pack(side=tk.LEFT, padx=5)
        return tabla

    def _poblar(self, tabla, consultas):
        for item in tabla.get_children():
            tabla.delete(item)
        for c in consultas:
            nombre_pac = ""
            if c.paciente_id:
                pac = self.controlador.obtener_paciente(c.paciente_id)
                nombre_pac = pac.nombre_completo() if pac else ""
            tabla.insert("", tk.END, iid=c._id, values=(
                c.dia, c.hora_inicio, c.hora_fin,
                c.estado, nombre_pac, c.comentario or ""
            ))

    def _al_seleccionar(self, tabla_origen):
        sel = tabla_origen.selection()
        self._seleccionado_id = sel[0] if sel else None
        for t in self._todas_las_tablas:
            if t is not tabla_origen:
                t.selection_remove(*t.selection())

    def _refrescar_todas(self):
        self._poblar(self._tabla_hoy,
                     self.controlador.listar_mis_consultas_hoy())
        self._poblar(self._tabla_pend,
                     self.controlador.listar_mis_consultas_pendientes())
        self._poblar(self._tabla_aten,
                     self.controlador.listar_mis_consultas_atendidas())
        self._poblar(self._tabla_todas,
                     self.controlador.listar_mis_consultas())

    def _abrir_gestion(self):
        if not self._seleccionado_id:
            self.mostrar_info("Selecciona una consulta.")
            return
        consulta = self.controlador.obtener_consulta(self._seleccionado_id)
        _FormularioMedicoConsulta(
            self, self.controlador, consulta, self._refrescar_todas)


class _FormularioMedicoConsulta(tk.Toplevel):
    def __init__(self, parent, controlador, consulta, callback):
        super().__init__(parent)
        self._ctrl = controlador
        self._consulta = consulta
        self._callback = callback
        self.title("Gestionar consulta (médico)")
        self.resizable(False, False)
        self.configure(bg=COLOR_FONDO)
        self._construir()
        self.grab_set()

    def _construir(self):
        c = self._consulta
        nombre_pac = "—"
        if c.paciente_id:
            pac = self._ctrl.obtener_paciente(c.paciente_id)
            nombre_pac = pac.nombre_completo() if pac else c.paciente_id

        info = tk.Frame(self, bg="#E3F2FD", bd=1, relief=tk.SUNKEN)
        info.pack(fill=tk.X, padx=15, pady=10)
        for texto in [
            f"Día: {c.dia}   Hora: {c.hora_inicio} – {c.hora_fin}",
            f"Estado: {c.estado}   Paciente: {nombre_pac}",
        ]:
            tk.Label(info, text=texto, bg="#E3F2FD",
                     font=FUENTE_NORMAL).pack(anchor=tk.W, padx=10, pady=2)

        form = tk.Frame(self, bg=COLOR_FONDO)
        form.pack(padx=20, pady=5)

        # Estados desde el controlador
        self._var_estado = campo_form(
            form, "Nuevo estado", 0,
            valores=self._ctrl.estados_consulta_medico())
        if c.estado in self._ctrl.estados_consulta_medico():
            self._var_estado.set(c.estado)

        tk.Label(form, text="Comentario:", bg=COLOR_FONDO,
                 font=FUENTE_NORMAL).grid(
            row=1, column=0, sticky=tk.NW, padx=10, pady=5)
        self._txt_comentario = tk.Text(form, width=38, height=5,
                                        font=FUENTE_NORMAL)
        self._txt_comentario.grid(row=1, column=1, padx=10, pady=5)
        if c.comentario:
            self._txt_comentario.insert("1.0", c.comentario)

        bar = tk.Frame(self, bg=COLOR_FONDO)
        bar.pack(pady=10)
        boton_primario(bar, "Guardar", self._guardar).pack(
            side=tk.LEFT, padx=5)
        boton_secundario(bar, "Cancelar", self.destroy).pack(
            side=tk.LEFT, padx=5)

    def _guardar(self):
        from tkinter import messagebox
        try:
            nuevo_estado = self._var_estado.get()
            if nuevo_estado:
                self._ctrl.actualizar_estado_consulta_medico(
                    self._consulta._id, nuevo_estado)
            comentario = self._txt_comentario.get("1.0", tk.END).strip()
            if comentario:
                self._ctrl.actualizar_comentario_consulta(
                    self._consulta._id, comentario)
            self._callback()
            self.destroy()
        except ValueError as e:
            messagebox.showerror("Validación", str(e), parent=self)
