from __future__ import annotations
from dataclasses import dataclass
from typing import Dict, List, Optional
import argparse
import pymysql
from flask import Flask, request, redirect, url_for

# -------------------------------
# Configuración conexión MySQL
# -------------------------------
DB_CONFIG = {
    "host": "localhost",
    "user": "root",       # cambia si tienes otro usuario
    "password": "",       # pon tu contraseña si configuraste una
    "database": "heladeria_colonsdb"  # nombre de tu BD en phpMyAdmin
}

# -------------------------------
# Modelo de Dominio (POO)
# -------------------------------
@dataclass
class Producto:
    id: Optional[int]
    nombre: str
    cantidad: int
    precio: float

    def set_nombre(self, nuevo_nombre: str) -> None:
        if not nuevo_nombre.strip():
            raise ValueError("El nombre no puede estar vacío")
        self.nombre = nuevo_nombre.strip()

    def set_cantidad(self, nueva_cantidad: int) -> None:
        if nueva_cantidad < 0:
            raise ValueError("La cantidad no puede ser negativa")
        self.cantidad = nueva_cantidad

    def set_precio(self, nuevo_precio: float) -> None:
        if nuevo_precio < 0:
            raise ValueError("El precio no puede ser negativo")
        self.precio = round(float(nuevo_precio), 2)


class Inventario:
    def __init__(self, db_config=DB_CONFIG):
        self.db_config = db_config
        self._cache: Dict[int, Producto] = {}
        self._ensure_schema()
        self._load_cache_from_db()

    def _conn(self):
        return pymysql.connect(
            host=self.db_config["host"],
            user=self.db_config["user"],
            password=self.db_config["password"],
            database=self.db_config["database"],
            cursorclass=pymysql.cursors.DictCursor
        )

    def _ensure_schema(self):
        with self._conn() as con:
            with con.cursor() as cur:
                cur.execute("""
                    CREATE TABLE IF NOT EXISTS productos (
                        id INT AUTO_INCREMENT PRIMARY KEY,
                        nombre VARCHAR(100) NOT NULL,
                        cantidad INT NOT NULL,
                        precio DECIMAL(10,2) NOT NULL
                    )
                """)
            con.commit()

    def _load_cache_from_db(self):
        self._cache.clear()
        with self._conn() as con:
            with con.cursor() as cur:
                cur.execute("SELECT * FROM productos")
                for row in cur.fetchall():
                    p = Producto(row["id"], row["nombre"], row["cantidad"], float(row["precio"]))
                    self._cache[p.id] = p

    # CRUD
    def anadir_producto(self, nombre: str, cantidad: int, precio: float) -> Producto:
        p = Producto(None, nombre, cantidad, precio)
        p.set_nombre(nombre)
        p.set_cantidad(cantidad)
        p.set_precio(precio)
        with self._conn() as con:
            with con.cursor() as cur:
                cur.execute(
                    "INSERT INTO productos (nombre, cantidad, precio) VALUES (%s, %s, %s)",
                    (p.nombre, p.cantidad, p.precio)
                )
                p.id = cur.lastrowid
            con.commit()
        self._cache[p.id] = p
        return p

    def eliminar_producto(self, id_producto: int) -> bool:
        with self._conn() as con:
            with con.cursor() as cur:
                cur.execute("DELETE FROM productos WHERE id = %s", (id_producto,))
                eliminado = cur.rowcount > 0
            con.commit()
        if eliminado:
            self._cache.pop(id_producto, None)
        return eliminado

    def actualizar_producto(self, id_producto: int, nombre=None, cantidad=None, precio=None) -> Optional[Producto]:
        p = self._cache.get(id_producto)
        if not p:
            return None
        if nombre: p.set_nombre(nombre)
        if cantidad is not None: p.set_cantidad(cantidad)
        if precio is not None: p.set_precio(precio)
        with self._conn() as con:
            with con.cursor() as cur:
                cur.execute(
                    "UPDATE productos SET nombre=%s, cantidad=%s, precio=%s WHERE id=%s",
                    (p.nombre, p.cantidad, p.precio, id_producto)
                )
            con.commit()
        return p

    def buscar_por_nombre(self, patron: str) -> List[Producto]:
        patron = patron.lower()
        return [p for p in self._cache.values() if patron in p.nombre.lower()]

    def obtener_todos(self) -> List[Producto]:
        return sorted(self._cache.values(), key=lambda p: p.id or 0)

    def total_items(self):
        return sum(p.cantidad for p in self._cache.values())

    def valor_inventario(self):
        return round(sum(p.cantidad * p.precio for p in self._cache.values()), 2)


