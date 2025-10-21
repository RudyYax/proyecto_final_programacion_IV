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

    cur.execute("""
    CREATE TABLE IF NOT EXISTS proveedores (
        id_proveedor INTEGER PRIMARY KEY AUTOINCREMENT,
        nombre TEXT NOT NULL,
        nit TEXT,
        telefono TEXT,
        direccion TEXT
    )
    """)#Rudy Yax

    cur.execute("""
    CREATE TABLE IF NOT EXISTS productos (
        id_producto INTEGER PRIMARY KEY AUTOINCREMENT,
        codigo TEXT NOT NULL,
        descripcion TEXT,
        precio TEXT,
        stock INTEGER DEFAULT 0
    )
    """)

    cur.execute("""
    CREATE TABLE IF NOT EXISTS compras (
        id_compra INTEGER PRIMARY KEY AUTOINCREMENT,
        numero_factura TEXT NOT NULL,
        proveedor_id INTEGER NOT NULL,
        producto_id INTEGER NOT NULL,
        cantidad INTEGER NOT NULL,
        precio_total REAL NOT NULL,
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

def ventana_inventario(parent):
    win = tk.Toplevel(parent)
    win.title("Inventario")
    win.geometry("480x260")

    tk.Label(win, text="Inventario", font=("Arial", 14, "bold")).pack(pady=10)

    tk.Button(win, text="Proveedor", font=("Arial", 12), width=22, command=lambda: ventana_proveedores(win)).pack(pady=8)
    tk.Button(win, text="Productos", font=("Arial", 12), width=22, command=lambda: ventana_productos(win)).pack(pady=8)
    tk.Button(win, text="Ingresar Compras", font=("Arial", 12), width=22, command=lambda: ventana_registrar_compra(win)).pack(pady=8)
    tk.Button(win, text="Entradas/Salidas (próximamente)", font=("Arial", 12), width=22, command=lambda: messagebox.showinfo("Info", "Pendiente")).pack(pady=4)

def ventana_proveedores(parent):
    win = tk.Toplevel(parent)
    win.title("Inventario - Proveedores")
    win.geometry("420x220")

    tk.Label(win, text="Proveedores", font=("Arial", 14, "bold")).pack(pady=10)

    tk.Button(win, text="Agregar Proveedor", font=("Arial", 12), width=22,
              command=lambda: ventana_crear_proveedor(win)).pack(pady=6)

    tk.Button(win, text="Mostrar Proveedores", font=("Arial", 12), width=22,
              command=lambda: ventana_listar_proveedores(win)).pack(pady=6)
def ventana_listar_proveedores(parent):
    win = tk.Toplevel(parent)
    win.title("Listado de Proveedores")
    win.geometry("750x420")

    tk.Label(win, text="Proveedores registrados", font=("Arial", 12, "bold")).grid(row=0, column=0, padx=8, pady=8, sticky="w")

    lst = tk.Listbox(win, width=100, height=18)
    lst.grid(row=1, column=0, padx=8, pady=8, sticky="nsew")

    scr = tk.Scrollbar(win, orient="vertical", command=lst.yview)
    scr.grid(row=1, column=1, sticky="ns", pady=8)
    lst.config(yscrollcommand=scr.set)

    lbl_total = tk.Label(win, text="0 resultados")
    lbl_total.grid(row=2, column=0, padx=8, pady=4, sticky="w")

    win.grid_rowconfigure(1, weight=1)
    win.grid_columnconfigure(0, weight=1)

    def cargar():
        lst.delete(0, tk.END)
        con = sqlite3.connect("empresa.db")
        cur = con.cursor()
        cur.execute("SELECT id_proveedor, nombre, IFNULL(nit,''), IFNULL(telefono,''), IFNULL(direccion,'') "
                    "FROM proveedores ORDER BY id_proveedor DESC")
        filas = cur.fetchall()
        con.close()

        for (pid, nom, nit, tel, dirx) in filas:
            lst.insert(tk.END, f"{pid:04d} | {nom} | NIT:{nit} | Tel:{tel} | Dir:{dirx}")

        lbl_total.config(text=f"{len(filas)} resultados")

    tk.Button(win, text="Actualizar", command=cargar).grid(row=0, column=1, padx=8)
    cargar()

def ventana_crear_proveedor(parent):
    win =tk.Toplevel(parent)
    win.title("Crear Proveedor")
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

    def guardar_proveedor():
        nom = e_nombre.get().strip()
        nit = e_nit.get().strip()
        tel = e_tel.get().strip()
        dire = e_dir.get().strip()

        if nom == "":
            messagebox.showwarning("Validación", "El nombre es obligatorio")
            return

        con = sqlite3.connect("empresa.db")
        cur = con.cursor()
        cur.execute("INSERT INTO proveedores (nombre, nit, telefono, direccion) VALUES (?,?,?,?)",
                    (nom, nit if nit else None, tel if tel else None, dire if dire else None))
        con.commit()
        con.close()

        messagebox.showinfo("Proveedores", "Proveedor creado correctamente")

        e_nombre.delete(0, tk.END)
        e_nit.delete(0, tk.END)
        e_tel.delete(0, tk.END)
        e_dir.delete(0, tk.END)

    btn_guardar = tk.Button(win, text="Guardar", font=("Arial", 12), bg="#4CAF50", fg="white",
                            command=guardar_proveedor, width=18)
    btn_guardar.grid(row=4, column=0, columnspan=2, pady=16)

def ventana_productos(parent):
    win = tk.Toplevel(parent)
    win.title("Inventario - Productos")
    win.geometry("420x220")

    tk.Label(win, text="Productos", font=("Arial", 14, "bold")).pack(pady=10)

    tk.Button(win, text="Agregar Producto", font=("Arial", 12), width=22,
              command=lambda: ventana_crear_productos(win)).pack(pady=6)

    tk.Button(win, text="Mostrar Productos", font=("Arial", 12), width=22,
              command=lambda: ventana_listar_productos(win)).pack(pady=6)

def ventana_listar_productos(parent):
    win = tk.Toplevel(parent)
    win.title("Listado de Productos")
    win.geometry("750x420")

    tk.Label(win, text="Productos registrados", font=("Arial", 12, "bold")).grid(row=0, column=0, padx=8, pady=8, sticky="w")

    lst = tk.Listbox(win, width=100, height=18)
    lst.grid(row=1, column=0, padx=8, pady=8, sticky="nsew")

    scr = tk.Scrollbar(win, orient="vertical", command=lst.yview)
    scr.grid(row=1, column=1, sticky="ns", pady=8)
    lst.config(yscrollcommand=scr.set)

    lbl_total = tk.Label(win, text="0 resultados")
    lbl_total.grid(row=2, column=0, padx=8, pady=4, sticky="w")

    win.grid_rowconfigure(1, weight=1)
    win.grid_columnconfigure(0, weight=1)

    def cargar():
        lst.delete(0, tk.END)
        con = sqlite3.connect("empresa.db")
        cur = con.cursor()
        cur.execute("SELECT id_producto, IFNULL(codigo,''), IFNULL(descripcion,''), IFNULL(precio,'') "
                    "FROM productos ORDER BY id_producto DESC")
        filas = cur.fetchall()
        con.close()

        for (pid, cod, des, pre) in filas:
            lst.insert(tk.END, f"{pid:04d} | COD:{cod} | {des} | Precio:{pre}")

        lbl_total.config(text=f"{len(filas)} resultados")

    tk.Button(win, text="Actualizar", command=cargar).grid(row=0, column=1, padx=8)
    cargar()
def ventana_crear_productos(parent):
    win =tk.Toplevel(parent)
    win.title("Crear Producto")
    win.geometry("540x300")

    tk.Label(win, text="Codigo:", font=("Arial", 12)).grid(row=0, column=0, padx=8, pady=6, sticky="e")
    e_Codigo = tk.Entry(win, font=("Arial", 12), width=30)
    e_Codigo.grid(row=0, column=1, padx=8, pady=6, sticky="w")

    tk.Label(win, text="Descripcion:", font=("Arial", 12)).grid(row=1, column=0, padx=8, pady=6, sticky="e")
    e_Descripcion = tk.Entry(win, font=("Arial", 12), width=30)
    e_Descripcion.grid(row=1, column=1, padx=8, pady=6, sticky="w")

    tk.Label(win, text="Precio:", font=("Arial", 12)).grid(row=2, column=0, padx=8, pady=6, sticky="e")
    e_Precio = tk.Entry(win, font=("Arial", 12), width=30)
    e_Precio.grid(row=2, column=1, padx=8, pady=6, sticky="w")


    def guardar_producto():
        cod = e_Codigo.get().strip()
        des = e_Descripcion.get().strip()
        prec = e_Precio.get().strip()

        if cod == "":
            messagebox.showwarning("Validación", "El Código es obligatorio")
            return
        if des == "":
            messagebox.showwarning("Validación", "La Descripcion es obligatorio")
            return
        if prec == "":
            messagebox.showwarning("Validación", "El Precio es obligatorio")
            return

        con = sqlite3.connect("empresa.db")
        cur = con.cursor()
        cur.execute("INSERT INTO productos(codigo, descripcion, precio) VALUES (?,?,?)",
                    (cod, des if des else None, prec if prec else None))
        con.commit()
        con.close()

        messagebox.showinfo("Producto", "Producto creado correctamente")

        e_Codigo.delete(0, tk.END)
        e_Descripcion.delete(0, tk.END)
        e_Precio.delete(0, tk.END)

    btn_guardar = tk.Button(win, text="Guardar", font=("Arial", 12), bg="#4CAF50", fg="white",
                            command=guardar_producto, width=18)
    btn_guardar.grid(row=4, column=0, columnspan=2, pady=16)

def ventana_registrar_compra(parent):
    win =tk.Toplevel(parent)
    win.title("Registrar Compra")
    win.geometry("540x300")
    proveedor_id_var = tk.IntVar(value=0)

    tk.Label(win, text="No. Factura:", font=("Arial", 12)).grid(row=0, column=0, padx=8, pady=6, sticky="e")
    e_fac = tk.Entry(win, font=("Arial", 12), width=30)
    e_fac.grid(row=0, column=1, padx=8, pady=6, sticky="w")

    tk.Label(win, text="Proveedor:", font=("Arial", 12)).grid(row=1, column=0, padx=8, pady=6, sticky="e")
    e_prov_nombre = tk.Entry(win, font=("Arial", 12), width=32, state="readonly")
    e_prov_nombre.grid(row=1, column=1, padx=8, pady=6, sticky="w")

    def set_proveedor(pid, nombre):
        proveedor_id_var.set(pid)
        e_prov_nombre.config(state="normal")
        e_prov_nombre.delete(0, tk.END)
        e_prov_nombre.insert(0, nombre)
        e_prov_nombre.config(state="readonly")

    tk.Button(win, text="Seleccionar...", font=("Arial", 11),
              command=lambda: ventana_seleccionar_proveedor(win, set_proveedor)).grid(row=1, column=2, padx=6, pady=6)

    tk.Label(win, text="Codigo del producto:", font=("Arial", 12)).grid(row=2, column=0, padx=8, pady=6, sticky="e")
    e_cod = tk.Entry(win, font=("Arial", 12), width=30)
    e_cod.grid(row=2, column=1, padx=8, pady=6, sticky="w")

    tk.Label(win, text="Cantidad:", font=("Arial", 12)).grid(row=3, column=0, padx=8, pady=6, sticky="e")
    e_cant = tk.Entry(win, font=("Arial", 12), width=30)
    e_cant.grid(row=3, column=1, padx=8, pady=6, sticky="w")

    tk.Label(win, text="Precio Total:", font=("Arial", 12)).grid(row=4, column=0, padx=8, pady=6, sticky="e")
    e_prec = tk.Entry(win, font=("Arial", 12), width=30)
    e_prec.grid(row=4, column=1, padx=8, pady=6, sticky="w")

    def guardar_compra():
        factura = e_fac.get().strip()
        proveedor_id = proveedor_id_var.get()
        codigo = e_cod.get().strip()
        cantidad = e_cant.get().strip()
        precio = e_prec.get().strip()

        if factura == "":
            messagebox.showwarning("Validación", "El Número de Factura es obligatorio")
            return
        if proveedor_id <= 0:
            messagebox.showwarning("Validación", "El Proveedor es obligatorio")
            return
        if codigo == "":
            messagebox.showwarning("Validación", "El Codigo del Producto es obligatorio")
            return
        if cantidad == "":
            messagebox.showerror("Validación", "La Cantidad del Producto es obligatorio")
            return
        if precio == "":
            messagebox.showerror("Validación", "EL precio total del Producto es obligatorio")
            return

        try:
            cantidad = int(cantidad)
            if cantidad <= 0: raise ValueError
        except ValueError:
            messagebox.showwarning("Validación", "Cantidad debe ser un entero positivo")
            return

        try:
            precio_total = float(precio)
            if precio_total <= 0: raise ValueError
        except ValueError:
            messagebox.showwarning("Validación", "Precio total debe ser un número positivo")
            return

        con = sqlite3.connect("empresa.db")
        cur = con.cursor()
        cur.execute("SELECT id_producto, COALESCE(stock,0) FROM productos WHERE codigo=?", (codigo,))
        fila_prod = cur.fetchone()
        if not fila_prod:
            con.close()
            messagebox.showerror("Compras", "Producto con ese código no existe")
            return
        producto_id, stock_actual = fila_prod

        from datetime import datetime
        ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        cur.execute(
            "INSERT INTO compras (numero_factura, proveedor_id, producto_id, cantidad, precio_total, fecha_hora) "
            "VALUES (?,?,?,?,?,?)",
            (factura, proveedor_id, producto_id, cantidad, precio_total, ts)
        )
        cur.execute("UPDATE productos SET stock = COALESCE(stock,0) + ? WHERE id_producto=?",(cantidad, producto_id))
        con.commit()
        con.close()

        messagebox.showinfo("Compras", f"Compra registrada. Stock actualizado: +{cantidad}")
        win.destroy()

    tk.Button(win, text="Guardar", font=("Arial", 12), bg="#4CAF50", fg="white",command=guardar_compra, width=18).grid(row=5, column=0, columnspan=3, pady=16)

def ventana_seleccionar_proveedor(parent, on_select):
    win = tk.Toplevel(parent)
    win.title("Seleccionar Proveedor")
    win.geometry("600x420")

    tk.Label(win, text="Doble clic o botón Seleccionar", font=("Arial", 11)).grid(row=0, column=0, padx=8, pady=6, sticky="w")

    lst = tk.Listbox(win, width=80, height=16)
    lst.grid(row=1, column=0, padx=8, pady=8, sticky="nsew")

    scr = tk.Scrollbar(win, orient="vertical", command=lst.yview)
    scr.grid(row=1, column=1, sticky="ns", pady=8)
    lst.config(yscrollcommand=scr.set)

    win.grid_rowconfigure(1, weight=1)
    win.grid_columnconfigure(0, weight=1)

    con = sqlite3.connect("empresa.db")
    cur = con.cursor()
    cur.execute("SELECT id_proveedor, nombre, IFNULL(nit,''), IFNULL(telefono,'') FROM proveedores ORDER BY nombre ASC")
    filas = cur.fetchall()
    con.close()
    data = []
    for (pid, nom, nit, tel) in filas:
        data.append((pid, nom))
        lst.insert(tk.END, f"{pid:04d} | {nom} | NIT:{nit} | Tel:{tel}")

    def seleccionar():
        sel = lst.curselection()
        if not sel:
            messagebox.showwarning("Seleccionar", "Elija un proveedor de la lista")
            return
        idx = sel[0]
        pid, nom = data[idx]
        on_select(pid, nom)
        win.destroy()

    lst.bind("<Double-Button-1>", lambda e: seleccionar())

    tk.Button(win, text="Seleccionar", command=seleccionar, width=18).grid(row=2, column=0, padx=8, pady=8, sticky="e")
    tk.Button(win, text="Cancelar", command=win.destroy, width=12).grid(row=2, column=0, padx=8, pady=8, sticky="w")

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
            ("Buscar Clientes", lambda: ventana_buscar_clientes(ventana)),
            ("Inventario", lambda: ventana_inventario(ventana)),
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
    canvas.create_window(ancho//2, y + 20, window=b_salir)

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