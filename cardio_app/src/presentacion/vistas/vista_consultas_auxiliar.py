"""Vista de gestión administrativa de consultas (Auxiliar).
IMPORTANTE: el auxiliar NO tiene acceso al campo Comentario en ninguna operación.
"""

import tkinter as tk
from tkinter import ttk
from src.presentacion.vistas.componentes import (
    MarcoBase, crear_tabla, boton_primario, boton_secundario,
    etiqueta_seccion, campo_form, COLOR_FONDO, FUENTE_TITULO,
    FUENTE_NORMAL, FUENTE_SUBTITULO, COLOR_PRIMARIO
)
from src.datos.modelos.entidades import EstadoConsulta


class VistaConsultasAuxiliar(MarcoBase):
    def __init__(self, parent, controlador, **kwargs):
        super().__init__(parent, controlador)
        self._servicio = controlador.servicios["consultas"]
        self._servicio_pac = controlador.servicios["pacientes"]
        self._seleccionado_id = None
        self._construir()

    def _construir(self):
        tk.Label(self, text="Gestión de Consultas", fg=COLOR_PRIMARIO,
                 bg=COLOR_FONDO, font=FUENTE_TITULO).pack(anchor=tk.W, padx=15, pady=10)

        etiqueta_seccion(self, "Listado de consultas")

        # NOTA: columna Comentario excluida intencionadamente (RF enunciado)
        cols = [
            ("Día", 100), ("H. Inicio", 80), ("H. Fin", 80),
            ("Médico DNI", 110), ("Estado", 90), ("Paciente", 170)
        ]
        self._tabla = crear_tabla(self, cols, alto=13)
        self._tabla.bind("<<TreeviewSelect>>", lambda e: self._al_seleccionar())
        self._cargar_tabla()

        bar = tk.Frame(self, bg=COLOR_FONDO)
        bar.pack(fill=tk.X, padx=10, pady=5)
        boton_secundario(bar, "🔄 Refrescar", self._cargar_tabla).pack(side=tk.LEFT, padx=3)
        boton_primario(bar, "✏️ Gestionar consulta", self._abrir_gestion).pack(
            side=tk.LEFT, padx=3)

    def _cargar_tabla(self):
        for item in self._tabla.get_children():
            self._tabla.delete(item)
        for c in self._servicio.listar_todas():
            nombre_pac = ""
            if c.paciente_id:
                pac = self._servicio_pac.obtener(c.paciente_id)
                nombre_pac = pac.nombre_completo() if pac else c.paciente_id
            # comentario deliberadamente omitido
            self._tabla.insert("", tk.END, iid=c._id, values=(
                c.dia, c.hora_inicio, c.hora_fin,
                c.medico_dni, c.estado, nombre_pac
            ))

    def _al_seleccionar(self):
        sel = self._tabla.selection()
        self._seleccionado_id = sel[0] if sel else None

    def _abrir_gestion(self):
        if not self._seleccionado_id:
            self.mostrar_info("Selecciona una consulta.")
            return
        consulta = self._servicio.obtener(self._seleccionado_id)
        _FormularioGestionConsulta(
            self, self._servicio, self._servicio_pac,
            consulta, self._cargar_tabla
        )


