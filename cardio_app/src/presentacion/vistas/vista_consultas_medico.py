"""Vista de gestión de consultas del Médico."""

import tkinter as tk
from tkinter import ttk
from src.presentacion.vistas.componentes import (
    MarcoBase, crear_tabla, boton_primario, boton_secundario,
    etiqueta_seccion, campo_form, COLOR_FONDO, FUENTE_TITULO,
    FUENTE_NORMAL, FUENTE_SUBTITULO, COLOR_PRIMARIO
)
from src.datos.modelos.entidades import EstadoConsulta


class VistaConsultasMedico(MarcoBase):
    def __init__(self, parent, controlador, **kwargs):
        super().__init__(parent, controlador)
        self._servicio = controlador.servicios["consultas"]
        self._servicio_pac = controlador.servicios["pacientes"]
        self._medico_dni = controlador.usuario_actual.dni
        self._seleccionado_id = None
        self._tabla_activa = None
        self._construir()

    def _construir(self):
        tk.Label(self, text="Mis Consultas", fg=COLOR_PRIMARIO,
                 bg=COLOR_FONDO, font=FUENTE_TITULO).pack(anchor=tk.W, padx=15, pady=10)

        notebook = ttk.Notebook(self)
        notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)

        cols = [("Día", 100), ("H. Inicio", 80), ("H. Fin", 75),
                ("Estado", 90), ("Paciente", 180), ("Comentario", 200)]

        # ── Pestaña: Hoy ──────────────────────────────────────────────────
        tab_hoy = tk.Frame(notebook, bg=COLOR_FONDO)
        notebook.add(tab_hoy, text="📅  Hoy")
        self._tabla_hoy = self._crear_tab_simple(
            tab_hoy, cols, self._servicio.listar_consultas_hoy)

        # ── Pestaña: Pendientes ───────────────────────────────────────────
        tab_pend = tk.Frame(notebook, bg=COLOR_FONDO)
        notebook.add(tab_pend, text="⏳  Pendientes")
        self._tabla_pend = self._crear_tab_simple(
            tab_pend, cols, self._servicio.listar_pendientes)

        # ── Pestaña: Atendidas ────────────────────────────────────────────
        tab_aten = tk.Frame(notebook, bg=COLOR_FONDO)
        notebook.add(tab_aten, text="✅  Atendidas")
        self._tabla_aten = self._crear_tab_simple(
            tab_aten, cols, self._servicio.listar_atendidas_por_medico)

        # ── Pestaña: Todas ────────────────────────────────────────────────
        tab_todas = tk.Frame(notebook, bg=COLOR_FONDO)
        notebook.add(tab_todas, text="📋  Todas")
        self._tabla_todas = self._crear_tab_simple(
            tab_todas, cols, self._servicio.listar_por_medico)

        # ── Pestaña: Por paciente (RF específico del enunciado) ───────────
        tab_pac = tk.Frame(notebook, bg=COLOR_FONDO)
        notebook.add(tab_pac, text="🔍  Por paciente")
        self._tabla_pac, self._var_busq_pac, self._pac_busq_map = \
            self._crear_tab_por_paciente(tab_pac, cols)

        self._notebook = notebook
        self._todas_las_tablas = [
            self._tabla_hoy, self._tabla_pend,
            self._tabla_aten, self._tabla_todas, self._tabla_pac
        ]

        # ── Botones globales ──────────────────────────────────────────────
        bar = tk.Frame(self, bg=COLOR_FONDO)
        bar.pack(fill=tk.X, padx=10, pady=5)
        boton_primario(bar, "✏️ Gestionar seleccionada",
                       self._abrir_gestion).pack(side=tk.LEFT, padx=3)
        boton_secundario(bar, "🔄 Refrescar todo",
                         self._refrescar_todas).pack(side=tk.LEFT, padx=3)

    # ── Helpers de construcción ───────────────────────────────────────────

    def _crear_tab_simple(self, parent, cols, funcion_datos) -> ttk.Treeview:
        tabla = crear_tabla(parent, cols, alto=10)
        tabla.bind("<<TreeviewSelect>>",
                   lambda e, t=tabla: self._al_seleccionar(t))
        self._cargar_en_tabla(tabla, funcion_datos)
        return tabla

    def _crear_tab_por_paciente(self, parent, cols):
        """Pestaña especial con selector de paciente y búsqueda."""
        # Obtener pacientes que tienen consultas con este médico
        consultas = self._servicio.listar_por_medico(self._medico_dni)
        pac_ids = list({c.paciente_id for c in consultas if c.paciente_id})
        pacientes = [self._servicio_pac.obtener(pid) for pid in pac_ids]
        pacientes = [p for p in pacientes if p]
        pac_map = {p.nombre_completo(): p._id for p in pacientes}

        barra = tk.Frame(parent, bg=COLOR_FONDO)
        barra.pack(fill=tk.X, padx=10, pady=8)

        tk.Label(barra, text="Paciente:", bg=COLOR_FONDO,
                 font=FUENTE_NORMAL).pack(side=tk.LEFT, padx=5)
        var = tk.StringVar()
        cb = ttk.Combobox(barra, textvariable=var, values=list(pac_map.keys()),
                          state="readonly", width=38, font=FUENTE_NORMAL)
        cb.pack(side=tk.LEFT, padx=5)

        tabla = crear_tabla(parent, cols, alto=9)
        tabla.bind("<<TreeviewSelect>>",
                   lambda e, t=tabla: self._al_seleccionar(t))

        def buscar():
            nombre = var.get()
            pac_id = pac_map.get(nombre)
            if not pac_id:
                return
            for item in tabla.get_children():
                tabla.delete(item)
            for c in self._servicio.listar_consultas_paciente_de_medico(
                self._medico_dni, pac_id
            ):
                tabla.insert("", tk.END, iid=c._id,
                             values=self._fila_consulta(c))

        boton_primario(barra, "Buscar", buscar).pack(side=tk.LEFT, padx=5)
        return tabla, var, pac_map

    # ── Carga de datos ────────────────────────────────────────────────────

    def _cargar_en_tabla(self, tabla, funcion):
        for item in tabla.get_children():
            tabla.delete(item)
        for c in funcion(self._medico_dni):
            tabla.insert("", tk.END, iid=c._id,
                         values=self._fila_consulta(c))

    def _fila_consulta(self, c) -> tuple:
        nombre_pac = ""
        if c.paciente_id:
            pac = self._servicio_pac.obtener(c.paciente_id)
            nombre_pac = pac.nombre_completo() if pac else c.paciente_id
        return (c.dia, c.hora_inicio, c.hora_fin,
                c.estado, nombre_pac, c.comentario or "")

    def _al_seleccionar(self, tabla_origen):
        sel = tabla_origen.selection()
        self._seleccionado_id = sel[0] if sel else None
        # Deseleccionar el resto de tablas
        for t in self._todas_las_tablas:
            if t is not tabla_origen:
                t.selection_remove(*t.selection())

    def _refrescar_todas(self):
        self._cargar_en_tabla(self._tabla_hoy,
                               self._servicio.listar_consultas_hoy)
        self._cargar_en_tabla(self._tabla_pend,
                               self._servicio.listar_pendientes)
        self._cargar_en_tabla(self._tabla_aten,
                               self._servicio.listar_atendidas_por_medico)
        self._cargar_en_tabla(self._tabla_todas,
                               self._servicio.listar_por_medico)

    # ── Gestión de consulta ───────────────────────────────────────────────

    def _abrir_gestion(self):
        if not self._seleccionado_id:
            self.mostrar_info("Selecciona una consulta.")
            return
        consulta = self._servicio.obtener(self._seleccionado_id)
        _FormularioMedicoConsulta(
            self, self._servicio, self._servicio_pac,
            consulta, self._refrescar_todas
        )


