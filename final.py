import os
import sqlite3
import tkinter as tk
from tkinter import messagebox
from PIL import Image, ImageTk

def crear_tablas():
    con = sqlite3.connect("empresa.db")
    cur = con.cursor()

    cur.execute("""
    CREATE TABLE IF NOT EXISTS usuarios (
        id_usuario INTEGER PRIMARY KEY AUTOINCREMENT,
        nombre TEXT NOT NULL,
        usuario TEXT UNIQUE NOT NULL,
        contraseña TEXT NOT NULL,
        rol TEXT CHECK(rol IN ('administrador','cobrador','tecnico')) NOT NULL
    )
    """)

    cur.execute("""
    CREATE TABLE IF NOT EXISTS clientes (
        id_cliente INTEGER PRIMARY KEY AUTOINCREMENT,
        nombre TEXT NOT NULL,
        nit TEXT,
        telefono TEXT,
        direccion TEXT
    )
    """)

    cur.execute("""
    CREATE TABLE IF NOT EXISTS asistencia (
        id_asistencia INTEGER PRIMARY KEY AUTOINCREMENT,
        usuario TEXT,
        accion TEXT,
        fecha_hora TEXT
    )
    """)

    usuarios_default = [
        ("Rudy Yax", "admin", "1234", "administrador"),
        ("Rudy Yax", "cobro1", "1234", "cobrador"),
        ("Rudy Yax", "tec1", "1234", "tecnico")
    ]
    for u in usuarios_default:
        try:
            cur.execute("INSERT INTO usuarios (nombre, usuario, contraseña, rol) VALUES (?, ?, ?, ?)", u)
        except sqlite3.IntegrityError:
            cur.execute("UPDATE usuarios SET nombre=? WHERE usuario=?", (u[0], u[1]))

    con.commit()
    con.close()

def verificar_login():
    usu = entry_usuario.get()
    pwd = entry_contraseña.get()

    con = sqlite3.connect("empresa.db")
    cur = con.cursor()
    cur.execute("SELECT nombre, rol FROM usuarios WHERE usuario=? AND contraseña=?", (usu, pwd))
    fila = cur.fetchone()
    con.close()

    if fila:
        nom = fila[0]
        rol = fila[1]
        messagebox.showinfo("Bienvenido", "Hola " + nom + "\nRol: " + rol)
        ventana_login.destroy()
        abrir_ventana_principal(nom, rol)
    else:
        messagebox.showerror("Error", "Usuario o contraseña incorrectos")

def ventana_crear_clientes(parent):
    win = tk.Toplevel(parent)
    win.title("Administración - Agregar Cliente")
    win.geometry("540x300")

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

    def guardar_cliente():
        nom = e_nombre.get().strip()
        nit = e_nit.get().strip()
        tel = e_tel.get().strip()
        dire = e_dir.get().strip()

        if nom == "":
            messagebox.showwarning("Validación", "El nombre es obligatorio")
            return

        con = sqlite3.connect("empresa.db")
        cur = con.cursor()
        cur.execute("INSERT INTO clientes (nombre, nit, telefono, direccion) VALUES (?,?,?,?)",
                    (nom, nit if nit else None, tel if tel else None, dire if dire else None))
        con.commit()
        con.close()

        messagebox.showinfo("Clientes", "Cliente creado correctamente")
        e_nombre.delete(0, tk.END)
        e_nit.delete(0, tk.END)
        e_tel.delete(0, tk.END)
        e_dir.delete(0, tk.END)

    btn_guardar = tk.Button(win, text="Guardar", font=("Arial", 12), bg="#4CAF50", fg="white",
                            command=guardar_cliente, width=18)
    btn_guardar.grid(row=4, column=0, columnspan=2, pady=16)

