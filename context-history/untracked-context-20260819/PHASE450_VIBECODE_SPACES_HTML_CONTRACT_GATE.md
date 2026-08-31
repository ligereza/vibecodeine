# Phase 450 — Tapiz Spaces HTML contract gate

## Alcance

Se auditó `projects/tapiz/vibecode_spaces.html` como herramienta visual para
leer la topología de espacios de código. Se verificó el contrato de paleta
contra `projects/flujo/flujo.json`, la carga local de archivos, el renderer de
espacios, el exportador HTML y la copia de despliegue.

## Dueño y contrato

```text
projects/flujo/flujo.json
  -> projects/tapiz/vibecode_spaces.html
       sample local de Python
       file picker .py/.txt/.js/.ts/.md/.json/.html/.css/.c/.cpp/.rs/.go
       canvas textual + modos flow/scan/drift/pulse/rain/void/length/blocks
       export HTML estático con paleta flujo forzada
  -> context/flujo_hub.html (enlace de retorno)
```

Es una herramienta local sin API, base de datos ni assets remotos. La paleta
`flujo` está primero y es el valor por defecto; la guardia avisa si se elige
una paleta interna y el exportador vuelve a forzar `flujo` antes de generar un
entregable.

## Validación foreground

Ejecutado desde `/home/mak/flujo`:

```text
Node new Function sobre script inline             -> exit 0
HTMLParser/static dependency assertions           -> exit 0
JSON parse projects/flujo/flujo.json               -> exit 0
cmp contra flujo-deploy/projects/tapiz/...         -> exit 0
```

El HTML tiene 19,675 bytes, 59 tags y un script inline sin `src`. No contiene
`fetch`, XMLHttpRequest, WebSocket, localStorage ni URLs HTTP(S). El script
real parsea con 11,994 bytes. `flujo.json` existe, parsea y declara la paleta
canónica exacta: ink `#1f2a24`, accent `#2d5a4a`, paper `#f8f1e3`, support
`#675f55` y alert `#c2410f`. La copia de `flujo-deploy` es idéntica, SHA-256
`fa6b22534036234e3207d74649741e89e0dd2b4cf2d9d3102fd8f8a67da9406e`.

## Dictamen

```text
VIBECODE_SPACES_OWNER_GREEN
VIBECODE_SPACES_BRAND_SOURCE_PRESENT
VIBECODE_SPACES_LOCAL_INPUT_GREEN
VIBECODE_SPACES_EXPORT_GUARD_PRESENT
VIBECODE_SPACES_DEPLOY_COPY_EXACT
```

Queda agrupado como laboratorio cultural/visual de Tapiz. No se fusiona con
`tapiz_renderer.html` porque no consume su schema de telemetría ni sus
payloads; comparte genealogía, no contrato runtime.

## Riesgos y rollback

- La exportación se genera solo por interacción del usuario y no se probó
  ejecutando un navegador; se verificó estáticamente el source y la guardia.
- Las paletas internas permanecen disponibles para exploración, pero el
  contrato impide que sean la paleta por defecto de un export pro.
- No hubo cambios en HTML, JSON, fuente o despliegue; rollback: no-op.

## Siguiente acción

Continuar con el siguiente HTML cultural independiente (`cultura/trilogia.3d.blender.html`), verificando su relación con el pipeline Blender/artefactos
locales y sin convertir una pieza visual histórica en servicio activo.
