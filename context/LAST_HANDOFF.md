# LAST HANDOFF -- estado para el proximo agente

Version: 0.51.0 | Fecha: 2026-07-12 | Identidad: Cauce | Suite: verde (cuando se
construyo; NO re-corrida al cerrar) | flujo verify: no re-corrido esta sesion

El plan largo vive en context/PLAN_SIGUIENTE_AGENTE.md. Este es el estado corto.
Historico viejo en git y docs/handoffs/archive/.

## Hecho (esta sesion, 2026-07-12 -- VOLA + portfolio)

PORTFOLIO-AUTO (repo aparte ligereza/portfolio-auto, LIVE, ya pusheado a su main
30be342 -- NO es el repo flujo):
- VOLA publicada: pieza nueva "lo visible y lo invisible" (vaso + vacio bajo la
  triada). Assets vola-vaso.svg + vola-void.svg en assets/works/, entrada en
  data/works.json. (VOLA lleva tilde aguda a proposito; el archivo va ASCII.)
- FIX del vaso: vola-vaso.svg estaba casi en blanco (opacidades 0.03-0.10, "umbral
  de percepcion"). Reconstruido con el campo de glifos legible de
  arte-ascii-readme.svg (original SOLO leido, no tocado) + animacion de "digestion"
  en overlay con mix-blend-mode:screen (solo aclara, no puede borrar). Legible ya,
  verificado por render headless-Edge contra doublecup.png. Commit 2b35a5b.
- 2 VISUALIZADORES INTERACTIVOS restaurados (auto-hosteados desde artifacts, ya no
  como artifact republicado -- esto CIERRA el viejo pendiente "republicar af6411d3"):
  - sala-3d.html  <- artifact af6411d3 (Three.js WebGL + CSS3D, galeria 3D real).
  - tapiz.html    <- artifact e414adac (TAPIZ system projection / psicosis-fungi).
  Tecnica: WebFetch de la URL del artifact GUARDA EL HTML CRUDO COMPLETO EN DISCO
  (header "full HTML saved to ...tool-results\\artifact-<id>-*.html"); se le quita
  el bloque <!-- frame-runtime --> ... <!-- /frame-runtime --> (wrapper iframe de
  claude.ai) con script, y queda pagina self-contained. js/app.js: el caso unico
  3d-immersion se generalizo a un mapa INTERACTIVE_PAGES (sala-3d, tapiz). Commit
  30be342. (Ver memoria reference_selfhost_artifact.md.)

FLUJO (este repo, TODO SIN COMMITEAR en main @1dd8342 -- el usuario dijo "olvida
github" para flujo; queda en disco, decidir despues si se versiona):
- Deuda tecnica P2: quitado stub mentiroso /api/materials/<id>/download en
  src/flujo/serve/server.py y linea de ayuda stale "brand analyze" en cli.py.
- projects/cultura/ 4 piezas-triada motor-omega (una por semilla viva), con .md
  (Omega11 escrita) y test cada una, suite verde al construir:
  fila_cero.py (+7 tests), tilde_paridad.py (+5), mecanismo_residuo.py (+6),
  marca_sin_precio.py (+8). Mapa: SUPER_PLAN_TRIADA.md. PENDIENTE humano: cada
  Omega11 espera su regularizador real (lector no-autor + plazo) para EXPONERSE y
  registrarse fechada; NADA entra a puente/SEMILLAS.md hasta eso (no se toco).
- projects/tapiz/ piezas VOLA: vaso_animado.svg/.py (+VASO_ANIMADO.md),
  vibecode/void_shapes.py + void modes en spaces.py/svg_export.py (aditivo, +11
  tests en test_tapiz_vibecode.py), void_animado.svg, VOLA.md (concepto),
  TILDE_DEL_HIGH.md (analisis cultural: el signo de la sustancia cruza, el estado
  "high" no; el LLM es Mary que nunca sale del cuarto). No reemplaza nada original.
- doublecup.png en la raiz: screenshot de referencia del README real (vaso legible).
  Untracked; borrable, no versionar si estorba.

## Doing / Next

- RESUELTO (portfolio "no puedo abrirlos" = salia una IMAGEN donde deberia estar
  el artefacto). ERA bug de codigo, NO cache (me equivoque antes diciendo cache).
  Causa real: los works interactivos (sala-3d, tapiz) llevan cover PNG + mediaType
  image, y varias rutas de render mostraban ESA imagen en vez de abrir la pagina
  viva: openLB (lightbox del home-else y del 2d masonry) y obra.js (obra.html?id=X,
  pagina de detalle) renderizaban <img> cover. Solo buildCard del home enrutaba
  bien. Fix (commit e4e43a5, pusheado): guard en openLB (si w.template esta en
  INTERACTIVE_PAGES -> location.href a la pagina) + INTERACTIVE_PAGES + redirect en
  obra.js. Ahora TODA ruta abre sala-3d.html / tapiz.html. NO pude click-test en
  navegador real (Chrome no instala sin admin, Playwright abortado); verifique
  rutas de codigo (deterministas) + paginas 200 + render headless. Limpieza menor
  pendiente: sala-3d/tapiz tienen mediaType "image" y se cuelan en la grilla 2d
  (el click igual abre la pagina por el guard; ideal quitar mediaType o filtrarlos).
- CUP: vola-vaso.svg estaba ESTIRADO (comprimido horizontal) ademas de casi-blanco.
  Reconstruido en scratchpad/build_vola_vaso.py DESDE la geometria real de
  arte-ascii-readme.svg (bloque unico <text white-space:pre 10px/12px, .b fondo /
  .g vidrio / .l liquido; la MISMA que produce doublecup.png), size explicito
  676x904, link <a> del repo desenvuelto, "digestion" como filter:brightness (no
  mueve glifos, no puede re-distorsionar). Proporcional y legible, verificado por
  render headless-Edge claro y oscuro. Original arte-ascii-readme.svg NO tocado.
  En commit e4e43a5.
- NO click-testeado en vivo: la sala 3D interior post-ENTRAR (WebGL, headless sin
  GPU). El agente reporto canvas three.js r149 init sin errores. Si post-ENTRAR
  sale negro, debuggear ahi.
- Decidir si el trabajo flujo sin commitear (arriba) se versiona o queda local.
- Carryover previo: PR #41 (tilde_residuo.py) -- confirmar si sigue abierto y
  decidir merge. branch protection en main + secret ANTHROPIC_API_KEY siguen sin
  configurar (ver SESSION_STATE.next).

## Blockers
- (+)2 (OBRA_02) bloqueada esperando lector humano.
- Cada Omega11 de projects/cultura/ espera regularizador humano (lector no-autor +
  plazo) antes de exponerse/registrarse.
- build_chataigne_noisette_experimental: falta .noisette real (NO re-adivinar).
- #2 duelo de modelos: Gemini PARKED, falta un 2do modelo util.

## Reglas vivas (no negociar)
- NO activar Claude via API en Actions (decision usuario 2026-07-12).
- El airdrop QUEDA COMO ESTA. puente/ es teorico (puente/README.md): no ejecutar,
  no limpiar, no reinterpretar lo fechado. NO tocar puente/SEMILLAS.md.
- README.md del repo y arte-ascii-readme.svg: obra terminada, no agregar/reemplazar.
- context/AVANCES_BLOCK.txt NO es doc muerto (input de tools/tapiz_telemetry.py).
- Cultura: descriptivo, nada generativo-de-sintesis; psicosis jamas perfila
  personas reales; precursor solo cultura/ley/estetica; NADA operativo de sustancias
  (dosis/sintesis/adquisicion).
- Ordenes destructivas de git van al hilo principal, no a subagentes.
- Nunca versionar secretos (.env, config.json, *.key). CLAUDE.md y este archivo:
  ASCII-only. portfolio-auto es PROJECT subpath: rutas RELATIVAS siempre (nunca
  /assets), o dan 404.

## Verificacion (antes de cerrar, si tocas flujo Python)
- py -m compileall src/flujo
- py -m pytest tests/ -q
- py -m flujo verify
- (si tocas web) cd web && npm run typecheck && npm run build:context

## Entrada
1. Este archivo. 2. context/PLAN_SIGUIENTE_AGENTE.md. 3. CLAUDE.md.
