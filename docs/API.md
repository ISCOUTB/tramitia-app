# API

Tramitia 2.4.0-rc1. Autenticación HTTP Basic en todo `/api` y en el panel. `/health`
es el único endpoint anónimo.

Todos los cuerpos son JSON (`Content-Type: application/json`). Los errores
devuelven `{"error": "<mensaje>"}` con el código correspondiente.

Si prefiere un cliente grafico a la terminal, en [`../bruno/`](../bruno/) esta la
misma API como coleccion de [Bruno](https://www.usebruno.com/), con las cuentas
ya configuradas y una asercion por cada respuesta que este documento promete.

## Ayudante para la terminal

Los dos ayudantes de abajo se llaman igual y reciben los mismos argumentos, de
modo que los ejemplos de este documento sirven en cualquiera de los dos sistemas:

```
<ayudante> <usuario> <METODO> <ruta> [cuerpo JSON]
```

### macOS y Linux (bash o zsh)

```bash
tramitia() {
  local usuario=$1 metodo=$2 ruta=$3 cuerpo=$4 puerto=${5:-5050}
  local clave
  case "$usuario" in
    ana.vargas)   clave='Tramitia2024' ;;
    bruno.mejia)  clave='bruno123' ;;
    carla.osorio) clave='Tramitia2024' ;;
    *) echo "usuario desconocido: $usuario" >&2; return 1 ;;
  esac
  if [ -n "$cuerpo" ]; then
    curl -s -u "$usuario:$clave" -X "$metodo"       -H 'Content-Type: application/json' -d "$cuerpo"       -w '
HTTP %{http_code}
' "http://127.0.0.1:$puerto$ruta"
  else
    curl -s -u "$usuario:$clave" -X "$metodo"       -w '
HTTP %{http_code}
' "http://127.0.0.1:$puerto$ruta"
  fi
}
```

Péguelo una vez en la terminal de peticiones. Para leer las respuestas con
sangría, encadene `| python3 -m json.tool` o, si tiene `jq`, `| jq`. El código
HTTP se imprime al final de cada respuesta, que es lo que interesa cuando se
comparan `200`, `403` y `429`.

En macOS, `curl` viene con el sistema; no hay que instalar nada.

Si trabaja en **Git Bash sobre Windows**, use el ayudante de PowerShell: al pasar
un argumento con acentos a `curl.exe` los caracteres se corrompen y el servidor
rechaza el cuerpo con un `400` que parece de validación. Si aun así necesita
`curl`, pase el cuerpo por archivo: `--data-binary @cuerpo.json`.

### Windows (PowerShell)

En PowerShell 5.1 las comillas del cuerpo JSON se destrozan al pasarlas a
`curl.exe`, que acaba enviando un cuerpo que el servidor rechaza. Use este
ayudante, que recibe el mismo JSON en texto:

```powershell
function tramitia($Usuario, $Metodo, $Ruta, $Cuerpo, $Puerto = 5050) {
  $clave = @{
    'ana.vargas'   = 'Tramitia2024'
    'bruno.mejia'  = 'bruno123'
    'carla.osorio' = 'Tramitia2024'
  }[$Usuario]
  $cred = [PSCredential]::new($Usuario, (ConvertTo-SecureString $clave -AsPlainText -Force))
  $opts = @{ Method = $Metodo; Uri = "http://127.0.0.1:$Puerto$Ruta"; Credential = $cred }
  if ($Cuerpo) {
    $opts.Body = [System.Text.Encoding]::UTF8.GetBytes($Cuerpo)
    $opts.ContentType = 'application/json; charset=utf-8'
  }
  try { Invoke-RestMethod @opts }
  catch { "HTTP $([int]$_.Exception.Response.StatusCode): $($_.ErrorDetails.Message)" }
}
```

Uso, idéntico en los dos sistemas:

```
tramitia ana.vargas GET /api/solicitudes
tramitia ana.vargas POST /api/solicitudes '{"area":"salud","resumen":"Caso nuevo","prioridad":3}'
```

## `GET /health`

Sin autenticación.

```json
{ "status": "ok", "version": "2.4.0-rc1", "modelo": "local" }
```

## Solicitudes

### `GET /api/solicitudes`

Listado visible para la identidad autenticada. Un `analista` recibe las suyas; un
`coordinador`, todas.

```json
[
  {
    "id": 1,
    "propietario": "ana.vargas",
    "area": "educacion",
    "resumen": "Revisar la retroalimentacion de la entrega 4 del programa de becas",
    "prioridad": 2,
    "creada_en": "2026-01-15T14:03:11+00:00"
  }
]
```

### `POST /api/solicitudes`

| Campo | Tipo | Reglas |
|---|---|---|
| `area` | texto | obligatorio; una de `salud`, `educacion`, `finanzas`, `derecho`, `industria`, `comunicacion` |
| `resumen` | texto | obligatorio; máximo 180 caracteres |
| `prioridad` | entero | opcional (1 por omisión); entre 1 y 5 |

Cualquier otro campo produce `400`. El propietario lo determina la sesión y no se
acepta en el cuerpo.

```
tramitia ana.vargas POST /api/solicitudes '{"area":"salud","resumen":"Caso nuevo","prioridad":3}'
```

Responde `201` con la solicitud creada.

### `GET /api/solicitudes/<id>`

Devuelve el detalle, o `404` si no existe.

### `PATCH /api/solicitudes/<id>`

Actualiza `resumen` y `prioridad` con las mismas reglas de validación. `area` y
`propietario` no son editables.

```
tramitia bruno.mejia PATCH /api/solicitudes/2 '{"resumen":"Texto corregido","prioridad":5}'
```

## Asistente

### `GET /api/asistente/herramientas`

Catálogo de herramientas y topes vigentes.

```json
{
  "herramientas": [
    { "name": "listar_solicitudes", "description": "...", "parameters": { } },
    { "name": "priorizar", "description": "...", "parameters": { } },
    { "name": "consultar_referencia", "description": "...", "parameters": { } }
  ],
  "limite_pasos": 4,
  "limite_tarea": 400,
  "presupuesto": 60
}
```

### `POST /api/asistente/ejecutar`

| Campo | Tipo | Reglas |
|---|---|---|
| `tarea` | texto | obligatorio; máximo 400 caracteres |
| `modelo` | texto | opcional; `local` (por omisión) o `muestreado` |
| `semilla` | entero | opcional; solo aplica al cliente `muestreado` |

```
tramitia carla.osorio POST /api/asistente/ejecutar '{"tarea":"Resume las solicitudes pendientes"}'
tramitia carla.osorio POST /api/asistente/ejecutar '{"tarea":"Resume las solicitudes pendientes","modelo":"muestreado","semilla":14}'
```

Respuesta:

| Campo | Significado |
|---|---|
| `respuesta` | Texto final del asistente |
| `pasos` | Un objeto por paso: `herramienta`, `argumentos`, `devueltas`, `url`, `error`, `contexto` |
| `herramientas_usadas` | Herramientas ejecutadas, en orden |
| `urls_consultadas` | Documentos que la herramienta de referencia alcanzó |
| `pasos_usados` / `limite_pasos` | Pasos consumidos y tope vigente |
| `detenido_por_limite` | El bucle se cortó por el tope de pasos |
| `solicitante` | Usuario autenticado que pidió la ejecución |
| `identidad_efectiva` | Identidad con la que corrieron las herramientas |
| `modelo` / `semilla` | Cliente de modelo usado y semilla aplicada |
| `invocaciones_usadas` / `presupuesto` | Consumo del usuario y tope |

`contexto` es el texto exacto que recibió el modelo en ese paso. Es el campo que
usa soporte para explicar una respuesta (ADR-007).

Con el presupuesto agotado responde `429`. Con una tarea de más de 400
caracteres, `400`.

### `POST /api/asistente/herramientas/priorizar`

Invocación directa de la herramienta, sin el modelo de por medio. La usa el
tablero del comité. Exige rol `coordinador`; con `analista` responde `403`.

```
tramitia carla.osorio POST /api/asistente/herramientas/priorizar '{}'
tramitia ana.vargas   POST /api/asistente/herramientas/priorizar '{}'   # 403
```

## Auditoría

### `GET /api/admin/auditoria`

Últimos eventos registrados por la plataforma. Parámetro `limite` (100 por
omisión).

```
tramitia carla.osorio GET '/api/admin/auditoria?limite=20'
```

```json
{
  "total": 3,
  "eventos": [
    { "ts": "...", "event": "solicitud.creada", "actor": "ana.vargas", "solicitud": 5 },
    { "ts": "...", "event": "herramienta.ejecutada", "actor": "ana.vargas",
      "herramienta": "listar_solicitudes", "principal": "svc-asistente",
      "rol_principal": "coordinador", "devueltas": 4 }
  ]
}
```

Eventos registrados: `auth.denegada`, `acceso.concedido`, `acceso.denegado`,
`solicitud.creada`, `solicitud.editada`, `asistente.ejecucion`,
`asistente.presupuesto_agotado`, `herramienta.ejecutada`, `herramienta.denegada`.
