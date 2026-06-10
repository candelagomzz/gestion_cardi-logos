"""Vista de gestión de tensiones arteriales (Médico)."""

import tkinter as tk
from tkinter import ttk
from src.presentacion.vistas.componentes import (
    MarcoBase, crear_tabla, boton_primario, boton_secundario,
    etiqueta_seccion, campo_form, COLOR_FONDO, FUENTE_TITULO,
    FUENTE_NORMAL, FUENTE_SUBTITULO, COLOR_PRIMARIO
)


class VistaTensiones(MarcoBase):
    def __init__(self, parent, controlador, **kwargs):
        super().__init__(parent, controlador)
        self._toma_sel_id = None
        self._pac_map = {}
        self._construir()

    def _construir(self):
        tk.Label(self, text="Tensiones Arteriales de Pacientes",
                 fg=COLOR_PRIMARIO, bg=COLOR_FONDO,
                 font=FUENTE_TITULO).pack(anchor=tk.W, padx=15, pady=10)

        # ── Selección de paciente ────────────────────────────────────────
        panel_pac = tk.LabelFrame(self, text="Paciente", bg=COLOR_FONDO,
                                   font=FUENTE_SUBTITULO, padx=10, pady=5)
        panel_pac.pack(fill=tk.X, padx=15, pady=5)

        pacientes = self.controlador.listar_pacientes_del_medico()
        self._pac_map = {
            f"{p.nombre_completo()} ({p._id[:8]}…)": p._id
            for p in pacientes
        }
        self._var_paciente = tk.StringVar()
        ttk.Combobox(panel_pac, textvariable=self._var_paciente,
                     values=list(self._pac_map.keys()),
                     state="readonly", width=42,
                     font=FUENTE_NORMAL).pack(side=tk.LEFT, padx=5)
        boton_primario(panel_pac, "Ver tensiones",
                       self._cargar_tensiones).pack(side=tk.LEFT, padx=5)

        # ── Filtros (4 campos del enunciado) ────────────────────────────
        panel_filtros = tk.LabelFrame(self, text="Filtros", bg=COLOR_FONDO,
                                       font=FUENTE_SUBTITULO, padx=10, pady=5)
        panel_filtros.pack(fill=tk.X, padx=15, pady=3)

        etiquetas = ["Método", "Sitio cuerpo", "Brazalete", "Dispositivo"]
        # Valores de listas desde el controlador, sin importar entidades
        listas = [
            [""] + self.controlador.metodos_tension(),
            [""] + self.controlador.sitios_cuerpo(),
            [""] + self.controlador.tamanos_brazalete(),
            [],
        ]
        self._vars_filtro = []
        for col, (etq, vals) in enumerate(zip(etiquetas, listas)):
            tk.Label(panel_filtros, text=etq + ":", bg=COLOR_FONDO,
                     font=FUENTE_NORMAL).grid(
                row=0, column=col * 2, padx=(10, 2), pady=4, sticky=tk.W)
            var = tk.StringVar()
            if vals:
                w = ttk.Combobox(panel_filtros, textvariable=var,
                                  values=vals, state="readonly",
                                  width=16, font=FUENTE_NORMAL)
            else:
                w = tk.Entry(panel_filtros, textvariable=var,
                              width=18, font=FUENTE_NORMAL)
            w.grid(row=0, column=col * 2 + 1,
                   padx=(0, 8), pady=4, sticky=tk.W)
            self._vars_filtro.append(var)

        boton_secundario(panel_filtros, "Aplicar filtros",
                         self._aplicar_filtros).grid(
            row=1, column=0, columnspan=4, padx=10, pady=4, sticky=tk.W)
        boton_secundario(panel_filtros, "Limpiar",
                         self._limpiar_filtros).grid(
            row=1, column=4, padx=2, pady=4, sticky=tk.W)

        # ── Media de tensiones ──────────────────────────────────────────
        panel_media = tk.LabelFrame(self, text="Media de tensiones",
                                    bg=COLOR_FONDO, font=FUENTE_SUBTITULO,
                                    padx=10, pady=5)
        panel_media.pack(fill=tk.X, padx=15, pady=3)

        fila_media = tk.Frame(panel_media, bg=COLOR_FONDO)
        fila_media.pack(fill=tk.X)

        tk.Label(fila_media,
                text="Últimas N tomas (vacío = todas):",
                bg=COLOR_FONDO, font=FUENTE_NORMAL).pack(
            side=tk.LEFT, padx=5)

        self._var_n = tk.StringVar()

        tk.Entry(fila_media, textvariable=self._var_n, width=6,
                font=FUENTE_NORMAL).pack(side=tk.LEFT, padx=5)

        boton_secundario(fila_media, "Calcular media",
                        self._calcular_media).pack(side=tk.LEFT, padx=8)

        self._lbl_media = tk.Label(panel_media, text="", bg=COLOR_FONDO,
                                    font=FUENTE_SUBTITULO, fg=COLOR_PRIMARIO,
                                    anchor="w", justify="left", wraplength=1000)
        self._lbl_media.pack(fill=tk.X, padx=5, pady=(8, 2))

        # ── Tabla ───────────────────────────────────────────────────────
        etiqueta_seccion(self, "Tomas registradas")
        cols = [("Fecha", 100), ("Sistólica", 85), ("Diastólica", 85),
                ("Método", 120), ("Sitio", 130), ("Brazalete", 100),
                ("Dispositivo", 140), ("En rango", 75), ("Estado", 90)]
        self._tabla = crear_tabla(self, cols, alto=7)
        self._tabla.bind("<<TreeviewSelect>>",
                          lambda e: self._al_seleccionar())

        bar = tk.Frame(self, bg=COLOR_FONDO)
        bar.pack(fill=tk.X, padx=10, pady=5)
        boton_primario(bar, "➕ Registrar toma",
                       self._abrir_nueva).pack(side=tk.LEFT, padx=3)
        boton_secundario(bar, "✏️ Editar",
                          self._abrir_editar).pack(side=tk.LEFT, padx=3)

    # ── Helpers ──────────────────────────────────────────────────────────

    def _get_pac_id(self):
        return self._pac_map.get(self._var_paciente.get())

    def _cargar_tensiones(self):
        pac_id = self._get_pac_id()
        if not pac_id:
            self.mostrar_info("Selecciona un paciente.")
            return
        self._poblar(self.controlador.listar_tensiones_paciente(pac_id))

    def _aplicar_filtros(self):
        pac_id = self._get_pac_id()
        if not pac_id:
            self.mostrar_info("Selecciona un paciente primero.")
            return
        metodo, sitio, brazalete, dispositivo = [
            v.get() or None for v in self._vars_filtro]
        self._poblar(self.controlador.filtrar_tensiones(
            pac_id, metodo=metodo, sitio_cuerpo=sitio,
            tamano_brazalete=brazalete, dispositivo=dispositivo))

    def _limpiar_filtros(self):
        for v in self._vars_filtro:
            v.set("")

    def _calcular_media(self):
        pac_id = self._get_pac_id()
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
        media = self.controlador.media_tensiones(pac_id, ultimas_n=n)
        if media["total"] == 0:
            self._lbl_media.config(text="Sin tomas registradas.")
        else:
            scope = f"últimas {n}" if n else "todas"
            self._lbl_media.config(
                text=(f"({scope} · {media['total']} tomas)  "
                      f"Sistólica: {media['sistolica']} mmHg  |  "
                      f"Diastólica: {media['diastolica']} mmHg"))

    def _poblar(self, tomas):
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

    def _abrir_nueva(self):
        pac_id = self._get_pac_id()
        if not pac_id:
            self.mostrar_info("Selecciona un paciente primero.")
            return
        _FormularioToma(self, self.controlador, pac_id, None,
                        self._cargar_tensiones)

    def _abrir_editar(self):
        if not self._toma_sel_id:
            self.mostrar_info("Selecciona una toma.")
            return
        toma = self.controlador.obtener_tension(self._toma_sel_id)
        _FormularioToma(self, self.controlador, toma.paciente_id,
                        toma, self._cargar_tensiones)


