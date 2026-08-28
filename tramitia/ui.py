"""Panel web de la plataforma."""

from __future__ import annotations

from flask import Blueprint, render_template

from .audit import trail
from .auth import COORDINADOR, authenticated, current_user
from .db import as_dict, propias, todas


bp = Blueprint("ui", __name__)


@bp.get("/")
@authenticated
def panel():
    usuario = current_user()
    if usuario["role"] == COORDINADOR:
        filas = todas()
    else:
        filas = propias(usuario["username"])
    return render_template(
        "panel.html",
        usuario=usuario,
        solicitudes=[as_dict(fila) for fila in filas],
        actividad=trail()[-12:],
    )
