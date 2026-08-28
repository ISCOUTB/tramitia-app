# Tramitia

[![CI](https://github.com/ISCOUTB/tramitia-app/actions/workflows/ci.yml/badge.svg)](https://github.com/ISCOUTB/tramitia-app/actions/workflows/ci.yml)

Plataforma de recepciÃ³n y triaje de solicitudes de la **DirecciÃ³n de Servicios
Compartidos (DSC)**, con asistente automatizado para apoyar a los analistas en
la revisiÃ³n y el resumen de casos.

VersiÃ³n de este paquete: **2.4.0-rc1** (candidata a producciÃ³n).
Desarrollada por **Cuadrante Digital S.A.S.** â€” equipo de plataforma.

> Este paquete se entrega para revisiÃ³n tÃ©cnica previa al despliegue. Antes de
> ejecutarlo lea [`ENTREGA.md`](ENTREGA.md) y
> [`ENCARGO-DE-REVISION.md`](ENCARGO-DE-REVISION.md).

## Descarga

El paquete de la versiÃ³n candidata estÃ¡ publicado como archivo adjunto en la
secciÃ³n *Releases* del repositorio, con la etiqueta `v2.4.0-rc1`.

```powershell
# Con el cliente de GitHub
gh release download v2.4.0-rc1 --repo ISCOUTB/tramitia-app
Expand-Archive tramitia-2.4.0-rc1.zip -DestinationPath tramitia

# O clonando el repositorio en la etiqueta entregada
git clone --branch v2.4.0-rc1 --depth 1 https://github.com/ISCOUTB/tramitia-app.git
```

El contenido del archivo adjunto y el del repositorio en esa etiqueta son
idÃ©nticos. Trabaje sobre una copia y no modifique el paquete original de la
entrega.

## QuÃ© hace

Cada analista radica solicitudes en un Ã¡rea temÃ¡tica, les asigna prioridad y las
mantiene actualizadas. La coordinaciÃ³n consolida el listado completo para el
comitÃ© semanal.

Sobre esa base, el asistente responde consultas en lenguaje natural
(Â«resume las solicitudes pendientesÂ», Â«consulta la guÃ­a de clasificaciÃ³n
vigenteÂ»). No responde de memoria: decide quÃ© herramienta usar, la plataforma la
ejecuta, el resultado vuelve al contexto y el ciclo se repite hasta el tope de
pasos configurado. Hay tres herramientas: `listar_solicitudes`, `priorizar` y
`consultar_referencia`.

## Requisitos

- Python 3.11 o superior
- Flask 3.1 (Ãºnica dependencia)

No hay servicios externos: la base es SQLite en archivo y el cliente de modelo
que se incluye es local.

## Puesta en marcha

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt

Copy-Item .env.example .env
python run.py
```

La plataforma queda en `http://127.0.0.1:5050/`. ComprobaciÃ³n rÃ¡pida, sin
credenciales:

```powershell
Invoke-RestMethod http://127.0.0.1:5050/health
```

Con Docker:

```powershell
docker compose build
docker compose up -d
```

## Cuentas del ambiente

El conector con el directorio institucional (LDAP) estÃ¡ pendiente para 2.5.0, asÃ­
que el ambiente resuelve las credenciales contra una tabla local. Personas y
casos son ficticios.

| Usuario | ContraseÃ±a | Rol |
|---|---|---|
| `ana.vargas` | `Tramitia2024` | analista |
| `bruno.mejia` | `bruno123` | analista |
| `carla.osorio` | `Tramitia2024` | coordinador |

## Endpoints

AutenticaciÃ³n HTTP Basic en todo `/api`. El detalle de cuerpos y respuestas estÃ¡
en [`docs/API.md`](docs/API.md).

| MÃ©todo y ruta | DescripciÃ³n |
|---|---|
| `GET /` | Panel web de solicitudes y asistente |
| `GET /health` | Estado y versiÃ³n |
| `GET /api/solicitudes` | Listado visible para la identidad actual |
| `POST /api/solicitudes` | Radica una solicitud |
| `GET /api/solicitudes/<id>` | Detalle |
| `PATCH /api/solicitudes/<id>` | Actualiza resumen y prioridad |
| `GET /api/asistente/herramientas` | CatÃ¡logo de herramientas y topes vigentes |
| `POST /api/asistente/ejecutar` | Ejecuta el asistente sobre una tarea |
| `POST /api/asistente/herramientas/priorizar` | InvocaciÃ³n directa, para el tablero del comitÃ© |
| `GET /api/admin/auditoria` | Ãšltimos eventos registrados |

## El asistente

`POST /api/asistente/ejecutar` recibe `tarea` y opcionalmente `modelo` y
`semilla`. Devuelve la respuesta final y la traza completa: herramientas usadas,
argumentos, contexto que recibiÃ³ el modelo en cada paso, URLs consultadas,
identidad efectiva y consumo. La traza fue un pedido explÃ­cito de soporte para
poder explicar a un analista por quÃ© el asistente respondiÃ³ lo que respondiÃ³.

### Clientes de modelo

El paquete incluye dos clientes **locales**, sin credenciales ni salida a
internet, para que la revisiÃ³n pueda hacerse sin acceso al proveedor:

- `local` â€” determinista. Es el que usa la suite de pruebas: con la misma
  entrada produce siempre la misma salida.
- `muestreado` â€” con variabilidad, como el modelo del proveedor. Acepta
  `semilla` para reproducir una corrida concreta.

El cliente del proveedor se habilita en el despliegue apuntando
`TRAMITIA_MODELO` al nombre correspondiente; ver
[`docs/PENDIENTES.md`](docs/PENDIENTES.md).

## ConfiguraciÃ³n

Todas las variables, con sus valores por defecto, estÃ¡n documentadas en
[`.env.example`](.env.example) y en [`docs/OPERACION.md`](docs/OPERACION.md).

## Pruebas

```powershell
python -m unittest discover -s tests -t tests
```

35 pruebas, alrededor de 5 segundos. Cubren la API de solicitudes, la validaciÃ³n
del cuerpo, el bucle del asistente, los topes de consumo, el catÃ¡logo de
herramientas, el panel web y el registro de auditorÃ­a. **La suite pasa completa
en esta versiÃ³n.**

### IntegraciÃ³n continua

`.github/workflows/ci.yml` corre en cada `push` y en cada *pull request* contra
`main`:

| Trabajo | QuÃ© hace |
|---|---|
| `pruebas` | Instala dependencias y corre la suite en Python 3.11 y 3.12 |
| `imagen` | Construye la imagen de contenedor, la levanta y comprueba `/health` |

El *pipeline* estÃ¡ en verde en la etiqueta `v2.4.0-rc1`, que es la que se
entrega.

## Consideraciones de seguridad

Lo que el equipo de plataforma afirma sobre esta versiÃ³n. EstÃ¡n numeradas porque
el encargo de revisiÃ³n pide un veredicto por cada una
([`ENCARGO-DE-REVISION.md`](ENCARGO-DE-REVISION.md)).

- **C-1** Toda la API exige autenticaciÃ³n; no hay endpoints anÃ³nimos salvo
  `/health`.
- **C-2** La validaciÃ³n del cuerpo se hace en el servidor contra listas de
  valores permitidos, no solo en el portal.
- **C-3** El lÃ­mite de 180 caracteres del resumen evita que alguien inserte en
  el campo contenido con marcado o con instrucciones.
- **C-4** Un analista solo puede ver y modificar sus propias solicitudes; la
  coordinaciÃ³n ve todas.
- **C-5** Las instrucciones del asistente le prohÃ­ben expresamente revelar la
  polÃ­tica interna de escalamiento.
- **C-6** El asistente no puede ejecutar herramientas privilegiadas: `priorizar`
  exige rol coordinador.
- **C-7** La herramienta `consultar_referencia` solo resuelve documentos del
  catÃ¡logo de normativa de la DSC.
- **C-8** Toda decisiÃ³n de acceso y toda invocaciÃ³n de herramienta queda
  registrada en la auditorÃ­a con la identidad que la ejecutÃ³.
- **C-9** El asistente tiene topes de consumo: pasos por ejecuciÃ³n, longitud de
  la tarea e invocaciones por usuario.

## Estructura

```
tramitia/
  __init__.py        factory de la aplicacion y /health
  api.py             API de solicitudes
  admin.py           consulta de auditoria
  ui.py              panel web
  templates/
    panel.html       plantilla unica, sin recursos externos
  auth.py            autenticacion y cuenta tecnica
  audit.py           registro append-only
  db.py              SQLite y datos de arranque
  asistente/
    api.py           endpoints del asistente
    loop.py          bucle de herramientas e instrucciones del sistema
    tools.py         listar_solicitudes, priorizar, consultar_referencia
    modelo/
      base.py        contrato del cliente de modelo
      local.py       cliente determinista
      muestreado.py  cliente con variabilidad
      _heuristica.py apoyo interno de los clientes locales
tests/               suite de la iteracion
docs/                arquitectura, API, operacion, decisiones y pendientes
.github/
  workflows/ci.yml   pruebas y construccion de la imagen
  ISSUE_TEMPLATE/    ficha de hallazgo de revision
  PULL_REQUEST_TEMPLATE.md
  CODEOWNERS
```

## Documentos del repositorio

| Archivo | Contenido |
|---|---|
| [`ENTREGA.md`](ENTREGA.md) | Acta de entrega: quÃ© se entrega, estado, advertencias y cronograma |
| [`ENCARGO-DE-REVISION.md`](ENCARGO-DE-REVISION.md) | Encargo de la revisiÃ³n previa al despliegue |
| [`CHANGELOG.md`](CHANGELOG.md) | Cambios por versiÃ³n |
| [`SECURITY.md`](SECURITY.md) | Canal y reglas para reportar hallazgos |
| [`LICENSE`](LICENSE) | Aviso de uso |
| [`docs/ARQUITECTURA.md`](docs/ARQUITECTURA.md) | Componentes, flujos y fronteras de confianza |
| [`docs/API.md`](docs/API.md) | Referencia de endpoints |
| [`docs/OPERACION.md`](docs/OPERACION.md) | Variables, despliegue, registros y respaldo |
| [`docs/DECISIONES.md`](docs/DECISIONES.md) | Registro de decisiones de diseÃ±o (ADR) |
| [`docs/PENDIENTES.md`](docs/PENDIENTES.md) | Backlog y deuda tÃ©cnica al cierre de la iteraciÃ³n |

## Contacto

Equipo de plataforma, Cuadrante Digital S.A.S. â€” `plataforma@cuadrantedigital.example`
