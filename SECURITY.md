# Reporte de problemas de seguridad

## Versión bajo revisión

`2.4.0-rc1` es una versión **candidata** que no ha pasado revisión de seguridad
y no está desplegada. No la exponga en ninguna red compartida.

## Cómo reportar

Durante la revisión previa al despliegue, los hallazgos se reportan por el canal
del encargo ([`ENCARGO-DE-REVISION.md`](ENCARGO-DE-REVISION.md)):

- Una ficha por hallazgo, con los nueve campos que exige la sección 5.1 del
  encargo. La plantilla de *issue* «Hallazgo de revisión de seguridad» los pide
  en orden.
- No abra un *pull request* con la corrección antes de que el hallazgo esté
  aceptado: la Dirección de Servicios Compartidos prioriza la ventana de
  correcciones a partir del informe.

Para reportes fuera del proceso de revisión:
`seguridad@cuadrantedigital.example`.

## Qué no hacer

- No pruebe contra ningún despliegue de la DSC: el alcance autorizado es la copia
  local de quien revisa.
- No cargue datos personales ni institucionales reales en el ambiente. Los datos
  de arranque son ficticios y deben seguir siéndolo.
- Mantenga `TRAMITIA_TRANSPORTE=offline`. Con ese perfil la aplicación no abre
  conexiones de red y la revisión no puede alcanzar sistemas de terceros.

## Alcance de la respuesta

| Tipo | Compromiso |
|---|---|
| Hallazgo del proceso de revisión | Respuesta dentro de la ventana de correcciones del cronograma |
| Reporte externo sobre `2.4.0-rc1` | Acuse en 5 días hábiles |
| Versiones anteriores a `2.4` | Sin soporte: no están desplegadas |
