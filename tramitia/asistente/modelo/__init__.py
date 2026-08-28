"""Clientes de modelo disponibles.

El paquete de entrega incluye unicamente los dos clientes locales, que no
requieren credenciales ni salida a internet:

- ``local``: determinista. Es el que usa la suite de pruebas.
- ``muestreado``: con variabilidad; acepta semilla para reproducir una corrida.

El cliente del proveedor se agrega en el despliegue instalando su SDK y
apuntando ``TRAMITIA_MODELO`` al nombre correspondiente (ver docs/PENDIENTES.md).
"""

from __future__ import annotations

from .base import ClienteModelo, Decision, LlamadaHerramienta, Respuesta
from .local import ClienteLocal
from .muestreado import ClienteMuestreado


CLIENTES = ("local", "muestreado")


def obtener_cliente(nombre: str | None = None, seed: int | None = None) -> ClienteModelo:
    resuelto = (nombre or "local").strip().lower()
    if resuelto == "local":
        return ClienteLocal()
    if resuelto == "muestreado":
        return ClienteMuestreado(seed=seed)
    raise ValueError(
        f"cliente de modelo no disponible: {resuelto}. "
        f"Disponibles: {', '.join(CLIENTES)}"
    )


__all__ = [
    "CLIENTES",
    "ClienteLocal",
    "ClienteModelo",
    "ClienteMuestreado",
    "Decision",
    "LlamadaHerramienta",
    "Respuesta",
    "obtener_cliente",
]
