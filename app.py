from flask import Flask, render_template, request, redirect, url_for, jsonify
from inventario import Inventario
from flask_sqlalchemy import SQLAlchemy

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

# Carpeta para archivos de datos
RUTA_DATOS = "datos"

# -----------------------------
# Configuración MySQL / PHPMyAdmin
# -----------------------------
# Cambia 'usuario', 'password' y 'heladeria_colon' según tu base de datos
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql:""//root:@localhost3308/heladeriasdb'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# -----------------------------
# Modelo Cliente / Pedido
# -----------------------------
class Cliente(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(50))
    producto = db.Column(db.String(50))
    cantidad = db.Column(db.Integer)
    email = db.Column(db.String(50))

# Crear tabla (solo la primera vez)
with app.app_context():
    db.create_all()

# -----------------------------
# Rutas principales
# -----------------------------
@app.route('/')
def index():
    return render_template("formulario.html")  # Formulario para registrar pedidos/clientes

# -----------------------------
# Persistencia TXT
# -----------------------------
@app.route('/guardar_txt', methods=['POST'])
def guardar_txt():
    nombre = request.form['nombre']
    producto = request.form['producto']
    cantidad = request.form['cantidad']
    email = request.form['email']

    ruta_txt = os.path.join(RUTA_DATOS, "clientes.txt")
    with open(ruta_txt, "a") as f:
        f.write(f"{nombre},{producto},{cantidad},{email}\n")
    return redirect(url_for('index'))

@app.route('/leer_txt')
def leer_txt():
    datos = []
    ruta_txt = os.path.join(RUTA_DATOS, "clientes.txt")
    if os.path.exists(ruta_txt):
        with open(ruta_txt, "r") as f:
            for linea in f:
                nombre, producto, cantidad, email = linea.strip().split(",")
                datos.append({
                    "nombre": nombre,
                    "producto": producto,
                    "cantidad": cantidad,
                    "email": email
                })
    return render_template("resultado.html", datos=datos)

# -----------------------------
# Persistencia JSON
# -----------------------------
@app.route('/guardar_json', methods=['POST'])
def guardar_json():
    nombre = request.form['nombre']
    producto = request.form['producto']
    cantidad = request.form['cantidad']
    email = request.form['email']

    ruta_json = os.path.join(RUTA_DATOS, "clientes.json")
    datos = []
    if os.path.exists(ruta_json):
        with open(ruta_json, "r") as f:
            datos = json.load(f)

    datos.append({
        "nombre": nombre,
        "producto": producto,
        "cantidad": cantidad,
        "email": email
    })

    with open(ruta_json, "w") as f:
        json.dump(datos, f, indent=4)

    return redirect(url_for('index'))

@app.route('/leer_json')
def leer_json():
    ruta_json = os.path.join(RUTA_DATOS, "clientes.json")
    datos = []
    if os.path.exists(ruta_json):
        with open(ruta_json, "r") as f:
            datos = json.load(f)
    return render_template("resultado.html", datos=datos)

# -----------------------------
# Persistencia CSV
# -----------------------------
@app.route('/guardar_csv', methods=['POST'])
def guardar_csv():
    nombre = request.form['nombre']
    producto = request.form['producto']
    cantidad = request.form['cantidad']
    email = request.form['email']

    ruta_csv = os.path.join(RUTA_DATOS, "clientes.csv")
    file_exists = os.path.exists(ruta_csv)

    with open(ruta_csv, "a", newline='') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=["nombre", "producto", "cantidad", "email"])
        if not file_exists:
            writer.writeheader()
        writer.writerow({
            "nombre": nombre,
            "producto": producto,
            "cantidad": cantidad,
            "email": email
        })

    return redirect(url_for('index'))

@app.route('/leer_csv')
def leer_csv():
    datos = []
    ruta_csv = os.path.join(RUTA_DATOS, "clientes.csv")
    if os.path.exists(ruta_csv):
        with open(ruta_csv, newline='') as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                datos.append(row)
    return render_template("resultado.html", datos=datos)

# -----------------------------
# Persistencia MySQL / PHPMyAdmin
# -----------------------------
@app.route('/guardar_db', methods=['POST'])
def guardar_db():
    nombre = request.form['nombre']
    producto = request.form['producto']
    cantidad = request.form['cantidad']
    email = request.form['email']

    cliente = Cliente(nombre=nombre, producto=producto, cantidad=int(cantidad), email=email)
    db.session.add(cliente)
    db.session.commit()
    return redirect(url_for('index'))

@app.route('/leer_db')
def leer_db():
    datos = Cliente.query.all()
    return render_template("resultado.html", datos=datos)

# -----------------------------
# Ejecutar servidor
# -----------------------------


if __name__ == "__main__":
    app.run(debug=True)
