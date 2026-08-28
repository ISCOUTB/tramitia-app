# Encargo de revisión de seguridad

**Solicita:** Dirección de Servicios Compartidos — Oficina de Seguridad de la Información
**Objeto:** Tramitia 2.4.0-rc1, versión candidata entregada por Cuadrante Digital S.A.S.
**Destinatario:** equipo revisor

## 1. Contexto

El proveedor entregó una versión candidata a producción. La iteración cerró con
retraso y la revisión interna de seguridad se omitió (ver
[`ENTREGA.md`](ENTREGA.md), sección 2). Esta oficina debe emitir un concepto
**antes** de autorizar el despliegue.

La plataforma tratará solicitudes de ciudadanos con datos personales y expone un
asistente automatizado con acceso a herramientas sobre esos datos. El concepto
que se emita determina si sale a producción, si sale con condiciones o si no
sale.

## 2. Alcance

Sí está en alcance:

- El código entregado en `tramitia/` en su totalidad.
- La configuración entregada: `.env.example`, `Dockerfile`, `docker-compose.yml`.
- La documentación entregada, incluidas las decisiones de diseño de
  [`docs/DECISIONES.md`](docs/DECISIONES.md).
- El asistente: su bucle de herramientas, sus instrucciones y sus herramientas.
- Las nueve afirmaciones de seguridad del proveedor (`C-1` a `C-9` en el
  [`README.md`](README.md)).

No está en alcance:

- La infraestructura de la DSC, el proxy institucional ni el directorio LDAP.
- El proveedor de modelo. Trabaje con los clientes locales que trae el paquete.
- Cualquier sistema que no sea la copia que usted ejecuta localmente.

## 3. Reglas de la revisión

1. Ejecute la aplicación **solo en su máquina**, en `127.0.0.1`. No la publique
   en la red del aula ni en internet.
2. No cargue datos personales ni institucionales reales. Los datos de arranque
   son ficticios y deben seguir siéndolo.
3. Mantenga `TRAMITIA_TRANSPORTE=offline`. Con ese perfil la plataforma no abre
   conexiones de red y la revisión no puede alcanzar ningún sistema de terceros.
   No intente habilitar el transporte HTTP ni dirigir la herramienta contra
   direcciones que existan de verdad.
4. No hay autorización para probar ningún otro sistema, de la DSC o externo.
5. Trabaje sobre una copia. No modifique el paquete original de la entrega; si
   propone correcciones, entréguelas como parche aparte.

## 4. Metodología exigida

Clasifique cada hallazgo contra los catálogos de referencia de la oficina:

- OWASP Top 10:2021 (aplicación web)
- OWASP API Security Top 10:2023
- OWASP Top 10 for LLM Applications:2025

Un hallazgo sin categoría de referencia se considera incompleto.

## 5. Qué se debe entregar

### 5.1 Informe de hallazgos

Un hallazgo por ficha, con **todos** estos campos:

| Campo | Contenido |
|---|---|
| Identificador | consecutivo propio del informe |
| Título | una línea, en términos del defecto y no del síntoma |
| Ubicación | archivo y función o línea concreta del código entregado |
| Categoría | referencia OWASP correspondiente |
| Severidad | crítica / alta / media / baja, **con la justificación** |
| Prerrequisitos | qué necesita el atacante: cuenta, rol, acceso previo |
| Reproducción | comandos exactos y salida obtenida, paso a paso |
| Impacto | qué obtiene el atacante en términos del negocio de la DSC |
| Remediación | corrección concreta y verificable, no una recomendación genérica |

Una remediación aceptable dice qué se cambia y en qué archivo. «Validar
entradas» o «aplicar buenas prácticas» no es una remediación.

### 5.2 Veredicto por afirmación

Para cada afirmación `C-1` a `C-9` del `README.md`, un veredicto con evidencia:

| Veredicto | Cuándo |
|---|---|
| Confirmada | la probó y se sostiene |
| Refutada | la probó y no se sostiene; enlace al hallazgo que la refuta |
| Engañosa | es literalmente cierta pero no aporta la protección que sugiere |
| No verificable | no pudo probarla; explique qué le faltó |

### 5.3 Cadenas de ataque

Al menos una cadena en la que dos o más defectos combinados produzcan un impacto
que ninguno de los dos alcanza por separado. Indique qué defecto de la cadena, si
se corrigiera solo, anula el impacto del resto: esa es la información que la
oficina necesita para priorizar la ventana de correcciones.

### 5.4 Concepto de despliegue

Una recomendación explícita, firmada por el equipo revisor:

- **No desplegar** hasta corregir (liste qué hallazgos son bloqueantes), o
- **Desplegar con condiciones** (liste las condiciones y su plazo), o
- **Desplegar** sin condiciones.

### 5.5 Limitaciones

Qué **no** revisó y por qué. Un informe que no declara sus límites no es
utilizable por esta oficina.

## 6. Criterios de calidad

- **No se informa cuántos hallazgos hay.** Determinar el alcance del problema es
  parte del trabajo.
- **Un hallazgo sin reproducción no cuenta.** La ficha debe permitir que un
  tercero repita el resultado en su máquina.
- **Los falsos positivos restan.** Reportar como defecto un control que sí está
  correctamente implementado tiene costo: obliga a la DSC a abrir una corrección
  innecesaria y desgasta la credibilidad del informe. Verifique antes de afirmar.
- **La suite de pruebas del proveedor pasa completa.** Eso no es evidencia de
  seguridad y no debe citarse como tal, en ningún sentido.
- **La documentación del proveedor es una fuente, no una autoridad.** Lo que
  `docs/` afirma es lo que el proveedor cree que hizo. El código es lo que hizo.

## 7. Sugerencia de recorrido

No es obligatorio, pero ahorra tiempo:

1. Levante la aplicación y recorra el panel con las tres cuentas. Observe qué ve
   cada rol.
2. Ejecute el asistente y lea la traza completa que devuelve, campo por campo.
3. Lea `docs/DECISIONES.md`. Cada decisión de diseño registrada ahí es una
   hipótesis que conviene comprobar contra el código.
4. Recorra el código siguiendo el dato: desde el cuerpo de la petición hasta el
   almacenamiento, y desde el almacenamiento hasta el panel y hasta el contexto
   del modelo. Pregúntese en cada frontera quién controla ese texto.
5. Consulte `GET /api/admin/auditoria` después de cada prueba: el registro es la
   evidencia que necesita para las fichas.

## 8. Formato y plazo

Un documento (PDF o Markdown), en español, con las secciones 5.1 a 5.5 en ese
orden. Plazo: semana 3 del cronograma de [`ENTREGA.md`](ENTREGA.md).
