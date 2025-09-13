from flask import render_template, request, redirect, url_for
from conexion.conexion import app, db  # importamos app y db desde conexion.py

# Modelo Cliente
class Cliente(db.Model):
    __tablename__ = 'clientes'
    id_cliente = db.Column(db.Integer, primary_key=True, autoincrement=True)
    nombre = db.Column(db.String(100), nullable=False)
    direccion = db.Column(db.String(200))
    correo = db.Column(db.String(100))
    telefono = db.Column(db.String(20))

    def __repr__(self):
        return f"<Cliente {self.id_cliente} - {self.nombre}>"


# --------------------- RUTAS ------------------------

@app.route("/")
def index():
    clientes = Cliente.query.all()
    return render_template("index_clientes.html", clientes=clientes)


@app.route("/agregar_cliente", methods=["POST"])
def agregar_cliente():
    nombre = request.form["nombre"]
    direccion = request.form["direccion"]
    correo = request.form["correo"]
    telefono = request.form["telefono"]

    nuevo_cliente = Cliente(
        nombre=nombre,
        direccion=direccion,
        correo=correo,
        telefono=telefono
    )

    db.session.add(nuevo_cliente)
    db.session.commit()

    return redirect(url_for("index"))


@app.route("/eliminar_cliente/<int:id>")
def eliminar_cliente(id):
    cliente = Cliente.query.get(id)
    if cliente:
        db.session.delete(cliente)
        db.session.commit()
    return redirect(url_for("index"))


@app.route("/editar_cliente/<int:id>", methods=["POST"])
def editar_cliente(id):
    cliente = Cliente.query.get(id)
    if cliente:
        cliente.nombre = request.form["nombre"]
        cliente.direccion = request.form["direccion"]
        cliente.correo = request.form["correo"]
        cliente.telefono = request.form["telefono"]

        db.session.commit()

    return redirect(url_for("index"))


# --------------------- MAIN ------------------------

if __name__ == "__main__":
    app.run(debug=True)
