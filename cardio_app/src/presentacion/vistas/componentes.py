"""Utilidades y componentes reutilizables de la capa de presentación."""

import tkinter as tk
from tkinter import ttk, messagebox
from typing import List, Tuple, Optional, Callable


# Paleta de colores
COLOR_PRIMARIO = "#1565C0"
COLOR_SECUNDARIO = "#E3F2FD"
COLOR_ACENTO = "#FF6F00"
COLOR_FONDO = "#F5F5F5"
COLOR_TEXTO = "#212121"
COLOR_ERROR = "#C62828"
COLOR_EXITO = "#2E7D32"
FUENTE_TITULO = ("Segoe UI", 14, "bold")
FUENTE_SUBTITULO = ("Segoe UI", 11, "bold")
FUENTE_NORMAL = ("Segoe UI", 10)
FUENTE_PEQUENA = ("Segoe UI", 9)


class MarcoBase(tk.Frame):
    """Marco base con fondo estandarizado."""

    def __init__(self, parent, controlador, **kwargs):
        super().__init__(parent, bg=COLOR_FONDO, **kwargs)
        self.controlador = controlador

    def mostrar_error(self, mensaje: str):
        messagebox.showerror("Error", mensaje)

    def mostrar_info(self, mensaje: str):
        messagebox.showinfo("Información", mensaje)

    def confirmar(self, mensaje: str) -> bool:
        return messagebox.askyesno("Confirmar", mensaje)


class BarraSuperior(tk.Frame):
    """Barra de navegación superior común."""

    def __init__(self, parent, controlador, titulo: str):
        super().__init__(parent, bg=COLOR_PRIMARIO, height=50)
        self.pack_propagate(False)

        tk.Label(
            self, text=titulo, bg=COLOR_PRIMARIO, fg="white",
            font=FUENTE_TITULO
        ).pack(side=tk.LEFT, padx=15, pady=10)

        if controlador.usuario_actual:
            info = (
                f"  {controlador.usuario_actual.nombre_completo()} "
                f"[{controlador.usuario_actual.rol}]  "
            )
            tk.Label(self, text=info, bg=COLOR_PRIMARIO, fg="#BBDEFB",
                     font=FUENTE_NORMAL).pack(side=tk.RIGHT, padx=5)

            tk.Button(
                self, text="Cerrar sesión", bg=COLOR_ACENTO, fg="white",
                font=FUENTE_PEQUENA, relief=tk.FLAT, cursor="hand2",
                command=controlador.cerrar_sesion
            ).pack(side=tk.RIGHT, padx=10, pady=10)


def crear_tabla(parent, columnas: List[Tuple[str, int]], alto: int = 15) -> ttk.Treeview:
    """Crea un Treeview estilizado con scrollbar."""
    marco = tk.Frame(parent, bg=COLOR_FONDO)
    marco.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

    estilo = ttk.Style()
    estilo.configure("App.Treeview", font=FUENTE_NORMAL, rowheight=24, background="white")
    estilo.configure("App.Treeview.Heading", font=FUENTE_SUBTITULO, background=COLOR_PRIMARIO,
                     foreground="white")
    estilo.map("App.Treeview", background=[("selected", COLOR_SECUNDARIO)],
               foreground=[("selected", COLOR_TEXTO)])

    ids_col = [col[0] for col in columnas]
    tabla = ttk.Treeview(marco, columns=ids_col, show="headings",
                         height=alto, style="App.Treeview")

    for col_id, ancho in columnas:
        tabla.heading(col_id, text=col_id)
        tabla.column(col_id, width=ancho, anchor=tk.W)

    scroll_v = ttk.Scrollbar(marco, orient=tk.VERTICAL, command=tabla.yview)
    scroll_h = ttk.Scrollbar(marco, orient=tk.HORIZONTAL, command=tabla.xview)
    tabla.configure(yscrollcommand=scroll_v.set, xscrollcommand=scroll_h.set)

    tabla.grid(row=0, column=0, sticky="nsew")
    scroll_v.grid(row=0, column=1, sticky="ns")
    scroll_h.grid(row=1, column=0, sticky="ew")
    marco.rowconfigure(0, weight=1)
    marco.columnconfigure(0, weight=1)

    return tabla


def campo_form(parent, etiqueta: str, fila: int, valores: Optional[List[str]] = None,
               es_password: bool = False) -> tk.Variable:
    """Crea un campo de formulario (Entry o Combobox) y retorna la variable."""
    tk.Label(parent, text=etiqueta + ":", bg=COLOR_FONDO, font=FUENTE_NORMAL,
             anchor=tk.W).grid(row=fila, column=0, padx=10, pady=4, sticky=tk.W)

    var = tk.StringVar()
    if valores:
        widget = ttk.Combobox(parent, textvariable=var, values=valores,
                              state="readonly", width=28, font=FUENTE_NORMAL)
    elif es_password:
        widget = tk.Entry(parent, textvariable=var, show="*", width=30, font=FUENTE_NORMAL)
    else:
        widget = tk.Entry(parent, textvariable=var, width=30, font=FUENTE_NORMAL)
    widget.grid(row=fila, column=1, padx=10, pady=4, sticky=tk.W)
    return var


def boton_primario(parent, texto: str, comando: Callable, **kwargs) -> tk.Button:
    return tk.Button(
        parent, text=texto, command=comando,
        bg=COLOR_PRIMARIO, fg="white", font=FUENTE_NORMAL,
        relief=tk.FLAT, padx=12, pady=5, cursor="hand2", **kwargs
    )


def boton_secundario(parent, texto: str, comando: Callable, **kwargs) -> tk.Button:
    return tk.Button(
        parent, text=texto, command=comando,
        bg="#757575", fg="white", font=FUENTE_NORMAL,
        relief=tk.FLAT, padx=12, pady=5, cursor="hand2", **kwargs
    )


def boton_peligro(parent, texto: str, comando: Callable, **kwargs) -> tk.Button:
    return tk.Button(
        parent, text=texto, command=comando,
        bg=COLOR_ERROR, fg="white", font=FUENTE_NORMAL,
        relief=tk.FLAT, padx=12, pady=5, cursor="hand2", **kwargs
    )


def etiqueta_seccion(parent, texto: str) -> tk.Label:
    lbl = tk.Label(parent, text=texto, bg=COLOR_FONDO, fg=COLOR_PRIMARIO,
                   font=FUENTE_SUBTITULO)
    lbl.pack(anchor=tk.W, padx=10, pady=(10, 2))
    return lbl
