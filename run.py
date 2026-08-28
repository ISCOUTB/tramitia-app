"""Punto de entrada para desarrollo y para el ambiente de revision.

En produccion el servicio se levanta con gunicorn detras del proxy
institucional; ver docs/OPERACION.md.
"""

import os

from tramitia import __version__, create_app


app = create_app()


def main() -> None:
    host = os.getenv("TRAMITIA_HOST", "127.0.0.1")
    port = int(os.getenv("TRAMITIA_PORT", "5050"))
    debug = os.getenv("TRAMITIA_DEBUG", "0") not in ("", "0", "false", "False")

    print(f"Tramitia {__version__} en http://{host}:{port} (debug={debug})")
    app.run(host=host, port=port, debug=debug)


if __name__ == "__main__":
    main()
