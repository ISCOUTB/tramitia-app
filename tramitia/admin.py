"""Consultas de soporte y trazabilidad."""

from __future__ import annotations

from flask import Blueprint, jsonify, request

from .audit import trail
from .auth import authenticated


bp = Blueprint("admin", __name__, url_prefix="/api/admin")


@bp.get("/auditoria")
@authenticated
def auditoria():
    """Ultimos eventos registrados por la plataforma.

    Lo consume el tablero de soporte para diagnosticar reclamos de usuarios sin
    tener que pedir acceso al servidor.
    """
    limite = request.args.get("limite", type=int) or 100
    eventos = trail()[-limite:]
    return jsonify(total=len(eventos), eventos=eventos)