def ventana_buscar_clientes(parent):
    win = tk.Toplevel(parent)
    win.title("Buscar Clientes")
    win.geometry("700x400")

    tk.Label(win, text="Buscar por nombre o código:").pack(pady=5)
    entrada = tk.Entry(win, width=40)
    entrada.pack(pady=5)

    lista = tk.Listbox(win, width=90, height=12)
    lista.pack(pady=10)

    def buscar():
        busqueda = entrada.get().strip()
        if busqueda == "":
            messagebox.showwarning("Buscar", "Escribe algo para buscar.")
            return

        con = sqlite3.connect("empresa.db")
        cur = con.cursor()

        if busqueda.isdigit():
            cur.execute("SELECT id_cliente, nombre, nit, telefono, direccion FROM clientes WHERE id_cliente=? OR nombre LIKE ?", (busqueda, f"%{busqueda}%"))
        else:
            cur.execute("SELECT id_cliente, nombre, nit, telefono, direccion FROM clientes WHERE nombre LIKE ?", (f"%{busqueda}%",))

        filas = cur.fetchall()
        con.close()

        lista.delete(0, tk.END)
        if not filas:
            lista.insert(tk.END, "No se encontraron clientes.")
            return

        for fila in filas:
            idc, nom, nit, tel, dire = fila
            texto = f"ID: {idc} | {nom} | NIT: {nit or ''} | Tel: {tel or ''} | Dir: {dire or ''}"
            lista.insert(tk.END, texto)

    boton_buscar = tk.Button(win, text="Buscar", command=buscar, width=15, bg="#4CAF50", fg="white")
    boton_buscar.pack(pady=5)

    def limpiar():
        entrada.delete(0, tk.END)
        lista.delete(0, tk.END)

    boton_limpiar = tk.Button(win, text="Limpiar", command=limpiar, width=15, bg="orange", fg="white")
    boton_limpiar.pack(pady=5)

def ventana_ver_asistencias(parent):
    win = tk.Toplevel(parent)
    win.title("Administración - Ver Asistencias")
    win.geometry("780x520")

    tk.Label(win, text="Usuario:").grid(row=0, column=0, padx=6, pady=6)
    e_user = tk.Entry(win, width=18)
    e_user.grid(row=0, column=1)

    tk.Label(win, text="Fecha (YYYY-MM-DD):").grid(row=0, column=2, padx=6, pady=6)
    e_fecha = tk.Entry(win, width=14)
    e_fecha.grid(row=0, column=3)

    lst = tk.Listbox(win, width=100, height=20)
    lst.grid(row=1, column=0, columnspan=4, padx=8, pady=8)

    def cargar_asistencia():
        lst.delete(0, tk.END)
        user_like = "%" + (e_user.get().strip() if e_user.get() else "") + "%"
        fecha_txt = e_fecha.get().strip() if e_fecha.get() else ""

        con = sqlite3.connect("empresa.db")
        cur = con.cursor()

        if fecha_txt != "":
            cur.execute(
                "SELECT usuario, accion, fecha_hora FROM asistencia "
                "WHERE usuario LIKE ? AND date(fecha_hora)=date(?) "
                "ORDER BY id_asistencia DESC",
                (user_like, fecha_txt)
            )
        else:
            cur.execute(
                "SELECT usuario, accion, fecha_hora FROM asistencia "
                "WHERE usuario LIKE ? "
                "ORDER BY id_asistencia DESC",
                (user_like,)
            )

        filas = cur.fetchall()
        for fila in filas:
            u = fila[0]
            a = fila[1]
            f = fila[2]
            lst.insert(tk.END, f + " | " + u + " | " + a)

        con.close()

    tk.Button(win, text="Cargar", command=cargar_asistencia).grid(row=0, column=4, padx=6)
    cargar_asistencia()

