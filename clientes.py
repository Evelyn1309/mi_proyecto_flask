import json, os

class Cliente:
    def __init__(self, id_cliente, nombre, direccion, correo, telefono):
        self.id_cliente = id_cliente
        self.nombre = nombre
        self.direccion = direccion
        self.correo = correo
        self.telefono = telefono

class InventarioClientes:
    def __init__(self):
        self.clientes = {}
        self.siguiente_id = 1
        self.ruta = "datos/clientes.json"

    # Cargar clientes desde JSON
    def cargar_desde_bd(self):
        if os.path.exists(self.ruta):
            with open(self.ruta, "r") as f:
                lista = json.load(f)
                self.clientes = {}
                for c in lista:
                    cliente = Cliente(c["id_cliente"], c["nombre"], c["direccion"], c["correo"], c["telefono"])
                    self.clientes[cliente.id_cliente] = cliente
                if lista:
                    self.siguiente_id = max(c["id_cliente"] for c in lista) + 1

    # Guardar clientes en JSON
    def guardar_en_bd(self):
        lista = []
        for c in self.clientes.values():
            lista.append({
                "id_cliente": c.id_cliente,
                "nombre": c.nombre,
                "direccion": c.direccion,
                "correo": c.correo,
                "telefono": c.telefono
            })
        os.makedirs(os.path.dirname(self.ruta), exist_ok=True)
        with open(self.ruta, "w") as f:
            json.dump(lista, f, indent=4)

    # Agregar cliente
    def agregar_cliente(self, nombre, direccion, correo, telefono):
        cliente = Cliente(self.siguiente_id, nombre, direccion, correo, telefono)
        self.clientes[self.siguiente_id] = cliente
        self.siguiente_id += 1
        self.guardar_en_bd()

    # Eliminar cliente
    def eliminar_cliente(self, id_cliente):
        if id_cliente in self.clientes:
            del self.clientes[id_cliente]
            self.guardar_en_bd()

    # Actualizar cliente
    def actualizar_cliente(self, id_cliente, nombre=None, direccion=None, correo=None, telefono=None):
        if id_cliente in self.clientes:
            c = self.clientes[id_cliente]
            if nombre: c.nombre = nombre
            if direccion: c.direccion = direccion
            if correo: c.correo = correo
            if telefono: c.telefono = telefono
            self.guardar_en_bd()
