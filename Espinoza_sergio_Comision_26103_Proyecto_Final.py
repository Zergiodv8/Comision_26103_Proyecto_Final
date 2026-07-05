# ============================================================
# Sistema de Gestion de Productos - Proyecto Final Integrador
# Espinoza Sergio Daniel - Comision 26103 - Python Inicial
# ============================================================
# Este programa gestiona el inventario de productos de un kiosco
# usando una base de datos SQLite (inventario.db).
# Permite: agregar, ver, buscar por ID, actualizar, eliminar
# productos y generar un reporte de stock bajo.
# ============================================================

import sqlite3   # modulo para trabajar con la base de datos
import os         # modulo para trabajar con rutas de archivos


# ------------------------------------------------------------
# CONEXION Y CREACION DE LA BASE DE DATOS
# ------------------------------------------------------------
def conectar_db():
    """Conecta con inventario.db y crea la tabla productos si no existe.
    La base se crea/busca siempre en la misma carpeta que este archivo .py,
    sin importar desde donde se ejecute el programa."""
    # Carpeta donde esta guardado este archivo .py
    carpeta = os.path.dirname(os.path.abspath(__file__))
    # Ruta completa a la base, uniendo la carpeta con el nombre del archivo
    ruta_db = os.path.join(carpeta, "inventario.db")
    conexion = sqlite3.connect(ruta_db)
    cursor = conexion.cursor()
    # La tabla tiene las 6 columnas que pide la consigna
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS productos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nombre TEXT NOT NULL,
            categoria TEXT,
            descripcion TEXT,
            cantidad INTEGER NOT NULL,
            precio REAL NOT NULL
        )
    """)
    conexion.commit()
    return conexion


# ------------------------------------------------------------
# FUNCIONES DE VALIDACION (para no repetir codigo)
# ------------------------------------------------------------
def pedir_texto(mensaje):
    """Pide un texto y no lo acepta vacio."""
    while True:
        valor = input(mensaje).strip()
        if valor != "":
            return valor
        print("Este campo no puede quedar vacio.")


def pedir_entero(mensaje):
    """Pide un numero entero mayor o igual a cero."""
    while True:
        valor = input(mensaje).strip()
        if valor.isdigit():
            return int(valor)
        print("Ingresa un numero entero valido (ej: 10).")


def pedir_precio(mensaje):
    """Pide un precio (numero con o sin decimales) mayor a cero."""
    while True:
        entrada = input(mensaje).strip().replace(",", ".")
        try:
            precio = float(entrada)
            if precio > 0:
                return precio
            print("El precio debe ser mayor a cero.")
        except ValueError:
            print("Ingresa un numero valido (ej: 1500.50).")


# ------------------------------------------------------------
# 1) AGREGAR PRODUCTO
# ------------------------------------------------------------
def agregar_producto(conexion):
    """Pide los datos de un producto nuevo y lo guarda en la base."""
    print("\n--- Agregar producto ---")
    nombre = pedir_texto("Nombre: ")
    categoria = pedir_texto("Categoria: ")
    descripcion = pedir_texto("Descripcion: ")
    cantidad = pedir_entero("Cantidad: ")
    precio = pedir_precio("Precio: $")

    cursor = conexion.cursor()
    try:
        cursor.execute(
            "INSERT INTO productos (nombre, categoria, descripcion, cantidad, precio) VALUES (?, ?, ?, ?, ?)",
            (nombre, categoria, descripcion, cantidad, precio)
        )
        conexion.commit()
        print("Producto agregado correctamente.")
    except sqlite3.Error as error:
        conexion.rollback()
        print("Error al guardar el producto:", error)


# ------------------------------------------------------------
# 2) VER PRODUCTOS
# ------------------------------------------------------------
def ver_productos(conexion):
    """Muestra todos los productos en una tabla ordenada por ID."""
    cursor = conexion.cursor()
    cursor.execute(
        "SELECT id, nombre, categoria, descripcion, cantidad, precio FROM productos ORDER BY id"
    )
    filas = cursor.fetchall()

    if len(filas) == 0:
        print("\nNo hay productos cargados.")
        return

    print("\n" + "-" * 82)
    print(f"{'ID':<4} {'NOMBRE':<18} {'CATEGORIA':<14} {'DESCRIPCION':<20} {'CANT':<6} {'PRECIO':>10}")
    print("-" * 82)
    for id_, nombre, categoria, descripcion, cantidad, precio in filas:
        # Recorto los textos largos para que la tabla no se desalinee
        print(f"{id_:<4} {nombre[:18]:<18} {categoria[:14]:<14} {descripcion[:20]:<20} {cantidad:<6} ${precio:>9,.2f}")
    print("-" * 82)
    print("Total de productos:", len(filas))


# ------------------------------------------------------------
# 3) BUSCAR PRODUCTO POR ID
# ------------------------------------------------------------
def buscar_producto(conexion):
    """Busca un producto por su ID y muestra sus datos completos."""
    print("\n--- Buscar producto por ID ---")
    id_buscar = pedir_entero("Ingresa el ID a buscar: ")

    cursor = conexion.cursor()
    cursor.execute(
        "SELECT id, nombre, categoria, descripcion, cantidad, precio FROM productos WHERE id = ?",
        (id_buscar,)
    )
    fila = cursor.fetchone()

    if fila is None:
        print("No existe un producto con el ID", id_buscar)
        return

    print("\nProducto encontrado:")
    print("  ID:         ", fila[0])
    print("  Nombre:     ", fila[1])
    print("  Categoria:  ", fila[2])
    print("  Descripcion:", fila[3])
    print("  Cantidad:   ", fila[4])
    print(f"  Precio:      ${fila[5]:,.2f}")


# ------------------------------------------------------------
# 4) ACTUALIZAR PRODUCTO POR ID
# ------------------------------------------------------------
def actualizar_producto(conexion):
    """Actualiza los datos de un producto identificado por su ID.
    Si un campo se deja vacio, se conserva el valor anterior."""
    print("\n--- Actualizar producto ---")
    id_actualizar = pedir_entero("Ingresa el ID del producto a actualizar: ")

    cursor = conexion.cursor()
    cursor.execute(
        "SELECT nombre, categoria, descripcion, cantidad, precio FROM productos WHERE id = ?",
        (id_actualizar,)
    )
    fila = cursor.fetchone()

    if fila is None:
        print("No existe un producto con el ID", id_actualizar)
        return

    # Desarmo la fila en variables con los valores actuales
    nombre_actual, categoria_actual, descripcion_actual, cantidad_actual, precio_actual = fila
    print("Dejá el campo vacio y presioná Enter para mantener el valor actual.")

    # Si el usuario no escribe nada, el "or" conserva el valor anterior
    nombre = input(f"Nombre [{nombre_actual}]: ").strip() or nombre_actual
    categoria = input(f"Categoria [{categoria_actual}]: ").strip() or categoria_actual
    descripcion = input(f"Descripcion [{descripcion_actual}]: ").strip() or descripcion_actual

    entrada_cantidad = input(f"Cantidad [{cantidad_actual}]: ").strip()
    cantidad = int(entrada_cantidad) if entrada_cantidad.isdigit() else cantidad_actual

    entrada_precio = input(f"Precio [{precio_actual}]: ").strip().replace(",", ".")
    try:
        precio = float(entrada_precio) if entrada_precio != "" else precio_actual
    except ValueError:
        precio = precio_actual

    try:
        cursor.execute(
            "UPDATE productos SET nombre=?, categoria=?, descripcion=?, cantidad=?, precio=? WHERE id=?",
            (nombre, categoria, descripcion, cantidad, precio, id_actualizar)
        )
        conexion.commit()
        print("Producto actualizado correctamente.")
    except sqlite3.Error as error:
        conexion.rollback()
        print("Error al actualizar:", error)


# ------------------------------------------------------------
# 5) ELIMINAR PRODUCTO POR ID
# ------------------------------------------------------------
def eliminar_producto(conexion):
    """Elimina un producto identificado por su ID, pidiendo confirmacion."""
    print("\n--- Eliminar producto ---")
    id_eliminar = pedir_entero("Ingresa el ID del producto a eliminar: ")

    cursor = conexion.cursor()
    cursor.execute("SELECT nombre FROM productos WHERE id = ?", (id_eliminar,))
    fila = cursor.fetchone()

    if fila is None:
        print("No existe un producto con el ID", id_eliminar)
        return

    nombre = fila[0]
    confirmar = input(f"Seguro que queres eliminar '{nombre}'? (s/n): ").strip().lower()
    if confirmar != "s":
        print("Operacion cancelada.")
        return

    try:
        cursor.execute("DELETE FROM productos WHERE id = ?", (id_eliminar,))
        conexion.commit()
        print("Producto eliminado correctamente.")
    except sqlite3.Error as error:
        conexion.rollback()
        print("Error al eliminar:", error)


# ------------------------------------------------------------
# 6) REPORTE DE STOCK BAJO
# ------------------------------------------------------------
def reporte_stock_bajo(conexion):
    """Muestra los productos cuya cantidad es menor o igual a un limite."""
    print("\n--- Reporte de stock bajo ---")
    limite = pedir_entero("Mostrar productos con cantidad menor o igual a: ")

    cursor = conexion.cursor()
    cursor.execute(
        "SELECT id, nombre, categoria, cantidad FROM productos WHERE cantidad <= ? ORDER BY cantidad",
        (limite,)
    )
    filas = cursor.fetchall()

    if len(filas) == 0:
        print("No hay productos con stock igual o menor a", limite)
        return

    print(f"\nProductos con stock <= {limite}:")
    print("-" * 60)
    for id_, nombre, categoria, cantidad in filas:
        print(f"ID {id_:<3} | {nombre[:20]:<20} | {categoria[:12]:<12} | cantidad: {cantidad}")
    print("-" * 60)
    print("Total encontrados:", len(filas))


# ------------------------------------------------------------
# 7) IMPORTAR PRODUCTOS DESDE UN ARCHIVO TXT
# ------------------------------------------------------------
def importar_desde_txt(conexion):
    """Importa varios productos de una vez desde un archivo de texto.
    Cada linea del archivo debe tener los datos separados por punto y coma (;)
    en este orden:  nombre;categoria;descripcion;cantidad;precio
    Ejemplo de linea:  Coca Cola;Bebidas;Gaseosa 500ml;10;1200.50
    """
    print("\n--- Importar productos desde un archivo TXT ---")
    print("Formato de cada linea:  nombre;categoria;descripcion;cantidad;precio")

    nombre_archivo = input("Nombre del archivo (ej: productos.txt): ").strip()
    if nombre_archivo == "":
        print("No ingresaste ningun nombre de archivo.")
        return

    # Busco el archivo en la misma carpeta que este .py
    carpeta = os.path.dirname(os.path.abspath(__file__))
    ruta_archivo = os.path.join(carpeta, nombre_archivo)

    # Verifico que el archivo exista antes de abrirlo
    if not os.path.exists(ruta_archivo):
        print("No se encontro el archivo:", nombre_archivo)
        print("Asegurate de que este en la misma carpeta que el programa.")
        return

    cursor = conexion.cursor()
    importados = 0   # cuento cuantos productos se cargaron bien
    ignorados = 0    # cuento cuantas lineas tenian errores

    # Abro el archivo y lo recorro linea por linea
    with open(ruta_archivo, "r", encoding="utf-8") as archivo:
        for numero_linea, linea in enumerate(archivo, start=1):
            linea = linea.strip()
            if linea == "":
                continue  # salteo las lineas vacias

            partes = linea.split(";")
            # Cada linea tiene que tener exactamente 5 datos
            if len(partes) != 5:
                print(f"Linea {numero_linea} ignorada (no tiene 5 datos): {linea}")
                ignorados += 1
                continue

            nombre = partes[0].strip()
            categoria = partes[1].strip()
            descripcion = partes[2].strip()
            texto_cantidad = partes[3].strip()
            texto_precio = partes[4].strip().replace(",", ".")

            # Valido nombre no vacio y que la cantidad sea un numero entero
            if nombre == "" or not texto_cantidad.isdigit():
                print(f"Linea {numero_linea} ignorada (datos invalidos): {linea}")
                ignorados += 1
                continue

            # Valido que el precio sea un numero valido
            try:
                precio = float(texto_precio)
            except ValueError:
                print(f"Linea {numero_linea} ignorada (precio invalido): {linea}")
                ignorados += 1
                continue

            cantidad = int(texto_cantidad)

            # Si paso todas las validaciones, lo guardo en la base
            cursor.execute(
                "INSERT INTO productos (nombre, categoria, descripcion, cantidad, precio) VALUES (?, ?, ?, ?, ?)",
                (nombre, categoria, descripcion, cantidad, precio)
            )
            importados += 1

    conexion.commit()
    print(f"\nImportacion terminada. Agregados: {importados} | Ignorados: {ignorados}")


# ------------------------------------------------------------
# MENU PRINCIPAL
# ------------------------------------------------------------
def mostrar_menu():
    """Imprime las opciones del menu."""
    print("\n" + "=" * 40)
    print("   SISTEMA DE GESTION DE PRODUCTOS")
    print("=" * 40)
    print("1 - Agregar producto")
    print("2 - Ver productos")
    print("3 - Buscar producto por ID")
    print("4 - Actualizar producto")
    print("5 - Eliminar producto")
    print("6 - Reporte de stock bajo")
    print("7 - Importar productos desde TXT")
    print("8 - Salir")
    print("-" * 40)


def main():
    """Funcion principal: conecta la base y ejecuta el menu."""
    conexion = conectar_db()
    seguir = True

    while seguir:
        mostrar_menu()
        opcion = input("Elegí una opcion (1-8): ").strip()

        if opcion == "1":
            agregar_producto(conexion)
        elif opcion == "2":
            ver_productos(conexion)
        elif opcion == "3":
            buscar_producto(conexion)
        elif opcion == "4":
            actualizar_producto(conexion)
        elif opcion == "5":
            eliminar_producto(conexion)
        elif opcion == "6":
            reporte_stock_bajo(conexion)
        elif opcion == "7":
            importar_desde_txt(conexion)
        elif opcion == "8":
            print("\nCerrando el sistema. Hasta luego!")
            seguir = False
        else:
            print("Opcion no valida. Elegí un numero del 1 al 8.")

    conexion.close()


# Esta linea hace que el programa arranque al ejecutarlo
if __name__ == "__main__":
    main()
