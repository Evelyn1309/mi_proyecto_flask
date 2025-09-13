{% extends "base.html" %}
{% block title %}{{ 'Nuevo cliente' if modo=='crear' else 'Editar cliente' }}{% endblock %}

{% block content %}
<h1>Fromulario de creación de producto </h1>
<h1>{{ 'Nuevo cliente' if modo=='crear' else 'Editar cliente' }}</h1>

<form method="post" novalidate class="form-card">
  {{ form.hidden_tag() }}

  <div class="form-group">
    <label>{{ form.nombre.label }}</label>
    {{ form.nombre(class="input") }}
    {% for e in form.nombre.errors %}<small class="error">{{ e }}</small>{% endfor %}
  </div>

  <div class="form-group">
    <label>{{ form.telefono.label }}</label>
    {{ form.telefono(class="input") }}
    {% for e in form.telefono.errors %}<small class="error">{{ e }}</small>{% endfor %}
  </div>

<div class="form-group">
    <label>{{ form.direccion.label }}</label>
    {{ form.direccion(class="input") }}
    {% for e in form.direccion.errors %}<small class="error">{{ e }}</small>{% endfor %}
  </div>

  <div class="form-group">
    <label>{{ form.correo.label }}</label>
    {{ form.correo(class="input") }}
    {% for e in form.correo.errors %}<small class="error">{{ e }}</small>{% endfor %}
  </div>


  <div class="form-actions">
    {{ form.submit(class="btn btn-primary") }}
    <a class="btn btn-secondary" href="{{ url_for('listar_productos') }}">Cancelar</a>
  </div>
</form>
{% endblock %}