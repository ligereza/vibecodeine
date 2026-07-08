# LAST_HANDOFF - flujo (formato YAML, ASCII-only)
# Lo continua Claude (director) para cerrar pendientes y arrancar el flujo.

handoff:
  date: 2026-07-08
  version: 0.48.5            # debe coincidir con pyproject.toml / src/flujo/version.py
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

  done_this_session:
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
      - "Aider descartado: es local; el norte es Actions"

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
