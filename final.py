import os
import sqlite3
import tkinter as tk
from tkinter import messagebox
from PIL import Image, ImageTk

def configurar_teclado_rapido(widget, funcion_enter=None, funcion_escape=None):
    if funcion_enter:
        widget.bind("<Return>", lambda e: funcion_enter())
    if funcion_escape:
        widget.bind("<Escape>", lambda e: funcion_escape())

def navegar_con_enter(widget_actual, widget_siguiente):
    def navegar(event):
        widget_siguiente.focus()
    widget_actual.bind("<Return>", navegar)

def validar_y_ejecutar(widgets, funcion_ejecutar):
    def validar():
        for widget in widgets:
            if isinstance(widget, tk.Entry) and not widget.get().strip():
                messagebox.showwarning("Datos incompletos", "Complete todos los campos")
                widget.focus()
                return
        funcion_ejecutar()
    return  validar

def crear_campo_con_enter(padre, text_label, fila, columna, widget_siguiente=None):
    tk.Label(padre, text=text_label, font=("Arial", 12)).grid(
        row=fila, column=columna, padx=8, pady=6, sticky="e"
    )

    entrada = tk.Entry(padre, font=("Arial", 12), width=30)
    entrada.grid(row=fila, column=columna+1, padx=8, pady=6, sticky="w")

    if widget_siguiente:
        navegar_con_enter(entrada, widget_siguiente)

    return  entrada

def crear_boton_con_teclado(padre, texto, funcion, fila, columnas, color= "#4CAF50"):
    boton = tk.Button(
        padre,
        text=texto,
        font=("Arial", 12),
        bg=color,
        fg="white",
        command=funcion,
        width=18
    )
    boton.grid(row=fila, column=columnas[0], columnspan=columnas[1], pady=16)
    configurar_teclado_rapido(boton, funcion_enter=funcion)
    return boton

def crear_tablas():
    con = sqlite3.connect("empresa.db")
    cur = con.cursor()
    cur.execute("""
    CREATE TABLE IF NOT EXISTS usuarios (
        id_usuario INTEGER PRIMARY KEY AUTOINCREMENT,
        nombre VARCHAR(50) NOT NULL,
        usuario VARCHAR(50) NOT NULL,
        contraseña VARCHAR(50) NOT NULL,
        rol VARCHAR(50) NOT NULL
    )
    """)

    cur.execute("""
    CREATE TABLE IF NOT EXISTS clientes (
        id_cliente INTEGER PRIMARY KEY AUTOINCREMENT,
        nombre VARCHAR(50) NOT NULL,
        nit VARCHAR(50),
        telefono VARCHAR(50),
        direccion VARCHAR(50),
        estado VARCHAR(50) DEFAULT 'ACTIVO'
    )
    """)
    try:
        cur.execute("SELECT estado FROM clientes LIMIT 1")
    except sqlite3.OperationalError:
        cur.execute("ALTER TABLE clientes ADD COLUMN estado VARCHAR(50) DEFAULT 'ACTIVO'")

    cur.execute("""
    CREATE TABLE IF NOT EXISTS asistencia (
        id_asistencia INTEGER PRIMARY KEY AUTOINCREMENT,
        usuario VARCHAR(50),
        accion VARCHAR(50),
        fecha_hora VARCHAR(50)
    )
    """)
    cur.execute("""
    CREATE TABLE IF NOT EXISTS proveedores (
        id_proveedor INTEGER PRIMARY KEY AUTOINCREMENT,
        nombre VARCHAR(50) NOT NULL,
        nit VARCHAR(50),
        telefono VARCHAR(50),
        direccion VARCHAR(50)
    )
    """)
    cur.execute("""
    CREATE TABLE IF NOT EXISTS productos (
        id_producto INTEGER PRIMARY KEY AUTOINCREMENT,
        codigo VARCHAR(50) NOT NULL,
        descripcion VARCHAR(50),
        precio VARCHAR(50),
        stock INTEGER DEFAULT 0
    )
    """)
    cur.execute("""
    CREATE TABLE IF NOT EXISTS compras (
        id_compra INTEGER PRIMARY KEY AUTOINCREMENT,
        numero_factura VARCHAR(50) NOT NULL,
        proveedor_id INTEGER NOT NULL,
        producto_id INTEGER NOT NULL,
        cantidad INTEGER NOT NULL,
        precio_total REAL NOT NULL,
        fecha_hora VARCHAR(50)
    )
    """)
    cur.execute("""
    CREATE TABLE IF NOT EXISTS ordenes_trabajo (
        id_orden INTEGER PRIMARY KEY AUTOINCREMENT,
        cliente_id INTEGER NOT NULL,
        falla VARCHAR(50) NOT NULL,
        fecha_revision VARCHAR(50),
        fecha_creacion VARCHAR(50)
    )
    """)
    cur.execute("SELECT COUNT(*) FROM usuarios")
    total_usuarios = cur.fetchone()[0]
    if total_usuarios == 0:
        usuarios_default = [
            ("Rudy Yax", "admin", "1234", "administrador"),
            ("Rudy Yax", "cobro1", "1234", "cobrador"),
            ("Rudy Yax", "tec1", "1234", "tecnico")
        ]
        for u in usuarios_default:
            cur.execute("INSERT INTO usuarios (nombre, usuario, contraseña, rol) VALUES (?, ?, ?, ?)", u)

    con.commit()
    con.close()

def verificar_inicio():
    usuario_txt = entrada_usuario.get()
    clave_txt = entrada_contraseña.get()

    con = sqlite3.connect("empresa.db")
    cur = con.cursor()
    cur.execute("SELECT nombre, rol FROM usuarios WHERE usuario=? AND contraseña=?", (usuario_txt, clave_txt))
    fila = cur.fetchone()
    con.close()

    if fila:
        nombre = fila[0]
        rol = fila[1]
        messagebox.showinfo("Bienvenido", f"Hola {nombre}\nRol: {rol}")
        ventana_login.destroy()
        abrir_panel_principal(nombre, rol)
    else:
        messagebox.showerror("Error", "Usuario o contraseña incorrectos")


