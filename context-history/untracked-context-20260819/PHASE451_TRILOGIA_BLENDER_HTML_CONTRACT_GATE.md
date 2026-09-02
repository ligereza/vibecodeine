# Phase 451 — Trilogía Blender HTML contract gate

## Alcance

Se auditó `cultura/trilogia.3d.blender.html`. Aunque el nombre conserva la
genealogía Blender, el archivo actual no carga un `.blend` ni inicia Blender:
es una obra Canvas 2D autónoma que modela mezcla, mapa de pertenencia y
relieve como dos lecturas hermanas (bump/desplazamiento).

## Dueño y contrato

```text
cultura/trilogia.3d.blender.html
  -> Canvas 2D local
  -> 15 modos de blend + 33x33 algebra probe
  -> address map u, campos T1/T2, iteración h
  -> twin render: bump / displacement
```

No tiene contrato con Blender, archivos 3D, bases de datos, APIs o assets
externos. Por eso se clasifica como pieza cultural interactiva autónoma, no
como servicio ni como consumidor del pipeline Plano/Venue.

## Validación foreground

Ejecutado desde `/home/mak/flujo`:

```text
Node new Function sobre script inline                    -> exit 0
Node extraction de M + grilla 33x33                     -> exit 0
HTMLParser/static dependency assertions                  -> exit 0
cmp contra flujo-deploy/cultura/trilogia.3d.blender.html -> exit 0
```

El script real tiene 8,636 bytes y parsea. Las 15 fórmulas extraídas del
bloque `M` producen valores en `[0,1]` en 16,335 evaluaciones de una grilla
33x33. El HTML tiene 12,673 bytes, 50 tags, un script inline, cero fuentes
externas, `fetch`, WebSocket, localStorage, URLs HTTP(S), `.blend` o `.gltf`.
La copia de `flujo-deploy` es idéntica, SHA-256
`eeda9681fc42847fb09fc754ae3f22e67b8bfa9dcf86a06830adcd749e0ee4a5`.

## Dictamen

```text
TRILOGIA_OWNER_GREEN
TRILOGIA_BLEND_FORMULAS_RANGE_GREEN
TRILOGIA_CANVAS_SELF_CONTAINED_GREEN
TRILOGIA_BLENDER_RUNTIME_NOT_REQUIRED
TRILOGIA_DEPLOY_COPY_EXACT
```

El sufijo `.blender` es genealogía/idea, no una dependencia actual. No se
fusiona con Blend Math Lab aunque comparten fórmulas: Blend Math es laboratorio
de superficies e histogramas; Trilogía es una pieza semántica iterativa con
relieve y dos lecturas.

## Riesgos y rollback

- La comprobación es estática y matemática; no se inició un navegador para
  medir el raster Canvas o la respuesta táctil.
- El archivo sigue usando `lang="en"` aunque contiene texto bilingüe; esto es
  una cuestión editorial de presentación, no un fallo de runtime. No se
  reescribió sin una decisión de idioma del portafolio.
- No hubo cambios en HTML, fuente, datos o despliegue; rollback: no-op.

## Siguiente acción

Continuar con la siguiente pieza HTML cultural/portfolio independiente desde
`/home/mak/*`, priorizando `tools/tapiz_three.html` ya clasificado y luego
revisar los restantes HTML visuales no cubiertos. Mantener separadas las
genealogías que comparten fórmulas pero no consumidores.
