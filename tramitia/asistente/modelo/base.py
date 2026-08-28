"""Contrato del cliente de modelo.

La plataforma no depende de un proveedor concreto: el bucle del asistente solo
conoce esta interfaz. El cliente productivo se inyecta por configuracion.
"""

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(frozen=True)
class LlamadaHerramienta:
    """El modelo pide ejecutar una herramienta."""

    herramienta: str
    argumentos: dict = field(default_factory=dict)
    motivo: str = ""


@dataclass(frozen=True)
class Respuesta:
    """El modelo entrega la respuesta final al usuario."""

    texto: str


Decision = LlamadaHerramienta | Respuesta


class ClienteModelo:
    name = "base"

    def decidir(self, mensajes: list[dict], herramientas: list[dict]) -> Decision:
        raise NotImplementedError