# -------------------------------
# Flask
# -------------------------------
app = Flask(__name__)
inventario = Inventario()

@app.route("/")
def index():
    q = request.args.get("q", "")
    productos = inventario.buscar_por_nombre(q) if q else inventario.obtener_todos()
    html = "<h1>Inventario Heladería Colón</h1>"
    html += "<a href='/add'>Añadir producto</a><br><br>"
    html += "<form><input name='q' placeholder='Buscar'><button>Buscar</button></form>"
    html += "<table border=1><tr><th>ID</th><th>Nombre</th><th>Cantidad</th><th>Precio</th><th>Acciones</th></tr>"
    for p in productos:
        html += f"<tr><td>{p.id_producto}</td><td>{p.nombre_producto}</td>td>{p.id_categoria}</td><td>{p.precio}</td><td>{p.stock}</td>"
        html += f"<td><a href='/edit/{p.id_producto}'>Editar</a> | "
        html += f"<a href='/delete/{p.id_producto}'>Eliminar</a></td></tr>"
    html += "</table>"
    html += f"<p>Total items: {inventario.total_items()} | Valor: ${inventario.valor_inventario()}</p>"
    return html

@app.route("/add", methods=["GET", "POST"])
def add():
    if request.method == "POST":
        inventario.anadir_producto(request.form["nombre_producto"], int(request.form["cantidad"]), float(request.form["precio"]))
        return redirect(url_for("index"))
    return """
    <h2>Añadir producto</h2>
    <form method='post'>
      Nombre: <input name='nombre'><br>
      Cantidad: <input type='number' name='cantidad'><br>
      Precio: <input type='number' step='0.01' name='precio'><br>
      <button type='submit'>Guardar</button>
    </form>
    """

@app.route("/edit/<int:pid>", methods=["GET", "POST"])
def edit(pid):
    p = next((x for x in inventario.obtener_todos() if x.id == pid), None)
    if not p:
        return "No encontrado", 404
    if request.method == "POST":
        inventario.actualizar_producto(pid, request.form["nombre"], int(request.form["cantidad"]), float(request.form["precio"]))
        return redirect(url_for("index"))
    return f"""
    <h2>Editar producto #{p.id}</h2>
    <form method='post'>
      Nombre: <input name='nombre' value='{p.nombre}'><br>
      Cantidad: <input type='number' name='cantidad' value='{p.cantidad}'><br>
      Precio: <input type='number' step='0.01' name='precio' value='{p.precio}'><br>
      <button type='submit'>Guardar</button>
    </form>
    """

@app.route("/delete/<int:pid>")
def delete(pid):
    inventario.eliminar_producto(pid)
    return redirect(url_for("index"))

# -------------------------------
# Menú consola
# -------------------------------
def menu_consola():
    while True:
        print("\nInventario Heladería Colón")
        print("1. Mostrar todos")
        print("2. Añadir")
        print("3. Editar")
        print("4. Eliminar")
        print("5. Buscar")
        print("0. Salir")
        op = input("> ")
        if op == "1":
            for p in inventario.obtener_todos():
                print(p)
        elif op == "2":
            n = input("Nombre: "); c = int(input("Cantidad: ")); pr = float(input("Precio: "))
            inventario.anadir_producto(n,c,pr)
        elif op == "3":
            i = int(input("ID: "))
            n = input("Nombre: "); c = int(input("Cantidad: ")); pr = float(input("Precio: "))
            inventario.actualizar_producto(i,n,c,pr)
        elif op == "4":
            i = int(input("ID: "))
            inventario.eliminar_producto(i)
        elif op == "5":
            q = input("Buscar: ")
            for p in inventario.buscar_por_nombre(q):
                print(p)
        elif op == "0":
            break

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--web", action="store_true")
    parser.add_argument("--cli", action="store_true")
    args = parser.parse_args()
    if args.web:
        inventario._load_cache_from_db()
        app.run(debug=True)
    elif args.cli:
        menu_consola()
    else:
        print("Usa --web para Flask o --cli para consola")
