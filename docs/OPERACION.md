# Operación

Tramitia 2.4.0-rc1. Manual para el equipo de operaciones de la DSC y para quien
ejecute el paquete en el ambiente de revisión.

## Variables de entorno

| Variable | Valor por omisión | Efecto |
|---|---|---|
| `TRAMITIA_SECRET` | valor de respaldo interno | Clave de firma de la aplicación. En producción la entrega el gestor de secretos; si no está definida, la aplicación arranca con el valor de respaldo. |
| `TRAMITIA_DATABASE` | `tramitia.sqlite3` | Ruta del archivo SQLite, o `:memory:` |
| `TRAMITIA_AUDITORIA` | `tramitia-auditoria.jsonl` | Ruta del log de auditoría, o `:memory:` |
| `TRAMITIA_HOST` | `127.0.0.1` | Interfaz de escucha. El contenedor usa `0.0.0.0` y el compose publica solo en bucle. |
| `TRAMITIA_PORT` | `5050` | Puerto |
| `TRAMITIA_DEBUG` | `0` | Recarga automática y trazas en el navegador. Útil en desarrollo. |
| `TRAMITIA_MODELO` | `local` | Cliente de modelo: `local` o `muestreado` |
| `TRAMITIA_MODELO_SEMILLA` | vacía | Semilla del cliente `muestreado`; vacía = variable en cada ejecución |
| `TRAMITIA_TRANSPORTE` | `offline` | Transporte de `consultar_referencia`. El paquete solo incluye `offline`. |
| `TRAMITIA_PRESUPUESTO_ASISTENTE` | `60` | Invocaciones del asistente por usuario mientras el proceso esté arriba |

## Arranque en desarrollo

```powershell
Copy-Item .env.example .env
python run.py
```

Con `TRAMITIA_DEBUG=1` (así viene en `.env.example`) el servidor recarga al
guardar y muestra la traza del error en el navegador, que es lo que se quiere
mientras se desarrolla. En producción debe quedar en `0`.

## Arranque en producción

La DSC levanta el servicio con gunicorn detrás del proxy institucional, que
termina TLS:

```bash
gunicorn --workers 1 --bind 127.0.0.1:5050 'tramitia:create_app()'
```

Un solo worker: el contador de invocaciones del asistente vive en memoria del
proceso y con varios workers dejaría de ser consistente. La versión persistente
está en el backlog.

## Contenedor

```powershell
docker compose build
docker compose up -d
docker compose ps          # el healthcheck debe pasar a healthy
docker compose logs -f
```

El compose publica el puerto únicamente en `127.0.0.1`. La base y la auditoría
viven en el volumen `datos`, así que sobreviven al reinicio del contenedor.
`docker compose down -v` borra también el volumen.

Dentro de la imagen:

```powershell
docker compose exec tramitia python -m unittest discover -s tests -t tests
```

## Registros

| Archivo | Contenido |
|---|---|
| `tramitia-auditoria.jsonl` | Un evento por línea, append-only. Es el registro de trazabilidad de la plataforma. |
| salida estándar | Log de acceso de Flask/gunicorn |

El log de auditoría lo rota `logrotate` con la configuración estándar del
servidor (semanal, 8 copias). El archivo se crea con los permisos por omisión del
proceso.

Los eventos incluyen el actor, la solicitud afectada y, en las ejecuciones del
asistente, la identidad efectiva y las herramientas usadas. El formato está en
[`API.md`](API.md).

## Respaldo

```powershell
Copy-Item tramitia.sqlite3 "respaldo-$(Get-Date -Format yyyyMMdd).sqlite3"
```

Detenga el servicio antes de copiar el archivo, o use `sqlite3 .backup`.

## Comprobación de salud

```powershell
Invoke-RestMethod http://127.0.0.1:5050/health
```

Devuelve estado, versión y cliente de modelo activo. Es lo que consulta el
`HEALTHCHECK` de la imagen.

## Problemas frecuentes

| Síntoma | Causa probable |
|---|---|
| `401` en todo `/api` | Falta el encabezado `Authorization`, o la contraseña no corresponde |
| `429` al ejecutar el asistente | Presupuesto del usuario agotado; reinicie el proceso o suba `TRAMITIA_PRESUPUESTO_ASISTENTE` |
| El asistente responde distinto cada vez | Está usando el cliente `muestreado`. Fije `semilla` o use `local` |
| «documento no disponible en el catalogo local» | La URL no está en el catálogo del perfil sin conexión |
| La base no refleja los datos esperados | Está apuntando a otro archivo; verifique `TRAMITIA_DATABASE` |

## Empezar de cero

```powershell
Remove-Item tramitia.sqlite3, tramitia-auditoria.jsonl -ErrorAction SilentlyContinue
```

Al arrancar, la aplicación recrea el esquema y vuelve a cargar las cuatro
solicitudes de arranque.
