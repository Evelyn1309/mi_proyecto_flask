"""
Sistema Avanzado de Gestión de Inventario - Heladería Colón
Usa POO y colecciones (diccionarios) para manejar productos
y se conecta a MySQL (phpMyAdmin).
"""

import mysql.connector
from mysql.connector import Error
import json
from dataclasses import dataclass, asdict
from typing import Dict, Optional


# --------- CONFIGURACIÓN ---------
def load_config(path="config.json"):
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


CONFIG = load_config()  # espera host,user,password,database,port


# --------- CLASE PRODUCTO ---------
@dataclass
class Producto:
    id_producto: int
    nombre_producto: str
    id_categoria: int
    precio: float
    stock: int


# --------- CLASE INVENTARIO ---------
class Inventario:
    def __init__(self):
        self.productos: Dict[int, Producto] = {}

    def conectar(self):
        return mysql.connector.connect(
            host=CONFIG["host"],
            user=CONFIG["user"],
            password=CONFIG["password"],
            database=CONFIG["database"],
            port=CONFIG.get("port", 3308)
        )

    # ---------- Cargar desde BD ----------
    def cargar_desde_bd(self):
        try:
            conn = self.conectar()
            cursor = conn.cursor(dictionary=True)
            cursor.execute("SELECT id_producto, nombre_producto, id_categoria, precio, stock FROM productos")
            self.productos.clear()
            for row in cursor.fetchall():
                prod = Producto(**row)
                self.productos[prod.id_producto] = prod
            cursor.close()
            conn.close()
        except Error as e:
            print("Error al cargar desde BD:", e)

    # ---------- Mostrar todos ----------
    def mostrar_todos(self):
        for p in self.productos.values():
            print(f"[{p.id_producto}] {p.nombre_producto} | Cat: {p.id_categoria} | Precio: {p.precio} | Stock: {p.stock}")

    # ---------- Añadir ----------
    def agregar_producto(self, nombre: str, id_categoria: int, precio: float, stock: int):
        try:
            conn = self.conectar()
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO productos (nombre_producto, id_categoria, precio, stock) VALUES (%s, %s, %s, %s)",
                (nombre, id_categoria, precio, stock)
            )
            conn.commit()
            cursor.close()
            conn.close()
            print("✅ Producto agregado con éxito.")
        except Error as e:
            print("Error al agregar:", e)

    # ---------- Eliminar ----------
    def eliminar_producto(self, idproducto: int):
        try:
            conn = self.conectar()
            cursor = conn.cursor()
            cursor.execute("DELETE FROM productos WHERE idproducto = %s", (id_producto,))
            conn.commit()
            cursor.close()
            conn.close()
            print("🗑️ Producto eliminado con éxito.")
        except Error as e:
            print("Error al eliminar:", e)

    # ---------- Actualizar ----------
    def actualizar_producto(self, id_producto: int, precio: Optional[float] = None, stock: Optional[int] = None):
        try:
            conn = self.conectar()
            cursor = conn.cursor()

            if precio is not None:
                cursor.execute("UPDATE productos SET precio = %s WHERE idproducto = %s", (precio, id_producto))
            if stock is not None:
                cursor.execute("UPDATE productos SET stock = %s WHERE idproducto = %s", (stock, id_producto))

            conn.commit()
            cursor.close()
            conn.close()
            print("✏️ Producto actualizado con éxito.")
        except Error as e:
            print("Error al actualizar:", e)

    # ---------- Buscar por nombre ----------
    def buscar_por_nombre(self, nombre: str):
        encontrados = [p for p in self.productos.values() if nombre.lower() in p.nombre_producto.lower()]
        for p in encontrados:
            print(f"[{p.id_producto}] {p.nombre_producto} | Cat: {p.id_categoria} | Precio: {p.precio} | Stock: {p.stock}")
        if not encontrados:
            print("⚠️ No se encontraron productos con ese nombre.")


# --------- PROGRAMA PRINCIPAL (MENÚ CONSOLA) ---------
if __name__ == "__main__":
    inv = Inventario()
    inv.cargar_desde_bd()

    while True:
        print("\n📦 Menú Inventario")
        print("1. Mostrar productos")
        print("2. Agregar producto")
        print("3. Eliminar producto")
        print("4. Actualizar producto")
        print("5. Buscar producto por nombre")
        print("6. Recargar desde BD")
        print("0. Salir")

        opcion = input("Elige una opción: ")

        if opcion == "1":
            inv.mostrar_todos()
        elif opcion == "2":
            nombre = input("Nombre del producto: ")
            idcat = int(input("ID de categoría: "))
            precio = float(input("Precio: "))
            stock = int(input("Stock: "))
            inv.agregar_producto(nombre, idcat, precio, stock)
        elif opcion == "3":
            pid = int(input("ID del producto a eliminar: "))
            inv.eliminar_producto(pid)
        elif opcion == "4":
            pid = int(input("ID del producto a actualizar: "))
            nuevo_precio = input("Nuevo precio (Enter para omitir): ")
            nuevo_stock = input("Nuevo stock (Enter para omitir): ")
            inv.actualizar_producto(
                pid,
                precio=float(nuevo_precio) if nuevo_precio else None,
                stock=int(nuevo_stock) if nuevo_stock else None
            )
        elif opcion == "5":
            nombre = input("Nombre a buscar: ")
            inv.buscar_por_nombre(nombre)
        elif opcion == "6":
            inv.cargar_desde_bd()
            print("🔄 Inventario recargado desde BD.")
        elif opcion == "0":
            break
        else:
            print("❌ Opción no válida.")
