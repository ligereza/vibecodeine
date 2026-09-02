# Phase 453 — RD identity palette owner gate

## Alcance

Se auditó el HTML cultural/RD `projects/cultura/identidad/identidad_rd.html`
y su dueño real `projects/cultura/paleta_reactivos.py`. La pregunta de
consolidación era si el HTML debía fusionarse con Gota RD o con la tabla
operativa de reactivos. La respuesta es no: esta pieza es una hoja de
identidad/paleta visual, mientras Gota y `reactivo_matcher` son consumidores
distintos.

## Dueño y contrato

```text
projects/cultura/paleta_reactivos.py
  -> projects/cultura/identidad/reactivos.json
  -> projects/cultura/identidad/identidad_rd.html
```

El generador declara 23 reacciones y 6 colores de marca. La salida contiene
un disclaimer PRESUNTIVO y marca que los colores son referencia estética, no
un kit de análisis ni una confirmación de sustancia. `tools/gota_rd/index.html`
mantiene su propia tabla DEMO y no debe importar esta paleta como verdad
operativa. La base RD y el matcher tampoco se reescriben a partir de este
HTML.

## Validación foreground

Ejecutado desde `/home/mak/flujo`:

```text
py_compile paleta_reactivos.py                         -> exit 0
generator.py --out /tmp/mak-identidad-check.*         -> exit 0
cmp temp/reactivos.json vs canonical                  -> exit 0
cmp temp/identidad_rd.html vs canonical                -> exit 0
HTMLParser + disclaimer/traceability assertions        -> exit 0
```

La salida temporal produjo 23 reacciones + 6 colores de marca. El HTML
generado tiene 5,675 bytes, 143 tags y cero scripts/links. Los swatches son
trazables a los hex del JSON y el disclaimer está presente en JSON y HTML.
La salida canónica coincide byte a byte con la generación fresca, por lo que
no existe una divergencia oculta que reparar.

## Dictamen

```text
RD_IDENTITY_PALETTE_OWNER_GREEN
RD_IDENTITY_GENERATOR_DETERMINISTIC_GREEN
RD_IDENTITY_DISCLAIMER_GREEN
RD_IDENTITY_SWATCH_TRACEABILITY_GREEN
RD_IDENTITY_NOT_OFFICIAL_REACTION_TABLE
RD_IDENTITY_NOT_GOTA_RUNTIME
```

La pieza queda agrupada con Cultura/RD identidad visual, separada de la tabla
oficial futura, del matcher y de Gota. Esto evita convertir una paleta estética
en una afirmación de análisis químico.

## Riesgos y rollback

- Las afirmaciones de reacciones son material sensible y presuntivo; cualquier
  uso operativo requiere revisión de fuente oficial RD. En esta fase solo se
  validó el contrato del generador, no la verdad química.
- La generación se ejecutó únicamente en `/tmp`; no se tocó la identidad
  canónica ni la base RD.
- No hubo cambios en archivos versionados, datos, HTML o evidencia; rollback:
  no-op.

## Siguiente acción

Continuar con la siguiente superficie HTML no cubierta, priorizando una pieza
visual no sensible. Mantener la separación entre identidad estética,
reactivos operativos, Gota DEMO y base RD.
