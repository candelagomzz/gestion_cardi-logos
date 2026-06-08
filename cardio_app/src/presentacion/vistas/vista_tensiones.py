"""Vista de gestión de tensiones arteriales (Médico)."""

import tkinter as tk
from tkinter import ttk
from src.presentacion.vistas.componentes import (
    MarcoBase, crear_tabla, boton_primario, boton_secundario,
    etiqueta_seccion, campo_form, COLOR_FONDO, FUENTE_TITULO,
    FUENTE_NORMAL, FUENTE_SUBTITULO, COLOR_PRIMARIO
)
from src.datos.modelos.entidades import (
    TomaTension, MetodoTension, SitioCuerpo, TamanoBrazalete,
    EstadoObservacionFHIR
)


class VistaTensiones(MarcoBase):
    def __init__(self, parent, controlador, **kwargs):
        super().__init__(parent, controlador)
        self._servicio = controlador.servicios["tensiones"]
        self._servicio_pac = controlador.servicios["pacientes"]
        self._servicio_consultas = controlador.servicios["consultas"]
        self._medico_dni = controlador.usuario_actual.dni
        self._paciente_sel_id = None
        self._toma_sel_id = None
        self._construir()

    def _construir(self):
        tk.Label(self, text="Tensiones Arteriales de Pacientes", fg=COLOR_PRIMARIO,
                 bg=COLOR_FONDO, font=FUENTE_TITULO).pack(anchor=tk.W, padx=15, pady=10)

        # ── Selección de paciente ──────────────────────────────────────────
        panel_pac = tk.LabelFrame(self, text="Paciente", bg=COLOR_FONDO,
                                  font=FUENTE_SUBTITULO, padx=10, pady=5)
        panel_pac.pack(fill=tk.X, padx=15, pady=5)

        consultas = self._servicio_consultas.listar_por_medico(self._medico_dni)
        pac_ids = list({c.paciente_id for c in consultas if c.paciente_id})
        pacientes = [self._servicio_pac.obtener(pid) for pid in pac_ids]
        pacientes = [p for p in pacientes if p]
        self._pac_map = {
            f"{p.nombre_completo()} ({p._id[:8]}…)": p._id for p in pacientes
        }

        self._var_paciente = tk.StringVar()
        cb = ttk.Combobox(panel_pac, textvariable=self._var_paciente,
                          values=list(self._pac_map.keys()),
                          state="readonly", width=42, font=FUENTE_NORMAL)
        cb.pack(side=tk.LEFT, padx=5)
        boton_primario(panel_pac, "Ver tensiones", self._cargar_tensiones).pack(
            side=tk.LEFT, padx=5)

        # ── Filtros (4 campos del enunciado) ──────────────────────────────
        panel_filtros = tk.LabelFrame(self, text="Filtros", bg=COLOR_FONDO,
                                      font=FUENTE_SUBTITULO, padx=10, pady=5)
        panel_filtros.pack(fill=tk.X, padx=15, pady=3)

        self._var_f_metodo = campo_form(
            panel_filtros, "Método", 0, valores=[""] + MetodoTension.VALORES)
        self._var_f_sitio = campo_form(
            panel_filtros, "Sitio cuerpo", 1, valores=[""] + SitioCuerpo.VALORES)
        self._var_f_brazalete = campo_form(
            panel_filtros, "Brazalete", 0,
            valores=[""] + TamanoBrazalete.VALORES)
        # Recolocamos brazalete y dispositivo en columnas 2-3
        panel_filtros.grid_slaves(row=0, column=0)[0].grid(
            row=0, column=0, padx=5, pady=3, sticky=tk.W)

        # Reconstruimos el grid de filtros manualmente para 4 columnas
        for w in panel_filtros.winfo_children():
            w.destroy()

        etiquetas = ["Método", "Sitio cuerpo", "Brazalete", "Dispositivo"]
        valores_listas = [
            [""] + MetodoTension.VALORES,
            [""] + SitioCuerpo.VALORES,
            [""] + TamanoBrazalete.VALORES,
            [],   # dispositivo: texto libre
        ]
        self._vars_filtro = []
        for col, (etq, vals) in enumerate(zip(etiquetas, valores_listas)):
            tk.Label(panel_filtros, text=etq + ":", bg=COLOR_FONDO,
                     font=FUENTE_NORMAL).grid(row=0, column=col * 2, padx=(10, 2), pady=4, sticky=tk.W)
            var = tk.StringVar()
            if vals:
                w = ttk.Combobox(panel_filtros, textvariable=var, values=vals,
                                 state="readonly", width=16, font=FUENTE_NORMAL)
            else:
                w = tk.Entry(panel_filtros, textvariable=var, width=18, font=FUENTE_NORMAL)
            w.grid(row=0, column=col * 2 + 1, padx=(0, 8), pady=4, sticky=tk.W)
            self._vars_filtro.append(var)

        boton_secundario(panel_filtros, "Aplicar filtros",
                         self._aplicar_filtros).grid(row=1, column=0, columnspan=4,
                                                      padx=10, pady=4, sticky=tk.W)
        boton_secundario(panel_filtros, "Limpiar filtros",
                         self._limpiar_filtros).grid(row=1, column=4, columnspan=4,
                                                      padx=2, pady=4, sticky=tk.W)

        # ── Media de tensiones ────────────────────────────────────────────
        panel_media = tk.LabelFrame(self, text="Media de tensiones", bg=COLOR_FONDO,
                                    font=FUENTE_SUBTITULO, padx=10, pady=5)
        panel_media.pack(fill=tk.X, padx=15, pady=3)

        tk.Label(panel_media, text="Últimas N tomas (vacío = todas):",
                 bg=COLOR_FONDO, font=FUENTE_NORMAL).pack(side=tk.LEFT, padx=5)
        self._var_n = tk.StringVar()
        tk.Entry(panel_media, textvariable=self._var_n, width=6,
                 font=FUENTE_NORMAL).pack(side=tk.LEFT, padx=5)
        boton_secundario(panel_media, "Calcular media",
                         self._calcular_media).pack(side=tk.LEFT, padx=8)
        self._lbl_media = tk.Label(panel_media, text="", bg=COLOR_FONDO,
                                   font=FUENTE_SUBTITULO, fg=COLOR_PRIMARIO)
        self._lbl_media.pack(side=tk.LEFT, padx=10)

        # ── Tabla de tomas ────────────────────────────────────────────────
        etiqueta_seccion(self, "Tomas registradas")
        cols = [
            ("Fecha", 100), ("Sistólica", 85), ("Diastólica", 85),
            ("Método", 120), ("Sitio", 130), ("Brazalete", 100),
            ("Dispositivo", 140), ("En rango", 75), ("Estado", 90)
        ]
        self._tabla = crear_tabla(self, cols, alto=8)
        self._tabla.bind("<<TreeviewSelect>>", lambda e: self._al_seleccionar())

        # ── Botones de acción ─────────────────────────────────────────────
        bar = tk.Frame(self, bg=COLOR_FONDO)
        bar.pack(fill=tk.X, padx=10, pady=5)
        boton_primario(bar, "➕ Registrar toma", self._abrir_nueva_toma).pack(
            side=tk.LEFT, padx=3)
        boton_secundario(bar, "✏️ Editar toma", self._abrir_editar_toma).pack(
            side=tk.LEFT, padx=3)

    # ── Helpers ───────────────────────────────────────────────────────────

    def _get_paciente_id(self):
        return self._pac_map.get(self._var_paciente.get())

    def _cargar_tensiones(self):
        pac_id = self._get_paciente_id()
        if not pac_id:
            self.mostrar_info("Selecciona un paciente.")
            return
        self._poblar_tabla(self._servicio.listar_por_paciente(pac_id))

    def _aplicar_filtros(self):
        pac_id = self._get_paciente_id()
        if not pac_id:
            self.mostrar_info("Selecciona un paciente primero.")
            return
        metodo, sitio, brazalete, dispositivo = [v.get() or None
                                                  for v in self._vars_filtro]
        tomas = self._servicio.filtrar(
            pac_id,
            metodo=metodo,
            sitio_cuerpo=sitio,
            tamano_brazalete=brazalete,
            dispositivo=dispositivo,
        )
        self._poblar_tabla(tomas)

    def _limpiar_filtros(self):
        for v in self._vars_filtro:
            v.set("")

    def _calcular_media(self):
        pac_id = self._get_paciente_id()
        if not pac_id:
            self.mostrar_info("Selecciona un paciente primero.")
            return
        n_str = self._var_n.get().strip()
        n = None
        if n_str:
            try:
                n = int(n_str)
                if n <= 0:
                    raise ValueError
            except ValueError:
                self.mostrar_error("N debe ser un número entero positivo.")
                return
        media = self._servicio.media_tensiones(pac_id, ultimas_n=n)
        if media["total"] == 0:
            self._lbl_media.config(text="Sin tomas registradas.")
        else:
            scope = f"últimas {n}" if n else "todas"
            self._lbl_media.config(
                text=(f"({scope} · {media['total']} tomas)  "
                      f"Sistólica: {media['sistolica']} mmHg  |  "
                      f"Diastólica: {media['diastolica']} mmHg")
            )

    def _poblar_tabla(self, tomas):
        for item in self._tabla.get_children():
            self._tabla.delete(item)
        for t in tomas:
            self._tabla.insert("", tk.END, iid=t._id, values=(
                t.fecha, t.sistolica, t.diastolica,
                t.metodo, t.sitio_cuerpo, t.tamano_brazalete,
                t.dispositivo, "✓" if t.en_rango else "✗", t.estado
            ))

    def _al_seleccionar(self):
        sel = self._tabla.selection()
        self._toma_sel_id = sel[0] if sel else None

    def _abrir_nueva_toma(self):
        pac_id = self._get_paciente_id()
        if not pac_id:
            self.mostrar_info("Selecciona un paciente primero.")
            return
        _FormularioToma(self, self._servicio, pac_id, None, self._cargar_tensiones)

    def _abrir_editar_toma(self):
        if not self._toma_sel_id:
            self.mostrar_info("Selecciona una toma.")
            return
        toma = self._servicio.obtener(self._toma_sel_id)
        _FormularioToma(self, self._servicio, toma.paciente_id,
                        toma, self._cargar_tensiones)


