"""Vista de acceso al sistema."""

import tkinter as tk
from src.presentacion.vistas.componentes import (
    MarcoBase, COLOR_PRIMARIO, COLOR_FONDO, COLOR_SECUNDARIO,
    FUENTE_TITULO, FUENTE_NORMAL, FUENTE_SUBTITULO,
    boton_primario,
)


class VistaLogin(MarcoBase):
    def __init__(self, parent, controlador):
        super().__init__(parent, controlador)

        # Panel central
        panel = tk.Frame(self, bg="white", relief=tk.RAISED, bd=1)
        panel.place(relx=0.5, rely=0.5, anchor=tk.CENTER, width=380, height=300)

        tk.Label(panel, text="Cardio Consultas ♥", bg="white", fg=COLOR_PRIMARIO,
                 font=("Segoe UI", 16, "bold")).pack(pady=(30, 5))
        tk.Label(panel, text="Centro Sanitario – Acceso al sistema",
                 bg="white", fg="#757575", font=FUENTE_NORMAL).pack(pady=(0, 20))

        form = tk.Frame(panel, bg="white")
        form.pack(padx=30, fill=tk.X)

        # DNI
        tk.Label(form, text="DNI:", bg="white", font=FUENTE_NORMAL,
                 anchor=tk.W).grid(row=0, column=0, sticky=tk.W, pady=5)
        self._var_dni = tk.StringVar()
        tk.Entry(form, textvariable=self._var_dni, width=25,
                 font=FUENTE_NORMAL).grid(row=0, column=1, sticky=tk.W, pady=5, padx=8)

        # Contraseña
        tk.Label(form, text="Contraseña:", bg="white", font=FUENTE_NORMAL,
                 anchor=tk.W).grid(row=1, column=0, sticky=tk.W, pady=5)
        self._var_pass = tk.StringVar()
        self._entry_pass = tk.Entry(form, textvariable=self._var_pass, show="*",
                                     width=25, font=FUENTE_NORMAL)
        self._entry_pass.grid(row=1, column=1, sticky=tk.W, pady=5, padx=8)
        self._entry_pass.bind("<Return>", lambda e: self._intentar_login())

        self._lbl_error = tk.Label(panel, text="", fg="#C62828", bg="white",
                                    font=("Segoe UI", 9))
        self._lbl_error.pack()

        boton_primario(panel, "Entrar", self._intentar_login).pack(pady=10)

    def _intentar_login(self):
        dni = self._var_dni.get().strip()
        pwd = self._var_pass.get()
        if not dni or not pwd:
            self._lbl_error.config(text="Introduce DNI y contraseña.")
            return
        ok = self.controlador.autenticar(dni, pwd)
        if not ok:
            self._lbl_error.config(text="Credenciales incorrectas o usuario inactivo.")
            self._var_pass.set("")
