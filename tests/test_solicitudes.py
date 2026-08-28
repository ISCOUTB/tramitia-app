"""Pruebas de la API de solicitudes."""

from __future__ import annotations

import unittest

from support import ANA, BRUNO, CARLA, CasoBase, basic


class SaludTest(CasoBase):
    def test_health_responde_sin_credenciales(self):
        respuesta = self.client().get("/health")
        self.assertEqual(200, respuesta.status_code)
        self.assertEqual("ok", respuesta.get_json()["status"])

    def test_api_exige_autenticacion(self):
        respuesta = self.client().get("/api/solicitudes")
        self.assertEqual(401, respuesta.status_code)

    def test_credenciales_invalidas_rechazadas(self):
        respuesta = self.client().get(
            "/api/solicitudes", headers=basic(("ana.vargas", "clave-incorrecta"))
        )
        self.assertEqual(401, respuesta.status_code)


class ListadoTest(CasoBase):
    def test_analista_ve_solo_sus_solicitudes(self):
        client = self.client()
        cuerpo = client.get("/api/solicitudes", headers=basic(ANA)).get_json()
        self.assertTrue(cuerpo)
        self.assertEqual({"ana.vargas"}, {fila["propietario"] for fila in cuerpo})

    def test_coordinacion_ve_todas(self):
        client = self.client()
        cuerpo = client.get("/api/solicitudes", headers=basic(CARLA)).get_json()
        propietarios = {fila["propietario"] for fila in cuerpo}
        self.assertIn("ana.vargas", propietarios)
        self.assertIn("bruno.mejia", propietarios)


class CreacionTest(CasoBase):
    def test_crea_con_cuerpo_valido(self):
        client = self.client()
        creada = self.crear(client, ANA, area="finanzas", resumen="Revisar soporte")
        self.assertEqual("ana.vargas", creada["propietario"])
        self.assertEqual("finanzas", creada["area"])
        self.assertIn("creada_en", creada)

    def test_area_fuera_del_catalogo_rechazada(self):
        client = self.client()
        respuesta = client.post(
            "/api/solicitudes",
            headers=basic(ANA),
            json={"area": "otra-cosa", "resumen": "x", "prioridad": 1},
        )
        self.assertEqual(400, respuesta.status_code)
        self.assertIn("area", respuesta.get_json()["error"])

    def test_resumen_vacio_rechazado(self):
        client = self.client()
        respuesta = client.post(
            "/api/solicitudes",
            headers=basic(ANA),
            json={"area": "salud", "resumen": "   ", "prioridad": 1},
        )
        self.assertEqual(400, respuesta.status_code)

    def test_resumen_demasiado_largo_rechazado(self):
        client = self.client()
        respuesta = client.post(
            "/api/solicitudes",
            headers=basic(ANA),
            json={"area": "salud", "resumen": "x" * 181, "prioridad": 1},
        )
        self.assertEqual(400, respuesta.status_code)
        self.assertIn("180", respuesta.get_json()["error"])

    def test_prioridad_fuera_de_rango_rechazada(self):
        client = self.client()
        respuesta = client.post(
            "/api/solicitudes",
            headers=basic(ANA),
            json={"area": "salud", "resumen": "x", "prioridad": 9},
        )
        self.assertEqual(400, respuesta.status_code)

    def test_campo_no_reconocido_rechazado(self):
        client = self.client()
        respuesta = client.post(
            "/api/solicitudes",
            headers=basic(ANA),
            json={
                "area": "salud",
                "resumen": "x",
                "prioridad": 1,
                "propietario": "carla.osorio",
            },
        )
        self.assertEqual(400, respuesta.status_code)
        self.assertIn("propietario", respuesta.get_json()["error"])


class DetalleTest(CasoBase):
    def test_lee_su_propia_solicitud(self):
        client = self.client()
        creada = self.crear(client, ANA)
        respuesta = client.get(
            f"/api/solicitudes/{creada['id']}", headers=basic(ANA)
        )
        self.assertEqual(200, respuesta.status_code)
        self.assertEqual(creada["id"], respuesta.get_json()["id"])

    def test_solicitud_inexistente_devuelve_404(self):
        respuesta = self.client().get("/api/solicitudes/9999", headers=basic(ANA))
        self.assertEqual(404, respuesta.status_code)

    def test_edita_resumen_y_prioridad(self):
        client = self.client()
        creada = self.crear(client, BRUNO, resumen="Original", prioridad=2)
        respuesta = client.patch(
            f"/api/solicitudes/{creada['id']}",
            headers=basic(BRUNO),
            json={"resumen": "Actualizado", "prioridad": 5},
        )
        self.assertEqual(200, respuesta.status_code)
        cuerpo = respuesta.get_json()
        self.assertEqual("Actualizado", cuerpo["resumen"])
        self.assertEqual(5, cuerpo["prioridad"])

    def test_edicion_valida_el_cuerpo(self):
        client = self.client()
        creada = self.crear(client, BRUNO)
        respuesta = client.patch(
            f"/api/solicitudes/{creada['id']}",
            headers=basic(BRUNO),
            json={"prioridad": 0},
        )
        self.assertEqual(400, respuesta.status_code)


if __name__ == "__main__":
    unittest.main()
