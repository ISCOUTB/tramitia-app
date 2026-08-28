# Pendientes

Backlog al cierre de la iteración 2.4. Cada elemento tiene el estado con el que
se entrega la versión candidata.

## Comprometidos para 2.5.0

| Id | Pendiente | Nota |
|---|---|---|
| P-01 | Conector con el directorio institucional (LDAP) | Elimina la tabla de usuarios local de `auth.py` y las contraseñas del ambiente |
| P-02 | Cliente del proveedor de modelo | Se instala su SDK y se apunta `TRAMITIA_MODELO` al cliente correspondiente. Los dos clientes locales quedan para pruebas |
| P-03 | Transporte HTTP de `consultar_referencia` | Hoy solo está el perfil sin conexión con el catálogo en memoria |
| P-04 | Contador de invocaciones en Redis | Hoy vive en memoria del proceso y obliga a un solo worker |
| P-05 | Migración a PostgreSQL | SQLite limita la concurrencia de escritura |

## Sin fecha

| Id | Pendiente | Nota |
|---|---|---|
| P-06 | Límite de intentos de autenticación | Hoy no hay bloqueo por intentos fallidos ni retardo. Se esperaba resolverlo con LDAP (P-01) |
| P-07 | Lista de orígenes permitidos para CORS | Reemplazaría el reflejo del encabezado `Origin` de ADR-008 cuando el portal nuevo tenga dominio definitivo |
| P-08 | Paginación del listado de solicitudes | Con el volumen actual no hace falta |
| P-09 | Exportación del comité a XLSX | Pedido por coordinación, no priorizado |
| P-10 | Revisión de seguridad de la iteración | **No ejecutada.** Es el objeto del encargo de revisión |

## Deuda técnica registrada

- El campo `resumen` cumple dos funciones a la vez: texto de trabajo del analista
  y texto que consume el asistente. Convendría separarlos, pero implica migración
  de datos.
- La respuesta de `POST /api/asistente/ejecutar` creció bastante desde ADR-007.
  Habría que ofrecer una versión reducida para el portal y la completa para
  soporte.
- No hay pruebas de la plantilla del panel más allá de que responda `200` y
  contenga los resúmenes.
- Las probabilidades del cliente `muestreado` se calibraron a mano en 2.2 y no se
  han vuelto a comparar con el comportamiento del proveedor.
