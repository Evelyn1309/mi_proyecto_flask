{% extends "base.html" %}
{% block title %}Clientes{% endblock %}

{% block content %}
<h1>Inventario Clientes</h1>

<form method="get" action="{{ url_for('listar_clientes') }}" class="form-inline">
  <input type="text" name="q" placeholder="Buscar por nombre" value="{{ q or '' }}">
  <button type="submit" class="btn">Buscar</button>
  <a class="btn btn-primary" href="{{ url_for('crear_cliente') }}" > Nuevo</a>
</form>

{% if Clientes %}
<h1> Ver si ingresa</h1>
<table class="table">
  <thead>
    <tr>
      <th>ID</th><th>Nombre</th><th>Telefono</th><th>Direccion</th><th>Correo</th>
    </tr>
  </thead>
  <tbody>
    {% for C in Clientes %}
    <tr>
      <td>{{ p.id }}</td>
      <td>{{ p.nombre }}</td>
      <td>{{ p.telefono }}</td>
      <td>{{ p.direccion }}</td>
      <td>{{ p.correo }}</td>
      
      <td>
        <a class="btn btn-small" href="{{ url_for('editar_cliente', pid=p.id) }}">Editar</a>
        <form method="post" action="{{ url_for('eliminar_cliente', pid=p.id) }}" style="display:inline"
              onsubmit="return confirm('¿Eliminar {{ p.nombre }}?');">
          <button type="submit" class="btn btn-danger btn-small">Eliminar</button>
        </form>
      </td>
    </tr>
    {% endfor %}
  </tbody>
</table>
{% else %}
<p>No hay clientes para mostrar.</p>
{% endif %}
{% endblock %}