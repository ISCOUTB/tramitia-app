"""Endpoints del asistente."""

from __future__ import annotations

from flask import Blueprint, current_app, jsonify, request

from ..audit import record
from ..auth import COORDINADOR, CUENTA_SERVICIO, authenticated, current_user
from ..db import as_dict, todas
from .loop import MAX_PASOS, ejecutar_asistente
from .modelo import obtener_cliente
from .tools import especificaciones


MAX_TAREA = 400

bp = Blueprint("asistente", __name__, url_prefix="/api/asistente")


def problem(mensaje: str, status: int):
    return jsonify(error=mensaje), status


def identidad_efectiva(usuario: dict) -> dict:
    """Identidad con la que se ejecutaran las herramientas del asistente.

    Ver ADR-004: el asistente resuelve sus consultas con la cuenta tecnica de
    la plataforma para no depender del perfil de cada analista.
    """
    return dict(CUENTA_SERVICIO)


def consumir_presupuesto(username: str) -> int:
    """Cuenta invocaciones por usuario y devuelve el total incluida esta.

    El contador vive en memoria del proceso: se reinicia con el servicio. La
    version persistente en Redis quedo pendiente (docs/PENDIENTES.md).
    """
    consumo = current_app.extensions.setdefault("tramitia_consumo", {})
    consumo[username] = consumo.get(username, 0) + 1
    return consumo[username]


@bp.get("/herramientas")
@authenticated
def herramientas():
    return jsonify(
        herramientas=especificaciones(),
        limite_pasos=MAX_PASOS,
        limite_tarea=MAX_TAREA,
        presupuesto=current_app.config["ASSISTANT_BUDGET"],
    )


@bp.post("/ejecutar")
@authenticated
def ejecutar():
    data = request.get_json(silent=True) or {}

    tarea = str(data.get("tarea", "")).strip()
    if not tarea:
        return problem("tarea es obligatoria", 400)
    if len(tarea) > MAX_TAREA:
        return problem(f"tarea no puede superar {MAX_TAREA} caracteres", 400)

    usuario = current_user()
    presupuesto = current_app.config["ASSISTANT_BUDGET"]
    usadas = consumir_presupuesto(usuario["username"])
    if usadas > presupuesto:
        record("asistente.presupuesto_agotado", solicitante=usuario["username"], usadas=usadas)
        return problem(
            f"presupuesto de {presupuesto} invocaciones agotado para "
            f"{usuario['username']}",
            429,
        )

    semilla = data.get("semilla", current_app.config.get("MODEL_SEED"))
    if semilla is not None:
        try:
            semilla = int(semilla)
        except (TypeError, ValueError):
            return problem("semilla debe ser un entero", 400)

    try:
        cliente = obtener_cliente(
            data.get("modelo") or current_app.config["MODEL_CLIENT"], seed=semilla
        )
    except ValueError as error:
        return problem(str(error), 400)

    principal = identidad_efectiva(usuario)

    try:
        resultado = ejecutar_asistente(tarea, principal, cliente, max_pasos=MAX_PASOS)
    except RuntimeError as error:  # pragma: no cover - fallo del proveedor
        return problem(str(error), 502)

    record(
        "asistente.ejecucion",
        solicitante=usuario["username"],
        principal=principal["username"],
        modelo=cliente.name,
        semilla=semilla,
        herramientas=resultado.herramientas_usadas or None,
        invocaciones_usadas=usadas,
    )

    payload = resultado.as_dict()
    payload.update(
        solicitante=usuario["username"],
        identidad_efectiva=principal,
        modelo=cliente.name,
        semilla=semilla,
        invocaciones_usadas=usadas,
        presupuesto=presupuesto,
    )
    return jsonify(payload)


@bp.post("/herramientas/priorizar")
@authenticated
def priorizar_directo():
    """Invocacion directa de la herramienta, sin el modelo de por medio.

    La usa el tablero del comite para armar el orden del dia.
    """
    usuario = current_user()
    if usuario["role"] != COORDINADOR:
        record("herramienta.denegada", herramienta="priorizar", rol=usuario["role"])
        return problem("la herramienta requiere el rol coordinador", 403)
    filas = todas(orden="prioridad")
    record(
        "herramienta.ejecutada",
        herramienta="priorizar",
        principal=usuario["username"],
        rol_principal=usuario["role"],
        devueltas=len(filas),
    )
    return jsonify(
        herramienta="priorizar", solicitudes=[as_dict(fila) for fila in filas]
    )