def ventana_crear_clientes(padre):
    ventana = tk.Toplevel(padre)
    ventana.title("Administración - Agregar Cliente")
    ventana.geometry("540x300")

    configurar_teclado_rapido(ventana, funcion_escape=ventana.destroy)

    # Crear campos con navegación por ENTER
    campos = [
        ("Nombre:", "entrada_nombre"),
        ("NIT:", "entrada_nit"),
        ("Teléfono:", "entrada_tel"),
        ("Dirección:", "entrada_dir")
    ]

    entradas = {}
    entrada_anterior = None

    for i, (label, nombre) in enumerate(campos):
        tk.Label(ventana, text=label, font=("Arial", 12)).grid(
            row=i, column=0, padx=8, pady=6, sticky="e"
        )

        entrada = tk.Entry(ventana, font=("Arial", 12), width=30)
        entrada.grid(row=i, column=1, padx=8, pady=6, sticky="w")
        entradas[nombre] = entrada

        # Configurar navegación con ENTER
        if entrada_anterior:
            navegar_con_enter(entrada_anterior, entrada)
        entrada_anterior = entrada

    def guardar_cliente():
        nom = entradas["entrada_nombre"].get().strip()
        nit = entradas["entrada_nit"].get().strip()
        tel = entradas["entrada_tel"].get().strip()
        dire = entradas["entrada_dir"].get().strip()

        if not nom:
            messagebox.showwarning("Validación", "El nombre es obligatorio")
            entradas["entrada_nombre"].focus()
            return

        con = sqlite3.connect("empresa.db")
        cur = con.cursor()
        cur.execute("INSERT INTO clientes (nombre, nit, telefono, direccion, estado) VALUES (?,?,?,?,?)",
                    (nom, nit if nit else None, tel if tel else None, dire if dire else None, "ACTIVO"))
        con.commit()
        con.close()

        messagebox.showinfo("Clientes", "Cliente creado correctamente")

        for entrada in entradas.values():
            entrada.delete(0, tk.END)
        entradas["entrada_nombre"].focus()

    boton_guardar = crear_boton_con_teclado(
        ventana,
        "Guardar Cliente",
        guardar_cliente,
        len(campos),
        [0, 2]
    )

    funcion_guardar_validado = validar_y_ejecutar(
        [entradas["entrada_nombre"]],
        guardar_cliente
    )
    configurar_teclado_rapido(entradas["entrada_dir"], funcion_enter=funcion_guardar_validado)

    entradas["entrada_nombre"].focus()

def obtener_cliente_por_id(id_cliente):
    try:
        cid = int(id_cliente)
    except (ValueError, TypeError):
        return None
    con = sqlite3.connect("empresa.db")
    cur = con.cursor()
    cur.execute("""
        SELECT id_cliente, IFNULL(nombre,''), IFNULL(nit,''), IFNULL(telefono,''), IFNULL(direccion,''), IFNULL(estado,'ACTIVO')
        FROM clientes
        WHERE id_cliente=?
    """, (cid,))
    fila = cur.fetchone()
    con.close()
    return fila


def mostrar_cliente_por_id(padre, id_cliente):
    fila = obtener_cliente_por_id(id_cliente)
    if not fila:
        messagebox.showwarning("Cliente", "No se encontró el cliente con ese ID", parent=padre)
        return
    cid, nombre, nit, tel, dire, estado = fila
    msg = (
        f"ID: {cid}\n"
        f"Nombre: {nombre}\n"
        f"NIT: {nit}\n"
        f"Teléfono: {tel}\n"
        f"Dirección: {dire}\n"
        f"Estado: {estado}"
    )
    messagebox.showinfo("Datos del Cliente", msg, parent=padre)


