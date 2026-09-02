# Phase 448 — Tapiz Three external dependency gate

## Alcance

Se auditó estáticamente `tools/tapiz_three.html`, la variante 3D del renderer
Tapiz. Se verificaron su import map, fallback local, contrato de input,
sintaxis del módulo y copia de despliegue. No se solicitó el CDN y no se
levantó servidor.

## Dueño y contrato

```text
tools/compete_engine.py --demo
  -> tools/dist/system_status.json
  -> tools/tapiz_three.html
       importmap: three@0.160.0 desde unpkg (dependencia externa explícita)
       file-picker: tools/dist/system_status.json (fallback file://)
```

La variante 3D está correctamente separada de `tools/tapiz_renderer.html`: el
renderer local no requiere Three.js, mientras que esta pieza sí lo requiere
para instanciación de cubos, cámara, raycaster y overlay de payloads.

## Validación foreground

Ejecutado desde `/home/mak/flujo`:

```text
Node SourceTextModule parse del módulo inline        -> exit 0
HTMLParser/importmap/input assertions                -> exit 0
cmp contra flujo-deploy/tools/tapiz_three.html       -> exit 0
```

El módulo inline tiene 10,827 bytes y parsea sin ejecutar imports. El HTML
tiene 16,353 bytes, 37 tags, un import map y un módulo inline. El import map
apunta exactamente a
`https://unpkg.com/three@0.160.0/build/three.module.js`; esto fue solo lectura
estática, sin request de red. El input esperado es
`dist/system_status.json`, con selector local `.json` para el caso `file://`.
La copia de `flujo-deploy` es idéntica, SHA-256
`00c80dc35c014cd41ea15bd26a8e8ab3f7a2268f62c411e70a94ddd80c5006e9`.

## Dictamen

```text
TAPIZ_THREE_OWNER_GREEN
TAPIZ_THREE_MODULE_SYNTAX_GREEN
TAPIZ_THREE_LOCAL_FILE_FALLBACK_GREEN
TAPIZ_THREE_EXTERNAL_CDN_EXPLICIT_AND_GATED
TAPIZ_THREE_DEPLOY_COPY_EXACT
```

La pieza está integrada como proyección 3D condicionada a disponibilidad del
CDN. No se debe declarar runtime completo hasta probarla en un navegador con
Three.js disponible; esa prueba requiere una decisión de red/entorno distinta
y no se simula aquí.

## Riesgos y rollback

- Sin CDN, el import de Three.js no resuelve; la pieza conserva el selector de
  JSON pero no puede renderizar la escena 3D.
- El estado JSON es el input demo ya validado por `system_map.py`; no es
  telemetría viva ni diagnóstico.
- No hubo cambios en HTML, JSON, fuente, despliegue o evidencia; rollback:
  no-op.

## Siguiente acción

Continuar con la siguiente superficie cultural/visual independiente desde
`/home/mak/*`, empezando por `cultura/blend-math-lab.html` o
`projects/tapiz/vibecode_spaces.html`, y mantener esta dependencia CDN
explícitamente separada de RD, Venue, Plano/Rider, Sala3D y XIO.
