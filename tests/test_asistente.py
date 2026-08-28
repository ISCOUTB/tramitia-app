"""Pruebas del asistente: bucle, herramientas y limites."""

from __future__ import annotations

import unittest

from support import ANA, BRUNO, CARLA, CasoBase, basic


class CatalogoTest(CasoBase):
    def test_publica_las_tres_herramientas_y_los_limites(self):
        cuerpo = self.client().get(
            "/api/asistente/herramientas", headers=basic(ANA)
        ).get_json()
        nombres = {h["name"] for h in cuerpo["herramientas"]}
        self.assertEqual(
            {"listar_solicitudes", "priorizar", "consultar_referencia"}, nombres
        )
        self.assertEqual(4, cuerpo["limite_pasos"])
        self.assertEqual(400, cuerpo["limite_tarea"])
        self.assertEqual(60, cuerpo["presupuesto"])


class EjecucionTest(CasoBase):
    def test_responde_y_reporta_la_traza(self):
        client = self.client()
        cuerpo = self.ejecutar(client, ANA)
        self.assertTrue(cuerpo["respuesta"])
        self.assertEqual(["listar_solicitudes"], cuerpo["herramientas_usadas"])
        self.assertEqual(1, cuerpo["pasos_usados"])
        self.assertFalse(cuerpo["detenido_por_limite"])
        self.assertEqual("local", cuerpo["modelo"])

    def test_tarea_obligatoria(self):
        respuesta = self.client().post(
            "/api/asistente/ejecutar", headers=basic(ANA), json={"tarea": "   "}
        )
        self.assertEqual(400, respuesta.status_code)

    def test_tarea_demasiado_larga_rechazada(self):
        respuesta = self.client().post(
            "/api/asistente/ejecutar", headers=basic(ANA), json={"tarea": "x" * 401}
        )
        self.assertEqual(400, respuesta.status_code)
        self.assertIn("400", respuesta.get_json()["error"])

    def test_cliente_de_modelo_desconocido_rechazado(self):
        respuesta = self.client().post(
            "/api/asistente/ejecutar",
            headers=basic(ANA),
            json={"tarea": "hola", "modelo": "gpt-inexistente"},
        )
        self.assertEqual(400, respuesta.status_code)

    def test_semilla_no_numerica_rechazada(self):
        respuesta = self.client().post(
            "/api/asistente/ejecutar",
            headers=basic(ANA),
            json={"tarea": "hola", "semilla": "abc"},
        )
        self.assertEqual(400, respuesta.status_code)

    def test_presupuesto_por_usuario_devuelve_429(self):
        client = self.client(ASSISTANT_BUDGET=2)
        self.ejecutar(client, ANA)
        self.ejecutar(client, ANA)
        respuesta = client.post(
            "/api/asistente/ejecutar", headers=basic(ANA), json={"tarea": "otra vez"}
        )
        self.assertEqual(429, respuesta.status_code)

    def test_el_presupuesto_es_por_usuario(self):
        client = self.client(ASSISTANT_BUDGET=1)
        self.ejecutar(client, ANA)
        self.ejecutar(client, BRUNO)
        self.assertEqual(
            429,
            client.post(
                "/api/asistente/ejecutar", headers=basic(ANA), json={"tarea": "x"}
            ).status_code,
        )

    def test_cliente_muestreado_es_reproducible_con_semilla(self):
        client = self.client()
        primera = self.ejecutar(client, ANA, modelo="muestreado", semilla=7)
        segunda = self.ejecutar(client, ANA, modelo="muestreado", semilla=7)
        self.assertEqual(primera["respuesta"], segunda["respuesta"])


class ReferenciaTest(CasoBase):
    def test_consulta_la_guia_de_clasificacion(self):
        cuerpo = self.ejecutar(
            self.client(), ANA, tarea="Consulta la guia de clasificacion vigente"
        )
        self.assertEqual(["consultar_referencia"], cuerpo["herramientas_usadas"])
        self.assertEqual(
            ["https://normativa.dsc.local/guia-clasificacion-2024"],
            cuerpo["urls_consultadas"],
        )

    def test_documento_fuera_del_catalogo_reporta_error(self):
        cuerpo = self.ejecutar(
            self.client(),
            ANA,
            tarea="Consulta el documento en https://ejemplo.invalido/nada",
        )
        self.assertEqual([], cuerpo["urls_consultadas"])
        self.assertIn("no disponible", cuerpo["pasos"][0]["error"])


class PriorizarTest(CasoBase):
    def test_coordinacion_puede_invocar_la_herramienta(self):
        respuesta = self.client().post(
            "/api/asistente/herramientas/priorizar", headers=basic(CARLA), json={}
        )
        self.assertEqual(200, respuesta.status_code)
        prioridades = [s["prioridad"] for s in respuesta.get_json()["solicitudes"]]
        self.assertEqual(sorted(prioridades, reverse=True), prioridades)

    def test_analista_no_puede_invocar_la_herramienta(self):
        respuesta = self.client().post(
            "/api/asistente/herramientas/priorizar", headers=basic(ANA), json={}
        )
        self.assertEqual(403, respuesta.status_code)

    def test_requiere_autenticacion(self):
        respuesta = self.client().post(
            "/api/asistente/herramientas/priorizar", json={}
        )
        self.assertEqual(401, respuesta.status_code)


if __name__ == "__main__":
    unittest.main()