def ventana_gestion_clientes(padre):
    ventana = tk.Toplevel(padre)
    ventana.title("Gestión de Clientes")
    ventana.geometry("860x560")

    tk.Label(ventana, text="Buscar (nombre o código):").grid(row=0, column=0, padx=8, pady=8, sticky="e")
    entrada_busqueda = tk.Entry(ventana, width=30)
    entrada_busqueda.grid(row=0, column=1, padx=8, pady=8, sticky="w")
    entrada_busqueda.bind("<Return>", lambda e: buscar())

    boton_buscar = tk.Button(ventana, text="Buscar", width=12)
    boton_buscar.grid(row=0, column=2, padx=6, pady=8)
    boton_limpiar = tk.Button(ventana, text="Limpiar", width=12)
    boton_limpiar.grid(row=0, column=3, padx=6, pady=8)

    lista = tk.Listbox(ventana, width=110, height=16)
    lista.grid(row=1, column=0, columnspan=4, padx=8, pady=6, sticky="nsew")

    barra = tk.Scrollbar(ventana, orient="vertical", command=lista.yview)
    barra.grid(row=1, column=4, sticky="ns", pady=6)
    lista.config(yscrollcommand=barra.set)

    ventana.grid_rowconfigure(1, weight=1)
    ventana.grid_columnconfigure(1, weight=1)

    marco = tk.Frame(ventana)
    marco.grid(row=2, column=0, columnspan=4, padx=8, pady=10, sticky="we")

    variable_id = tk.StringVar()
    variable_estado = tk.StringVar(value="—")

    tk.Label(marco, text="ID:").grid(row=0, column=0, sticky="e", padx=6, pady=4)
    tk.Label(marco, textvariable=variable_id, width=10).grid(row=0, column=1, sticky="w", padx=6, pady=4)

    tk.Label(marco, text="Estado:").grid(row=0, column=2, sticky="e", padx=6, pady=4)
    tk.Label(marco, textvariable=variable_estado).grid(row=0, column=3, sticky="w", padx=6, pady=4)

    tk.Label(marco, text="Nombre:").grid(row=1, column=0, sticky="e", padx=6, pady=4)
    entrada_nombre = tk.Entry(marco, width=32)
    entrada_nombre.grid(row=1, column=1, sticky="w", padx=6, pady=4)

    tk.Label(marco, text="Teléfono:").grid(row=1, column=2, sticky="e", padx=6, pady=4)
    entrada_tel = tk.Entry(marco, width=22)
    entrada_tel.grid(row=1, column=3, sticky="w", padx=6, pady=4)

    tk.Label(marco, text="Dirección:").grid(row=2, column=0, sticky="e", padx=6, pady=4)
    entrada_dir = tk.Entry(marco, width=60)
    entrada_dir.grid(row=2, column=1, columnspan=3, sticky="we", padx=6, pady=4)

    boton_guardar = tk.Button(marco, text="Guardar Cambios", width=18, bg="#4CAF50", fg="white")
    boton_guardar.grid(row=3, column=0, padx=6, pady=8, sticky="w")

    boton_alternar = tk.Button(marco, text="Desactivar", width=14)
    boton_alternar.grid(row=3, column=1, padx=6, pady=8, sticky="w")

    boton_cerrar = tk.Button(marco, text="Cerrar", width=10, command=ventana.destroy)
    boton_cerrar.grid(row=3, column=3, padx=6, pady=8, sticky="e")

    ventana.resultados = []

    def mostrar_resultados(filas):
        lista.delete(0, tk.END)
        ventana.resultados = filas
        if not filas:
            lista.insert(tk.END, "Sin resultados")
            return
        for (cid, nom, tel, dire, est) in filas:
            lista.insert(tk.END, f"[{cid}] {nom} | Tel:{tel or ''} | Dir:{dire or ''} | {est}")

    def buscar():
        q = entrada_busqueda.get().strip()
        if q == "":
            messagebox.showwarning("Buscar", "Escribe un nombre o un código.")
            return

        con = sqlite3.connect("empresa.db")
        cur = con.cursor()

        if q.isdigit():
            cur.execute(
                """
                SELECT id_cliente, nombre, telefono, direccion, IFNULL(estado,'ACTIVO') AS estado
                FROM clientes
                WHERE id_cliente = ? OR nombre LIKE ?
                ORDER BY nombre
                """,
                (int(q), f"%{q}%")
            )
        else:
            cur.execute(
                """
                SELECT id_cliente, nombre, telefono, direccion, IFNULL(estado,'ACTIVO') AS estado
                FROM clientes
                WHERE nombre LIKE ?
                ORDER BY nombre
                """,
                (f"%{q}%",)
            )
        filas = cur.fetchall()
        con.close()
        mostrar_resultados(filas)

    def limpiar():
        entrada_busqueda.delete(0, tk.END)
        lista.delete(0, tk.END)
        variable_id.set("")
        variable_estado.set("—")
        entrada_nombre.delete(0, tk.END)
        entrada_tel.delete(0, tk.END)
        entrada_dir.delete(0, tk.END)
        ventana.resultados = []

    def cargar_detalle(indice):
        if indice is None or indice < 0 or indice >= len(ventana.resultados):
            return
        cid, nom, tel, dire, est = ventana.resultados[indice]
        variable_id.set(str(cid))
        variable_estado.set(est or "ACTIVO")
        entrada_nombre.delete(0, tk.END); entrada_nombre.insert(0, nom or "")
        entrada_tel.delete(0, tk.END); entrada_tel.insert(0, tel or "")
        entrada_dir.delete(0, tk.END); entrada_dir.insert(0, dire or "")
        boton_alternar.config(text="Desactivar" if (est or "ACTIVO") == "ACTIVO" else "Activar")

    def al_seleccionar(_):
        sel = lista.curselection()
        if not sel:
            return
        cargar_detalle(sel[0])

    def guardar_cambios():
        if variable_id.get() == "":
            messagebox.showwarning("Guardar", "Selecciona un cliente.")
            return
        cid = int(variable_id.get())
        nom = entrada_nombre.get().strip()
        tel = entrada_tel.get().strip()
        dire = entrada_dir.get().strip()
        if nom == "":
            messagebox.showwarning("Validación", "El nombre es obligatorio.")
            return
        con = sqlite3.connect("empresa.db")
        cur = con.cursor()
        cur.execute("UPDATE clientes SET nombre=?, telefono=?, direccion=? WHERE id_cliente=?",
                    (nom, tel if tel else None, dire if dire else None, cid))
        con.commit()
        con.close()
        messagebox.showinfo("Guardar", "Datos actualizados.")
        buscar()

    def alternar_estado_cliente():
        if variable_id.get() == "":
            messagebox.showwarning("Estado", "Selecciona un cliente.")
            return

        id_cliente = int(variable_id.get())
        estado_actual = variable_estado.get() or "ACTIVO"

        if estado_actual == "ACTIVO":
            confirmar = messagebox.askyesno("Confirmar", f"¿Dar de baja al cliente {id_cliente}?")
            if not confirmar:
                return
            con = sqlite3.connect("empresa.db")
            cur = con.cursor()
            cur.execute("UPDATE clientes SET estado=? WHERE id_cliente=?", ("DE BAJA", id_cliente))
            con.commit()
            con.close()
            messagebox.showinfo("Cliente", "Cliente dado de baja correctamente.")
            ventana.bell()
        else:
            confirmar = messagebox.askyesno("Confirmar", f"¿Reactivar al cliente {id_cliente}?")
            if not confirmar:
                return
            con = sqlite3.connect("empresa.db")
            cur = con.cursor()
            cur.execute("UPDATE clientes SET estado=? WHERE id_cliente=?", ("ACTIVO", id_cliente))
            con.commit()
            con.close()
            messagebox.showinfo("Cliente", "Cliente reactivado correctamente.")
            ventana.bell()

        buscar()

    boton_buscar.config(command=buscar)
    boton_limpiar.config(command=limpiar)
    lista.bind("<<ListboxSelect>>", al_seleccionar)
    boton_guardar.config(command=guardar_cambios)
    boton_alternar.config(command=alternar_estado_cliente)
    entrada_busqueda.bind("<Return>", lambda e: buscar())

def ventana_ver_asistencias(padre):
    ventana = tk.Toplevel(padre)
    ventana.title("Administración - Ver Asistencias")
    ventana.geometry("780x520")

    tk.Label(ventana, text="Usuario:").grid(row=0, column=0, padx=6, pady=6)
    entrada_usuario_busq = tk.Entry(ventana, width=18)
    entrada_usuario_busq.grid(row=0, column=1)

    tk.Label(ventana, text="Fecha (YYYY-MM-DD):").grid(row=0, column=2, padx=6, pady=6)
    entrada_fecha = tk.Entry(ventana, width=14)
    entrada_fecha.grid(row=0, column=3)

    lista = tk.Listbox(ventana, width=100, height=20)
    lista.grid(row=1, column=0, columnspan=4, padx=8, pady=8)

    def cargar_asistencia():
        lista.delete(0, tk.END)
        usuario_like = "%" + (entrada_usuario_busq.get().strip() if entrada_usuario_busq.get() else "") + "%"
        fecha_txt = entrada_fecha.get().strip() if entrada_fecha.get() else ""

        con = sqlite3.connect("empresa.db")
        cur = con.cursor()

        if fecha_txt != "":
            cur.execute(
                "SELECT usuario, accion, fecha_hora FROM asistencia "
                "WHERE usuario LIKE ? AND date(fecha_hora)=date(?) "
                "ORDER BY id_asistencia DESC",
                (usuario_like, fecha_txt)
            )
        else:
            cur.execute(
                "SELECT usuario, accion, fecha_hora FROM asistencia "
                "WHERE usuario LIKE ? "
                "ORDER BY id_asistencia DESC",
                (usuario_like,)
            )

        filas = cur.fetchall()
        for fila in filas:
            usuario, accion, fecha = fila
            lista.insert(tk.END, f"{fecha} | {usuario} | {accion}")

        con.close()

    tk.Button(ventana, text="Cargar", command=cargar_asistencia).grid(row=0, column=4, padx=6)
    cargar_asistencia()