class _FormularioGestionConsulta(tk.Toplevel):
    """
    Formulario de gestión para Auxiliar.
    No muestra ni permite editar el campo Comentario.
    Permite dar de alta un paciente nuevo desde aquí si no existe.
    """

    def __init__(self, parent, servicio, servicio_pac, consulta, callback):
        super().__init__(parent)
        self._servicio = servicio
        self._servicio_pac = servicio_pac
        self._consulta = consulta
        self._callback = callback
        self.title("Gestionar consulta")
        self.resizable(False, False)
        self.configure(bg="#F5F5F5")
        self._construir()
        self.grab_set()

    def _construir(self):
        # ── Info de la consulta (solo lectura, sin comentario) ─────────────
        info = tk.Frame(self, bg="#E3F2FD", bd=1, relief=tk.SUNKEN)
        info.pack(fill=tk.X, padx=15, pady=10)
        c = self._consulta
        for texto in [
            f"Día: {c.dia}   Hora: {c.hora_inicio} – {c.hora_fin}",
            f"Médico: {c.medico_dni}   Estado actual: {c.estado}",
        ]:
            tk.Label(info, text=texto, bg="#E3F2FD",
                     font=FUENTE_NORMAL).pack(anchor=tk.W, padx=10, pady=2)

        # ── Nuevo estado ───────────────────────────────────────────────────
        form = tk.Frame(self, bg="#F5F5F5")
        form.pack(padx=20, pady=5, fill=tk.X)

        estados = [EstadoConsulta.LIBRE, EstadoConsulta.OCUPADA,
                   EstadoConsulta.CANCELADA, EstadoConsulta.ELIMINADA]
        self._var_estado = campo_form(form, "Nuevo estado", 0, valores=estados)
        self._var_estado.set(c.estado)
        self._var_estado.trace_add("write", self._al_cambiar_estado)

        # ── Selección de paciente (visible solo si estado = ocupada) ───────
        self._frame_pac = tk.Frame(self, bg="#F5F5F5")
        self._frame_pac.pack(padx=20, fill=tk.X)

        tk.Label(self._frame_pac, text="Paciente:", bg="#F5F5F5",
                 font=FUENTE_NORMAL).grid(row=0, column=0, sticky=tk.W, padx=10, pady=4)

        pacientes = self._servicio_pac.listar()
        self._pac_map = {
            f"{p.nombre_completo()}": p._id for p in pacientes if p.activo
        }
        self._var_paciente = tk.StringVar()
        self._cb_paciente = ttk.Combobox(
            self._frame_pac, textvariable=self._var_paciente,
            values=list(self._pac_map.keys()),
            state="readonly", width=35, font=FUENTE_NORMAL
        )
        self._cb_paciente.grid(row=0, column=1, padx=5, pady=4, sticky=tk.W)

        # Preseleccionar paciente actual si existe
        if c.paciente_id:
            pac = self._servicio_pac.obtener(c.paciente_id)
            if pac:
                self._var_paciente.set(pac.nombre_completo())

        # Botón para dar de alta paciente nuevo desde aquí
        boton_secundario(
            self._frame_pac, "➕ Nuevo paciente",
            self._alta_paciente_rapida
        ).grid(row=0, column=2, padx=8, pady=4)

        # Mostrar/ocultar frame paciente según estado inicial
        self._al_cambiar_estado()

        # ── Botones ────────────────────────────────────────────────────────
        bar = tk.Frame(self, bg="#F5F5F5")
        bar.pack(pady=12)
        boton_primario(bar, "Guardar", self._guardar).pack(side=tk.LEFT, padx=5)
        boton_secundario(bar, "Cancelar", self.destroy).pack(side=tk.LEFT, padx=5)

    def _al_cambiar_estado(self, *_):
        """Muestra el selector de paciente solo cuando el estado es 'ocupada'."""
        if self._var_estado.get() == EstadoConsulta.OCUPADA:
            self._frame_pac.pack(padx=20, fill=tk.X)
        else:
            self._frame_pac.pack_forget()

    def _alta_paciente_rapida(self):
        """Abre formulario de alta de paciente. Al guardar, refresca el combo."""
        from src.presentacion.vistas.vista_pacientes import _FormularioPaciente

        def _tras_alta():
            # Recargar pacientes en el combobox
            pacientes = self._servicio_pac.listar()
            self._pac_map = {
                f"{p.nombre_completo()}": p._id for p in pacientes if p.activo
            }
            self._cb_paciente["values"] = list(self._pac_map.keys())

        _FormularioPaciente(self, self._servicio_pac, None, _tras_alta)

    def _guardar(self):
        from tkinter import messagebox
        nuevo_estado = self._var_estado.get()
        try:
            if nuevo_estado == EstadoConsulta.OCUPADA:
                nombre_pac = self._var_paciente.get()
                pac_id = self._pac_map.get(nombre_pac, "")
                if not pac_id:
                    messagebox.showerror("Error",
                                         "Selecciona o da de alta un paciente.",
                                         parent=self)
                    return
                self._servicio.asignar_paciente(self._consulta._id, pac_id)
            else:
                self._servicio.modificar_estado_auxiliar(
                    self._consulta._id, nuevo_estado)
            self._callback()
            self.destroy()
        except ValueError as e:
            messagebox.showerror("Validación", str(e), parent=self)
