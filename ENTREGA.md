# Acta de entrega â€” Tramitia 2.4.0-rc1

**De:** Cuadrante Digital S.A.S., equipo de plataforma
**Para:** DirecciÃ³n de Servicios Compartidos â€” Oficina de Seguridad de la InformaciÃ³n
**Asunto:** entrega de la versiÃ³n candidata para revisiÃ³n previa al despliegue

## 1. QuÃ© se entrega

El cÃ³digo completo de la aplicaciÃ³n, la suite de pruebas de la iteraciÃ³n, los
manifiestos de contenedor y la documentaciÃ³n tÃ©cnica. Nada del paquete requiere
credenciales de terceros para ejecutarse.

| Elemento | UbicaciÃ³n |
|---|---|
| CÃ³digo de la aplicaciÃ³n | `tramitia/` |
| Suite de pruebas | `tests/` |
| DocumentaciÃ³n tÃ©cnica | `docs/` |
| Contenedor | `Dockerfile`, `docker-compose.yml` |
| ConfiguraciÃ³n de referencia | `.env.example` |
| IntegraciÃ³n continua | `.github/workflows/ci.yml` |
| Plantillas de reporte y de correcciÃ³n | `.github/ISSUE_TEMPLATE/`, `.github/PULL_REQUEST_TEMPLATE.md` |

La entrega corresponde a la etiqueta `v2.4.0-rc1` del repositorio
`ISCOUTB/tramitia-app`, publicada ademÃ¡s como archivo adjunto en la
secciÃ³n *Releases*. Ambos contenidos son idÃ©nticos.

No se entrega: el cliente del proveedor de modelo (queda por instalar en el
despliegue), el conector LDAP ni los scripts de migraciÃ³n a PostgreSQL. Ver
[`docs/PENDIENTES.md`](docs/PENDIENTES.md).

## 2. Estado de la versiÃ³n

- Las 35 pruebas de la suite pasan.
- La integraciÃ³n continua estÃ¡ en verde en la etiqueta entregada, en Python 3.11
  y 3.12.
- La imagen de contenedor construye y el `HEALTHCHECK` responde.
- Las funcionalidades comprometidas para la iteraciÃ³n 2.4 estÃ¡n implementadas
  (ver [`CHANGELOG.md`](CHANGELOG.md)).
- No hay incidentes abiertos de funcionalidad.

Esta versiÃ³n **no ha pasado por revisiÃ³n de seguridad**. La iteraciÃ³n se cerrÃ³
con dos semanas de retraso y la revisiÃ³n interna se sacrificÃ³ para no mover la
fecha de salida a producciÃ³n. Es justamente lo que se solicita en este encargo.

## 3. Datos del ambiente

La base de datos que se crea al arrancar contiene cuatro solicitudes de arranque
con personas y casos ficticios. No hay datos de ciudadanos reales en el paquete
ni deben cargarse durante la revisiÃ³n.

## 4. Advertencias operativas para quien revise

- El paquete estÃ¡ configurado para escuchar en `127.0.0.1`. `docker-compose.yml`
  publica el puerto Ãºnicamente en la interfaz de bucle. **No exponga esta
  versiÃ³n en una red compartida**: es una candidata sin revisar.
- La herramienta `consultar_referencia` viene con el perfil sin conexiÃ³n
  (`TRAMITIA_TRANSPORTE=offline`). Con ese perfil la plataforma resuelve los
  documentos contra un catÃ¡logo en memoria y **nunca abre una conexiÃ³n de red**,
  de modo que la revisiÃ³n no genera trÃ¡fico hacia ningÃºn sistema externo. El
  transporte HTTP real no viene incluido en este paquete.
- La base de datos y el log de auditorÃ­a son archivos locales. BÃ³rrelos para
  empezar de cero (`tramitia.sqlite3`, `tramitia-auditoria.jsonl`); en Docker,
  `docker compose down -v`.

## 5. Cronograma

| Hito | Fecha |
|---|---|
| Entrega del paquete | semana 1 |
| Informe de revisiÃ³n esperado | semana 3 |
| Ventana de correcciones | semana 4 |
| Despliegue previsto | semana 5 |

## 6. Canal de hallazgos

Los hallazgos se reportan como *issues* del repositorio con la plantilla
Â«Hallazgo de revisiÃ³n de seguridadÂ», que pide los nueve campos del encargo. Las
correcciones, si la DSC las solicita, se entregan como *pull request* con la
plantilla correspondiente. Ver [`SECURITY.md`](SECURITY.md).

## 7. Contactos

| Tema | Responsable |
|---|---|
| Plataforma y API | equipo de plataforma â€” `plataforma@cuadrantedigital.example` |
| Asistente y cliente de modelo | `asistente@cuadrantedigital.example` |
| Infraestructura y despliegue | DSC, operaciones â€” `operaciones@dsc.example` |

## 8. Firma

Entregado por el equipo de plataforma de Cuadrante Digital S.A.S. como versiÃ³n
candidata. Cualquier hallazgo debe reportarse por el canal del encargo y no
directamente sobre el repositorio.
