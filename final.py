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
        estado VARCHAR(50) DEFAULT 'ACTIVO',
        por_cobrar BOOLEAN DEFAULT 1,
        fecha_ultimo_cobro VARCHAR (50)
    )
    """)
    try:
        cur.execute("SELECT por_cobrar FROM clientes LIMIT 1")
    except sqlite3.OperationalError:
        cur.execute("ALTER TABLE clientes ADD COLUMN por_cobrar BOOLEAN DEFAULT 1")

    try:
        cur.execute("SELECT fecha_ultimo_cobro FROM clientes LIMIT 1")
    except sqlite3.OperationalError:
        cur.execute("ALTER TABLE clientes ADD COLUMN fecha_ultimo_cobro VARCHAR(50)")

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
    cur.execute("""
    CREATE TABLE IF NOT EXISTS material_instalado ( 
    id_instalacion INTEGER PRIMARY KEY AUTOINCREMENT, 
    cliente_id INTEGER NOT NULL, 
    producto_id INTEGER NOT NULL, 
    cantidad INTEGER NOT NULL, 
    tecnico VARCHAR(50), 
    fecha_instalacion VARCHAR(50), 
    observaciones TEXT, 
    FOREIGN KEY (cliente_id) REFERENCES clientes (id_cliente),
    FOREIGN KEY (producto_id) REFERENCES productos (id_producto)
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
        cur.execute("INSERT INTO clientes (nombre, nit, telefono, direccion, estado, por_cobrar) VALUES (?,?,?,?,?,?)",
                    (nom, nit if nit else None, tel if tel else None, dire if dire else None, "ACTIVO", 1))
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
    ventana.geometry("800x550")

    configurar_teclado_rapido(ventana, funcion_escape=ventana.destroy)

    tk.Label(ventana, text="Usuario:").grid(row=0, column=0, padx=6, pady=6)
    entrada_usuario_busq = tk.Entry(ventana, width=18)
    entrada_usuario_busq.grid(row=0, column=1, padx=6, pady=6)

    tk.Label(ventana, text="Fecha (YYYY-MM-DD):").grid(row=0, column=2, padx=6, pady=6)
    entrada_fecha = tk.Entry(ventana, width=14)
    entrada_fecha.grid(row=0, column=3, padx=6, pady=6)

    marco_lista = tk.Frame(ventana)
    marco_lista.grid(row=1, column=0, columnspan=5, padx=8, pady=8, sticky="nsew")

    lista = tk.Listbox(marco_lista, width=100, height=20)
    lista.pack(side="left", fill="both", expand=True)

    scrollbar = tk.Scrollbar(marco_lista, orient="vertical", command=lista.yview)
    scrollbar.pack(side="right", fill="y")
    lista.config(yscrollcommand=scrollbar.set)

    etiqueta_contador = tk.Label(ventana, text="0 registros encontrados")
    etiqueta_contador.grid(row=2, column=0, columnspan=3, padx=8, pady=4, sticky="w")

    def cargar_asistencia():
        lista.delete(0, tk.END)
        usuario_like = f"%{entrada_usuario_busq.get().strip()}%"
        fecha_txt = entrada_fecha.get().strip()

        con = sqlite3.connect("empresa.db")
        cur = con.cursor()

        try:
            if fecha_txt:
                cur.execute(
                    "SELECT usuario, accion, fecha_hora FROM asistencia "
                    "WHERE usuario LIKE ? AND fecha_hora LIKE ? "
                    "ORDER BY id_asistencia DESC",
                    (usuario_like, f"{fecha_txt}%")
                )
            else:
                cur.execute(
                    "SELECT usuario, accion, fecha_hora FROM asistencia "
                    "WHERE usuario LIKE ? "
                    "ORDER BY id_asistencia DESC",
                    (usuario_like,)
                )

            filas = cur.fetchall()

            if not filas:
                lista.insert(tk.END, "No se encontraron registros")
            else:
                for usuario, accion, fecha in filas:
                    lista.insert(tk.END, f"{fecha} | {usuario} | {accion}")

            etiqueta_contador.config(text=f"{len(filas)} registros encontrados")

        except sqlite3.Error as e:
            lista.insert(tk.END, f"Error en base de datos: {e}")
        finally:
            con.close()

    boton_cargar = crear_boton_con_teclado(
        ventana,
        "Cargar",
        cargar_asistencia,
        0,
        [4, 1]
    )
    configurar_teclado_rapido(entrada_usuario_busq, funcion_enter=cargar_asistencia)
    configurar_teclado_rapido(entrada_fecha, funcion_enter=cargar_asistencia)

    def limpiar_busqueda():
        entrada_usuario_busq.delete(0, tk.END)
        entrada_fecha.delete(0, tk.END)
        cargar_asistencia()
        entrada_usuario_busq.focus()

    boton_limpiar = tk.Button(ventana, text="Limpiar", command=limpiar_busqueda, width=12)
    boton_limpiar.grid(row=0, column=5, padx=6, pady=6)
    configurar_teclado_rapido(boton_limpiar, funcion_enter=limpiar_busqueda)

    cargar_asistencia()
    entrada_usuario_busq.focus()

    ventana.grid_rowconfigure(1, weight=1)
    ventana.grid_columnconfigure(0, weight=1)

def ventana_marcar_asistencia(padre):
    ventana = tk.Toplevel(padre)
    ventana.title("Marcar Asistencia")
    ventana.geometry("450x280")

    configurar_teclado_rapido(ventana, funcion_escape=ventana.destroy)

    tk.Label(ventana, text="Registro de Asistencia", font=("Arial", 14, "bold")).grid(
        row=0, column=0, columnspan=2, pady=15
    )

    tk.Label(ventana, text="Usuario:", font=("Arial", 12)).grid(row=1, column=0, padx=8, pady=8, sticky="e")
    entrada_user = tk.Entry(ventana, font=("Arial", 12), width=20)
    entrada_user.grid(row=1, column=1, padx=8, pady=8, sticky="w")

    tk.Label(ventana, text="Contraseña:", font=("Arial", 12)).grid(row=2, column=0, padx=8, pady=8, sticky="e")
    entrada_pwd = tk.Entry(ventana, font=("Arial", 12), width=20, show='*')
    entrada_pwd.grid(row=2, column=1, padx=8, pady=8, sticky="w")

    def marcar(accion):
        u = entrada_user.get().strip()
        p = entrada_pwd.get().strip()

        if not u or not p:
            messagebox.showwarning("Validación", "Usuario y contraseña requeridos")
            entrada_user.focus()
            return

        con = sqlite3.connect("empresa.db")
        cur = con.cursor()
        cur.execute("SELECT nombre FROM usuarios WHERE usuario=? AND contraseña=?", (u, p))
        resultado = cur.fetchone()

        if not resultado:
            con.close()
            messagebox.showerror("Asistencia", "Credenciales inválidas")
            entrada_pwd.delete(0, tk.END)
            entrada_pwd.focus()
            return

        nombre_usuario = resultado[0]
        from datetime import datetime
        ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        cur.execute("INSERT INTO asistencia (usuario, accion, fecha_hora) VALUES (?,?,?)", (u, accion, ts))
        con.commit()
        con.close()

        messagebox.showinfo(
            "Asistencia Registrada",
            f"{accion.capitalize()} registrada para:\n"
            f"Usuario: {nombre_usuario}\n"
            f"Fecha/Hora: {ts}"
        )

        entrada_pwd.delete(0, tk.END)
        entrada_user.focus()

    marco_botones = tk.Frame(ventana)
    marco_botones.grid(row=3, column=0, columnspan=2, pady=20)

    boton_entrada = tk.Button(
        marco_botones,
        text=" Marcar ENTRADA",
        command=lambda: marcar('entrada'),
        font=("Arial", 12),
        bg="#4CAF50",
        fg="white",
        width=16
    )
    boton_entrada.grid(row=0, column=0, padx=5)
    configurar_teclado_rapido(boton_entrada, funcion_enter=lambda: marcar('entrada'))

    boton_salida = tk.Button(
        marco_botones,
        text=" Marcar SALIDA",
        command=lambda: marcar('salida'),
        font=("Arial", 12),
        bg="#2196F3",
        fg="white",
        width=16
    )
    boton_salida.grid(row=0, column=1, padx=5)
    configurar_teclado_rapido(boton_salida, funcion_enter=lambda: marcar('salida'))

    navegar_con_enter(entrada_user, entrada_pwd)

    configurar_teclado_rapido(entrada_pwd, funcion_enter=lambda: marcar('entrada'))

    tk.Label(ventana, text="💡 ENTER en contraseña marca ENTRADA • ESC para salir",
             font=("Arial", 9), fg="gray").grid(row=4, column=0, columnspan=2, pady=5)

    entrada_user.focus()

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
    ventana.geometry("420x280")

    tk.Label(ventana, text="Productos", font=("Arial", 14, "bold")).pack(pady=10)

    tk.Button(ventana, text="Agregar Producto", font=("Arial", 12), width=22,
              command=lambda: ventana_crear_productos(ventana)).pack(pady=6)

    tk.Button(ventana, text="Mostrar Productos", font=("Arial", 12), width=22,
              command=lambda: ventana_listar_productos(ventana)).pack(pady=6)
    tk.Button(ventana, text="Eliminar Productos", font=("Arial", 12), width=22,
              command=lambda: ventana_eliminar_productos(ventana), bg="#f44336", fg="white").pack(pady=6)

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

    tk.Label(ventana, text="Precio unit o por mt:", font=("Arial", 12)).grid(row=2, column=0, padx=8, pady=6, sticky="e")
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

def ventana_eliminar_productos(padre):
    ventana = tk.Toplevel(padre)
    ventana.title("Eliminar Productos")
    ventana.geometry("700x500")

    tk.Label(ventana, text="Eliminar Productos", font=("Arial", 14, "bold")).pack(pady=10)

    tk.Label(ventana, text="Buscar producto (código o nombre):", font=("Arial", 12)).pack(pady=5)
    entrada_busqueda = tk.Entry(ventana, font=("Arial", 12), width=30)
    entrada_busqueda.pack(pady=5)

    lista = tk.Listbox(ventana, width=80, height=15)
    lista.pack(padx=20, pady=10, fill="both", expand=True)

    scrollbar = tk.Scrollbar(lista)
    scrollbar.pack(side="right", fill="y")
    lista.config(yscrollcommand=scrollbar.set)
    scrollbar.config(command=lista.yview)

    productos_encontrados = []

    def buscar_productos():
        nonlocal productos_encontrados
        lista.delete(0, tk.END)
        busqueda = entrada_busqueda.get().strip()

        if not busqueda:
            messagebox.showwarning("Búsqueda", "Ingresa un código o nombre para buscar")
            return

        con = sqlite3.connect("empresa.db")
        cur = con.cursor()

        if busqueda.isdigit():
            cur.execute("""
                SELECT id_producto, codigo, descripcion, precio, COALESCE(stock,0) 
                FROM productos 
                WHERE id_producto = ? OR codigo LIKE ? OR descripcion LIKE ?
            """, (int(busqueda), f"%{busqueda}%", f"%{busqueda}%"))
        else:
            cur.execute("""
                SELECT id_producto, codigo, descripcion, precio, COALESCE(stock,0) 
                FROM productos 
                WHERE codigo LIKE ? OR descripcion LIKE ?
            """, (f"%{busqueda}%", f"%{busqueda}%"))

        productos_encontrados = cur.fetchall()
        con.close()

        if not productos_encontrados:
            lista.insert(tk.END, "No se encontraron productos")
        else:
            for id_prod, codigo, descripcion, precio, stock in productos_encontrados:
                lista.insert(tk.END, f"ID:{id_prod} | COD:{codigo} | {descripcion} | Q{precio} | Stock:{stock}")

    def eliminar_seleccionado():
        seleccion = lista.curselection()
        if not seleccion:
            messagebox.showwarning("Selección", "Selecciona un producto de la lista")
            return

        producto = productos_encontrados[seleccion[0]]
        id_prod, codigo, descripcion, precio, stock = producto

        if stock > 0:
            messagebox.showwarning("Stock",
                                   f"No se puede eliminar '{descripcion}'\nTodavía tiene {stock} unidades en stock\nPrimero debe vender o ajustar el inventario")
            return

        confirmar = messagebox.askyesno(
            "Confirmar Eliminación",
            f"¿Estás seguro de eliminar este producto?\n\n"
            f"Código: {codigo}\n"
            f"Descripción: {descripcion}\n"
            f"Precio: Q{precio}"
        )

        if not confirmar:
            return

        con = sqlite3.connect("empresa.db")
        cur = con.cursor()

        try:
            cur.execute("DELETE FROM productos WHERE id_producto = ?", (id_prod,))
            con.commit()
            messagebox.showinfo("Éxito", f"Producto '{descripcion}' eliminado correctamente")
            buscar_productos()
        except sqlite3.Error as e:
            messagebox.showerror("Error", f"No se pudo eliminar el producto: {e}")
        finally:
            con.close()

    marco_botones = tk.Frame(ventana)
    marco_botones.pack(pady=10)

    tk.Button(marco_botones, text=" Buscar", command=buscar_productos,
              font=("Arial", 12), bg="#2196F3", fg="white").pack(side="left", padx=5)

    tk.Button(marco_botones, text=" Eliminar Seleccionado", command=eliminar_seleccionado,
              font=("Arial", 12), bg="#f44336", fg="white").pack(side="left", padx=5)

    tk.Button(marco_botones, text="Cerrar", command=ventana.destroy,
              font=("Arial", 12)).pack(side="left", padx=5)

    entrada_busqueda.bind("<Return>", lambda e: buscar_productos())
    entrada_busqueda.focus()

def ventana_registrar_compra(padre):
    ventana = tk.Toplevel(padre)
    ventana.title("Registrar Compra")
    ventana.geometry("600x550")
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

        cur.execute("""
            SELECT id_compra, numero_factura, proveedor_id, producto_id, cantidad, precio_total, IFNULL(fecha_hora,'')
            FROM compras
            ORDER BY id_compra DESC
        """)
        filas = cur.fetchall()

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
        cur.execute("SELECT id_producto, IFNULL(codigo,''), COALESCE(stock,0) FROM productos ORDER BY codigo")
        productos = cur.fetchall()
        total_items = 0
        for (pid, codigo, stock) in productos:

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
    etiqueta_total.grid(row=2, column=0, padx=8, pady=4, sticky="w")

def ventana_reportar_material(padre):
    ventana = tk.Toplevel(padre)
    ventana.title("Reportar Material Usado")
    ventana.geometry("500x400")

    tk.Label(ventana, text="Reportar Material de Instalacion", font=("Arial", 14, "bold")).pack(pady=15)

    tk.Label(ventana, text="ID Cliente:", font=("Arial", 12)).pack(pady=5)
    entrada_cliente_id = tk.Entry(ventana, font=("Arial", 12), width=20)
    entrada_cliente_id.pack(pady=5)

    tk.Label(ventana, text="Codigo Producto:", font=("Arial", 12)).pack(pady=5)
    entrada_producto_cod = tk.Entry(ventana, font=("Arial", 12), width=20)
    entrada_producto_cod.pack(pady=5)

    tk.Label(ventana, text="Cantidad usada:", font=("Arial", 12)).pack(pady=5)
    entrada_cantidad = tk.Entry(ventana, font=("Arial", 12), width=10)
    entrada_cantidad.pack(pady=5)

    tk.Label(ventana, text="Tu nombre:", font=("Arial", 12)).pack(pady=5)
    entrada_tecnico = tk.Entry(ventana, font=("Arial", 12), width=25)
    entrada_tecnico.pack(pady=5)

    def reportar():
        cliente_id = entrada_cliente_id.get().strip()
        producto_cod = entrada_producto_cod.get().strip()
        cantidad = entrada_cantidad.get().strip()
        tecnico = entrada_tecnico.get().strip()

        if not all([cliente_id, producto_cod, cantidad, tecnico]):
            messagebox.showwarning("Error", "Completa todos los campos")
            return
        try:
            cliente_id = int(cliente_id)
            cantidad = int(cantidad)
        except:
            messagebox.showwarning("Error", "ID Cliente y Cantidad deben ser numeros")
            return

        con = sqlite3.connect("empresa.db")
        cur = con.cursor()

        cur.execute("SELECT nombre FROM clientes WHERE id_cliente=?", (cliente_id,))
        cliente = cur.fetchone()
        if not cliente:
            messagebox.showerror("Error", f"No existe cliente con ID {cliente_id}")
            con.close()
            return

        cur.execute("SELECT id_producto, descripcion, COALESCE(stock,0) FROM productos WHERE codigo=?", (producto_cod,))
        producto = cur.fetchone()
        if not producto:
            messagebox.showerror("Error", f"No existe producto con codigo {producto_cod}")
            con.close()
            return
        producto_id, descripcion, stock = producto

        if cantidad > stock:
            messagebox.showerror("Stock", f"No hay suficiente stock. Disponible: {stock}")
            con.close()
            return

        from datetime import datetime
        fecha = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        cur.execute(
            "INSERT INTO material_instalado (cliente_id, producto_id, cantidad, tecnico, fecha_instalacion) VALUES (?, ?, ?, ?, ?)",
            (cliente_id, producto_id, cantidad, tecnico, fecha))

        cur.execute("UPDATE productos SET stock = stock - ? WHERE id_producto=?", (cantidad, producto_id))

        con.commit()
        con.close()

        messagebox.showinfo("Exito", f"Material reportado:\n{descripcion} x{cantidad}\nCliente ID: {cliente_id}")

        entrada_producto_cod.delete(0, tk.END)
        entrada_cantidad.delete(0, tk.END)

    tk.Button(ventana, text="Reportar Material", command=reportar, font=("Arial", 12), bg="#4CAF50", fg="white",
              width=20).pack(pady=20)

def ventana_ver_material_instalado(padre):
    ventana = tk.Toplevel(padre)
    ventana.title("Material Instalado - Reportes")
    ventana.geometry("900x500")

    tk.Label(ventana, text="Material Instalado por Tecnicos", font=("Arial", 16, "bold")).pack(pady=15)

    marco_lista = tk.Frame(ventana)
    marco_lista.pack(fill="both", expand=True, padx=20, pady=10)

    lista = tk.Listbox(marco_lista, font=("Arial", 10), width=110)
    lista.pack(side="left", fill="both", expand=True)

    scrollbar = tk.Scrollbar(marco_lista, orient="vertical", command=lista.yview)
    scrollbar.pack(side="right", fill="y")
    lista.config(yscrollcommand=scrollbar.set)

    def cargar_reportes():
        lista.delete(0, tk.END)

        con = sqlite3.connect("empresa.db")
        cur = con.cursor()

        cur.execute("""
            SELECT m.fecha_instalacion, m.tecnico, c.nombre, p.descripcion, m.cantidad 
            FROM material_instalado m
            JOIN clientes c ON m.cliente_id = c.id_cliente
            JOIN productos p ON m.producto_id = p.id_producto
            ORDER BY m.fecha_instalacion DESC
        """)

        reportes = cur.fetchall()
        con.close()

        if not reportes:
            lista.insert(tk.END, "No hay reportes de material instalado")
        else:
            for fecha, tecnico, cliente, producto, cantidad in reportes:
                lista.insert(tk.END, f"{fecha} | {tecnico} | {cliente} | {producto} x{cantidad}")

    marco_botones = tk.Frame(ventana)
    marco_botones.pack(pady=10)

    tk.Button(marco_botones, text="Actualizar", command=cargar_reportes, font=("Arial", 12)).pack(side="left", padx=5)

    tk.Button(marco_botones, text="Cerrar", command=ventana.destroy, font=("Arial", 12), bg="#f44336", fg="white").pack(
        side="left", padx=5)

    cargar_reportes()

def ventana_clientes_por_cobrar(padre):
    ventana = tk.Toplevel(padre)
    ventana.title("Clientes por Cobrar")
    ventana.geometry("1000x700")

    tk.Label(ventana, text="Seguimiento de Cobros", font=("Arial", 16, "bold")).pack(pady=15)

    def mostrar_estadisticas():
        con = sqlite3.connect("empresa.db")
        cur = con.cursor()

        cur.execute("SELECT COUNT(*) FROM clientes WHERE estado='ACTIVO' AND por_cobrar=1")
        pendientes = cur.fetchone()[0]

        cur.execute("SELECT COUNT(*) FROM clientes WHERE estado='ACTIVO' AND por_cobrar=0")
        cobrados = cur.fetchone()[0]

        cur.execute("SELECT COUNT(*) FROM clientes WHERE estado='ACTIVO'")
        total = cur.fetchone()[0]

        con.close()

        messagebox.showinfo("Estadisticas",
                            f"Clientes activos: {total}\nPendientes de cobro: {pendientes}\nYa cobrados: {cobrados}\nProgreso: {cobrados}/{total}")

    marco_principal = tk.Frame(ventana)
    marco_principal.pack(fill="both", expand=True, padx=20, pady=10)

    marco_controles = tk.Frame(marco_principal)
    marco_controles.pack(fill="x", pady=10)

    marco_lista = tk.Frame(marco_principal)
    marco_lista.pack(fill="both", expand=True)

    canvas = tk.Canvas(marco_lista, bg="white")
    scrollbar = tk.Scrollbar(marco_lista, orient="vertical", command=canvas.yview)
    scrollable_frame = tk.Frame(canvas, bg="white")

    scrollable_frame.bind(
        "<Configure>",
        lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
    )
    canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
    canvas.configure(yscrollcommand=scrollbar.set)

    canvas.pack(side="left", fill="both", expand=True)
    scrollbar.pack(side="right", fill="y")

    check_vars = []
    clientes_data = []
    label_clientes = []

    def cargar_clientes():
        for widget in scrollable_frame.winfo_children():
            widget.destroy()
        check_vars.clear()
        clientes_data.clear()
        label_clientes.clear()

        con = sqlite3.connect("empresa.db")
        cur = con.cursor()

        cur.execute("""
            SELECT id_cliente, nombre, telefono, direccion, fecha_ultimo_cobro, por_cobrar
            FROM clientes 
            WHERE estado = 'ACTIVO'
            ORDER BY por_cobrar DESC, nombre ASC
        """)

        clientes = cur.fetchall()
        con.close()

        if not clientes:
            tk.Label(scrollable_frame, text="No hay clientes activos",
                     font=("Arial", 12), fg="gray", bg="white").pack(pady=20)
        else:
            pendientes = 0
            cobrados = 0

            for i, (id_cliente, nombre, telefono, direccion, fecha_cobro, por_cobrar) in enumerate(clientes):
                frame_cliente = tk.Frame(scrollable_frame, relief="solid", bd=1, bg="white")
                frame_cliente.pack(fill="x", padx=10, pady=3)

                var = tk.BooleanVar(value=not por_cobrar)
                check_vars.append(var)
                clientes_data.append((id_cliente, por_cobrar))

                check = tk.Checkbutton(frame_cliente, variable=var,
                                       command=lambda idx=i: toggle_cobrado(idx),
                                       bg="white")
                check.pack(side="left", padx=8, pady=8)

                info_text = f"{id_cliente} - {nombre}"
                if telefono:
                    info_text += f" | Tel: {telefono}"
                if direccion:
                    info_text += f" | {direccion}"

                if por_cobrar:
                    label = tk.Label(frame_cliente, text=info_text, font=("Arial", 11),
                                     bg="white", fg="black", anchor="w", justify="left")
                    pendientes += 1
                else:
                    label = tk.Label(frame_cliente, text=info_text, font=("Arial", 11),
                                     bg="white", fg="gray", anchor="w", justify="left")
                    label.config(font=("Arial", 11, "overstrike"))
                    cobrados += 1

                label.pack(side="left", fill="x", expand=True, padx=5, pady=8)
                label_clientes.append(label)

                tk.Button(frame_cliente, text="Ver", font=("Arial", 9),
                          command=lambda cid=id_cliente: mostrar_detalle_cliente(cid),
                          bg="#e0e0e0", relief="flat", width=3).pack(side="right", padx=5)

            if pendientes > 0 and cobrados > 0:
                separator = tk.Frame(scrollable_frame, height=2, bg="#e0e0e0")
                separator.pack(fill="x", padx=20, pady=10)

                tk.Label(scrollable_frame, text=f"{cobrados} elementos completados",
                         font=("Arial", 11, "italic"), fg="gray", bg="white").pack(pady=5)

        ventana.title(f"Clientes por Cobrar ({pendientes} pendientes, {cobrados} cobrados)")

    def toggle_cobrado(index):
        id_cliente, estado_actual = clientes_data[index]
        nuevo_estado = not estado_actual

        con = sqlite3.connect("empresa.db")
        cur = con.cursor()

        from datetime import datetime
        fecha_cobro = datetime.now().strftime("%Y-%m-%d") if nuevo_estado == 0 else None

        cur.execute("UPDATE clientes SET por_cobrar = ?, fecha_ultimo_cobro = ? WHERE id_cliente = ?",
                    (nuevo_estado, fecha_cobro, id_cliente))

        con.commit()
        con.close()

        if nuevo_estado == 0:
            label_clientes[index].config(fg="gray", font=("Arial", 11, "overstrike"))
        else:
            label_clientes[index].config(fg="black", font=("Arial", 11))

        cargar_clientes()

    def mostrar_detalle_cliente(cliente_id):
        fila = obtener_cliente_por_id(cliente_id)
        if fila:
            cid, nombre, nit, tel, dire, estado = fila
            con = sqlite3.connect("empresa.db")
            cur = con.cursor()
            cur.execute("SELECT por_cobrar, fecha_ultimo_cobro FROM clientes WHERE id_cliente=?", (cliente_id,))
            estado_cobro, fecha_cobro = cur.fetchone()
            con.close()

            estado_texto = "PENDIENTE de cobro" if estado_cobro else f"COBRADO el {fecha_cobro}"

            mensaje = f"ID: {cid}\nNombre: {nombre}\nTel: {tel}\nDir: {dire}\nEstado: {estado}\nCobro: {estado_texto}"
            messagebox.showinfo("Detalle Cliente", mensaje)

    tk.Button(marco_controles, text="Actualizar", font=("Arial", 12),
              command=cargar_clientes).pack(side="left", padx=5)

    tk.Button(marco_controles, text="Estadisticas", font=("Arial", 12),
              command=mostrar_estadisticas).pack(side="left", padx=5)

    marco_botones = tk.Frame(ventana)
    marco_botones.pack(pady=10)

    tk.Button(marco_botones, text="Cerrar",
              command=ventana.destroy, font=("Arial", 12),
              bg="#f44336", fg="white").pack(side="left", padx=5)
    cargar_clientes()

def ventana_crear_usuario(padre):
    ventana = tk.Toplevel(padre)
    ventana.title("Crear nuevo usuario")
    ventana.geometry("500x450")

    configurar_teclado_rapido(ventana, funcion_escape=ventana.destroy)
    tk.Label(ventana, text="Crear nuevo usuario", font=("Arial", 16, "bold")).pack(pady=20)
    marco_campos = tk.Frame(ventana)
    marco_campos.pack(pady=10, padx=20, fill="x")

    tk.Label(marco_campos, text="Nombre Completo:", font=("Arial", 12)).grid(row=0, column=0, padx=5, pady=8,
                                                                             sticky="e")
    entrada_nombre = tk.Entry(marco_campos, font=("Arial", 12), width=25)
    entrada_nombre.grid(row=0, column=1, padx=5, pady=8, sticky="w")

    tk.Label(marco_campos, text="Usuario:", font=("Arial", 12)).grid(row=1, column=0, padx=5, pady=8, sticky="e")
    entrada_usuario = tk.Entry(marco_campos, font=("Arial", 12), width=25)
    entrada_usuario.grid(row=1, column=1, padx=5, pady=8, sticky="w")

    tk.Label(marco_campos, text="Contraseña:", font=("Arial", 12)).grid(row=2, column=0, padx=5, pady=8, sticky="e")
    entrada_contraseña = tk.Entry(marco_campos, font=("Arial", 12), width=25, show="•")
    entrada_contraseña.grid(row=2, column=1, padx=5, pady=8, sticky="w")

    tk.Label(marco_campos, text="Confirmar Contraseña:", font=("Arial", 12)).grid(row=3, column=0, padx=5, pady=8,
                                                                                  sticky="e")
    entrada_confirmar = tk.Entry(marco_campos, font=("Arial", 12), width=25, show="•")
    entrada_confirmar.grid(row=3, column=1, padx=5, pady=8, sticky="w")

    tk.Label(marco_campos, text="Rol:", font=("Arial", 12)).grid(row=4, column=0, padx=5, pady=8, sticky="e")

    combo_rol = tk.StringVar(value="tecnico")
    opciones_rol =  tk.OptionMenu(marco_campos, combo_rol, "administrador", "cobrador", "tecnico")
    opciones_rol.config(font=("Arial", 12), width=22)
    opciones_rol.grid(row=4, column=1, padx=5, pady=8, sticky="w")

    def guardar_usuario():
        nombre = entrada_nombre.get().strip()
        usuario = entrada_usuario.get().strip()
        contraseña = entrada_contraseña.get().strip()
        confirmar = entrada_confirmar.get().strip()
        rol = combo_rol.get()

        if not  nombre:
            messagebox.showwarning("Validación", "El nombre completo es obligatorio")
            entrada_nombre.focus()
            return
        if not usuario:
            messagebox.showwarning("Validación", "El usuario es obligatorio")
            return
        if not contraseña:
            messagebox.showwarning("Validación", "La contraseña es obligatoria")
            return
        if contraseña != confirmar:
            messagebox.showwarning("Validación", "Las contraseñas no coinciden")
            entrada_contraseña.delete(0, tk.END)
            entrada_confirmar.delete(0, tk.END)
            entrada_contraseña.focus()
            return
        if len(contraseña)<4:
            messagebox.showwarning("Validación", "La contraseña debe tener al menos 4 caracteres")
            entrada_contraseña.focus()
            return

        con = sqlite3.connect("empresa.db")
        cur = con.cursor()
        cur.execute("SELECT COUNT (*) FROM usuarios WHERE usuario = ?", (usuario,))
        existe =  cur.fetchone()[0]> 0

        if existe:
            messagebox.showwarning("Error", f"El usuario {usuario} ya existe")
            entrada_usuario.delete(0, tk.END)
            entrada_usuario.focus()
            con.close()
            return

        try:
            cur.execute(
                "INSERT INTO usuarios (nombre, usuario, contraseña, rol) VALUES (?,?,?,?)",
                (nombre, usuario, contraseña, rol)
            )
            con.commit()
            messagebox.showinfo("Éxito", f"Usuarios '{usuario}' creado correctamente\nRol: {rol}")
            limpiar_campos()
        except sqlite3.Error as e:
            messagebox.showerror("Error", f"Error al crear usuario {e}")
        finally:
            con.close()

    def limpiar_campos():
        entrada_nombre.delete(0, tk.END)
        entrada_usuario.delete(0, tk.END)
        entrada_contraseña.delete(0, tk.END)
        entrada_confirmar.delete(0, tk.END)
        combo_rol.set("tecnico")
        entrada_nombre.focus()

    marco_botones = tk.Frame(ventana)
    marco_botones.pack(pady=20)

    boton_guardar = crear_boton_con_teclado(
        marco_botones,
        "Guardar Usuario",
        guardar_usuario,
        0,
        [0,1],
        "#4CAF50"
    )
    boton_limpiar= tk.Button(
        marco_botones,
        text="Limpiar Campos",
        command= limpiar_campos,
        font=("Arial", 12),
        bg= "#FF9800",
        fg="white",
        width=15
    )
    boton_limpiar.grid(row=0, column=1, pady=10)
    configurar_teclado_rapido(boton_limpiar, funcion_enter=limpiar_campos)

    boton_cerrar= tk.Button(
        marco_botones,
        text="Cerrar",
        command=ventana.destroy,
        font=("Arial", 12),
        bg="#f44336",
        fg="white",
        width=12
    )
    boton_cerrar.grid(row=0, column=2, padx=10)
    configurar_teclado_rapido(boton_cerrar, funcion_enter=ventana.destroy)

    navegar_con_enter(entrada_nombre, entrada_usuario)
    navegar_con_enter(entrada_usuario, entrada_contraseña)
    navegar_con_enter(entrada_contraseña, entrada_confirmar)

    funcion_guardar_validado = validar_y_ejecutar(
        [entrada_nombre, entrada_usuario, entrada_contraseña, entrada_confirmar],
        guardar_usuario
    )
    configurar_teclado_rapido(entrada_confirmar, funcion_enter=funcion_guardar_validado)
    configurar_teclado_rapido(opciones_rol, funcion_enter=funcion_guardar_validado)

    tk.Label(
        ventana,
        text="Usa ENTER para navegar, ESC para salir\nContraseña minima de 4 caracteres",
        font=("Arial", 9),
        fg="gray",
        justify="center").pack(pady=10)

    entrada_nombre.focus()

def ventana_cobros(padre):
    ventana = tk.Toplevel(padre)
    ventana.title("Sistema de Cobros")
    ventana.geometry("600x700")
    ventana.configure(bg='white')

    cliente_actual = None
    casillas = []

    tk.Label(ventana, text="SISTEMA DE COBROS", font=("Arial", 14, "bold"), bg='white').pack(pady=10)

    marco_busqueda = tk.Frame(ventana, bg='white')
    marco_busqueda.pack(pady=10)

    entrada_busqueda = tk.Entry(marco_busqueda, font=("Arial", 12), width=25)
    entrada_busqueda.pack(side="left", padx=5)

    def buscar_cliente():
        consulta = entrada_busqueda.get().strip()
        if not consulta:
            messagebox.showwarning("Búsqueda", "Ingrese código o nombre")
            return

        conexion = sqlite3.connect("empresa.db")
        cursor = conexion.cursor()

        if consulta.isdigit():
            cursor.execute("SELECT id_cliente, nombre FROM clientes WHERE id_cliente = ? AND estado='ACTIVO'",
                           (int(consulta),))
        else:
            cursor.execute("SELECT id_cliente, nombre FROM clientes WHERE nombre LIKE ? AND estado='ACTIVO'",
                           (f"%{consulta}%",))

        clientes = cursor.fetchall()
        conexion.close()

        lista_clientes.delete(0, tk.END)
        for id_cliente, nombre in clientes:
            lista_clientes.insert(tk.END, f"{id_cliente} - {nombre}")

    boton_buscar = tk.Button(marco_busqueda, text="Buscar", font=("Arial", 10), command=buscar_cliente, bg="#4CAF50",
                             fg="white")
    boton_buscar.pack(side="left", padx=5)

    lista_clientes = tk.Listbox(ventana, height=3, font=("Arial", 10))
    lista_clientes.pack(pady=5, padx=20, fill="x")

    marco_info = tk.Frame(ventana, bg='#f0f0f0', relief='solid', bd=1)
    marco_info.pack(pady=10, padx=20, fill="x")

    etiqueta_nombre = tk.Label(marco_info, text="Nombre: ---", font=("Arial", 10), bg='#f0f0f0')
    etiqueta_nombre.pack(anchor="w", padx=10, pady=2)

    etiqueta_direccion = tk.Label(marco_info, text="Dirección: ---", font=("Arial", 10), bg='#f0f0f0')
    etiqueta_direccion.pack(anchor="w", padx=10, pady=2)

    etiqueta_ultimo = tk.Label(marco_info, text="Último cobro: ---", font=("Arial", 10), bg='#f0f0f0')
    etiqueta_ultimo.pack(anchor="w", padx=10, pady=2)

    tk.Label(ventana, text="MESES PENDIENTES", font=("Arial", 11, "bold"), bg='white').pack(pady=5)

    marco_scroll = tk.Frame(ventana, bg='white')
    marco_scroll.pack(pady=5, padx=20, fill="both", expand=True)

    lienzo = tk.Canvas(marco_scroll, bg='white', height=150)
    barra_desplazamiento = tk.Scrollbar(marco_scroll, orient="vertical", command=lienzo.yview)
    marco_meses = tk.Frame(lienzo, bg='white')

    marco_meses.bind("<Configure>", lambda e: lienzo.configure(scrollregion=lienzo.bbox("all")))
    lienzo.create_window((0, 0), window=marco_meses, anchor="nw")
    lienzo.configure(yscrollcommand=barra_desplazamiento.set)

    lienzo.pack(side="left", fill="both", expand=True)
    barra_desplazamiento.pack(side="right", fill="y")

    marco_totales = tk.Frame(ventana, bg='white')
    marco_totales.pack(pady=10, fill="x")

    tk.Label(marco_totales, text="TOTAL:", font=("Arial", 12, "bold"), bg='white').pack(side="left", padx=10)

    etiqueta_total = tk.Label(marco_totales, text="Q 0.00", font=("Arial", 12, "bold"), bg='white', fg="#2E7D32")
    etiqueta_total.pack(side="left", padx=10)

    marco_abonar = tk.Frame(ventana, bg='white')
    marco_abonar.pack(pady=5)

    tk.Label(marco_abonar, text="Abonar la cantidad de:", font=("Arial", 11), bg='white').pack()

    etiqueta_abonar = tk.Label(marco_abonar, text="Q 0.00", font=("Arial", 14, "bold"), bg='white', fg="#D32F2F")
    etiqueta_abonar.pack()

    marco_botones = tk.Frame(ventana, bg='white')
    marco_botones.pack(pady=15)

    def seleccionar_cliente(evento):
        seleccion = lista_clientes.curselection()
        if not seleccion:
            return

        texto = lista_clientes.get(seleccion[0])
        cliente_id = int(texto.split(' - ')[0])
        nonlocal cliente_actual
        cliente_actual = cliente_id

        conexion = sqlite3.connect("empresa.db")
        cursor = conexion.cursor()
        cursor.execute("SELECT nombre, direccion, fecha_ultimo_cobro FROM clientes WHERE id_cliente=?", (cliente_id,))
        datos_cliente = cursor.fetchone()
        conexion.close()

        if datos_cliente:
            nombre, direccion, ultimo_cobro = datos_cliente
            etiqueta_nombre.config(text=f"Nombre: {nombre}")
            etiqueta_direccion.config(text=f"Dirección: {direccion or 'No registrada'}")
            etiqueta_ultimo.config(text=f"Último cobro: {ultimo_cobro or 'Nunca'}")

            cargar_meses_pendientes(ultimo_cobro)

    def cargar_meses_pendientes(ultimo_pago):
        for widget in marco_meses.winfo_children():
            widget.destroy()

        nonlocal casillas
        casillas = []

        from datetime import datetime

        nombres_meses = ["ENERO", "FEBRERO", "MARZO", "ABRIL", "MAYO", "JUNIO",
                         "JULIO", "AGOSTO", "SEPTIEMBRE", "OCTUBRE", "NOVIEMBRE", "DICIEMBRE"]

        hoy = datetime.now()
        mes_actual = hoy.month
        año_actual = hoy.year

        if not ultimo_pago:
            nombre_mes = f"{nombres_meses[mes_actual - 1]} {año_actual}"

            marco_mes = tk.Frame(marco_meses, bg='white')
            marco_mes.pack(fill="x", pady=1)

            variable = tk.BooleanVar()
            casillas.append(variable)

            casilla = tk.Checkbutton(marco_mes, variable=variable, command=calcular_total, bg='white',
                                     font=("Arial", 9))
            casilla.pack(side="left", padx=5)

            tk.Label(marco_mes, text=nombre_mes, font=("Arial", 9), bg='white', width=20, anchor='w').pack(side="left",
                                                                                                           padx=5)
            tk.Label(marco_mes, text="Q 75.00", font=("Arial", 9), bg='white').pack(side="right", padx=10)

        else:
            try:
                fecha_pago = datetime.strptime(ultimo_pago, "%Y-%m-%d %H:%M:%S")
                mes_ultimo_pago = fecha_pago.month
                año_ultimo_pago = fecha_pago.year

                total_meses_debe = ((año_actual - año_ultimo_pago) * 12) + (mes_actual - mes_ultimo_pago)

                mes_mostrar = mes_ultimo_pago + 1
                año_mostrar = año_ultimo_pago

                for i in range(total_meses_debe):
                    if mes_mostrar > 12:
                        mes_mostrar = 1
                        año_mostrar += 1

                    nombre_mes = f"{nombres_meses[mes_mostrar - 1]} {año_mostrar}"

                    marco_mes = tk.Frame(marco_meses, bg='white')
                    marco_mes.pack(fill="x", pady=1)

                    variable = tk.BooleanVar()
                    casillas.append(variable)

                    casilla = tk.Checkbutton(marco_mes, variable=variable, command=calcular_total, bg='white',
                                             font=("Arial", 9))
                    casilla.pack(side="left", padx=5)

                    tk.Label(marco_mes, text=nombre_mes, font=("Arial", 9), bg='white', width=20, anchor='w').pack(
                        side="left", padx=5)
                    tk.Label(marco_mes, text="Q 75.00", font=("Arial", 9), bg='white').pack(side="right", padx=10)

                    mes_mostrar += 1
            except:
                nombre_mes = f"{nombres_meses[mes_actual - 1]} {año_actual}"

                marco_mes = tk.Frame(marco_meses, bg='white')
                marco_mes.pack(fill="x", pady=1)

                variable = tk.BooleanVar()
                casillas.append(variable)

                casilla = tk.Checkbutton(marco_mes, variable=variable, command=calcular_total, bg='white',
                                         font=("Arial", 9))
                casilla.pack(side="left", padx=5)

                tk.Label(marco_mes, text=nombre_mes, font=("Arial", 9), bg='white', width=20, anchor='w').pack(
                    side="left", padx=5)
                tk.Label(marco_mes, text="Q 75.00", font=("Arial", 9), bg='white').pack(side="right", padx=10)

    def calcular_total():
        total = 0
        monto_mes = 75.00

        for variable in casillas:
            if variable.get():
                total += monto_mes

        etiqueta_total.config(text=f"Q {total:.2f}")
        etiqueta_abonar.config(text=f"Q {total:.2f}")

    def pagar():
        nonlocal cliente_actual

        if not cliente_actual:
            messagebox.showwarning("Pago", "Seleccione un cliente primero")
            return

        meses_seleccionados = []
        total = 0

        for indice, variable in enumerate(casillas):
            if variable.get():
                total += 75.00
                meses_seleccionados.append(indice)

        if not meses_seleccionados:
            messagebox.showwarning("Pago", "Seleccione al menos un mes")
            return

        confirmar = messagebox.askyesno("Confirmar Pago",
                                        f"¿Confirmar pago de {len(meses_seleccionados)} mes(es) por Q {total:.2f}?")

        if confirmar:
            try:
                conexion = sqlite3.connect("empresa.db")
                cursor = conexion.cursor()

                from datetime import datetime
                fecha_actual = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

                cursor.execute("UPDATE clientes SET fecha_ultimo_cobro=?, por_cobrar=0 WHERE id_cliente=?",
                               (fecha_actual, cliente_actual))

                conexion.commit()
                conexion.close()

                messagebox.showinfo("Pago Exitoso",
                                    f"Pago registrado exitosamente:\nCliente ID: {cliente_actual}\nMeses pagados: {len(meses_seleccionados)}\nTotal: Q {total:.2f}\nFecha: {fecha_actual}")
                ventana.destroy()

            except sqlite3.Error as e:
                messagebox.showerror("Error", f"No se pudo registrar el pago: {e}")

    boton_siguiente = tk.Button(marco_botones, text="PAGAR", font=("Arial", 11), command=pagar, bg="#4CAF50",
                                fg="white", width=12)
    boton_siguiente.pack(side="left", padx=10)

    boton_cancelar = tk.Button(marco_botones, text="CANCELAR", font=("Arial", 11), command=ventana.destroy,
                               bg="#f44336", fg="white", width=12)
    boton_cancelar.pack(side="left", padx=10)

    lista_clientes.bind('<<ListboxSelect>>', seleccionar_cliente)
    entrada_busqueda.bind("<Return>", lambda e: buscar_cliente())
    entrada_busqueda.focus()

def ventana_resumen_cobros(padre):
    ventana = tk.Toplevel(padre)
    ventana.title("Resumen de Cobros Diarios")
    ventana.geometry("800x600")
    ventana.configure(bg='white')

    tk.Label(ventana, text="RESUMEN DE COBROS DIARIOS", font=("Arial", 16, "bold"), bg='white').pack(pady=15)

    marco_principal = tk.Frame(ventana, bg='white')
    marco_principal.pack(fill="both", expand=True, padx=20, pady=10)

    marco_fechas = tk.Frame(marco_principal, bg='white', relief='solid', bd=1)
    marco_fechas.pack(side="left", fill="y", padx=(0, 10))

    tk.Label(marco_fechas, text="FECHAS CON COBROS", font=("Arial", 12, "bold"), bg='white').pack(pady=10)

    lista_fechas = tk.Listbox(marco_fechas, font=("Arial", 11), width=15, height=20)
    lista_fechas.pack(padx=10, pady=10, fill="both", expand=True)

    marco_detalles = tk.Frame(marco_principal, bg='white', relief='solid', bd=1)
    marco_detalles.pack(side="right", fill="both", expand=True)

    tk.Label(marco_detalles, text="DETALLE DE COBROS", font=("Arial", 12, "bold"), bg='white').pack(pady=10)

    marco_scroll = tk.Frame(marco_detalles, bg='white')
    marco_scroll.pack(fill="both", expand=True, padx=10, pady=10)

    canvas = tk.Canvas(marco_scroll, bg='white')
    scrollbar = tk.Scrollbar(marco_scroll, orient="vertical", command=canvas.yview)
    marco_detalles_interior = tk.Frame(canvas, bg='white')

    marco_detalles_interior.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
    canvas.create_window((0, 0), window=marco_detalles_interior, anchor="nw")
    canvas.configure(yscrollcommand=scrollbar.set)

    canvas.pack(side="left", fill="both", expand=True)
    scrollbar.pack(side="right", fill="y")

    marco_totales = tk.Frame(marco_detalles, bg='white')
    marco_totales.pack(fill="x", padx=10, pady=5)

    etiqueta_total = tk.Label(marco_totales, text="TOTAL DEL DÍA: Q 0.00",
                              font=("Arial", 12, "bold"), bg='white', fg="#2E7D32")
    etiqueta_total.pack()

    def cargar_fechas_con_cobros():
        try:
            conexion = sqlite3.connect("empresa.db")
            cursor = conexion.cursor()

            cursor.execute("""
                SELECT DISTINCT date(fecha_ultimo_cobro) as fecha_cobro
                FROM clientes 
                WHERE fecha_ultimo_cobro IS NOT NULL
                ORDER BY fecha_cobro DESC
            """)
            fechas = cursor.fetchall()
            conexion.close()

            lista_fechas.delete(0, tk.END)

            for fecha in fechas:
                if fecha[0]:
                    lista_fechas.insert(tk.END, fecha[0])

        except sqlite3.Error as e:
            messagebox.showerror("Error", f"No se pudieron cargar las fechas: {e}")

    def cargar_detalles_cobros(event):
        seleccion = lista_fechas.curselection()
        if not seleccion:
            return
        fecha_seleccionada = lista_fechas.get(seleccion[0])
        try:
            conexion = sqlite3.connect("empresa.db")
            cursor = conexion.cursor()

            cursor.execute("""
                SELECT id_cliente, nombre
                FROM clientes 
                WHERE date(fecha_ultimo_cobro) = ?
                ORDER BY fecha_ultimo_cobro
            """, (fecha_seleccionada,))

            cobros = cursor.fetchall()
            conexion.close()

            for widget in marco_detalles_interior.winfo_children():
                widget.destroy()

            total_dia = 0
            monto_por_mes = 75.00

            tk.Label(marco_detalles_interior, text=fecha_seleccionada,
                     font=("Arial", 14, "bold"), bg='white').pack(anchor="w", pady=(0, 5))

            for id_cliente, nombre in cobros:
                marco_cliente = tk.Frame(marco_detalles_interior, bg='white')
                marco_cliente.pack(fill="x", pady=2)

                tk.Label(marco_cliente, text=f"{id_cliente} - {nombre}",
                         font=("Arial", 9), bg='white', anchor='w').pack(side="left")

                tk.Label(marco_cliente, text="Q 75.00",
                         font=("Arial", 9), bg='white').pack(side="right")

                total_dia += monto_por_mes

            tk.Label(marco_detalles_interior, text=f"Cantidad: {len(cobros)}",
                     font=("Arial", 11, "bold"), bg='white').pack(anchor="w", pady=(10, 0))

            etiqueta_total.config(text=f"TOTAL DEL {fecha_seleccionada}: Q {total_dia:.2f}")

        except sqlite3.Error as e:
            messagebox.showerror("Error", f"No se pudieron cargar los detalles: {e}")

    lista_fechas.bind('<<ListboxSelect>>', cargar_detalles_cobros)

    def actualizar_lista():
        cargar_fechas_con_cobros()
        for widget in marco_detalles_interior.winfo_children():
            widget.destroy()
        etiqueta_total.config(text="TOTAL DEL DÍA: Q 0.00")

    marco_botones = tk.Frame(ventana, bg='white')
    marco_botones.pack(pady=10)

    boton_actualizar = tk.Button(marco_botones, text="Actualizar Lista", font=("Arial", 11),
                                 command=actualizar_lista, bg="#2196F3", fg="white")
    boton_actualizar.pack()

    ventana.after(100, cargar_fechas_con_cobros)

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
            ("Listado Clientes por Visitar", lambda: ventana_clientes_por_cobrar(ventana)),
            ("Órdenes de Trabajo", lambda: ventana_ordenes_trabajo(ventana)),
            ("Material Instalado", lambda: ventana_ver_material_instalado(ventana) ),
            ("Resumen de Cobros", lambda: ventana_resumen_cobros(ventana)),
            ("Facturar", lambda : ventana_cobros(ventana)),
            ("Crear Usuarios", lambda: ventana_crear_usuario(ventana)),
        ]
    elif rol == "cobrador":
        botones = [
            ("Asistencia", lambda: ventana_marcar_asistencia(ventana)),
            ("Gestión de Clientes", lambda: ventana_gestion_clientes(ventana)),
            ("Listado Clientes Visitar", lambda: ventana_clientes_por_cobrar(ventana)),
            ("Resumen de Cobros", lambda: ventana_resumen_cobros(ventana)),
            ("Facturar", lambda: ventana_cobros(ventana)),
        ]
    else:
        botones = [
            ("Asistencia", lambda: ventana_marcar_asistencia(ventana)),
            ("Gestión de Clientes", lambda: ventana_gestion_clientes(ventana)),
            ("Reportar Material", lambda: ventana_reportar_material(ventana)),
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