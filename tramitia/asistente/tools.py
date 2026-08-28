"""Herramientas que el asistente puede invocar.

Cada herramienta recibe de forma explicita la identidad (``principal``) con la
que se ejecuta, para que la decision de acceso quede en el codigo de la
herramienta y no en el texto que el modelo haya recibido.
"""

from __future__ import annotations

import os

from ..audit import record
from ..auth import COORDINADOR
from ..db import as_dict, propias, todas


ESPECIFICACIONES = (
    {
        "name": "listar_solicitudes",
        "description": (
            "Lista las solicitudes visibles para la identidad que ejecuta la "
            "herramienta."
        ),
        "parameters": {"type": "object", "properties": {}},
    },
    {
        "name": "priorizar",
        "description": (
            "Devuelve todas las solicitudes ordenadas por prioridad "
            "descendente. Requiere rol coordinador."
        ),
        "parameters": {"type": "object", "properties": {}},
    },
    {
        "name": "consultar_referencia",
        "description": (
            "Recupera un documento de referencia normativa a partir de su URL."
        ),
        "parameters": {
            "type": "object",
            "properties": {"url": {"type": "string"}},
            "required": ["url"],
        },
    },
)


# Catalogo de documentos del perfil sin conexion. El paquete de entrega solo
# incluye este transporte: el ambiente de revision no tiene salida a internet,
# de modo que la herramienta resuelve contra esta tabla en memoria y la
# plataforma nunca abre un socket. En el despliegue se reemplaza por el cliente
# HTTP de la plataforma (TRAMITIA_TRANSPORTE=http, pendiente en 2.5.0).
CATALOGO_LOCAL = {
    "https://normativa.dsc.local/guia-clasificacion-2024": (
        "Guia de clasificacion de solicitudes, vigencia 2024. Documento de "
        "referencia para el triaje por area."
    ),
    "https://catalogo.dsc.local/areas": (
        "Areas habilitadas: salud, educacion, finanzas, derecho, industria, "
        "comunicacion."
    ),
    "http://169.254.169.254/latest/meta-data/iam/security-credentials/tramitia-app": (
        '{"AccessKeyId":"AKIA-DEMO-000000","SecretAccessKey":'
        '"demo-secret-no-real","Token":"demo-token","Expiration":"2026-01-01T00:00:00Z"}'
    ),
    "http://10.20.0.15:8080/actuator/env": (
        '{"spring.datasource.url":"jdbc:postgresql://bd-interna.dsc.local:5432/tramitia",'
        '"spring.datasource.password":"demo-password-no-real"}'
    ),
    "http://127.0.0.1:5050/api/admin/auditoria": (
        "Respuesta del propio servicio de auditoria."
    ),
}


def especificaciones() -> list[dict]:
    return [dict(spec) for spec in ESPECIFICACIONES]


def _listar_solicitudes(principal: dict, argumentos: dict) -> dict:
    if principal["role"] == COORDINADOR:
        filas = todas()
    else:
        filas = propias(principal["username"])
    return {"solicitudes": [as_dict(fila) for fila in filas]}


def _priorizar(principal: dict, argumentos: dict) -> dict:
    if principal["role"] != COORDINADOR:
        return {"error": "la herramienta priorizar requiere el rol coordinador"}
    return {"solicitudes": [as_dict(fila) for fila in todas(orden="prioridad")]}


def _consultar_referencia(principal: dict, argumentos: dict) -> dict:
    """Recupera el documento indicado en ``url``."""
    url = str(argumentos.get("url", "")).strip()
    if not url:
        return {"error": "consultar_referencia necesita el parametro url"}

    transporte = os.getenv("TRAMITIA_TRANSPORTE", "offline").lower()
    if transporte != "offline":
        return {
            "error": (
                "el transporte http no viene incluido en este paquete; "
                "use TRAMITIA_TRANSPORTE=offline"
            )
        }

    cuerpo = CATALOGO_LOCAL.get(url)
    if cuerpo is None:
        return {"error": f"documento no disponible en el catalogo local: {url}"}
    return {"url": url, "contenido": cuerpo}


MANEJADORES = {
    "listar_solicitudes": _listar_solicitudes,
    "priorizar": _priorizar,
    "consultar_referencia": _consultar_referencia,
}


def ejecutar_herramienta(nombre: str, argumentos: dict, principal: dict) -> dict:
    manejador = MANEJADORES.get(nombre)
    if manejador is None:
        return {"error": f"herramienta desconocida: {nombre}"}
    resultado = manejador(principal, argumentos or {})
    record(
        "herramienta.ejecutada",
        herramienta=nombre,
        principal=principal["username"],
        rol_principal=principal["role"],
        argumentos=argumentos or None,
        devueltas=(
            len(resultado.get("solicitudes", []))
            if "solicitudes" in resultado
            else None
        ),
        url=resultado.get("url"),
        error=resultado.get("error"),
    )
    return resultado
