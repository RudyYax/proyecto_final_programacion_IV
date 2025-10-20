import os
import sqlite3
import tkinter as tk
from tkinter import messagebox
from PIL import Image, ImageTk

# =====================================
# 1) BASE DE DATOS (agregamos CLIENTES)
# =====================================

def crear_tablas():
    conexion = sqlite3.connect("empresa.db")
    cursor = conexion.cursor()

    # Tabla de usuarios (igual que tu base)
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS usuarios (
            id_usuario INTEGER PRIMARY KEY AUTOINCREMENT,
            nombre TEXT NOT NULL,
            usuario TEXT UNIQUE NOT NULL,
            contraseña TEXT NOT NULL,
            rol TEXT CHECK(rol IN ('administrador','cobrador','tecnico')) NOT NULL
        )
        """
    )

    # NUEVO: Tabla de clientes (SQL básico)
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS clientes (
            id_cliente INTEGER PRIMARY KEY AUTOINCREMENT,
            nombre TEXT NOT NULL,
            nit TEXT,
            telefono TEXT,
            direccion TEXT
        )
        """
    )
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS asistencia (
        id_asistencia INTEGER PRIMARY KEY AUTOINCREMENT, 
        usuario TEXT,
        accion TEXT, 
        fecha_hora TEXT
        )
        """
    )

    usuarios_default = [
        ("Rudy Yax", "admin", "1234", "administrador"),
        ("Rudy Yax", "cobro1", "1234", "cobrador"),
        ("Rudy Yax", "tec1", "1234", "tecnico")
    ]
    for u in usuarios_default:
        try:
            cursor.execute("INSERT INTO usuarios (nombre, usuario, contraseña, rol) VALUES (?, ?, ?, ?)", u)
        except sqlite3.IntegrityError:
            cursor.execute("UPDATE usuarios SET nombre=? WHERE usuario=?", (u[0], u[1]))

    conexion.commit()
    conexion.close()

# =====================================
# 2) LOGIN
# =====================================

def verificar_login():
    usuario = entry_usuario.get()
    contraseña = entry_contraseña.get()
    conexion = sqlite3.connect("empresa.db")
    cursor = conexion.cursor()
    cursor.execute("SELECT nombre, rol FROM usuarios WHERE usuario=? AND contraseña=?", (usuario, contraseña))
    resultado = cursor.fetchone()
    conexion.close()
    if resultado:
        nombre, rol = resultado
        messagebox.showinfo("Bienvenido", f"Hola {nombre}\nRol: {rol}")
        ventana_login.destroy()
        abrir_ventana_principal(nombre, rol)
    else:
        messagebox.showerror("Error", "Usuario o contraseña incorrectos")

# =====================================
# 3) ADMIN: CREAR CLIENTES (ventana)
# =====================================

def ventana_crear_clientes(parent):
    """Ventana simple SOLO para AGREGAR clientes (sin listado)."""
    win = tk.Toplevel(parent)
    win.title("Administración - Agregar Cliente")
    win.geometry("540x300")

    # --- Formulario ---
    tk.Label(win, text="Nombre:", font=("Arial", 12)).grid(row=0, column=0, padx=8, pady=6, sticky="e")
    e_nombre = tk.Entry(win, font=("Arial", 12), width=30)
    e_nombre.grid(row=0, column=1, padx=8, pady=6, sticky="w")

    tk.Label(win, text="NIT:", font=("Arial", 12)).grid(row=1, column=0, padx=8, pady=6, sticky="e")
    e_nit = tk.Entry(win, font=("Arial", 12), width=30)
    e_nit.grid(row=1, column=1, padx=8, pady=6, sticky="w")

    tk.Label(win, text="Teléfono:", font=("Arial", 12)).grid(row=2, column=0, padx=8, pady=6, sticky="e")
    e_tel = tk.Entry(win, font=("Arial", 12), width=30)
    e_tel.grid(row=2, column=1, padx=8, pady=6, sticky="w")

    tk.Label(win, text="Dirección:", font=("Arial", 12)).grid(row=3, column=0, padx=8, pady=6, sticky="e")
    e_dir = tk.Entry(win, font=("Arial", 12), width=30)
    e_dir.grid(row=3, column=1, padx=8, pady=6, sticky="w")

    def insertar_cliente():
        nombre = e_nombre.get().strip()
        if not nombre:
            messagebox.showwarning("Validación", "El nombre es obligatorio")
            return
        nit = e_nit.get().strip() or None
        tel = e_tel.get().strip() or None
        dire = e_dir.get().strip() or None
        con = sqlite3.connect("empresa.db")
        cur = con.cursor()
        cur.execute(
            "INSERT INTO clientes (nombre, nit, telefono, direccion) VALUES (?,?,?,?)",
            (nombre, nit, tel, dire)
        )
        con.commit()
        con.close()
        messagebox.showinfo("Clientes", "Cliente creado correctamente")
        # Limpiar campos
        e_nombre.delete(0, tk.END)
        e_nit.delete(0, tk.END)
        e_tel.delete(0, tk.END)
        e_dir.delete(0, tk.END)

    tk.Button(
        win,
        text="Guardar (INSERT)",
        font=("Arial", 12),
        bg="#4CAF50",
        fg="white",
        command=insertar_cliente,
        width=18,
    ).grid(row=4, column=0, columnspan=2, pady=16)
# =====================================
# 4) PANEL PRINCIPAL (agregamos acción al botón "Crear Clientes")
# =====================================

def abrir_ventana_principal(nombre, rol):
    ventana = tk.Tk()
    ventana.title(f"Panel - {rol.capitalize()}")
    ventana.attributes('-fullscreen', True)

    ancho = ventana.winfo_screenwidth()
    alto = ventana.winfo_screenheight()
    ruta_base = os.path.dirname(__file__)
    ruta_fondo = os.path.join(ruta_base, "fondo.png")

    if not os.path.exists(ruta_fondo):
        messagebox.showerror("Error", f"No se encontró la imagen: {ruta_fondo}")
        ventana.destroy()
        return

    fondo = Image.open(ruta_fondo)
    fondo = fondo.resize((ancho, alto), Image.Resampling.LANCZOS)
    fondo_tk = ImageTk.PhotoImage(fondo)

    canvas = tk.Canvas(ventana, width=ancho, height=alto)
    canvas.pack(fill="both", expand=True)
    canvas.create_image(0, 0, image=fondo_tk, anchor="nw")

    canvas.create_text(ancho//2, 80, text=f"Bienvenido, {nombre}", font=("Arial", 24, "bold"), fill="white")
    canvas.create_text(ancho//2, 130, text=f"Rol: {rol.upper()}", font=("Arial", 18), fill="white")

    if rol == "administrador":
        botones = [
            ("Crear Clientes", lambda: ventana_crear_clientes(ventana)),
            ("Ver Asistencias", None),
            ("Buscar Clientes", None),
            ("Inventario", None),
            ("Listado Clientes por Visitar", None),
            ("Órdenes de Trabajo", None),
            ("Material Instalado", None),
            ("Control de Cobros", None),
            ("Facturar", None),
            ("Crear Usuarios", None),
        ]
    elif rol == "cobrador":
        botones = [
            ("Asistencia", None),
            ("Buscar Clientes", None),
            ("Listado Clientes Visitar", None),
            ("Control de Cobros", None),
            ("Facturar", None),
        ]
    else:
        botones = [
            ("Asistencia", None),
            ("Buscar Clientes", None),
            ("Listado Clientes por Visitar", None),
            ("Control de Cobros", None),
            ("Facturar", None),
        ]

    y = 200
    for texto, cmd in botones:
        if cmd is None:
            boton = tk.Button(ventana, text=texto, width=25, font=("Arial", 14),
                              command=lambda t=texto: messagebox.showinfo("Info", f"'{t}' aún no está implementado"))
        else:
            boton = tk.Button(ventana, text=texto, width=25, font=("Arial", 14), command=cmd)
        canvas.create_window(ancho//2, y, window=boton)
        y += 50

    boton_salir = tk.Button(ventana, text="Cerrar Sesión", command=ventana.destroy,
                            bg="red", fg="white", font=("Arial", 14), width=25)
    canvas.create_window(ancho//2, y + 50, window=boton_salir)

    ventana.fondo_tk = fondo_tk
    ventana.mainloop()

# =====================================
# 5) LOGIN GUI (sin cambios, salvo que ya existe tabla clientes)
# =====================================

def ventana_login_gui():
    global ventana_login, entry_usuario, entry_contraseña, imagen_logo
    ventana_login = tk.Tk()
    ventana_login.title("Inicio de Sesión - Empresa")
    ventana_login.attributes('-fullscreen', True)

    ancho = ventana_login.winfo_screenwidth()
    alto = ventana_login.winfo_screenheight()
    ruta_base = os.path.dirname(__file__)
    ruta_fondo = os.path.join(ruta_base, "fondo.png")
    ruta_logo = os.path.join(ruta_base, "logo.png")

    if not os.path.exists(ruta_fondo) or not os.path.exists(ruta_logo):
        messagebox.showerror("Error", "Faltan las imágenes 'fondo.png' o 'logo.png'")
        ventana_login.destroy()
        return

    fondo = Image.open(ruta_fondo)
    fondo = fondo.resize((ancho, alto), Image.Resampling.LANCZOS)
    fondo_tk = ImageTk.PhotoImage(fondo)

    canvas = tk.Canvas(ventana_login, width=ancho, height=alto)
    canvas.pack(fill="both", expand=True)
    canvas.create_image(0, 0, image=fondo_tk, anchor="nw")

    logo = Image.open(ruta_logo)
    logo = logo.resize((300, 300), Image.Resampling.LANCZOS)
    imagen_logo = ImageTk.PhotoImage(logo)
    canvas.create_image(ancho//2, 200, image=imagen_logo)

    canvas.create_text(ancho//2, 380, text="Inicio de Sesión", font=("Arial", 20, "bold"), fill="black")
    canvas.create_text(ancho//2, 430, text="Usuario:", font=("Arial", 14), fill="black")
    canvas.create_text(ancho//2, 490, text="Contraseña:", font=("Arial", 14), fill="black")

    entry_usuario = tk.Entry(ventana_login, font=("Arial", 14))
    canvas.create_window(ancho//2, 460, window=entry_usuario, width=250)

    entry_contraseña = tk.Entry(ventana_login, show="*", font=("Arial", 14))
    canvas.create_window(ancho//2, 520, window=entry_contraseña, width=250)

    boton_login = tk.Button(ventana_login, text="Iniciar Sesión", command=verificar_login,
                            bg="#4CAF50", fg="white", font=("Arial", 14), width=20)
    canvas.create_window(ancho//2, 580, window=boton_login)

    boton_salir = tk.Button(ventana_login, text="Salir", command=ventana_login.destroy,
                             bg="red", fg="white", font=("Arial", 14), width=20)
    canvas.create_window(ancho//2, 640, window=boton_salir)

    ventana_login.fondo_tk = fondo_tk
    ventana_login.mainloop()

# =====================================
# 6) MAIN
# =====================================
if __name__ == "__main__":
    crear_tablas()
    ventana_login_gui()