class _FormularioMedicoConsulta(tk.Toplevel):
    def __init__(self, parent, servicio, servicio_pac, consulta, callback):
        super().__init__(parent)
        self._servicio = servicio
        self._servicio_pac = servicio_pac
        self._consulta = consulta
        self._callback = callback
        self.title("Gestionar consulta (médico)")
        self.resizable(False, False)
        self.configure(bg="#F5F5F5")
        self._construir()
        self.grab_set()

    def _construir(self):
        c = self._consulta
        nombre_pac = "—"
        if c.paciente_id:
            pac = self._servicio_pac.obtener(c.paciente_id)
            nombre_pac = pac.nombre_completo() if pac else c.paciente_id

        info = tk.Frame(self, bg="#E3F2FD", bd=1, relief=tk.SUNKEN)
        info.pack(fill=tk.X, padx=15, pady=10)
        for texto in [
            f"Día: {c.dia}   Hora: {c.hora_inicio} – {c.hora_fin}",
            f"Estado actual: {c.estado}",
            f"Paciente: {nombre_pac}",
        ]:
            tk.Label(info, text=texto, bg="#E3F2FD",
                     font=FUENTE_NORMAL).pack(anchor=tk.W, padx=10, pady=2)

        form = tk.Frame(self, bg="#F5F5F5")
        form.pack(padx=20, pady=5)

        self._var_estado = campo_form(
            form, "Nuevo estado", 0,
            valores=[EstadoConsulta.ATENDIDA, EstadoConsulta.CANCELADA]
        )
        if c.estado in (EstadoConsulta.ATENDIDA, EstadoConsulta.CANCELADA):
            self._var_estado.set(c.estado)

        tk.Label(form, text="Comentario:", bg="#F5F5F5",
                 font=FUENTE_NORMAL).grid(row=1, column=0, sticky=tk.NW,
                                           padx=10, pady=5)
        self._txt_comentario = tk.Text(form, width=38, height=5,
                                        font=FUENTE_NORMAL)
        self._txt_comentario.grid(row=1, column=1, padx=10, pady=5)
        if c.comentario:
            self._txt_comentario.insert("1.0", c.comentario)

        bar = tk.Frame(self, bg="#F5F5F5")
        bar.pack(pady=10)
        boton_primario(bar, "Guardar", self._guardar).pack(side=tk.LEFT, padx=5)
        boton_secundario(bar, "Cancelar", self.destroy).pack(side=tk.LEFT, padx=5)

    def _guardar(self):
        from tkinter import messagebox
        try:
            nuevo_estado = self._var_estado.get()
            if nuevo_estado:
                self._servicio.actualizar_estado_medico(
                    self._consulta._id, nuevo_estado)
            comentario = self._txt_comentario.get("1.0", tk.END).strip()
            if comentario:
                self._servicio.actualizar_comentario(
                    self._consulta._id, comentario)
            self._callback()
            self.destroy()
        except ValueError as e:
            messagebox.showerror("Validación", str(e), parent=self)
