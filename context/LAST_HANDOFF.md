# LAST_HANDOFF - flujo (formato YAML, ASCII-only)
# Lo continua Claude (director) para cerrar pendientes y arrancar el flujo.

handoff:
  date: 2026-07-09
  version: 0.49.0            # debe coincidir con pyproject.toml / src/flujo/version.py
  assistant: Cauce
  repo: https://github.com/ligereza/vibecodeine
  to: Claude (director)

  role:
    you_are: director del equipo multi-agente
    team:
      gemini: interprete + voz + busqueda en vivo + lector pesado (tools/vibo_voz)
      arena: frontier gratis on-demand para arquitectura dura (sin API, airdrop chico)
      qwen: coder bruto de volumen; su salida pasa por el gate, no por ti
      claude_code: tus manos propias, solo para codigo critico
    rules:
      - no debuggees a Qwen; el gate es CI + revisor gratis (Gemini/Arena)
      - recibes pedidos ya comprimidos por el interprete, en YAML liviano
      - gastas cuota en dirigir + codigo critico, no en volumen
    canonical: ["CLAUDE.md (bloque 'Equipo multi-agente')"]

  done_this_session:   # sesion 2026-07-09 (seccion tools del hub: bugs + prioridad editables)
    - "rama claude/tools-section-improvements-2rhxhc: mejora de la seccion de herramientas del hub web. Pedido: fix bugs + priorizar las funciones editables dentro de la app."
    - "AppShell.tsx: nav del sidebar agrupado en 'Edicion' (herramientas que producen trabajo EN la app, con badge edit) y 'Consulta / referencia'. Orden RD: Plano/Rider, SVG Studio, Cotizacion, Intake (editables) -> Jobs (lectura). Orden Studio: SVG Studio, Mapping LED (editables) -> Eventos/IG, Resolume, Comandos (generadores de comando copy/paste, no ejecutan nada)."
    - "HubDashboard.tsx: tarjetas de acciones rapidas reordenadas editables-primero con badge 'editable'; descripciones de Eventos/Resolume sinceradas ('arma el comando', no ejecuta pipeline)."
    - "CommandCopy.tsx NUEVO compartido: el boton copiar estaba DUPLICADO identico en CommandPanel/EventsPanel/ResolumePanel y con bug real: mostraba 'copiado' aunque navigator.clipboard fallara (file:// o http de red local no tienen clipboard API). Ahora fallback a textarea+execCommand y estado failed visible (X roja)."
    - "EventsPanel.tsx: eliminado setTimeout(300ms) que FINGIA una llamada al backend con spinner; el comando se arma al instante (es concatenacion local, no fetch)."
    - "ResolumePanel.tsx: FPS y Puerto OSC solo aceptan digitos (antes texto libre -> comandos invalidos tipo --fps abc); fullCmd omite flags vacios."
    - "MappingTool.tsx: iframe /mapping.html (ruta absoluta) -> mapping.html relativa; la absoluta rompia el fallback file:// de context/flujo_hub.html."
    - "QuotePanel.tsx: logo de la cotizacion imprimible era <img> remota a reduciendodano.cl (sin internet el PDF salia sin logo); ahora RD_LOGO.white inline de rdBrand.ts."
    - "PlanoTool.tsx 3 fixes: (1) makeSymbolElement no asignaba category -> los simbolos agregados via checklist o boton + no aparecian en la leyenda agrupada (filtra por el.category); (2) loadFromBackend usaba ||300 que pisaba coordenada 0 legitima -> numOr con Number.isFinite; (3) snap de arrastre usaba literal 20 en vez de la constante GRID (2 sitios)."
    - "SvgVisualizer.tsx: exportPng revoca el blob URL tambien en onerror (antes quedaba filtrado si el SVG no cargaba)."
    - "JobsPanel.tsx: load() con .catch (antes promesa rechazada sin manejar si flujoApi lanzara)."
    - "Verificado: npm run typecheck OK, npm run build:context OK, smoke test Chromium headless (playwright-core + /opt/pw-browsers/chromium) sobre context/flujo_hub.html: nav agrupado correcto en RD y Studio, comando de eventos instantaneo, input FPS filtra letras (ab30x -> 30), 0 errores de consola. Screenshots en scratchpad de la sesion."
    - "Metodo (regla del runway): lectura pesada de los paneles delegada a Gemini API (REST directo, el SDK google-genai esta roto en el contenedor por cryptography) + subagente Sonnet para clasificar paneles chicos; Claude solo verifico los hallazgos en el codigo real antes de editar (2 de los bugs reportados por Gemini eran especulativos y se descartaron)."

  done_sesion_packs:   # sesion 2026-07-09 (PlanoTool: modelo de PACKS RD)
    - "rama claude/refine-local-plan-adgdga: se mergeo origin/fix/unfinished-tools-4 (9 commits que quedaron sueltos DESPUES del merge de PR #13 a main -- @96efa2e; nadie los habia mergeado). Trajo lo real: web/src/rdBrand.ts (paleta/logo RD dark-white), PlanoTool con tema+logo+cotizacion, scripts/export_propuesta_pdf.py, src/flujo/plano/{costs,engine,iconos}.py. Merge limpio, 0 conflictos reales."
    - "web/src/rdBrand.ts: PRESET_PARAMS/PRECIOS/calcCostos (costos calculados) -> PACKS (precio plano): Pack1 Testeo-o-Informativo 100.000/2vol, Pack2 Testeo-y-Informativo 300.000/6vol, Pack3 Completo 500.000/15vol. Cada pack trae m2/stands/inclusiones; COMPLETO ademas trae proporciones 60/14/10/9/7 (solo %, sin monto guardado). RD_PALETTE y RD_LOGO sin tocar (ya estaban bien)."
    - "Correccion de precios (2 vueltas): el primer valor puesto (INFO 100k/6vol, TESTEO 250k/6vol) salio de una instruccion de handoff anterior mal leida. Se investigo datadrops/cotizacion_general_eventos/ (250k/300k/500k) pero el usuario confirmo que es una oferta DISTINTA (cotizacion generica de agencia), no la fuente de los PACKS. Los valores reales los dio el usuario directo en el chat: 100k/2vol (testeo O informativo, a eleccion), 300k/6vol (testeo Y informativo, ambos), 500k/15vol (completo, sin cambio)."
    - "web/src/rdBrand.ts: porVoluntario y proporciones[].monto dejaron de guardarse como numero aparte (podian desincronizarse del precio, como paso en esta sesion). Ahora son funciones puras porVoluntario(pack)=precio/voluntarios y proporcionMonto(pack,prop)=precio*pct/100; PACKS solo guarda precio (unico valor absoluto editable) y pct (proporcion)."
    - "PlanoTool.tsx: buildElements(packId) redibuja por pack sin solapes (bug real: la 4a columna de COMPLETO invadia la leyenda tecnica default -- Coordinacion Operativa paso a apilarse bajo Mesa 3 en vez de 4a columna). PLANO_FRAME.h 1800->1950 (corrige margen inferior muerto). legendPos default + clamp de arrastre en pantalla (antes solo el print tenia clamp)."
    - "Elimina bloque JSX de impresion duplicado (viewBox 2970x2400, logo remoto <img>, sin tema) que no usaba el boton Imprimir Rider; printRider()/buildPrintableMapSvg quedan como unica fuente del PDF."
    - "Rider seccion de Cotizacion: de tabla comparativa de 3 presets a SOLO el pack elegido (precio/voluntarios/m2-stands/inclusiones, + tabla de proporciones si es COMPLETO). Paso de ser la seccion 5 a la seccion 4 al eliminar 'Detalle y Resumen' (ver abajo)."
    - "Ronda de pulido de impresion (feedback iterativo del usuario sobre los PDFs): (1) margen del PDF -- @page margin quedaba fuera del area pintable, mostrando papel blanco alrededor sin importar el tema; se paso a @page{margin:0} + padding en .page con background del tema (el margen impreso ahora es del color del tema). (2) seccion 'Detalle y Resumen de Elementos' (coordenadas X/Y y px de canvas interno, sin valor para el cliente) ELIMINADA por pedido explicito. (3) composicion: header fijo arriba + resto del contenido centrado en el espacio restante (.page-body) en las 3 paginas, en vez de todo apilado arriba con hueco muerto abajo. (4) titulos/logo(84px)/leyenda tecnica mas grandes; logo en las 3 paginas (antes solo pagina 1). (5) iconos del plano reorganizados por categoria (Servicios/Infraestructura/Coordinacion/Espacio/Zonas de Atencion -- mismas 4 categorias del checklist) en vez de una tira plana sin agrupar; fix real de bug encontrado en el camino: la leyenda tecnica mas ancha colisionaba con los stands y con Coordinacion Operativa, se reposicionaron ambos."
    - "Verificado en Chromium headless (playwright, /opt/pw-browsers): los 3 packs renderizan sin overlap, tema dark/white intercambia el logo RD correcto (negro.svg=texto blanco para fondo oscuro, blanco.svg=texto negro para fondo claro), PDF impreso con logo+cotizacion+margenes correctos. Screenshots en session scratchpad."
    - "Version 0.48.5 -> 0.49.0 (pyproject.toml, src/flujo/version.py + changelog, web/package.json); badges de version sincronizados en PlanoTool/AppShell/HubDashboard/flujoApi fallback."
    - "Deuda anotada (no se toco, fuera de alcance pedido por el usuario): src/flujo/plano/{engine,costs}.py y scripts/export_propuesta_pdf.py siguen en el modelo de presets under/base/mainstream; loadFromBackend() mapea INFO/TESTEO/COMPLETO -> under/base/mainstream solo para esa llamada demo."
    - "rama fix/unfinished-tools-4 pusheada (3 commits: eca7a28, cfe2654, fce7da6); PR pendiente: https://github.com/ligereza/vibecodeine/pull/new/fix/unfinished-tools-4"
    - "4 herramientas inconclusas terminadas: gota_rd (ENDPOINT configurable + fetch real), adobe_panel (REPO_TOOLS dinamico + config.json), ai_illustrator_bridge (MODE via config/dialogo, JSON.parse ES3-safe), logo_clean_master (backup automatico pre-destructivo). Codigo de Qwen web cherry-pickeado; revision via Gemini API."
    - "leccion Qwen: su rama tenia 81 archivos (borraba 10 skills activas, reescribia vibo.py). Solo se tomaron los 4 archivos de la tarea; la rama remota se borro. Regla nueva: scope-check del diff (git diff --stat vs lista permitida) ANTES de revisar contenido."
    - "tools/vibo_voz/pedir_codigo.py NUEVO: canal de escritura directo a API. Gemini primario (probado end-to-end en tareas reales); --proveedor nvidia (NIM saturado free tier, solo off-peak) y --proveedor github (GitHub Models deepseek-v3-0324, 8k in/4k out, solo tareas chicas). Scope-lock a archivos pasados, scrub de secretos, backup .bak."
    - "Aider + OpenRouter DESCARTADOS definitivo: aider desinstalado (bugs Windows: UnicodeEncodeError cp1252, browser spam en crash) y OpenRouter free tier 429 constante. pedir_codigo.py los reemplaza con menos piezas."
    - "pipeline flyer convergido: src/flujo/eventos/flyer_auto.py ahora espera activa al flyer_final.jpg del Droplet (mtime, 300s) y renderiza textura sobre RD.blend via src/flujo/eventos/blender_render.py (bpy headless, NUEVO); fallback cartelera.blend. tools/flyer_eventos/local/ eliminado (duplicaba flyer_auto). SPEC.md: checkbox Blender cerrado."
    - "fuera del repo: C:/rd/AUTOMATIZACION/actualizar.py arreglado (syntax error preexistente) + blender_render.py; queda como legacy de referencia, la version canonica es flujo eventos flyer-auto."

  done_sesion_anterior:
    - "cambio de modelo de sesion a Sonnet 5 (guardado como default)"
    - "commit c7500da: archivar docs obsoletos (paso 2 de restructure_optima) - .agent.md y docs/{AGENT_GUIDE,AGENT_OPERATING_MANUAL,DEMO_JEFE_2026-06-29,FASE5_CALIDAD,RELEASE_v016}.md movidos a _archive/legacy_20260708_0450/ (git mv, historial preservado; se archivan, no se borran, por regla de AGENTS.md)"
    - "CLAUDE.md: nueva seccion 'Mision (por que existe esta etapa)' explicando el norte ANTES/DESPUES de Claude en el repo"
    - "nota: estos cambios (archivado + seccion Mision) ya estaban hechos sin commitear al abrir esta sesion, de origen incierto (no de una conversacion registrada); se confirmo con el usuario y se commitearon como cierre"
    - "instalado caveman (JuliusBrussee/caveman) en .claude/skills/: 7 skills de compresion de tokens. Limpieza de duplicados (el instalador escribio 4 copias por falso-positivo en carpetas agent/ y data/ propias de flujo); solo queda .claude/skills/caveman* (copias reales, no symlinks). caveman-compress (sobrescribe .md via LLM) marcado High Risk por Snyk del instalador -- revisado el codigo: tiene denylist de nombres sensibles + backup fuera de repo + verificacion antes de sobrescribir; riesgo real bajo pero no usarlo sobre CLAUDE.md/LAST_HANDOFF.md sin revisar el diff (puede limar matices de las reglas)."
    - "restructure_optima paso 2 completo: AGENTS.md + docs/AI_OPERATING_LAYER.md + docs/AI_PROVIDER_ROUTING.md + docs/REPO_MAP.md fusionados en CLAUDE.md unico. AGENTS.md queda stub. Los 3 docs archivados en _archive/legacy_20260708_0450/. Referencias actualizadas en README.md, context/README.md, projects/README.md, docs/{CLI,TASK_PROMPTS,HIGIENE_REPO,AIDER_API_SETUP,AIRDROP,agents/PARA_IA_CONTEXT}.md, .claude/agents/.agent.md, .claude/skills/entregas-rd/SKILL.md, tools/vibo_voz/README.md."
    - "revision de GitHub: .github/workflows/claude.yml ya existia y esta activo (nadie lo tenia que crear). 5 PRs cerradas (10,11 mergeadas; 7,8,9 cerradas sin merge, ramas abandonadas con diffs masivos vs main, superadas). 6 issues abiertas (pedidos de producto suplementos/eventos), ninguna menciona @claude. Se encontro la rama claude/status-pending-items-51t92w (2 commits de contraportadas, trabajo del usuario en sesion aparte, sin PR) y se mergeo a main --no-ff con conflictos reales resueltos: gen_contraportadas.py + los 8 SVG de 09_contraportadas_dark/ tomados de la rama (--theirs, es el trabajo bueno); LAST_HANDOFF.md + SESSION_STATE.json tomados de esta sesion (--ours) y fusionados a mano."

  next:
    arrancar_flujo_github_actions:   # norte: que el repo funcione sin computador
      claude_hizo:
        - "[HECHO] .github/workflows/claude.yml ya existe y esta activo (creado 2026-07-04, anthropics/claude-code-action@v1). Dispara con @claude en issues/comentarios/PR review comments de OWNER/MEMBER/COLLABORATOR."
      usuario_hace:                  # manual, Claude no puede confirmar desde aqui
        - "confirmar que la GitHub App esta instalada y el secret ANTHROPIC_API_KEY existe (el workflow lo asume; no verificado desde este agente)"
        - "branch protection en main: require PR + require CI + require 1 review (correa de Qwen) -- pendiente de confirmar"
      test: abrir un issue con "@claude ..." y verificar que abre un PR
    pendientes_previos:
      - "[HECHO 2026-07-08] alineacion de las 8 contraportadas: el usuario lo trabajo en sesion aparte (rama claude/status-pending-items-51t92w, commits 28f903d + c347fb4 -- titulo a la izquierda en el ovalo sin kicker, texto calibrado a las cajas reales). Mergeado a main con --no-ff. Fuente ahora svg/suplementos_rd/_master_contraportadas.json (antes leia projects/piezas_vectoriales/.../contenido_suplementos_rd.json)."
      - "[DESCARTADO 2026-07-08] logo color vectorial: el usuario confirmo que es innecesario, no se hace."
      - probar bridges Photoshop/After Effects en apps reales [pospuesto]
      - "[DESCARTADO 2026-07-08] Aider: desinstalado (bugs Windows + free tier roulette); reemplazo pedir_codigo.py"
      - "[HECHO 2026-07-09] fix/unfinished-tools-4 (9 commits, incluye @96efa2e) mergeado a la rama claude/refine-local-plan-adgdga junto con el modelo de PACKS; llega a main cuando se mergee el PR de esta rama. La rama fix/unfinished-tools-4 remota queda obsoleta, se puede borrar despues del merge."
      - "abrir PR de claude/refine-local-plan-adgdga a main (packs RD + fix/unfinished-tools-4 recuperado)."
      - "deuda: src/flujo/plano/{engine,costs}.py y scripts/export_propuesta_pdf.py siguen en el modelo under/base/mainstream; no se alinearon al modelo de PACKS 100k/300k/500k (fuera de alcance, solo se pidio la app)."
      - "gota_rd backend [diferido]: decidir donde vive la data de reactivos antes de servir endpoint"
      - "tools/asistente_pedido y tools/canva_data: SPECs de una linea, pedir alcance antes de codear"
      - "test end-to-end Droplet+Blender en la maquina de render (repo compila, falta correr real)"

  blockers:
    - "cuota Claude: se resuelve sacando a Claude del chat -> Actions (ese es el flujo a arrancar)"
    - "build_chataigne_noisette_experimental: falta .noisette real; NO re-adivinar el schema (ya fallo 4 veces)"
    - "push directo a main lo bloquea el guardrail: usar PR o reintentar tras fetch; si falla, airdrop.zip"

  verify:
    local_windows:
      - py -m compileall src/flujo
      - py -m pytest tests/ -q
      - py -m flujo verify
      - cd web && npm run typecheck && npm run build:context
    ci_linux:
      - python -m compileall src/flujo
      - python -m pytest tests/ -q
      - python -m flujo verify

  hard_stops:
    - no reescribir src/flujo/resolume/automator.py sin .noisette real
    - no tocar src/flujo/airdrop.py sin --allow-airdrop-engine
    - nunca versionar secretos (.env, *.key, .aider.conf.yml)
    - LAST_HANDOFF.md y CLAUDE.md solo ASCII
    - cambios minimos - solo lo pedido, nada "de paso"

  on_close:
    - actualizar context/LAST_HANDOFF.md + context/SESSION_STATE.json (version/fecha reales, ASCII-only)
    - reporte formal de verificacion (formato en CLAUDE.md)

  critique_acida:   # vision critica sin filtro (pedida por el usuario)
    diagnostico:
      - "el repo documenta como trabajar mas de lo que trabaja: ~70 .md en docs/ y 4 entradas que se solapan (AGENTS, CLAUDE, .agent, README). El andamio pesa mas que el edificio."
      - "infra bespoke desproporcionada: vibo_voz (claude_bridge 24k, vibo 19k, personas CODE/VIBO/REDU que colapsaron a una), airdrop con validador+checks+backups, context_pack/token_budget/handoff. Todo para coordinar ayudantes IA de un repo que en el fondo hace flyers y shows."
      - "el airdrop es un sintoma, no una solucion: ingenieria para rodear que Arena no tiene API. Un workaround que se volvio pilar. Actions lo deja obsoleto y aun asi el repo carga todo el ceremonial."
      - "el thrash esta documentado como si fuera normal: automator.py reescrito 4 veces adivinando; SESSION_STATE quedo 6 versiones desfasado. La maquinaria de continuidad existe porque el sistema pierde estado; mas docs de continuidad tratan el sintoma, no la causa: demasiada entrada que leer -> los agentes la saltan."
      - "toda la arquitectura multi-agente nacio del miedo a gastar tokens de Claude, pero la cuota es buena; el gasto real era la MODALIDAD (chat). Mucha maquinaria resolvia un problema que Actions disuelve."
      - "dos mundos que no se tocan: el producto (src/flujo: CLI, suplementos, eventos, resolume, web) y el meta (vibo_voz, airdrop, docs, routing). El meta es elaborado; el producto avanza lento: contraportadas sin calibrar, logo color pendiente, .noisette bloqueado hace 4 versiones."
    veredicto: "es una maquina para administrar agentes que administran una maquina. La logistica de la fabrica esta sobre-optimizada mientras los productos quedan a medias en la linea."

  restructure_optima:   # camino logico y SUBTRACTIVO (menos, no mas)
    principio: "GitHub es el unico sustrato; todo lo demas se resta. El sistema optimo es mas chico, no mas grande."
    pasos:
      - "1. Matar el airdrop: Issue=tarea, PR=entrega, CI=verify, branch protection=gate. Borrar _airdrop, _airdrop_backups, validate_airdrop.py, run_airdrop_checks.py y sus docs. Cero ceremonia zip."
      - "2. [HECHO 2026-07-08] Una sola entrada: AGENTS.md + AI_OPERATING_LAYER + AI_PROVIDER_ROUTING + REPO_MAP fusionados en CLAUDE.md (secciones: Identidad, Mision, Equipo multi-agente, Entorno, Regla central, Como trabajar, Continuidad, Verificacion, Airdrop, Limpieza, Mapa del repo, Areas operativas, Entrega final). AGENTS.md quedo como stub de 4 lineas (compat con tools que buscan ese nombre por convencion). AI_OPERATING_LAYER/AI_PROVIDER_ROUTING/REPO_MAP archivados en _archive/legacy_20260708_0450/. Referencias cruzadas actualizadas en ~15 docs activos. Restan ~55 docs/ sin tocar (fuera de alcance de este paso; son referencia especifica de areas, no entrada)."
      - "3. El equipo, solo lo que tiene API: Gemini (interprete/voz/busqueda), Qwen (bulk), Claude (Actions: director+critico). Arena = consulta humana opcional, NO pilar automatizado. La voz (vibo_voz) es un front aparte; no enredarla con el pipeline de codigo."
      - "4. Dejar de optimizar tokens a mano: retirar spanish-optimizer y las capas de compress/escalate/offload en prosa. Claude-en-Actions + CLAUDE.md corto + CI es el 90% del ahorro con el 10% de la maquinaria. Conservar solo contexto_repo (0 tokens, util de verdad)."
      - "5. Congelar el borde del producto y terminarlo: contraportadas, logo color, packs de eventos = PRs por el pipe nuevo. .noisette: dejar de tocar automator.py (el repo ya lo dice 4 veces) -> conseguir el archivo real o BORRAR la funcion experimental. Decidir, no thrashear."
      - "6. Un loop probado punta a punta antes de agregar nada: meter UNA tarea real (ej: swap de logo color) por Issue -> @claude -> PR -> CI -> merge. Probar el pipe con el deliverable mas chico; despues todo es mas issues por el mismo tubo. No construir mas infra hasta que UNA cosa haya salido por el tubo nuevo."
    trade_off_honesto: "esto bota maquinaria que costo esfuerzo (airdrop, personas, docs): es costo hundido. Mantenerlo porque costo construirlo es la falacia del costo hundido; su impuesto continuo (mantencion, carga mental, sesiones perdidas releyendo) ya supera su valor ahora que existe Actions."
