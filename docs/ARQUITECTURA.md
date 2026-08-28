# Arquitectura

Tramitia 2.4.0-rc1. Documento del equipo de plataforma.

## Visión general

Una sola aplicación Flask, sin servicios auxiliares. La base es SQLite en
archivo. El asistente es una capa dentro del mismo proceso.

```
                    +-------------------------------------------+
   navegador  --->  |  Tramitia (proceso Flask)                 |
   cliente API      |                                           |
                    |  ui.py ........... panel web              |
                    |  api.py .......... API de solicitudes     |
                    |  admin.py ........ consulta de auditoria  |
                    |  auth.py ......... HTTP Basic             |
                    |  audit.py ........ registro append-only   |
                    |                                           |
                    |  asistente/                               |
                    |    api.py ........ endpoints              |
                    |    loop.py ....... bucle de herramientas  |
                    |    tools.py ...... 3 herramientas         |
                    |    modelo/ ....... cliente de modelo      |
                    +--------------------+----------------------+
                                         |
                                   SQLite (archivo)
                                   auditoria (JSONL)
```

## Flujo de una petición a la API

1. `auth.py` resuelve las credenciales HTTP Basic y deja `username` y `role` en
   el contexto de la petición.
2. El endpoint valida el cuerpo contra el contrato publicado (`api.py:validar`).
3. El endpoint consulta o modifica la base a través de `db.py`.
4. `audit.py` registra el evento con el actor.
5. La respuesta sale como JSON.

## Flujo de una ejecución del asistente

1. `asistente/api.py` autentica, valida la tarea y aplica los topes de consumo.
2. Resuelve la **identidad efectiva** con la que se ejecutarán las herramientas
   (`identidad_efectiva`, ver ADR-004).
3. `asistente/loop.py` arma el contexto: instrucciones del sistema + tarea del
   usuario.
4. El cliente de modelo decide: o pide una herramienta, o entrega la respuesta.
5. Si pide una herramienta, `asistente/tools.py` la ejecuta con la identidad
   efectiva y el resultado se formatea como texto y se agrega al contexto.
6. El ciclo se repite hasta la respuesta final o hasta el tope de 4 pasos.
7. La plataforma devuelve la respuesta y la traza completa de la ejecución.

## Fronteras de confianza

El equipo identificó dos fronteras:

| Frontera | Control |
|---|---|
| Internet / plataforma | Autenticación HTTP Basic sobre todo `/api` y sobre el panel. El proxy institucional termina TLS. |
| Plataforma / base de datos | La aplicación es el único cliente de la base. Todas las consultas son parametrizadas. |

Dentro de la aplicación, los datos que ya pasaron la validación de entrada se
consideran confiables: se almacenaron porque cumplieron el contrato, de modo que
no se vuelven a inspeccionar al leerlos.

## Modelo de roles

| Rol | Alcance |
|---|---|
| `analista` | Radica solicitudes y trabaja sobre las suyas |
| `coordinador` | Ve el listado completo y usa el tablero del comité |
| `svc-asistente` | Cuenta técnica con la que el asistente resuelve sus consultas (ADR-004) |

## Decisiones de persistencia

- Una sola tabla, `solicitudes`.
- La auditoría es un archivo JSONL append-only, más una copia de los últimos 500
  eventos en memoria para el panel y para `GET /api/admin/auditoria`.
- El contador de invocaciones del asistente vive en memoria del proceso y se
  reinicia con el servicio. La versión persistente está en el backlog.

## Lo que esta arquitectura no resuelve todavía

- Un solo proceso: no hay escalado horizontal y el contador de consumo no se
  comparte entre réplicas.
- SQLite limita la concurrencia de escritura. La migración a PostgreSQL está en
  el backlog.
- El cliente de modelo del proveedor no está integrado; los dos clientes que
  trae el paquete son locales.
