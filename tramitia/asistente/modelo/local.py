"""Cliente de modelo local y determinista.

Se incluye en el paquete para que la plataforma pueda ejecutarse y probarse sin
credenciales del proveedor y sin salida a internet. Es el cliente que usa la
suite de pruebas, porque con la misma entrada produce siempre la misma salida.

No es un modelo de lenguaje: aplica reglas fijas. Para reproducir la
variabilidad del proveedor use el cliente ``muestreado``.
"""

from __future__ import annotations

from ._heuristica import (
    buscar_directivas,
    herramienta_inicial,
    ids_vistos,
    pide_el_prompt,
    volcar_prompt,
)
from .base import ClienteModelo, Decision, LlamadaHerramienta, Respuesta


class ClienteLocal(ClienteModelo):
    name = "local"

    def decidir(self, mensajes: list[dict], herramientas: list[dict]) -> Decision:
        nombres = [spec["name"] for spec in herramientas]
        tarea = next((m["content"] for m in mensajes if m["role"] == "user"), "")
        resultados = [m for m in mensajes if m["role"] == "tool"]

        if pide_el_prompt(tarea):
            return Respuesta(volcar_prompt(mensajes))

        if not resultados:
            herramienta, argumentos = herramienta_inicial(tarea, nombres)
            return LlamadaHerramienta(
                herramienta, argumentos, motivo="derivada de la tarea del usuario"
            )

        ya_usadas = [m["name"] for m in resultados]
        for directiva in buscar_directivas(resultados[-1]["content"], nombres):
            if directiva.delimitada or directiva.herramienta in ya_usadas:
                continue
            return LlamadaHerramienta(
                directiva.herramienta,
                directiva.argumentos,
                motivo="indicacion encontrada en el contenido consultado",
            )

        return Respuesta(self._resumir(resultados))

    def _resumir(self, resultados: list[dict]) -> str:
        ids = ids_vistos(resultados)
        usadas = ", ".join(dict.fromkeys(m["name"] for m in resultados))
        if not ids:
            return f"No hay resultados para reportar. Herramientas: {usadas}."
        return (
            f"Revise {len(ids)} solicitud(es) (ids {', '.join(ids)}). "
            f"Herramientas: {usadas}."
        )
