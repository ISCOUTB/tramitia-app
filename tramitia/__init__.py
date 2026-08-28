"""Tramitia — plataforma de recepcion y triaje de solicitudes.

Desarrollada por Cuadrante Digital S.A.S. para la Direccion de Servicios
Compartidos (DSC). Version candidata a produccion.
"""

from __future__ import annotations

import os

from flask import Flask, g, jsonify, request

from . import admin, api, ui
from .asistente import api as asistente_api
from .db import connect, init_db


__version__ = "2.4.0-rc1"
__all__ = ["__version__", "create_app"]

# Valor de respaldo para que la aplicacion arranque en ambientes de desarrollo
# y de revision sin necesidad de aprovisionar el gestor de secretos.
SECRETO_POR_DEFECTO = "tramitia-dev-secret-cambiar-en-produccion"


def create_app(test_config: dict | None = None) -> Flask:
    app = Flask(__name__)
    app.config.from_mapping(
        DATABASE=os.getenv("TRAMITIA_DATABASE", "tramitia.sqlite3"),
        SECRET_KEY=os.getenv("TRAMITIA_SECRET", SECRETO_POR_DEFECTO),
        MODEL_CLIENT=os.getenv("TRAMITIA_MODELO", "local"),
        MODEL_SEED=os.getenv("TRAMITIA_MODELO_SEMILLA") or None,
        AUDIT_LOG=os.getenv("TRAMITIA_AUDITORIA", "tramitia-auditoria.jsonl"),
        ASSISTANT_BUDGET=int(os.getenv("TRAMITIA_PRESUPUESTO_ASISTENTE", "60")),
    )
    if test_config:
        app.config.update(test_config)

    if app.config["DATABASE"] == ":memory:" and (
        not test_config or "AUDIT_LOG" not in test_config
    ):
        app.config["AUDIT_LOG"] = ":memory:"

    app.extensions["tramitia_auditoria"] = []
    app.extensions["tramitia_consumo"] = {}
    if app.config["DATABASE"] == ":memory:":
        app.extensions["tramitia_db"] = connect(":memory:")

    with app.app_context():
        init_db()

    @app.teardown_appcontext
    def close_db(_error=None):
        db = g.pop("db", None)
        if db is not None and app.config["DATABASE"] != ":memory:":
            db.close()

    @app.after_request
    def cabeceras(response):
        # Habilitado en 2.3.0 para que el portal nuevo (servido desde otro
        # origen durante el desarrollo) pueda consumir la API con la sesion
        # del navegador.
        origen = request.headers.get("Origin")
        if origen:
            response.headers["Access-Control-Allow-Origin"] = origen
            response.headers["Access-Control-Allow-Credentials"] = "true"
        return response

    @app.get("/health")
    def health():
        return jsonify(
            status="ok",
            version=__version__,
            modelo=app.config["MODEL_CLIENT"],
        )

    app.register_blueprint(api.bp)
    app.register_blueprint(asistente_api.bp)
    app.register_blueprint(admin.bp)
    app.register_blueprint(ui.bp)
    return app
