# Acta de entrega — Tramitia 2.4.0-rc1

**De:** Cuadrante Digital S.A.S., equipo de plataforma
**Para:** Dirección de Servicios Compartidos — Oficina de Seguridad de la Información
**Asunto:** entrega de la versión candidata para revisión previa al despliegue

## 1. Qué se entrega

El código completo de la aplicación, la suite de pruebas de la iteración, los
manifiestos de contenedor y la documentación técnica. Nada del paquete requiere
credenciales de terceros para ejecutarse.

| Elemento | Ubicación |
|---|---|
| Código de la aplicación | `tramitia/` |
| Suite de pruebas | `tests/` |
| Documentación técnica | `docs/` |
| Contenedor | `Dockerfile`, `docker-compose.yml` |
| Configuración de referencia | `.env.example` |
| Integración continua | `.github/workflows/ci.yml` |
| Plantillas de reporte y de corrección | `.github/ISSUE_TEMPLATE/`, `.github/PULL_REQUEST_TEMPLATE.md` |

La entrega corresponde a la etiqueta `v2.4.0-rc1` del repositorio
`ISCOUTB/tramitia-app`, publicada además como archivo adjunto en la
sección *Releases*. Ambos contenidos son idénticos.

No se entrega: el cliente del proveedor de modelo (queda por instalar en el
despliegue), el conector LDAP ni los scripts de migración a PostgreSQL. Ver
[`docs/PENDIENTES.md`](docs/PENDIENTES.md).

## 2. Estado de la versión

- Las 35 pruebas de la suite pasan.
- La integración continua está en verde en la etiqueta entregada, en Python 3.11
  y 3.12.
- La imagen de contenedor construye y el `HEALTHCHECK` responde.
- Las funcionalidades comprometidas para la iteración 2.4 están implementadas
  (ver [`CHANGELOG.md`](CHANGELOG.md)).
- No hay incidentes abiertos de funcionalidad.

Esta versión **no ha pasado por revisión de seguridad**. La iteración se cerró
con dos semanas de retraso y la revisión interna se sacrificó para no mover la
fecha de salida a producción. Es justamente lo que se solicita en este encargo.

## 3. Datos del ambiente

La base de datos que se crea al arrancar contiene cuatro solicitudes de arranque
con personas y casos ficticios. No hay datos de ciudadanos reales en el paquete
ni deben cargarse durante la revisión.

## 4. Advertencias operativas para quien revise

- El paquete está configurado para escuchar en `127.0.0.1`. `docker-compose.yml`
  publica el puerto únicamente en la interfaz de bucle. **No exponga esta
  versión en una red compartida**: es una candidata sin revisar.
- La herramienta `consultar_referencia` viene con el perfil sin conexión
  (`TRAMITIA_TRANSPORTE=offline`). Con ese perfil la plataforma resuelve los
  documentos contra un catálogo en memoria y **nunca abre una conexión de red**,
  de modo que la revisión no genera tráfico hacia ningún sistema externo. El
  transporte HTTP real no viene incluido en este paquete.
- La base de datos y el log de auditoría son archivos locales. Bórrelos para
  empezar de cero (`tramitia.sqlite3`, `tramitia-auditoria.jsonl`); en Docker,
  `docker compose down -v`.

## 5. Cronograma

| Hito | Fecha |
|---|---|
| Entrega del paquete | semana 1 |
| Informe de revisión esperado | semana 3 |
| Ventana de correcciones | semana 4 |
| Despliegue previsto | semana 5 |

## 6. Canal de hallazgos

Los hallazgos se reportan como *issues* del repositorio con la plantilla
«Hallazgo de revisión de seguridad», que pide los nueve campos del encargo. Las
correcciones, si la DSC las solicita, se entregan como *pull request* con la
plantilla correspondiente. Ver [`SECURITY.md`](SECURITY.md).

## 7. Contactos

| Tema | Responsable |
|---|---|
| Plataforma y API | equipo de plataforma — `plataforma@cuadrantedigital.example` |
| Asistente y cliente de modelo | `asistente@cuadrantedigital.example` |
| Infraestructura y despliegue | DSC, operaciones — `operaciones@dsc.example` |

## 8. Firma

Entregado por el equipo de plataforma de Cuadrante Digital S.A.S. como versión
candidata. Cualquier hallazgo debe reportarse por el canal del encargo y no
directamente sobre el repositorio.