def ventana_marcar_asistencia(parent):
    win = tk.Toplevel(parent)
    win.title("Marcar Asistencia")
    win.geometry("420x220")

    tk.Label(win, text="Usuario:").grid(row=0, column=0, padx=6, pady=6)
    e_user = tk.Entry(win, width=22)
    e_user.grid(row=0, column=1)

    tk.Label(win, text="Contraseña:").grid(row=1, column=0, padx=6, pady=6)
    e_pwd = tk.Entry(win, width=22, show='*')
    e_pwd.grid(row=1, column=1)

    def marcar(accion):
        u = e_user.get().strip()
        p = e_pwd.get().strip()

        if u == "" or p == "":
            messagebox.showwarning("Validación", "Usuario y contraseña requeridos")
            return

        con = sqlite3.connect("empresa.db")
        cur = con.cursor()
        cur.execute("SELECT 1 FROM usuarios WHERE usuario=? AND contraseña=?", (u, p))
        ok = cur.fetchone() is not None

        if not ok:
            con.close()
            messagebox.showerror("Asistencia", "Credenciales inválidas")
            return

        from datetime import datetime
        ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        cur.execute("INSERT INTO asistencia (usuario, accion, fecha_hora) VALUES (?,?,?)", (u, accion, ts))
        con.commit()
        con.close()
        messagebox.showinfo("Asistencia", accion.capitalize() + " registrada: " + ts)

    tk.Button(win, text="Marcar ENTRADA", width=18, command=lambda: marcar('entrada')).grid(row=2, column=0, padx=6, pady=10)
    tk.Button(win, text="Marcar SALIDA",  width=18, command=lambda: marcar('salida')).grid(row=2, column=1, padx=6, pady=10)

def abrir_ventana_principal(nombre, rol):
    ventana = tk.Tk()
    ventana.title("Panel - " + rol.capitalize())
    ventana.attributes('-fullscreen', True)

    ancho = ventana.winfo_screenwidth()
    alto = ventana.winfo_screenheight()
    ruta_base = os.path.dirname(__file__)
    ruta_fondo = os.path.join(ruta_base, "fondo.png")

    if not os.path.exists(ruta_fondo):
        messagebox.showerror("Error", "No se encontró la imagen: " + ruta_fondo)
        ventana.destroy()
        return

    fondo = Image.open(ruta_fondo)
    fondo = fondo.resize((ancho, alto), Image.Resampling.LANCZOS)
    fondo_tk = ImageTk.PhotoImage(fondo)

    canvas = tk.Canvas(ventana, width=ancho, height=alto)
    canvas.pack(fill="both", expand=True)
    canvas.create_image(0, 0, image=fondo_tk, anchor="nw")

    canvas.create_text(ancho//2, 80, text="Bienvenido, " + nombre, font=("Arial", 24, "bold"), fill="white")
    canvas.create_text(ancho//2, 130, text="Rol: " + rol.upper(), font=("Arial", 18), fill="white")

    if rol == "administrador":
        botones = [
            ("Crear Clientes", lambda: ventana_crear_clientes(ventana)),
            ("Ver Asistencias", lambda: ventana_ver_asistencias(ventana)),
            ("Buscar Clientes", lambda : ventana_buscar_clientes(ventana)),
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
            b = tk.Button(ventana, text=texto, width=25, font=("Arial", 14),
                          command=lambda t=texto: messagebox.showinfo("Info", "'" + t + "' aún no está implementado"))
        else:
            b = tk.Button(ventana, text=texto, width=25, font=("Arial", 14), command=cmd)
        canvas.create_window(ancho//2, y, window=b)
        y += 50

    b_salir = tk.Button(ventana, text="Cerrar Sesión", command=ventana.destroy, bg="red", fg="white", font=("Arial", 14), width=25)
    canvas.create_window(ancho//2, y + 50, window=b_salir)

    ventana.fondo_tk = fondo_tk
    ventana.mainloop()

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

    b_login = tk.Button(ventana_login, text="Iniciar Sesión", command=verificar_login,
                        bg="#4CAF50", fg="white", font=("Arial", 14), width=20)
    canvas.create_window(ancho//2, 580, window=b_login)

    b_salir = tk.Button(ventana_login, text="Salir", command=ventana_login.destroy,
                        bg="red", fg="white", font=("Arial", 14), width=20)
    canvas.create_window(ancho//2, 640, window=b_salir)

    ventana_login.fondo_tk = fondo_tk
    ventana_login.mainloop()

if __name__ == "__main__":
    crear_tablas()
    ventana_login_gui()
