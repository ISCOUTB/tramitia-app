# Registro de cambios

## 2.4.0-rc1 — versión candidata entregada para revisión

- Topes de consumo del asistente: 4 pasos por ejecución, 400 caracteres por
  tarea y 60 invocaciones por usuario mientras el proceso esté arriba (ADR-009).
- Rechazo de campos no reconocidos en el cuerpo de `POST` y `PATCH` de
  solicitudes: antes se ignoraban en silencio.
- Nuevo campo `creada_en` en las solicitudes.
- `GET /api/admin/auditoria` acepta el parámetro `limite`.
- Cliente de modelo `muestreado` con semilla, para reproducir una corrida.
- La respuesta del asistente incluye `identidad_efectiva` y `urls_consultadas`.
- Corrección: el panel de coordinación no ordenaba el listado por prioridad en el
  tablero del comité.
- Suite de pruebas ampliada a 35 casos.

## 2.3.0

- Asistente con bucle de herramientas: `listar_solicitudes`, `priorizar` y
  `consultar_referencia`.
- Instrucciones del sistema con la política de escalamiento al comité (ADR-005).
- Los resultados de las herramientas se pasan al modelo como texto plano; se
  descartó la variante con etiquetas de delimitación por calidad de los
  resúmenes (ADR-006).
- La ejecución del asistente devuelve la traza completa, a pedido de soporte
  (ADR-007).
- El asistente resuelve sus consultas con la cuenta técnica `svc-asistente`
  (ADR-004).
- CORS con reflejo del encabezado `Origin` para el portal nuevo (ADR-008).
- Registro de auditoría append-only en JSONL.

## 2.2.0

- Validación del cuerpo en el servidor: área contra catálogo, longitud del
  resumen y rango de la prioridad (ADR-010).
- El resumen admite formato enriquecido en el panel (ADR-003).
- Panel web con listado por rol.

## 2.0.0

- Primera versión: API de solicitudes, autenticación HTTP Basic contra tabla
  local (ADR-002) y persistencia en SQLite (ADR-001).
