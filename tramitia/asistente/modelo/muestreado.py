"""Cliente de modelo local con variabilidad.

Igual que ``local``, no sale a la red ni requiere credenciales, pero en lugar
de aplicar una regla fija decide con una probabilidad, para reproducir el hecho
de que el modelo del proveedor no se comporta de forma identica ante la misma
entrada. Con la misma semilla la ejecucion es reproducible; sin semilla varia.

Las probabilidades de abajo son una calibracion aproximada hecha por el equipo
de plataforma a partir de las pruebas manuales de la iteracion 2.2. NO son
mediciones publicadas por el proveedor y no deberian citarse como tales.
"""

from __future__ import annotations

import random

from ._heuristica import (
    buscar_directivas,
    herramienta_inicial,
    ids_vistos,
    pide_el_prompt,
    volcar_prompt,
)
from .base import ClienteModelo, Decision, LlamadaHerramienta, Respuesta


PLANTILLAS = (
    "Revise {n} solicitud(es) (ids {ids}).",
    "Hay {n} solicitudes registradas: ids {ids}.",
    "Segun lo consultado, {n} solicitud(es) requieren atencion: {ids}.",
    "Resumen: {n} solicitud(es) en total, con ids {ids}.",
)

PLANTILLAS_VACIAS = (
    "No encontre solicitudes que reportar.",
    "La consulta no devolvio resultados.",
    "Sin solicitudes pendientes por ahora.",
)


class ClienteMuestreado(ClienteModelo):
    name = "muestreado"

    # Probabilidad de seguir una indicacion hallada en el contexto, segun si
    # llego delimitada como dato o mezclada con el resto del texto.
    P_SIN_DELIMITAR = 0.85
    P_DELIMITADA = 0.12

    def __init__(self, seed: int | None = None):
        self.seed = seed
        self._rng = random.Random(seed)

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
            if directiva.herramienta in ya_usadas:
                continue
            umbral = self.P_DELIMITADA if directiva.delimitada else self.P_SIN_DELIMITAR
            if self._rng.random() < umbral:
                return LlamadaHerramienta(
                    directiva.herramienta,
                    directiva.argumentos,
                    motivo="indicacion encontrada en el contenido consultado",
                )

        return Respuesta(self._resumir(resultados))

    def _resumir(self, resultados: list[dict]) -> str:
        ids = ids_vistos(resultados)
        if not ids:
            return self._rng.choice(PLANTILLAS_VACIAS)
        return self._rng.choice(PLANTILLAS).format(n=len(ids), ids=", ".join(ids))
