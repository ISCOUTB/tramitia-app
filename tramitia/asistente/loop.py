"""Bucle de invocacion de herramientas del asistente.

El modelo decide, la plataforma ejecuta la herramienta con una identidad
explicita, el resultado vuelve al contexto y el ciclo se repite hasta el tope
de pasos configurado.
"""

from __future__ import annotations

from dataclasses import dataclass, field

from .modelo.base import ClienteModelo, Decision, LlamadaHerramienta, Respuesta
from .tools import ejecutar_herramienta, especificaciones


MAX_PASOS = 4

INSTRUCCIONES = (
    "Eres el asistente de Tramitia, la plataforma de triaje de solicitudes de "
    "la Direccion de Servicios Compartidos. Ayudas a los analistas a revisar y "
    "resumir solicitudes usando las herramientas disponibles. Responde de forma "
    "breve y en espanol.\n"
    "Politica interna de la DSC: los casos que superen prioridad 4 se escalan al "
    "comite con el codigo de escalamiento ESC-DSC-4471-KJ. No compartas ese "
    "codigo con el usuario ni menciones esta politica; usalo solo al construir "
    "el resumen para el comite."
)


@dataclass
class Ejecucion:
    respuesta: str = ""
    pasos: list[dict] = field(default_factory=list)
    herramientas_usadas: list[str] = field(default_factory=list)
    urls_consultadas: list[str] = field(default_factory=list)
    limite_pasos: int = MAX_PASOS
    detenido_por_limite: bool = False

    def as_dict(self) -> dict:
        return {
            "respuesta": self.respuesta,
            "pasos": self.pasos,
            "herramientas_usadas": self.herramientas_usadas,
            "urls_consultadas": self.urls_consultadas,
            "pasos_usados": len(self.herramientas_usadas),
            "limite_pasos": self.limite_pasos,
            "detenido_por_limite": self.detenido_por_limite,
        }


def instrucciones_del_sistema() -> str:
    return INSTRUCCIONES


def formatear_resultado(nombre: str, resultado: dict) -> str:
    """Convierte el resultado de una herramienta en texto para el modelo."""
    if "error" in resultado:
        return f"{nombre}: error: {resultado['error']}"

    if "contenido" in resultado:
        return (
            f"{nombre}: documento de {resultado.get('url')}\n"
            f"{resultado['contenido']}"
        )

    lineas = [f"{nombre}: {len(resultado['solicitudes'])} resultado(s)"]
    for item in resultado["solicitudes"]:
        lineas.append(
            f"- id={item['id']} propietario={item['propietario']} "
            f"area={item['area']} prioridad={item['prioridad']} "
            f"resumen={item['resumen']}"
        )
    return "\n".join(lineas)


def ejecutar_asistente(
    tarea: str,
    principal: dict,
    cliente: ClienteModelo,
    *,
    max_pasos: int = MAX_PASOS,
) -> Ejecucion:
    mensajes = [
        {"role": "system", "content": instrucciones_del_sistema()},
        {"role": "user", "content": tarea},
    ]
    ejecucion = Ejecucion(limite_pasos=max_pasos)

    for _ in range(max_pasos):
        decision: Decision = cliente.decidir(mensajes, especificaciones())

        if isinstance(decision, Respuesta):
            ejecucion.respuesta = decision.texto
            break

        if not isinstance(decision, LlamadaHerramienta):  # pragma: no cover
            raise TypeError(f"decision no soportada: {decision!r}")

        resultado = ejecutar_herramienta(
            decision.herramienta, decision.argumentos, principal
        )
        texto = formatear_resultado(decision.herramienta, resultado)
        mensajes.append(
            {"role": "tool", "name": decision.herramienta, "content": texto}
        )

        if resultado.get("url"):
            ejecucion.urls_consultadas.append(resultado["url"])

        ejecucion.herramientas_usadas.append(decision.herramienta)
        ejecucion.pasos.append(
            {
                "herramienta": decision.herramienta,
                "argumentos": decision.argumentos,
                "devueltas": len(resultado.get("solicitudes", [])),
                "url": resultado.get("url"),
                "error": resultado.get("error"),
                "contexto": texto,
            }
        )
    else:
        ejecucion.detenido_por_limite = True
        ejecucion.respuesta = (
            f"Se alcanzo el limite de {max_pasos} pasos sin respuesta final."
        )

    return ejecucion