class _FormularioToma(tk.Toplevel):
    def __init__(self, parent, servicio, paciente_id, toma, callback):
        super().__init__(parent)
        self._servicio = servicio
        self._paciente_id = paciente_id
        self._toma = toma
        self._es_nuevo = toma is None
        self._callback = callback
        self.title("Registrar toma" if self._es_nuevo else "Editar toma")
        self.resizable(False, False)
        self.configure(bg="#F5F5F5")
        self._construir()
        self.grab_set()

    def _construir(self):
        form = tk.Frame(self, bg="#F5F5F5")
        form.pack(padx=20, pady=10)

        self._var_fecha = campo_form(form, "Fecha (YYYY-MM-DD)", 0)
        self._var_sistolica = campo_form(form, "Sistólica (mmHg)", 1)
        self._var_diastolica = campo_form(form, "Diastólica (mmHg)", 2)
        self._var_metodo = campo_form(form, "Método", 3,
                                      valores=MetodoTension.VALORES)
        self._var_sitio = campo_form(form, "Sitio cuerpo", 4,
                                     valores=SitioCuerpo.VALORES)
        self._var_brazalete = campo_form(form, "Brazalete", 5,
                                         valores=TamanoBrazalete.VALORES)
        self._var_dispositivo = campo_form(form, "Dispositivo", 6)
        self._var_estado = campo_form(form, "Estado (FHIR)", 7,
                                      valores=EstadoObservacionFHIR.VALORES)
        self._var_descripcion = campo_form(form, "Descripción", 8)

        if self._toma:
            t = self._toma
            self._var_fecha.set(t.fecha)
            self._var_sistolica.set(str(t.sistolica))
            self._var_diastolica.set(str(t.diastolica))
            self._var_metodo.set(t.metodo)
            self._var_sitio.set(t.sitio_cuerpo)
            self._var_brazalete.set(t.tamano_brazalete)
            self._var_dispositivo.set(t.dispositivo)
            self._var_estado.set(t.estado)
            self._var_descripcion.set(t.descripcion or "")

        bar = tk.Frame(self, bg="#F5F5F5")
        bar.pack(pady=10)
        boton_primario(bar, "Guardar", self._guardar).pack(side=tk.LEFT, padx=5)
        boton_secundario(bar, "Cancelar", self.destroy).pack(side=tk.LEFT, padx=5)

    def _guardar(self):
        from tkinter import messagebox
        try:
            sistolica = int(self._var_sistolica.get())
            diastolica = int(self._var_diastolica.get())
        except ValueError:
            messagebox.showerror("Error",
                                 "Sistólica y diastólica deben ser enteros.", parent=self)
            return
        try:
            if self._es_nuevo:
                toma = TomaTension(
                    paciente_id=self._paciente_id,
                    fecha=self._var_fecha.get().strip(),
                    sistolica=sistolica,
                    diastolica=diastolica,
                    metodo=self._var_metodo.get(),
                    sitio_cuerpo=self._var_sitio.get(),
                    tamano_brazalete=self._var_brazalete.get(),
                    dispositivo=self._var_dispositivo.get().strip(),
                    estado=self._var_estado.get(),
                    descripcion=self._var_descripcion.get().strip() or None,
                )
                self._servicio.registrar(toma)
            else:
                datos = {
                    "fecha": self._var_fecha.get().strip(),
                    "sistolica": sistolica,
                    "diastolica": diastolica,
                    "metodo": self._var_metodo.get(),
                    "sitio_cuerpo": self._var_sitio.get(),
                    "tamano_brazalete": self._var_brazalete.get(),
                    "dispositivo": self._var_dispositivo.get().strip(),
                    "estado": self._var_estado.get(),
                    "descripcion": self._var_descripcion.get().strip() or None,
                }
                self._servicio.modificar(self._toma._id, datos)
            self._callback()
            self.destroy()
        except ValueError as e:
            messagebox.showerror("Validación", str(e), parent=self)
