# AIRDROP: plan externo TAPIZ para agentes Arena (LMArena)

Fecha: 2026-07-10. Origen: sesion Cauce (Claude), PR #26 `worktree-tapiz-ecosystem`.
Este documento es AUTOCONTENIDO: pegalo completo en el chat de Arena junto con
la orden de trabajo (WO) elegida. El agente Arena NO tiene acceso al repo ni
puede ejecutar codigo: todo lo que necesita esta aca adentro.

## Contexto capsula (3 lineas)

Ecosistema artistico **Tapiz <-> Psicosis <-> Fungi**: telemetria de ingenieria
renderizada como arte. Un pipeline Python (`compete_engine.py`) compila
`system_status.json`; renderers independientes lo vuelven visual. Ya existe un
renderer 2D canvas (`tapiz_renderer.html`); las WO de abajo crean derivados.

## Reglas para el agente Arena (leer antes de trabajar)

1. Entrega UN archivo COMPLETO por respuesta, en un solo bloque de codigo.
   Prohibido: `TODO`, `...`, "completar luego", pseudocodigo, fragmentos.
2. NO inventes campos del JSON: usa SOLO el contrato de abajo. Si algo falta,
   escribi `ASSUMPTION:` al inicio de la respuesta y segui con lo asumido.
3. Vanilla JS (ES2020). Sin build tools, sin npm, sin frameworks salvo lo que
   la WO permita explicitamente. Un HTML debe abrir con doble click.
4. Todo texto visible ASCII o UTF-8 declarado (`<meta charset="utf-8">`).
5. Maneja SIEMPRE: JSON ausente (mostrar file-picker), seccion faltante
   (defaults), payload que no decodifica (mostrar `[decode failure]`, no crash).
6. `prefers-reduced-motion: reduce` => sin animaciones.
7. No pidas el repo ni mas archivos: si la WO no lo incluye, no lo necesitas.

## Contrato del JSON (fuente: tools/system_map.py, API_CONTRACT_SCHEMA)

`system_status.json` tiene exactamente 5 secciones:

```txt
meta: { ecosystem_version:str, compilation_timestamp:float,
        integrity_sigil:str(SHA-256 hex), embedding_target:str }
luminous_mesh_densities: { global_pressure:float 0..1,
        css_variables: { "--mesh-luminosity":float, "--mesh-density-throttle":float,
                         "--mesh-glitch-frequency":float },
        throttle_ratio:float, status:"STABLE"|"OVERLOADED" }
chromatic_frequency_masks: { max_risk_score:float 0..100, css_filter_string:str,
        mask_intensity:"CLEAR"|"CAUTION"|"CRITICAL", triggered_categories:[str] }
chronological_collision_buffers: { collision_count:int, css_keyframes_payload:str,
        animation_class:str, status:"SYNCHRONIZED"|"TEMPORAL_DEGRADED",
        affected_assets:[str] (solo si degradado) }
encoded_asset_payloads: { total_payloads:int,
        payloads: { "<asset_id>": { name:str, intent:str, data_chunks:[str],
                    chunk_count:int, decode_shift_key:int } },
        embedding_target:str, encoding_protocol:"Base64_Shift42_Chunked" }
```

Decodificacion de payloads (JS de referencia, YA CORREGIDO, usar tal cual):

```js
function decodeChunk(chunks, shiftKey = 42) {
    const combined = chunks.join('');
    const shiftedBytes = Uint8Array.from(atob(combined), c => c.charCodeAt(0));
    let b64 = '';
    for (const b of shiftedBytes) b64 += String.fromCharCode((b - shiftKey + 256) % 256);
    const utf8 = Uint8Array.from(atob(b64), c => c.charCodeAt(0));
    return new TextDecoder('utf-8').decode(utf8);
}
```

Muestra minima valida (para probar sin el archivo real; `data_chunks` decodifica a `hola tapiz`):