def ventana_marcar_asistencia(padre):
    ventana = tk.Toplevel(padre)
    ventana.title("Marcar Asistencia")
    ventana.geometry("420x220")

    tk.Label(ventana, text="Usuario:").grid(row=0, column=0, padx=6, pady=6)
    entrada_user = tk.Entry(ventana, width=22)
    entrada_user.grid(row=0, column=1)

    tk.Label(ventana, text="Contraseña:").grid(row=1, column=0, padx=6, pady=6)
    entrada_pwd = tk.Entry(ventana, width=22, show='*')
    entrada_pwd.grid(row=1, column=1)

    def marcar(accion):
        u = entrada_user.get().strip()
        p = entrada_pwd.get().strip()

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

    tk.Button(ventana, text="Marcar ENTRADA", width=18, command=lambda: marcar('entrada')).grid(row=2, column=0, padx=6, pady=10)
    tk.Button(ventana, text="Marcar SALIDA",  width=18, command=lambda: marcar('salida')).grid(row=2, column=1, padx=6, pady=10)


# =============================
# Inventario (Proveedores / Productos / Compras)
# =============================

def ventana_inventario(padre):
    ventana = tk.Toplevel(padre)
    ventana.title("Inventario")
    ventana.geometry("400x400")

    tk.Label(ventana, text="Inventario", font=("Arial", 14, "bold")).pack(pady=10)

    tk.Button(ventana, text="Proveedor", font=("Arial", 12), width=22, command=lambda: ventana_proveedores(ventana)).pack(pady=8)
    tk.Button(ventana, text="Productos", font=("Arial", 12), width=22, command=lambda: ventana_productos(ventana)).pack(pady=8)
    tk.Button(ventana, text="Ingresar Compras", font=("Arial", 12), width=22, command=lambda: ventana_registrar_compra(ventana)).pack(pady=8)
    tk.Button(ventana, text="Ver Compras Realizadas", font=("Arial", 12), width=22, command=lambda: ventana_ver_compras(ventana)).pack(pady=6)
    tk.Button(ventana, text="Inventario general", font=("Arial", 12), width=22, command=lambda: ventana_ver_inventario(ventana)).pack(pady=6)


def ventana_proveedores(padre):
    ventana = tk.Toplevel(padre)
    ventana.title("Inventario - Proveedores")
    ventana.geometry("420x220")

    tk.Label(ventana, text="Proveedores", font=("Arial", 14, "bold")).pack(pady=10)

    tk.Button(ventana, text="Agregar Proveedor", font=("Arial", 12), width=22,
              command=lambda: ventana_crear_proveedor(ventana)).pack(pady=6)

    tk.Button(ventana, text="Mostrar Proveedores", font=("Arial", 12), width=22,
              command=lambda: ventana_listar_proveedores(ventana)).pack(pady=6)


def ventana_listar_proveedores(padre):
    ventana = tk.Toplevel(padre)
    ventana.title("Listado de Proveedores")
    ventana.geometry("750x420")

    tk.Label(ventana, text="Proveedores registrados", font=("Arial", 12, "bold")).grid(row=0, column=0, padx=8, pady=8, sticky="w")

    lista = tk.Listbox(ventana, width=100, height=18)
    lista.grid(row=1, column=0, padx=8, pady=8, sticky="nsew")

    barra = tk.Scrollbar(ventana, orient="vertical", command=lista.yview)
    barra.grid(row=1, column=1, sticky="ns", pady=8)
    lista.config(yscrollcommand=barra.set)

    etiqueta_total = tk.Label(ventana, text="0 resultados")
    etiqueta_total.grid(row=2, column=0, padx=8, pady=4, sticky="w")

    ventana.grid_rowconfigure(1, weight=1)
    ventana.grid_columnconfigure(0, weight=1)

    def cargar():
        lista.delete(0, tk.END)
        con = sqlite3.connect("empresa.db")
        cur = con.cursor()
        cur.execute("SELECT id_proveedor, IFNULL(nombre,''), IFNULL(nit,''), IFNULL(telefono,''), IFNULL(direccion,'') FROM proveedores ORDER BY id_proveedor DESC")
        filas = cur.fetchall()
        con.close()

        for (pid, nom, nit, tel, dirx) in filas:
            lista.insert(tk.END, f"{pid:04d} | {nom} | NIT:{nit} | Tel:{tel} | Dir:{dirx}")

        etiqueta_total.config(text=f"{len(filas)} resultados")

    tk.Button(ventana, text="Actualizar", command=cargar).grid(row=0, column=1, padx=8)
    cargar()


def ventana_crear_proveedor(padre):
    ventana = tk.Toplevel(padre)
    ventana.title("Crear Proveedor")
    ventana.geometry("540x300")

    tk.Label(ventana, text="Nombre:", font=("Arial", 12)).grid(row=0, column=0, padx=8, pady=6, sticky="e")
    entrada_nombre = tk.Entry(ventana, font=("Arial", 12), width=30)
    entrada_nombre.grid(row=0, column=1, padx=8, pady=6, sticky="w")

    tk.Label(ventana, text="NIT:", font=("Arial", 12)).grid(row=1, column=0, padx=8, pady=6, sticky="e")
    entrada_nit = tk.Entry(ventana, font=("Arial", 12), width=30)
    entrada_nit.grid(row=1, column=1, padx=8, pady=6, sticky="w")

    tk.Label(ventana, text="Teléfono:", font=("Arial", 12)).grid(row=2, column=0, padx=8, pady=6, sticky="e")
    entrada_tel = tk.Entry(ventana, font=("Arial", 12), width=30)
    entrada_tel.grid(row=2, column=1, padx=8, pady=6, sticky="w")

    tk.Label(ventana, text="Dirección:", font=("Arial", 12)).grid(row=3, column=0, padx=8, pady=6, sticky="e")
    entrada_dir = tk.Entry(ventana, font=("Arial", 12), width=30)
    entrada_dir.grid(row=3, column=1, padx=8, pady=6, sticky="w")

    def guardar_proveedor():
        nom = entrada_nombre.get().strip()
        nit = entrada_nit.get().strip()
        tel = entrada_tel.get().strip()
        dire = entrada_dir.get().strip()

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

        entrada_nombre.delete(0, tk.END)
        entrada_nit.delete(0, tk.END)
        entrada_tel.delete(0, tk.END)
        entrada_dir.delete(0, tk.END)

    tk.Button(ventana, text="Guardar", font=("Arial", 12), bg="#4CAF50", fg="white",
              command=guardar_proveedor, width=18).grid(row=4, column=0, columnspan=2, pady=16)


