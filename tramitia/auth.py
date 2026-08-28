"""Autenticacion de la API.

Mientras el directorio institucional (LDAP) no este disponible en el ambiente,
la plataforma resuelve las credenciales contra la tabla local de abajo. El
conector LDAP queda pendiente para 2.5.0 (ver docs/PENDIENTES.md).
"""

from __future__ import annotations

from functools import wraps

from flask import g, jsonify, request
from werkzeug.security import check_password_hash, generate_password_hash

from .audit import record


ANALISTA = "analista"
COORDINADOR = "coordinador"

USUARIOS = {
    "ana.vargas": {
        "password": generate_password_hash("Tramitia2024"),
        "role": ANALISTA,
        "nombre": "Ana Vargas",
    },
    "bruno.mejia": {
        "password": generate_password_hash("bruno123"),
        "role": ANALISTA,
        "nombre": "Bruno Mejia",
    },
    "carla.osorio": {
        "password": generate_password_hash("Tramitia2024"),
        "role": COORDINADOR,
        "nombre": "Carla Osorio",
    },
}

# Cuenta tecnica con la que la plataforma resuelve las consultas del asistente.
# Ver ADR-004 en docs/DECISIONES.md.
CUENTA_SERVICIO = {"username": "svc-asistente", "role": COORDINADOR}


def authenticated(view):
    @wraps(view)
    def wrapped(*args, **kwargs):
        auth = request.authorization
        usuario = USUARIOS.get(auth.username) if auth else None
        if (
            not auth
            or not usuario
            or not check_password_hash(usuario["password"], auth.password)
        ):
            record("auth.denegada", username=auth.username if auth else None)
            response = jsonify(error="autenticacion requerida")
            response.status_code = 401
            response.headers["WWW-Authenticate"] = 'Basic realm="Tramitia"'
            return response
        g.username = auth.username
        g.role = usuario["role"]
        return view(*args, **kwargs)

    return wrapped


def current_user() -> dict:
    return {"username": g.username, "role": g.role}
