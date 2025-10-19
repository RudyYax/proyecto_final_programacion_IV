import os
import sqlite3
import tkinter as tk
from tkinter import messagebox
from PIL import Image, ImageTk

# ==========================
# FUNCIONES DE BASE DE DATOS
# ==========================

def crear_tablas():
    conexion = sqlite3.connect("empresa.db")
    cursor = conexion.cursor()

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS usuarios (
        id_usuario INTEGER PRIMARY KEY AUTOINCREMENT,
        nombre TEXT NOT NULL,
        usuario TEXT UNIQUE NOT NULL,
        contraseña TEXT NOT NULL,
        rol TEXT CHECK(rol IN ('administrador','cobrador','tecnico')) NOT NULL
    )
    """)

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

# ==========================
# FUNCIONES DE INTERFAZ
# ==========================

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

def abrir_ventana_principal(nombre, rol):
    ventana = tk.Tk()
    ventana.title(f"Panel - {rol.capitalize()}")
    ventana.attributes('-fullscreen', True)

    ancho = ventana.winfo_screenwidth()
    alto = ventana.winfo_screenheight()

    # ======== Cargar imágenes con rutas relativas ========
    ruta_base = os.path.dirname(__file__)
    ruta_fondo = os.path.join(ruta_base, "fondo.png")

    # Si no existe la imagen, mostrar error
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

    # ======== Botones según el rol ========
    if rol == "administrador":
        botones = ["Crear Clientes", "Asistencia", "Buscar Clientes", "Inventario",
                   "Listado Clientes por Visitar", "Órdenes de Trabajo", "Material Instalado",
                   "Control de Cobros", "Facturar"]
    elif rol == "cobrador":
        botones = ["Asistencia", "Buscar Clientes", "Listado Clientes Visitar",
                   "Control de Cobros", "Facturar"]
    else:
        botones = ["Asistencia", "Buscar Clientes", "Listado Clientes por Visitar",
                   "Control de Cobros", "Facturar"]

    y = 200
    for texto in botones:
        boton = tk.Button(ventana, text=texto, width=25, font=("Arial", 14))
        canvas.create_window(ancho//2, y, window=boton)
        y += 50

    boton_salir = tk.Button(ventana, text="Cerrar Sesión", command=ventana.destroy,
                            bg="red", fg="white", font=("Arial", 14), width=25)
    canvas.create_window(ancho//2, y + 50, window=boton_salir)

    ventana.fondo_tk = fondo_tk
    ventana.mainloop()

def ventana_login_gui():
    global ventana_login, entry_usuario, entry_contraseña, imagen_logo

    ventana_login = tk.Tk()
    ventana_login.title("Inicio de Sesión - Empresa")
    ventana_login.attributes('-fullscreen', True)

    ancho = ventana_login.winfo_screenwidth()
    alto = ventana_login.winfo_screenheight()

    # ======== Cargar imágenes con rutas relativas ========
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

# ==========================
# PROGRAMA PRINCIPAL
# ==========================

if __name__ == "__main__":
    crear_tablas()
    ventana_login_gui()