def ventana_productos(padre):
    ventana = tk.Toplevel(padre)
    ventana.title("Inventario - Productos")
    ventana.geometry("420x220")

    tk.Label(ventana, text="Productos", font=("Arial", 14, "bold")).pack(pady=10)

    tk.Button(ventana, text="Agregar Producto", font=("Arial", 12), width=22,
              command=lambda: ventana_crear_productos(ventana)).pack(pady=6)

    tk.Button(ventana, text="Mostrar Productos", font=("Arial", 12), width=22,
              command=lambda: ventana_listar_productos(ventana)).pack(pady=6)


def ventana_listar_productos(padre):
    ventana = tk.Toplevel(padre)
    ventana.title("Listado de Productos")
    ventana.geometry("750x420")

    tk.Label(ventana, text="Productos registrados", font=("Arial", 12, "bold")).grid(row=0, column=0, padx=8, pady=8, sticky="w")

    lista = tk.Listbox(ventana, width=100, height=18)
    lista.grid(row=1, column=0, padx=8, pady=8, sticky="nsew")

    barra = tk.Scrollbar(ventana, orient="vertical", command=lista.yview)
    barra.grid(row=1, column=1, sticky="ns", pady=8)
    lista.config(yscrollcommand=barra.set)

    etiqueta_total = tk.Label(ventana, text="0 resultados")
    etiqueta_total.grid(row=2, column=0, padx=8, pady=4, sticky="w")

    ventana.grid_rowconfigure(1, weight=1)
    ventana.grid_columnconfigure(0, weight=1)

    def cargar():
        lista.delete(0, tk.END)
        con = sqlite3.connect("empresa.db")
        cur = con.cursor()
        cur.execute("SELECT id_producto, IFNULL(codigo,''), IFNULL(descripcion,''), IFNULL(precio,'') FROM productos ORDER BY id_producto DESC")
        filas = cur.fetchall()
        con.close()

        for (pid, cod, des, pre) in filas:
            lista.insert(tk.END, f"{pid:04d} | COD:{cod} | {des} | Precio:{pre}")

        etiqueta_total.config(text=f"{len(filas)} resultados")

    tk.Button(ventana, text="Actualizar", command=cargar).grid(row=0, column=1, padx=8)
    cargar()


def ventana_crear_productos(padre):
    ventana = tk.Toplevel(padre)
    ventana.title("Crear Producto")
    ventana.geometry("580x350")

    tk.Label(ventana, text="Codigo:", font=("Arial", 12)).grid(row=0, column=0, padx=8, pady=6, sticky="e")
    entrada_codigo = tk.Entry(ventana, font=("Arial", 12), width=30)
    entrada_codigo.grid(row=0, column=1, padx=8, pady=6, sticky="w")

    tk.Label(ventana, text="Descripcion:", font=("Arial", 12)).grid(row=1, column=0, padx=8, pady=6, sticky="e")
    entrada_descripcion = tk.Entry(ventana, font=("Arial", 12), width=30)
    entrada_descripcion.grid(row=1, column=1, padx=8, pady=6, sticky="w")

    tk.Label(ventana, text="Precio:", font=("Arial", 12)).grid(row=2, column=0, padx=8, pady=6, sticky="e")
    entrada_precio = tk.Entry(ventana, font=("Arial", 12), width=30)
    entrada_precio.grid(row=2, column=1, padx=8, pady=6, sticky="w")

    def guardar_producto():
        cod = entrada_codigo.get().strip()
        des = entrada_descripcion.get().strip()
        prec = entrada_precio.get().strip()

        if cod == "":
            messagebox.showwarning("Validación", "El Código es obligatorio")
            return
        if des == "":
            messagebox.showwarning("Validación", "La Descripción es obligatoria")
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

        entrada_codigo.delete(0, tk.END)
        entrada_descripcion.delete(0, tk.END)
        entrada_precio.delete(0, tk.END)

    tk.Button(ventana, text="Guardar", font=("Arial", 12), bg="#4CAF50", fg="white",
              command=guardar_producto, width=18).grid(row=4, column=0, columnspan=2, pady=16)


def ventana_registrar_compra(padre):
    ventana = tk.Toplevel(padre)
    ventana.title("Registrar Compra")
    ventana.geometry("600x500")
    proveedor_id_var = tk.IntVar(value=0)

    tk.Label(ventana, text="No. Factura:", font=("Arial", 12)).grid(row=0, column=0, padx=8, pady=6, sticky="e")
    entrada_factura = tk.Entry(ventana, font=("Arial", 12), width=30)
    entrada_factura.grid(row=0, column=1, padx=8, pady=6, sticky="w")

    tk.Label(ventana, text="Proveedor:", font=("Arial", 12)).grid(row=1, column=0, padx=8, pady=6, sticky="e")
    entrada_prov_nombre = tk.Entry(ventana, font=("Arial", 12), width=32, state="readonly")
    entrada_prov_nombre.grid(row=1, column=1, padx=8, pady=6, sticky="w")

    def set_proveedor(pid, nombre):
        proveedor_id_var.set(pid)
        entrada_prov_nombre.config(state="normal")
        entrada_prov_nombre.delete(0, tk.END)
        entrada_prov_nombre.insert(0, nombre)
        entrada_prov_nombre.config(state="readonly")

    tk.Button(ventana, text="Seleccionar...", font=("Arial", 11),
              command=lambda: ventana_seleccionar_proveedor(ventana, set_proveedor)).grid(row=1, column=2, padx=6, pady=6)

    tk.Label(ventana, text="Codigo del producto:", font=("Arial", 12)).grid(row=2, column=0, padx=8, pady=6, sticky="e")
    entrada_codigo = tk.Entry(ventana, font=("Arial", 12), width=30)
    entrada_codigo.grid(row=2, column=1, padx=8, pady=6, sticky="w")

    tk.Label(ventana, text="Cantidad:", font=("Arial", 12)).grid(row=3, column=0, padx=8, pady=6, sticky="e")
    entrada_cant = tk.Entry(ventana, font=("Arial", 12), width=30)
    entrada_cant.grid(row=3, column=1, padx=8, pady=6, sticky="w")

    tk.Label(ventana, text="Precio Total:", font=("Arial", 12)).grid(row=4, column=0, padx=8, pady=6, sticky="e")
    entrada_prec = tk.Entry(ventana, font=("Arial", 12), width=30)
    entrada_prec.grid(row=4, column=1, padx=8, pady=6, sticky="w")

    def guardar_compra():
        factura = entrada_factura.get().strip()
        proveedor_id = proveedor_id_var.get()
        codigo = entrada_codigo.get().strip()
        cantidad = entrada_cant.get().strip()
        precio = entrada_prec.get().strip()

        if factura == "":
            messagebox.showwarning("Validación", "El Número de Factura es obligatorio")
            return
        if proveedor_id <= 0:
            messagebox.showwarning("Validación", "El Proveedor es obligatorio")
            return
        if codigo == "":
            messagebox.showwarning("Validación", "El Código del Producto es obligatorio")
            return
        if cantidad == "":
            messagebox.showerror("Validación", "La Cantidad del Producto es obligatoria")
            return
        if precio == "":
            messagebox.showerror("Validación", "El precio total del Producto es obligatorio")
            return

        try:
            cantidad = int(cantidad)
            if cantidad <= 0:
                raise ValueError
        except ValueError:
            messagebox.showwarning("Validación", "Cantidad debe ser un entero positivo")
            return

        try:
            precio_total = float(precio)
            if precio_total <= 0:
                raise ValueError
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
        cur.execute("UPDATE productos SET stock = COALESCE(stock,0) + ? WHERE id_producto=?", (cantidad, producto_id))
        con.commit()
        con.close()

        messagebox.showinfo("Compras", f"Compra registrada. Stock actualizado: +{cantidad}", parent=ventana)
        ventana.after(0, ventana.destroy)

    tk.Button(ventana, text="Guardar", font=("Arial", 12), bg="#4CAF50", fg="white",
              command=guardar_compra, width=18).grid(row=5, column=0, columnspan=3, pady=16)


