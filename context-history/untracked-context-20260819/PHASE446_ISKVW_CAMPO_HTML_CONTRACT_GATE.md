# Phase 446 — ISKVW Campo HTML contract gate

## Alcance

Se auditó el siguiente consumidor HTML independiente encontrado desde
`/home/mak/*`: la piel activa `iskvw/piel/campo/index.html`. Se verificó su
dueño físico, los datos que consume, el puente opcional con la piel de venue,
la copia de despliegue y la frontera con los artefactos históricos.

## Dueño y contrato

```text
iskvw/piel/campo/index.html
  -> iskvw/datos/archivo.json       (sustrato principal: piezas + vinculos)
  -> iskvw/datos/campo.json         (fallback de piezas)
  -> iskvw/datos/obras.json         (fallback final)
  -> iskvw/datos/tablero.json       (patch_efectos + mejoras.venue3d)
  -> iskvw/piel/venue/index.html    (enlace condicional ../venue/)
```

La piel abre sin servidor usando `RESPALDO.obras`; con servidor intenta primero
`archivo.json`, luego `campo.json` y finalmente `obras.json`. El archivo
`tablero.json` se lee una vez. Solo si `mejoras.venue3d === true` agrega el
enlace dinámico `../venue/`; no mezcla la base técnica de venues con la base
RD ni copia registros entre dominios.

## Validación foreground

Ejecutado desde `/home/mak/flujo`:

```text
node [new Function sobre el script inline]              -> exit 0
HTMLParser (19 tags, 1 script, 0 src externos)         -> exit 0
JSON parse de archivo/campo/obras/tablero              -> exit 0
cmp campo/index.html vs flujo-deploy copy              -> exit 0
```

El script inline tiene 69,467 bytes y pasa sintaxis. Los cuatro JSON existen y
se parsean. `archivo.json` tiene las claves `piezas`, `vinculos` y `meta`;
`campo.json` tiene 93,657 bytes; `obras.json` conserva 8 obras de respaldo;
`tablero.json` declara `mejoras.venue3d=true`. La piel canónica y su copia de
`flujo-deploy` son idénticas: 75,813 bytes,
SHA-256 `2e7548a3e7355716b7b151981287b73662299bb8666929bb8664959b4051d807`.
Los `http://` encontrados son únicamente namespaces SVG, no dependencias
externas de ejecución.

## Dictamen

```text
ISKVW_CAMPO_OWNER_GREEN
ISKVW_CAMPO_DATA_FALLBACK_GREEN
ISKVW_CAMPO_VENUE_SWITCH_GREEN
ISKVW_CAMPO_DEPLOY_COPY_EXACT
ISKVW_CAMPO_HISTORICAL_VARIANTS_PRESERVED
```

Es una piel activa de portafolio, no una herramienta RD ni un duplicado de la
piel venue. Su relación con venue es un enlace condicional gobernado por el
tablero, por lo que se mantiene como puente lógico.

## Riesgos y rollback

- Las copias de WIN, Vibecodeine y cuarentena tienen hashes/tamaños distintos;
  permanecen como evidencia histórica y no se promueven por similitud.
- La validación fue estática; no se inició servidor ni se automatizó un
  navegador. El fallback local y el gate de venue están explícitos en el
  código, pero un smoke visual queda como validación posterior si cambia el
  entorno de publicación.
- No hubo cambios en fuente, datos, HTML, venue ni despliegue; rollback:
  no-op.

## Siguiente acción

Continuar con `tools/tapiz_renderer.html`, verificando su contrato con
`tools/compete_engine.py`, `tools/system_map.py` y el input demo explícito.
Mantener separado el renderer 3D `tapiz_three.html`, que requiere el CDN de
Three.js y no debe confundirse con el renderer local ni con XIO.
