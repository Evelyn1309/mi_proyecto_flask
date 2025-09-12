from flask import Flask, render_template, request, redirect, url_for, jsonify
from inventario import Inventario

app = Flask(__name__)
inv = Inventario()


@app.route("/")
def index():
    inv.cargar_desde_bd()
    return render_template("index.html")


# -------- API para obtener datos en JSON --------
@app.route("/api/productos")
def api_productos():
    inv.cargar_desde_bd()
    return jsonify([p.__dict__ for p in inv.productos.values()])


@app.route("/agregar", methods=["POST"])
def agregar():
    nombre = request.form["nombre"]
    idcat = int(request.form["id_categoria"])
    precio = float(request.form["precio"])
    stock = int(request.form["stock"])
    inv.agregar_producto(nombre, idcat, precio, stock)
    return redirect(url_for("index"))


@app.route("/eliminar/<int:id_producto>", methods=["POST"])
def eliminar(id_producto):
    inv.eliminar_producto(id_producto)
    return jsonify({"status": "ok"})


@app.route("/actualizar/<int:id_producto>", methods=["POST"])
def actualizar(idproducto):
    nuevo_precio = request.form.get("precio")
    nuevo_stock = request.form.get("stock")
    inv.actualizar_producto(
        idproducto,
        precio=float(nuevo_precio) if nuevo_precio else None,
        stock=int(nuevo_stock) if nuevo_stock else None
    )
    return jsonify({"status": "ok"})


if __name__ == "__main__":
    app.run(debug=True)
