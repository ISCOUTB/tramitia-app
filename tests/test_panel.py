"""Pruebas del panel web y de la consulta de auditoria."""

from __future__ import annotations

import unittest

from support import ANA, CARLA, CasoBase, basic


class PanelTest(CasoBase):
    def test_panel_exige_sesion(self):
        self.assertEqual(401, self.client().get("/").status_code)

    def test_panel_muestra_las_solicitudes_del_analista(self):
        client = self.client()
        self.crear(client, ANA, resumen="Caso visible en el panel")
        html = client.get("/", headers=basic(ANA)).get_data(as_text=True)
        self.assertIn("Caso visible en el panel", html)
        self.assertIn("ana.vargas", html)

    def test_panel_de_coordinacion_incluye_otras_areas(self):
        html = self.client().get("/", headers=basic(CARLA)).get_data(as_text=True)
        self.assertIn("bruno.mejia", html)


class AuditoriaTest(CasoBase):
    def test_registra_la_creacion_de_solicitudes(self):
        client = self.client()
        self.crear(client, ANA)
        cuerpo = client.get("/api/admin/auditoria", headers=basic(ANA)).get_json()
        eventos = {evento["event"] for evento in cuerpo["eventos"]}
        self.assertIn("solicitud.creada", eventos)

    def test_registra_la_identidad_que_ejecuta_cada_herramienta(self):
        client = self.client()
        self.ejecutar(client, ANA)
        cuerpo = client.get("/api/admin/auditoria", headers=basic(ANA)).get_json()
        herramientas = [
            evento
            for evento in cuerpo["eventos"]
            if evento["event"] == "herramienta.ejecutada"
        ]
        self.assertTrue(herramientas)
        self.assertIn("principal", herramientas[0])

    def test_respeta_el_limite_de_eventos(self):
        client = self.client()
        self.crear(client, ANA)
        self.crear(client, ANA)
        cuerpo = client.get(
            "/api/admin/auditoria?limite=1", headers=basic(ANA)
        ).get_json()
        self.assertEqual(1, cuerpo["total"])


if __name__ == "__main__":
    unittest.main()