def ventana_seleccionar_proveedor(padre, al_seleccionar):
    ventana = tk.Toplevel(padre)
    ventana.title("Seleccionar Proveedor")
    ventana.geometry("600x420")

    tk.Label(ventana, text="Doble clic o botón Seleccionar", font=("Arial", 11)).grid(row=0, column=0, padx=8, pady=6, sticky="w")

    lista = tk.Listbox(ventana, width=80, height=16)
    lista.grid(row=1, column=0, padx=8, pady=8, sticky="nsew")

    barra = tk.Scrollbar(ventana, orient="vertical", command=lista.yview)
    barra.grid(row=1, column=1, sticky="ns", pady=8)
    lista.config(yscrollcommand=barra.set)

    ventana.grid_rowconfigure(1, weight=1)
    ventana.grid_columnconfigure(0, weight=1)

    con = sqlite3.connect("empresa.db")
    cur = con.cursor()
    cur.execute("SELECT id_proveedor, nombre, IFNULL(nit,''), IFNULL(telefono,'') FROM proveedores ORDER BY nombre ASC")
    filas = cur.fetchall()
    con.close()
    datos = []
    for (pid, nom, nit, tel) in filas:
        datos.append((pid, nom))
        lista.insert(tk.END, f"{pid:04d} | {nom} | NIT:{nit} | Tel:{tel}")

    def seleccionar():
        sel = lista.curselection()
        if not sel:
            messagebox.showwarning("Seleccionar", "Elija un proveedor de la lista")
            return
        idx = sel[0]
        pid, nom = datos[idx]
        al_seleccionar(pid, nom)
        ventana.destroy()

    lista.bind("<Double-Button-1>", lambda e: seleccionar())

    tk.Button(ventana, text="Seleccionar", command=seleccionar, width=18).grid(row=2, column=0, padx=8, pady=8, sticky="e")
    tk.Button(ventana, text="Cancelar", command=ventana.destroy, width=12).grid(row=2, column=0, padx=8, pady=8, sticky="w")


def ventana_ver_compras(padre):
    ventana = tk.Toplevel(padre)
    ventana.title("Compras Realizadas")
    ventana.geometry("860x460")

    tk.Label(ventana, text="Listado de Compras", font=("Arial", 13, "bold")).grid(row=0, column=0, padx=8, pady=8, sticky="w")

    lista = tk.Listbox(ventana, width=120, height=18)
    lista.grid(row=1, column=0, padx=8, pady=8, sticky="nsew")

    barra = tk.Scrollbar(ventana, orient="vertical", command=lista.yview)
    barra.grid(row=1, column=1, sticky="ns", pady=8)
    lista.config(yscrollcommand=barra.set)

    etiqueta_total = tk.Label(ventana, text="0 compras registradas")
    etiqueta_total.grid(row=2, column=0, padx=8, pady=4, sticky="w")

    def cargar():
        lista.delete(0, tk.END)
        con = sqlite3.connect("empresa.db")
        cur = con.cursor()
        # Traemos compras sin JOIN; luego resolvemos nombres con SELECT simples
        cur.execute("""
            SELECT id_compra, numero_factura, proveedor_id, producto_id, cantidad, precio_total, IFNULL(fecha_hora,'')
            FROM compras
            ORDER BY id_compra DESC
        """)
        filas = cur.fetchall()
        # Resolver nombres/códigos con SELECT simples
        for (idc, fac, prov_id, prod_id, cant, total, fecha) in filas:
            # proveedor
            cur.execute("SELECT IFNULL(nombre,'') FROM proveedores WHERE id_proveedor=?", (prov_id,))
            fila_p = cur.fetchone()
            nom_prov = fila_p[0] if fila_p else f"ID:{prov_id}"
            # producto
            cur.execute("SELECT IFNULL(codigo,'') FROM productos WHERE id_producto=?", (prod_id,))
            fila_pr = cur.fetchone()
            cod_prod = fila_pr[0] if fila_pr else f"ID:{prod_id}"
            lista.insert(tk.END, f"Factura: {fac} | Proveedor: {nom_prov} | Producto:{cod_prod} | Cant:{cant} | Total:{total} | {fecha}")
        con.close()
        etiqueta_total.config(text=f"{len(filas)} compras registradas")

    tk.Button(ventana, text="Actualizar", command=cargar).grid(row=0, column=1, padx=8)
    cargar()


