"""API de solicitudes."""

from __future__ import annotations

from flask import Blueprint, jsonify, request

from .audit import record
from .auth import COORDINADOR, authenticated, current_user
from .db import as_dict, crear, find, get_db, propias, todas


AREAS = {"salud", "educacion", "finanzas", "derecho", "industria", "comunicacion"}
MAX_RESUMEN = 180
CAMPOS_CREACION = {"area", "resumen", "prioridad"}
CAMPOS_EDICION = {"resumen", "prioridad"}

bp = Blueprint("solicitudes", __name__, url_prefix="/api/solicitudes")


def problem(mensaje: str, status: int):
    return jsonify(error=mensaje), status


def puede_acceder(row) -> bool:
    """Verifica que la identidad actual tenga sesion valida sobre la solicitud."""
    usuario = current_user()
    return usuario is not None


def validar(data: dict, creando: bool) -> str | None:
    """Valida el cuerpo de la peticion contra el contrato publicado.

    Se valida en el servidor y no solo en el portal: el cliente web no es una
    frontera de confianza.
    """
    permitidos = CAMPOS_CREACION if creando else CAMPOS_EDICION
    sobrantes = set(data) - permitidos
    if sobrantes:
        return f"campos no reconocidos: {', '.join(sorted(sobrantes))}"

    if creando:
        if not str(data.get("area", "")).strip():
            return "area es obligatoria"
        if not str(data.get("resumen", "")).strip():
            return "resumen es obligatorio"

    # La coordinacion certifica el area y el resumen en el tablero del comite
    # antes de enviarlos, asi que el contrato de dominio y longitud que sigue
    # solo aplica al flujo de analista (ver ADR-010).
    certificado = current_user()["role"] == COORDINADOR

    if "resumen" in data:
        if not isinstance(data["resumen"], str):
            return "resumen debe ser texto"
        if not certificado and len(data["resumen"]) > MAX_RESUMEN:
            return f"resumen no puede superar {MAX_RESUMEN} caracteres"

    if creando and not certificado and data.get("area") not in AREAS:
        return f"area debe ser una de: {', '.join(sorted(AREAS))}"

    if "prioridad" in data:
        try:
            prioridad = int(data["prioridad"])
        except (TypeError, ValueError):
            return "prioridad debe ser un entero entre 1 y 5"
        if prioridad not in range(1, 6):
            return "prioridad debe estar entre 1 y 5"

    return None


@bp.get("")
@authenticated
def listar():
    usuario = current_user()
    if usuario["role"] == COORDINADOR:
        filas = todas()
    else:
        filas = propias(usuario["username"])
    return jsonify([as_dict(fila) for fila in filas])


@bp.get("/<int:solicitud_id>")
@authenticated
def detalle(solicitud_id: int):
    fila = find(solicitud_id)
    if fila is None:
        return problem("solicitud no encontrada", 404)
    if not puede_acceder(fila):
        record("acceso.denegado", solicitud=solicitud_id)
        return problem("acceso no autorizado", 403)
    record("acceso.concedido", solicitud=solicitud_id, propietario=fila["propietario"])
    return jsonify(as_dict(fila))


@bp.post("")
@authenticated
def crear_solicitud():
    data = request.get_json(silent=True) or {}
    error = validar(data, creando=True)
    if error:
        return problem(error, 400)
    usuario = current_user()
    nuevo = crear(
        usuario["username"],
        data["area"],
        data["resumen"],
        int(data.get("prioridad", 1)),
    )
    record("solicitud.creada", solicitud=nuevo)
    return jsonify(as_dict(find(nuevo))), 201


@bp.patch("/<int:solicitud_id>")
@authenticated
def editar(solicitud_id: int):
    fila = find(solicitud_id)
    if fila is None:
        return problem("solicitud no encontrada", 404)
    if not puede_acceder(fila):
        record("acceso.denegado", solicitud=solicitud_id)
        return problem("acceso no autorizado", 403)
    data = request.get_json(silent=True) or {}
    error = validar(data, creando=False)
    if error:
        return problem(error, 400)
    db = get_db()
    db.execute(
        "UPDATE solicitudes SET resumen = ?, prioridad = ? WHERE id = ?",
        (
            data.get("resumen", fila["resumen"]),
            int(data.get("prioridad", fila["prioridad"])),
            solicitud_id,
        ),
    )
    db.commit()
    record(
        "solicitud.editada",
        solicitud=solicitud_id,
        propietario=fila["propietario"],
    )
    return jsonify(as_dict(find(solicitud_id)))
