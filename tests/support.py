"""Utilidades compartidas por las pruebas."""

from __future__ import annotations

import base64
import sys
import unittest
from pathlib import Path


sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from tramitia import create_app  # noqa: E402


ANA = ("ana.vargas", "Tramitia2024")
BRUNO = ("bruno.mejia", "bruno123")
CARLA = ("carla.osorio", "Tramitia2024")

TAREA = "Resume las solicitudes pendientes del area asignada."


def basic(usuario: tuple[str, str]) -> dict:
    token = base64.b64encode(f"{usuario[0]}:{usuario[1]}".encode()).decode()
    return {"Authorization": f"Basic {token}"}


class CasoBase(unittest.TestCase):
    """Base que crea aplicaciones aisladas en memoria y cierra su conexion."""

    def setUp(self):
        self._apps = []

    def tearDown(self):
        for app in self._apps:
            app.extensions["tramitia_db"].close()

    def make_app(self, **overrides):
        config = {
            "TESTING": True,
            "DATABASE": ":memory:",
            "SECRET_KEY": "solo-para-pruebas",
            "MODEL_CLIENT": "local",
        }
        config.update(overrides)
        app = create_app(config)
        self._apps.append(app)
        return app

    def client(self, **overrides):
        return self.make_app(**overrides).test_client()

    def crear(self, client, usuario, area="salud", resumen="Caso de prueba", prioridad=3):
        respuesta = client.post(
            "/api/solicitudes",
            headers=basic(usuario),
            json={"area": area, "resumen": resumen, "prioridad": prioridad},
        )
        self.assertEqual(201, respuesta.status_code, respuesta.get_json())
        return respuesta.get_json()

    def ejecutar(self, client, usuario, tarea=TAREA, modelo=None, semilla=None):
        cuerpo = {"tarea": tarea}
        if modelo is not None:
            cuerpo["modelo"] = modelo
        if semilla is not None:
            cuerpo["semilla"] = semilla
        respuesta = client.post(
            "/api/asistente/ejecutar", headers=basic(usuario), json=cuerpo
        )
        self.assertEqual(200, respuesta.status_code, respuesta.get_json())
        return respuesta.get_json()
