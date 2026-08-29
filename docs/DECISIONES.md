# Registro de decisiones de diseño

Decisiones tomadas por el equipo de plataforma durante las iteraciones 2.2 a
2.4, con el motivo que se registró en el momento. Se conservan tal como se
escribieron.

---

## ADR-001 — SQLite en archivo para la primera fase

**Estado:** aceptada (2.0)

El volumen esperado en el primer año es de unos cientos de solicitudes por mes.
SQLite evita aprovisionar y operar un motor aparte. La migración a PostgreSQL
queda planteada para cuando la concurrencia de escritura lo exija.

---

## ADR-002 — HTTP Basic mientras no exista el conector LDAP

**Estado:** aceptada (2.0), pendiente de revisión

El directorio institucional no estaba disponible al iniciar el proyecto. Se optó
por HTTP Basic contra una tabla de usuarios local, con la contraseña almacenada
mediante `werkzeug.security`. El proxy institucional termina TLS, así que las
credenciales no viajan en claro entre el navegador y el proxy.

Al integrar LDAP (2.5) esta tabla desaparece.

---

## ADR-003 — El resumen admite formato enriquecido

**Estado:** aceptada (2.2)

Los analistas pidieron poder resaltar texto y dejar vínculos al expediente
dentro del resumen. El editor del portal produce marcado ligero, de modo que el
resumen se inserta en el panel tal como fue guardado y no codificado; de otro
modo el usuario vería las etiquetas en pantalla en lugar del formato.

El riesgo se consideró bajo porque el campo tiene un tope de 180 caracteres y
solo lo escriben analistas autenticados de la DSC.

---

## ADR-004 — El asistente resuelve sus consultas con una cuenta técnica

**Estado:** aceptada (2.3)

Al construir el asistente se evaluaron dos opciones para ejecutar sus
herramientas:

1. Propagar la identidad del analista que hace la consulta.
2. Usar una cuenta técnica de la plataforma (`svc-asistente`).

Se eligió la segunda. Con la primera, el asistente devolvía resúmenes
incompletos cuando la consulta abarcaba solicitudes de varias áreas, y soporte
recibió tres reclamos en la prueba piloto por «el asistente no ve mis casos».
Con la cuenta técnica el asistente responde de forma consistente para cualquier
analista.

La cuenta técnica tiene rol coordinador porque necesita el listado completo para
resumir. El control de acceso del usuario final se mantiene en los endpoints de
la API, que es donde el analista consulta sus datos directamente.

---

## ADR-005 — La política de escalamiento va en las instrucciones del sistema

**Estado:** aceptada (2.3)

El asistente debe aplicar la regla de escalamiento al comité, que incluye el
código de escalamiento vigente. Se colocó en las instrucciones del sistema, con
la indicación expresa de no compartir el código con el usuario y de usarlo solo
al construir el resumen para el comité.

Se evaluó consultarlo desde un servicio aparte solo cuando fuera necesario, pero
implicaba una llamada adicional en cada ejecución.

---

## ADR-006 — Los resultados de las herramientas se pasan al modelo como texto plano

**Estado:** aceptada (2.3)

El resultado de cada herramienta se serializa como texto legible y se agrega al
contexto del modelo.

En las pruebas de la iteración 2.2 se probó una variante que envolvía el
contenido en etiquetas (`<untrusted_content>`) para separarlo del resto del
contexto. La variante se descartó: los resúmenes salían más pobres y en varios
casos el modelo mencionaba las etiquetas en su respuesta al usuario. El formato
plano dio mejores resúmenes.

---

## ADR-007 — La ejecución del asistente devuelve la traza completa

**Estado:** aceptada (2.3)

Soporte no podía explicar por qué el asistente había respondido lo que
respondió. Desde 2.3 la respuesta incluye herramientas usadas, argumentos, el
contexto que recibió el modelo en cada paso, las URLs consultadas, la identidad
efectiva y el consumo.

---

## ADR-008 — CORS con reflejo del origen

**Estado:** aceptada (2.3)

El portal nuevo se sirve desde otro origen durante el desarrollo. Para que
pudiera consumir la API con la sesión del navegador se agregó el reflejo del
encabezado `Origin` junto con `Access-Control-Allow-Credentials`. Un valor fijo
`*` no funciona con credenciales, y mantener una lista de orígenes obligaba a
tocar la configuración en cada ambiente.

---

## ADR-009 — Topes de consumo del asistente

**Estado:** aceptada (2.4)

Una ejecución del asistente puede encadenar llamadas al proveedor, y el
proveedor cobra por uso. Se fijaron tres topes:

- 4 pasos por ejecución;
- 400 caracteres por tarea;
- 60 invocaciones por usuario mientras el proceso esté arriba.

Los tres se aplican en el servidor. El tope de pasos, además, garantiza que el
bucle termine siempre.

Excepción: el comité pidió una vía para las tareas que marcan como `urgente`,
de modo que una alerta activa no espere el mismo turno que una consulta
ordinaria. Esas tareas no cuentan contra los tres topes.

---

## ADR-010 — La validación del cuerpo se hace en el servidor

**Estado:** aceptada (2.2)

El portal valida el formulario, pero la API es pública para clientes internos, de
modo que la validación se repite en el servidor: área contra la lista de áreas
habilitadas, longitud del resumen, rango de la prioridad y rechazo de campos no
reconocidos. Un campo que la API no espera es un error del cliente y se
responde `400` en lugar de ignorarlo en silencio.

La coordinación certifica área y resumen en el tablero del comité antes de
radicarlos, así que el contrato de dominio y de longitud no se repite para las
solicitudes que crea o edita ese rol. El rechazo de campos no reconocidos y el
rango de la prioridad sí se mantienen para todos los roles.