class _FormularioToma(tk.Toplevel):
    def __init__(self, parent, controlador, paciente_id, toma, callback):
        super().__init__(parent)
        self._ctrl = controlador
        self._paciente_id = paciente_id
        self._toma = toma
        self._es_nuevo = toma is None
        self._callback = callback
        self.title("Registrar toma" if self._es_nuevo else "Editar toma")
        self.resizable(False, False)
        self.configure(bg=COLOR_FONDO)
        self._construir()
        self.grab_set()

    def _construir(self):
        form = tk.Frame(self, bg=COLOR_FONDO)
        form.pack(padx=20, pady=10)

        self._var_fecha = campo_form(form, "Fecha (YYYY-MM-DD)", 0)
        self._var_sistolica = campo_form(form, "Sistólica (mmHg)", 1)
        self._var_diastolica = campo_form(form, "Diastólica (mmHg)", 2)
        # Listas de valores desde el controlador
        self._var_metodo = campo_form(
            form, "Método", 3,
            valores=self._ctrl.metodos_tension())
        self._var_sitio = campo_form(
            form, "Sitio cuerpo", 4,
            valores=self._ctrl.sitios_cuerpo())
        self._var_brazalete = campo_form(
            form, "Brazalete", 5,
            valores=self._ctrl.tamanos_brazalete())
        self._var_dispositivo = campo_form(form, "Dispositivo", 6)
        self._var_estado = campo_form(
            form, "Estado (FHIR)", 7,
            valores=self._ctrl.estados_observacion_fhir())
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

        bar = tk.Frame(self, bg=COLOR_FONDO)
        bar.pack(pady=10)
        boton_primario(bar, "Guardar", self._guardar).pack(
            side=tk.LEFT, padx=5)
        boton_secundario(bar, "Cancelar", self.destroy).pack(
            side=tk.LEFT, padx=5)

    def _guardar(self):
        from tkinter import messagebox
        try:
            sistolica = int(self._var_sistolica.get())
            diastolica = int(self._var_diastolica.get())
        except ValueError:
            messagebox.showerror(
                "Error", "Sistólica y diastólica deben ser enteros.",
                parent=self)
            return
        try:
            datos = {
                "paciente_id": self._paciente_id,
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
            if self._es_nuevo:
                self._ctrl.registrar_tension(datos)
            else:
                self._ctrl.modificar_tension(self._toma._id, datos)
            self._callback()
            self.destroy()
        except ValueError as e:
            messagebox.showerror("Validación", str(e), parent=self)