```json
{"meta":{"ecosystem_version":"1.0.0","compilation_timestamp":0.0,
 "integrity_sigil":"abc123","embedding_target":"</main>"},
 "luminous_mesh_densities":{"global_pressure":0.16,
  "css_variables":{"--mesh-luminosity":0.84,"--mesh-density-throttle":0.97,
   "--mesh-glitch-frequency":0.8},"throttle_ratio":0.97,"status":"STABLE"},
 "chromatic_frequency_masks":{"max_risk_score":13.5,"css_filter_string":"none",
  "mask_intensity":"CLEAR","triggered_categories":[]},
 "chronological_collision_buffers":{"collision_count":0,"css_keyframes_payload":"",
  "animation_class":"","status":"SYNCHRONIZED"},
 "encoded_asset_payloads":{"total_payloads":1,"payloads":{"ART-001":{
  "name":"Psicosis","intent":"demo","data_chunks":["i3FjnYN9bFqDgmyaj5FnZw=="],
  "chunk_count":1,"decode_shift_key":42}},"embedding_target":"</main>",
  "encoding_protocol":"Base64_Shift42_Chunked"}}
```

Mapa semantico (que significa cada seccion visualmente):

| Seccion | Metafora | Directiva |
|---|---|---|
| luminous_mesh | grilla bioluminiscente se apaga/ralea bajo presion de tokens | opacidad y densidad de la grilla = f(pressure, throttle) |
| chromatic_masks | velo que censura: mas riesgo, mas distorsion | aplicar distorsion global (filtro/fog/shader) segun max_risk_score |
| chronological | desgarros temporales por conflictos de estado | sacudidas/glitch proporcionales a collision_count |
| encoded_payloads | esporas: cuerpos enterrados, se exhuman con click | objetos clickeables -> decode -> mostrar contenido |
| sigil | sello de integridad de la compilacion | mostrar en HUD; si cambia, re-renderizar |

## WO-1: Tapiz 3D (Three.js) — PRIORIDAD

Crear `tapiz_three.html`: escena Three.js que renderiza el mismo contrato en 3D.

- Three.js r160+ via CDN import map (unico framework permitido):
  `<script type="importmap">{"imports":{"three":"https://unpkg.com/three@0.160.0/build/three.module.js"}}</script>`
- Carga del JSON: `<input type="file">` SIEMPRE visible al inicio (file:// no
  puede fetch); si `fetch('dist/system_status.json')` funciona, usarlo y
  ocultar el picker.
- Mapeo 3D: grilla de puntos/instancias (mesh luminoso) cuya emision y densidad
  siguen pressure/throttle; fog o postprocesado simple segun mask_intensity
  (nada de EffectComposer: usar fog + color de escena, mantenerlo simple);
  camera shake sutil proporcional a collision_count; esporas = esferas
  clickeables (raycaster) que abren un overlay HTML con el contenido
  decodificado; sigil como texto HUD (elemento DOM, no TextGeometry).
- Paleta: fondo #030507, verde bioluminiscente #b7ffd9 / #3f6b54, alarma #ff5577.
- Checklist de aceptacion (el agente la repite completada al final):
  [ ] abre con doble click sin consola roja
  [ ] muestra file-picker y carga la muestra minima de arriba
  [ ] esfera ART-001 clickeable muestra "hola tapiz"
  [ ] pressure alto (editar JSON a 1.0) apaga visiblemente la grilla
  [ ] reduced-motion respetado

## WO-2: spec de mapping Resolume/VJ (solo texto)

Escribir `TAPIZ_RESOLUME_SPEC.md`: como traducir cada campo del contrato a
parametros de Resolume Arena via OSC (direcciones `/composition/layers/N/...`),
capa por capa: mesh -> opacity/scale de una capa generativa; mask -> efectos
(blur/hue) con valores mapeados de max_risk_score 0..100 a 0..1; collisions ->
transform jitter; sigil -> texto. Formato: tabla campo->OSC->rango->curva.
Sin codigo, solo spec precisa que un operador VJ pueda implementar.

## WO-3 (opcional): pase estetico al renderer 2D

Si el usuario pega el contenido de `tapiz_renderer.html`, proponer mejoras
esteticas SIN romper: contrato intacto, IDs de elementos intactos, decodeChunk
intacto, reduced-motion intacto. Entregar archivo completo modificado.

## Gate local (lo corre el usuario, no el agente)

```bash
# validar cualquier JSON que el flujo produzca:
py tools/system_map.py validate tools/dist/system_status.json   # PASS x5 o falla
# tests del engine:
py -m pytest tests/test_compete_engine.py -q
# probar la pieza de Arena: guardar el HTML en tools/, abrir con doble click,
# apuntar el picker a tools/dist/system_status.json (generar con --demo/--stress/--live)
```

Si el gate falla: pegar al agente Arena SOLO la linea de error exacta + la
seccion del archivo afectada; no re-pegar todo el documento.