def ventana_ver_inventario(padre):
    ventana = tk.Toplevel(padre)
    ventana.title("Inventario - Costo por Unidad")
    ventana.geometry("860x460")

    tk.Label(ventana, text="Inventario (stock y costo unitario promedio)", font=("Arial", 13, "bold")).grid(row=0, column=0, padx=8, pady=8, sticky="w")

    lista = tk.Listbox(ventana, width=120, height=18)
    lista.grid(row=1, column=0, padx=8, pady=8, sticky="nsew")

    barra = tk.Scrollbar(ventana, orient="vertical", command=lista.yview)
    barra.grid(row=1, column=1, sticky="ns", pady=8)
    lista.config(yscrollcommand=barra.set)

    etiqueta_total = tk.Label(ventana, text="0 productos")
    etiqueta_total.grid(row=2, column=0, padx=8, pady=4, sticky="w")

    ventana.grid_rowconfigure(1, weight=1)
    ventana.grid_columnconfigure(0, weight=1)

    def cargar():
        lista.delete(0, tk.END)
        con = sqlite3.connect("empresa.db")
        cur = con.cursor()
        # Traemos productos; el costo promedio se calcula con dos consultas simples por producto (SUM)
        cur.execute("SELECT id_producto, IFNULL(codigo,''), COALESCE(stock,0) FROM productos ORDER BY codigo")
        productos = cur.fetchall()
        total_items = 0
        for (pid, codigo, stock) in productos:
            # SUM simples
            cur.execute("SELECT COALESCE(SUM(cantidad),0), COALESCE(SUM(precio_total),0.0) FROM compras WHERE producto_id=?", (pid,))
            sumas = cur.fetchone()
            suma_cant, suma_total = sumas if sumas else (0, 0.0)
            costo_unit = None
            if suma_cant and suma_cant > 0:
                try:
                    costo_unit = round(float(suma_total) / float(suma_cant), 2)
                except Exception:
                    costo_unit = None
            costo_txt = f"Q{costo_unit:.2f}" if costo_unit is not None else "s/d"
            lista.insert(tk.END, f"COD:{codigo} | Stock:{stock} | Costo/U:{costo_txt}")
            total_items += 1
        con.close()
        etiqueta_total.config(text=f"{total_items} productos")

    tk.Button(ventana, text="Actualizar", command=cargar).grid(row=0, column=1, padx=8)
    cargar()

def ventana_ordenes_trabajo(padre):
    ventana = tk.Toplevel(padre)
    ventana.title("Órdenes de Trabajo")
    ventana.geometry("420x420")

    tk.Label(ventana, text="Órdenes de Trabajo", font=("Arial", 14, "bold")).pack(pady=10)
    tk.Button(ventana, text="Crear Orden de Trabajo", font=("Arial", 12), width=28,
              command=lambda: ventana_crear_orden(ventana)).pack(pady=8)
    tk.Button(ventana, text="Mostrar Órdenes de Trabajo", font=("Arial", 12), width=28,
              command=lambda: ventana_listar_ordenes(ventana)).pack(pady=8)

def ventana_crear_orden(padre):
    ventana = tk.Toplevel(padre)
    ventana.title("Crear Orden")
    ventana.geometry("560x340")

    tk.Label(ventana, text="ID del cliente:", font=("Arial", 12)).grid(row=0, column=0, padx=8, pady=6, sticky="e")
    entrada_id_cli = tk.Entry(ventana, font=("Arial", 12), width=18)
    entrada_id_cli.grid(row=0, column=1, padx=8, pady=6, sticky="w")
    tk.Button(ventana, text="Ver datos", font=("Arial", 11),
              command=lambda: mostrar_cliente_por_id(ventana, entrada_id_cli.get().strip())).grid(row=0, column=2, padx=6, pady=6)

    tk.Label(ventana, text="Falla Registrada:", font=("Arial", 12)).grid(row=1, column=0, padx=8, pady=6, sticky="e")
    entrada_falla = tk.Entry(ventana, font=("Arial", 12), width=30)
    entrada_falla.grid(row=1, column=1, columnspan=2, padx=8, pady=6, sticky="w")

    tk.Label(ventana, text="Fecha de Revisión:", font=("Arial", 12)).grid(row=2, column=0, padx=8, pady=6, sticky="e")
    entrada_fecha = tk.Entry(ventana, font=("Arial", 12), width=30)
    entrada_fecha.grid(row=2, column=1, columnspan=2, padx=8, pady=6, sticky="w")

    def guardar_orden():
        cid_txt = entrada_id_cli.get().strip()
        falla = entrada_falla.get().strip()
        fecha_rev = entrada_fecha.get().strip()

        if cid_txt == "" or not cid_txt.isdigit():
            messagebox.showwarning("Validación", "Ingresa un ID de cliente numérico", parent=ventana)
            return
        if falla == "":
            messagebox.showwarning("Validación", "Describe la falla registrada", parent=ventana)
            return

        if not obtener_cliente_por_id(cid_txt):
            messagebox.showerror("Cliente", "No existe un cliente con ese ID", parent=ventana)
            return

        from datetime import datetime
        ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        con = sqlite3.connect("empresa.db")
        cur = con.cursor()
        cur.execute(
            "INSERT INTO ordenes_trabajo (cliente_id, falla, fecha_revision, fecha_creacion) VALUES (?,?,?,?)",
            (int(cid_txt), falla, fecha_rev if fecha_rev else None, ts)
        )
        con.commit()
        con.close()

        messagebox.showinfo("Órdenes", "Orden creada correctamente.", parent=ventana)
        ventana.destroy()

    tk.Button(ventana, text="Guardar Orden", font=("Arial", 12), bg="#4CAF50", fg="white", width=18,
              command=guardar_orden).grid(row=3, column=1, pady=16)
    tk.Button(ventana, text="Cancelar", font=("Arial", 12), width=12,
              command=ventana.destroy).grid(row=3, column=2, padx=6, pady=16)


