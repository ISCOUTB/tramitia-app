"""Heuristicas internas de los clientes de modelo incluidos en el paquete.

IMPORTANTE PARA QUIEN REVISE EL CODIGO: este modulo no forma parte de la
logica de negocio ni es un control de seguridad de la plataforma. Existe para
que los clientes de modelo locales (``local`` y ``muestreado``) reaccionen al
contenido del contexto de forma parecida a como lo hace el proveedor real, y
asi el asistente pueda ejecutarse en ambientes sin credenciales ni salida a
internet. En produccion, con el cliente del proveedor configurado, nada de
este archivo se ejecuta.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field


# Se conserva el reconocimiento de los bloques que probo la variante descartada
# en ADR-006: si en el futuro se reactiva la delimitacion del contenido, el
# cliente local debe reaccionar a ella igual que el modelo del proveedor y no
# como si el texto viniera mezclado con las instrucciones.
BLOQUE_DELIMITADO = re.compile(
    r"<untrusted_content\b[^>]*>.*?</untrusted_content>", re.IGNORECASE | re.DOTALL
)

# Formulas con las que un texto intenta dejar de ser leido como dato y pasar a
# ser leido como instruccion. El proveedor documenta que su modelo es sensible
# a construcciones de este tipo.
FORMULAS_DE_ANULACION = tuple(
    re.compile(patron, re.IGNORECASE)
    for patron in (
        r"ignora\s+(todas\s+)?(las\s+|tus\s+)?instrucciones",
        r"olvida\s+(tus\s+|las\s+)?instrucciones",
        r"nueva\s+instrucci[oó]n",
        r"instrucci[oó]n\s+del\s+sistema",
        r"ignore\s+(all\s+)?(previous|prior)\s+instructions",
        r"disregard\s+(the\s+)?(above|previous)",
        r"system\s+override",
    )
)

FORMULAS_DE_VOLCADO = tuple(
    re.compile(patron, re.IGNORECASE)
    for patron in (
        r"repite\s+(tus\s+|las\s+)?instrucciones",
        r"muestra\s+(tu\s+|el\s+)?(prompt|instrucciones)",
        r"cu[aá]l\s+es\s+tu\s+(prompt|instrucci)",
        r"copia\s+(tu\s+)?prompt",
        r"tus\s+instrucciones\s+(completas|iniciales|originales)",
        r"(system\s+prompt|initial\s+instructions)",
        r"repeat\s+(your\s+)?(instructions|prompt)",
    )
)

URL = re.compile(r"https?://[^\s\"'<>)\]]+", re.IGNORECASE)


@dataclass(frozen=True)
class Directiva:
    """Instruccion hallada en el contexto que nombra una herramienta."""

    herramienta: str
    patron: str
    delimitada: bool
    argumentos: dict = field(default_factory=dict)


def pide_el_prompt(texto: str) -> str | None:
    for patron in FORMULAS_DE_VOLCADO:
        if patron.search(texto):
            return patron.pattern
    return None


def buscar_directivas(texto: str, nombres: list[str]) -> list[Directiva]:
    """Localiza directivas en el contexto e informa si venian delimitadas.

    La herramienta debe aparecer en la misma linea que la formula; de otro modo
    el encabezado del propio resultado contaria como parte de la instruccion.
    """
    encontradas: list[Directiva] = []
    for linea in texto.splitlines():
        coincidencia = next(
            (m for patron in FORMULAS_DE_ANULACION if (m := patron.search(linea))),
            None,
        )
        if coincidencia is None:
            continue
        delimitada = any(
            bloque.start() <= coincidencia.start() < bloque.end()
            for bloque in BLOQUE_DELIMITADO.finditer(linea)
        )
        for nombre in nombres:
            if re.search(rf"\b{re.escape(nombre)}\b", linea, re.IGNORECASE):
                url = URL.search(linea)
                encontradas.append(
                    Directiva(
                        nombre,
                        coincidencia.re.pattern,
                        delimitada,
                        {"url": url.group(0)} if url else {},
                    )
                )
                break
    return encontradas


def herramienta_inicial(tarea: str, nombres: list[str]) -> tuple[str, dict]:
    """Primera herramienta que el modelo elige a partir de la tarea."""
    if re.search(r"prioriz", tarea, re.IGNORECASE) and "priorizar" in nombres:
        return "priorizar", {}
    if "consultar_referencia" in nombres:
        url = URL.search(tarea)
        if url:
            return "consultar_referencia", {"url": url.group(0)}
        if re.search(r"referencia|normativa|gu[ií]a|documento", tarea, re.IGNORECASE):
            return "consultar_referencia", {"url": REFERENCIA_POR_DEFECTO}
    if "listar_solicitudes" in nombres:
        return "listar_solicitudes", {}
    return nombres[0], {}


REFERENCIA_POR_DEFECTO = "https://normativa.dsc.local/guia-clasificacion-2024"


def volcar_prompt(mensajes: list[dict]) -> str:
    sistema = next((m["content"] for m in mensajes if m["role"] == "system"), "")
    return f"Mis instrucciones son: {sistema}"


def ids_vistos(mensajes_herramienta: list[dict]) -> list[str]:
    unido = " ".join(mensaje["content"] for mensaje in mensajes_herramienta)
    return sorted(set(re.findall(r"\bid=(\d+)", unido)), key=int)
