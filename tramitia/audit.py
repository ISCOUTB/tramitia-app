"""Registro de auditoria.

Cada decision de acceso y cada invocacion de herramienta del asistente queda
anotada con la identidad que la ejecuto. El archivo es append-only y lo rota
logrotate en el servidor (ver docs/OPERACION.md).
"""

from __future__ import annotations

import json
from datetime import datetime, timezone

from flask import current_app, g, has_app_context, has_request_context


MAXIMO_EN_MEMORIA = 500


def _ahora() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def record(event: str, **fields) -> dict:
    entry = {"ts": _ahora(), "event": event}
    if has_request_context() and "username" in g:
        entry["actor"] = g.username
    entry.update({key: value for key, value in fields.items() if value is not None})

    if not has_app_context():
        return entry

    trail = current_app.extensions.setdefault("tramitia_auditoria", [])
    trail.append(entry)
    del trail[:-MAXIMO_EN_MEMORIA]

    path = current_app.config.get("AUDIT_LOG")
    if path and path != ":memory:":
        with open(path, "a", encoding="utf-8") as handle:
            handle.write(json.dumps(entry, ensure_ascii=False) + "\n")
    return entry


def trail() -> list[dict]:
    if not has_app_context():
        return []
    return list(current_app.extensions.get("tramitia_auditoria", []))
