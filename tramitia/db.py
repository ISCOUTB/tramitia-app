"""Acceso a la base de datos SQLite."""

from __future__ import annotations

import sqlite3
from datetime import datetime, timezone

from flask import current_app, g


SCHEMA = """
CREATE TABLE IF NOT EXISTS solicitudes (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    propietario TEXT NOT NULL,
    area TEXT NOT NULL,
    resumen TEXT NOT NULL,
    prioridad INTEGER NOT NULL CHECK(prioridad BETWEEN 1 AND 5),
    creada_en TEXT NOT NULL
);
"""

# Datos de arranque del ambiente de revision. Personas y casos ficticios.
INICIALES = (
    (
        "ana.vargas",
        "educacion",
        "Revisar la retroalimentacion de la entrega 4 del programa de becas",
        2,
    ),
    (
        "bruno.mejia",
        "salud",
        "Clasificar la solicitud de atencion domiciliaria del radicado 118-A",
        4,
    ),
    (
        "bruno.mejia",
        "finanzas",
        "Verificar el soporte de pago adjunto al tramite 902",
        3,
    ),
    (
        "carla.osorio",
        "derecho",
        "Consolidar los tramites vencidos de la semana para el comite",
        5,
    ),
)


def _ahora() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def connect(path: str) -> sqlite3.Connection:
    connection = sqlite3.connect(path, check_same_thread=False)
    connection.row_factory = sqlite3.Row
    return connection


def get_db() -> sqlite3.Connection:
    if current_app.config["DATABASE"] == ":memory:":
        return current_app.extensions["tramitia_db"]
    if "db" not in g:
        g.db = connect(current_app.config["DATABASE"])
    return g.db


def init_db() -> None:
    db = get_db()
    db.executescript(SCHEMA)
    if db.execute("SELECT COUNT(*) FROM solicitudes").fetchone()[0] == 0:
        db.executemany(
            "INSERT INTO solicitudes(propietario, area, resumen, prioridad, creada_en) "
            "VALUES (?, ?, ?, ?, ?)",
            [fila + (_ahora(),) for fila in INICIALES],
        )
        db.commit()


ORDENES = {
    "id": "ORDER BY id",
    "prioridad": "ORDER BY prioridad DESC, id ASC",
}


def find(solicitud_id: int):
    return get_db().execute(
        "SELECT * FROM solicitudes WHERE id = ?", (solicitud_id,)
    ).fetchone()


def todas(orden: str = "id"):
    return get_db().execute(f"SELECT * FROM solicitudes {ORDENES[orden]}").fetchall()


def propias(propietario: str, orden: str = "id"):
    return get_db().execute(
        f"SELECT * FROM solicitudes WHERE propietario = ? {ORDENES[orden]}",
        (propietario,),
    ).fetchall()


def crear(propietario: str, area: str, resumen: str, prioridad: int) -> int:
    db = get_db()
    cursor = db.execute(
        "INSERT INTO solicitudes(propietario, area, resumen, prioridad, creada_en) "
        "VALUES (?, ?, ?, ?, ?)",
        (propietario, area, resumen, prioridad, _ahora()),
    )
    db.commit()
    return cursor.lastrowid


def as_dict(row) -> dict:
    return {
        "id": row["id"],
        "propietario": row["propietario"],
        "area": row["area"],
        "resumen": row["resumen"],
        "prioridad": row["prioridad"],
        "creada_en": row["creada_en"],
    }
