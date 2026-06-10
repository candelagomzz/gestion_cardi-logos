"""Vista de perfil: consulta y cambio de contraseña (Médico / Auxiliar)."""

import tkinter as tk
from src.presentacion.vistas.componentes import (
    MarcoBase, boton_primario, COLOR_FONDO,
    FUENTE_TITULO, FUENTE_NORMAL, FUENTE_SUBTITULO, COLOR_PRIMARIO, COLOR_EXITO
)


class VistaPerfil(MarcoBase):
    def __init__(self, parent, controlador, **kwargs):
        super().__init__(parent, controlador)
        self._construir()

    def _construir(self):
        u = self.controlador.usuario_actual

        tk.Label(self, text="Mi Perfil", fg=COLOR_PRIMARIO,
                 bg=COLOR_FONDO, font=FUENTE_TITULO).pack(
            anchor=tk.W, padx=15, pady=10)

        panel = tk.Frame(self, bg="white", relief=tk.RAISED, bd=1)
        panel.pack(padx=30, pady=10, fill=tk.X)

        for i, (etq, val) in enumerate([
            ("Nombre", u.nombre),
            ("Apellidos", u.apellidos),
            ("DNI", u.dni),
            ("Rol", u.rol),
            ("Activo", "Sí" if u.activo else "No"),
        ]):
            tk.Label(panel, text=f"{etq}:", bg="white",
                     font=FUENTE_SUBTITULO, anchor=tk.W,
                     width=12).grid(row=i, column=0, padx=15, pady=5,
                                    sticky=tk.W)
            tk.Label(panel, text=val, bg="white",
                     font=FUENTE_NORMAL, anchor=tk.W).grid(
                row=i, column=1, padx=5, pady=5, sticky=tk.W)

        tk.Label(self, text="Cambiar contraseña", fg=COLOR_PRIMARIO,
                 bg=COLOR_FONDO, font=FUENTE_SUBTITULO).pack(
            anchor=tk.W, padx=15, pady=(20, 5))

        form = tk.Frame(self, bg=COLOR_FONDO)
        form.pack(padx=30, anchor=tk.W)

        tk.Label(form, text="Nueva contraseña:", bg=COLOR_FONDO,
                 font=FUENTE_NORMAL).grid(row=0, column=0, sticky=tk.W, pady=5)
        self._var_p1 = tk.StringVar()
        tk.Entry(form, textvariable=self._var_p1, show="*", width=25,
                  font=FUENTE_NORMAL).grid(row=0, column=1, padx=10, pady=5)

        tk.Label(form, text="Repetir contraseña:", bg=COLOR_FONDO,
                 font=FUENTE_NORMAL).grid(row=1, column=0, sticky=tk.W, pady=5)
        self._var_p2 = tk.StringVar()
        tk.Entry(form, textvariable=self._var_p2, show="*", width=25,
                  font=FUENTE_NORMAL).grid(row=1, column=1, padx=10, pady=5)

        self._lbl_msg = tk.Label(self, text="", bg=COLOR_FONDO,
                                  font=FUENTE_NORMAL)
        self._lbl_msg.pack(anchor=tk.W, padx=30)

        boton_primario(self, "Cambiar contraseña",
                       self._cambiar).pack(anchor=tk.W, padx=30, pady=10)

    def _cambiar(self):
        p1, p2 = self._var_p1.get(), self._var_p2.get()
        if p1 != p2:
            self._lbl_msg.config(
                text="❌ Las contraseñas no coinciden.", fg="#C62828")
            return
        try:
            self.controlador.cambiar_contrasena_perfil(p1)
            self._lbl_msg.config(
                text="✅ Contraseña actualizada.", fg=COLOR_EXITO)
            self._var_p1.set("")
            self._var_p2.set("")
        except ValueError as e:
            self._lbl_msg.config(text=f"❌ {e}", fg="#C62828")