def ventana_listar_ordenes(padre):
    ventana = tk.Toplevel(padre)
    ventana.title("Órdenes de Trabajo")
    ventana.geometry("860x460")

    tk.Label(ventana, text="Listado de Órdenes", font=("Arial", 13, "bold")).grid(row=0, column=0, padx=8, pady=8, sticky="w")

    lista = tk.Listbox(ventana, width=120, height=18)
    lista.grid(row=1, column=0, padx=8, pady=8, sticky="nsew")

    barra = tk.Scrollbar(ventana, orient="vertical", command=lista.yview)
    barra.grid(row=1, column=1, sticky="ns", pady=8)
    lista.config(yscrollcommand=barra.set)

    etiqueta_total = tk.Label(ventana, text="0 órdenes")
    etiqueta_total.grid(row=2, column=0, padx=8, pady=4, sticky="w")

    def cargar():
        lista.delete(0, tk.END)
        con = sqlite3.connect("empresa.db")
        cur = con.cursor()
        # Consultamos órdenes sin JOIN
        cur.execute("""
            SELECT id_orden, cliente_id, IFNULL(falla,''), IFNULL(fecha_revision,''), IFNULL(fecha_creacion,'')
            FROM ordenes_trabajo
            ORDER BY id_orden DESC
        """)
        filas = cur.fetchall()
        total = 0
        for (id_orden, cliente_id, falla, frev, fcrea) in filas:
            # Obtener nombre del cliente con SELECT simple
            cur.execute("SELECT IFNULL(nombre,'') FROM clientes WHERE id_cliente=?", (cliente_id,))
            fila_nom = cur.fetchone()
            nombre_cli = fila_nom[0] if fila_nom else ""
            lista.insert(tk.END, f"OT:{id_orden:04d} | Cliente:{cliente_id} - {nombre_cli} | Falla:{falla} | Rev:{frev} | Creada:{fcrea}")
            total += 1
        con.close()
        etiqueta_total.config(text=f"{total} órdenes")

    tk.Button(ventana, text="Actualizar", command=cargar).grid(row=0, column=1, padx=8)
    cargar()

def abrir_panel_principal(nombre, rol):
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

    lienzo = tk.Canvas(ventana, width=ancho, height=alto)
    lienzo.pack(fill="both", expand=True)
    lienzo.create_image(0, 0, image=fondo_tk, anchor="nw")

    lienzo.create_text(ancho//2, 80, text="Bienvenido, " + nombre, font=("Arial", 24, "bold"), fill="white")
    lienzo.create_text(ancho//2, 130, text="Rol: " + rol.upper(), font=("Arial", 18), fill="white")

    if rol == "administrador":
        botones = [
            ("Crear Clientes", lambda: ventana_crear_clientes(ventana)),
            ("Ver Asistencias", lambda: ventana_ver_asistencias(ventana)),
            ("Gestión de Clientes", lambda: ventana_gestion_clientes(ventana)),
            ("Inventario", lambda: ventana_inventario(ventana)),
            ("Listado Clientes por Visitar", lambda: ventana_listar_ordenes(ventana)),  # placeholder (usa órdenes para mostrar)
            ("Órdenes de Trabajo", lambda: ventana_ordenes_trabajo(ventana)),
            ("Material Instalado", None),
            ("Control de Cobros", None),
            ("Facturar", None),
            ("Crear Usuarios", None),
        ]
    elif rol == "cobrador":
        botones = [
            ("Asistencia", lambda: ventana_marcar_asistencia(ventana)),
            ("Gestión de Clientes", lambda: ventana_gestion_clientes(ventana)),
            ("Listado Clientes Visitar", lambda: ventana_listar_ordenes(ventana)),
            ("Control de Cobros", None),
            ("Facturar", None),
        ]
    else:
        botones = [
            ("Asistencia", lambda: ventana_marcar_asistencia(ventana)),
            ("Gestión de Clientes", lambda: ventana_gestion_clientes(ventana)),
            ("Listado Clientes por Visitar", lambda: ventana_listar_ordenes(ventana)),
            ("Control de Cobros", None),
            ("Facturar", None),
        ]

    y = 200
    for texto, cmd in botones:
        if cmd is None:
            b = tk.Button(ventana, text=texto, width=25, font=("Arial", 14),
                          command=lambda t=texto: messagebox.showinfo("Info", f"'{t}' aún no está implementado"))
        else:
            b = tk.Button(ventana, text=texto, width=25, font=("Arial", 14), command=cmd)
        lienzo.create_window(ancho//2, y, window=b)
        y += 50

    boton_salir = tk.Button(ventana, text="Cerrar Sesión", command=ventana.destroy, bg="red", fg="white", font=("Arial", 14), width=25)
    lienzo.create_window(ancho//2, y + 20, window=boton_salir)

    ventana.fondo_tk = fondo_tk
    ventana.mainloop()


def ventana_login_gui():
    global ventana_login, entrada_usuario, entrada_contraseña, imagen_logo
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

    lienzo = tk.Canvas(ventana_login, width=ancho, height=alto)
    lienzo.pack(fill="both", expand=True)
    lienzo.create_image(0, 0, image=fondo_tk, anchor="nw")

    logo = Image.open(ruta_logo)
    logo = logo.resize((300, 300), Image.Resampling.LANCZOS)
    imagen_logo = ImageTk.PhotoImage(logo)
    lienzo.create_image(ancho//2, 200, image=imagen_logo)

    lienzo.create_text(ancho//2, 380, text="Inicio de Sesión", font=("Arial", 20, "bold"), fill="black")
    lienzo.create_text(ancho//2, 430, text="Usuario:", font=("Arial", 14), fill="black")
    lienzo.create_text(ancho//2, 490, text="Contraseña:", font=("Arial", 14), fill="black")

    entrada_usuario = tk.Entry(ventana_login, font=("Arial", 14))
    lienzo.create_window(ancho//2, 460, window=entrada_usuario, width=250)
    entrada_contraseña= tk.Entry(ventana_login, show="*", font=("Arial", 14))
    lienzo.create_window(ancho//2, 520, window=entrada_contraseña, width=250)
    boton_login= tk.Button(ventana_login, text="Iniciar Sesión", command=verificar_inicio,
                           bg="#4CAF50", fg="white", font=("Arial", 14), width=20)
    lienzo.create_window(ancho//2, 580, window=boton_login)
    boton_salir = tk.Button(ventana_login, text="Salir", command=ventana_login.destroy,
                            bg="red", fg="white", font=("Arial", 14), width=20)
    lienzo.create_window(ancho//2, 640, window=boton_salir)

    navegar_con_enter(entrada_usuario, entrada_contraseña)
    funcion_login_validado = validar_y_ejecutar(
        [entrada_usuario, entrada_contraseña],
        verificar_inicio
    )
    configurar_teclado_rapido(entrada_contraseña, funcion_login_validado)
    configurar_teclado_rapido(boton_login, verificar_inicio)
    configurar_teclado_rapido(ventana_login, funcion_escape=ventana_login.destroy)
    entrada_usuario.focus()

    lienzo.create_text(ancho//2, 680, text="Usa ENTER para navegar, ESC para salir...",
                       font=("Arial", 10,), fill="gray")

    ventana_login.fondo_tk = fondo_tk
    ventana_login.mainloop()

if __name__ == "__main__":
    crear_tablas()
    ventana_login_gui()
