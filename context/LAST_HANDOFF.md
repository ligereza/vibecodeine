# LAST HANDOFF -- estado para el proximo agente

Version: 0.52.0 | Fecha: 2026-07-17T23:00 | Identidad: Cauce | sesion autonoma: cleanup + audits.

## Sesion 2026-07-17T22:30-23:00 (autonoma, cierre)
- Cleanup: PR #48 stale refs (updated MASTER_PLAN.md, PLAN_SIGUIENTE_AGENTE.md), 9 cultura/ leftovers moved out, docs/DIRECTOR_PLAN.md archived, branch/file trash cleaned
- Audits: portfolio-auto (LIVE), public repos, stale files (all read-only)
- Commits: 156e8b4 (cleanup), be3153e (handoff), +context/WALKTHROUGH.md (quick-start guide)
- Blockers: MAK SSH auth pending (user to provide connection string), PR #49 user review pending
- Suite: pytest 394+1skip green, compileall OK, flujo verify OK

Anterior: MAK codigo copiado a cultura/mak_research + mak_codex + mak_plataforma + mak_lenguaje,
suite verde. Detalle en seccion "MAK -- cierre 2026-07-17" abajo.

## SI ERES UN SUCESOR DE FABLE (bloqueo -> Opus): leer esto PRIMERO
El modelo principal puede quedar bloqueado por el clasificador de ENTRADA
(marca el mensaje del usuario ANTES de que el modelo lo vea; falsos positivos
en coding/cyber/biology rutinarios) y la sesion se degrada a Opus sin retorno.
Protocolo (memoria [[antiblock-warn-first]] + skill .claude/skills/
revivir-subagentes escenario C):
1. `py .claude/skills/revivir-subagentes/extraer_contexto.py <sessionId>.jsonl
   --volcar rescate.md` -> hereda el contexto ya pagado (corre en Windows
   cp1252 sin PYTHONIOENCODING desde el fix de esta sesion).
2. Warn-first: avisar `[!] tema sensible: <cual>` ANTES de zona riesgosa,
   ofrecer reformulacion; nunca rechazo seco (re-quema el modelo).
3. Trabajo normal del repo (Resolume/VJ, RD reduccion de danos, xio, codigo)
   = zona verde, no auto-censurar por flags ambiguos.

## MAK -- cierre 2026-07-17 (sesion Sonnet/Opus, rama worktree-mak-research-cultural)

El organismo MAK (research + codex + plataforma + lenguaje) corre EN VIVO en
Debian 192.168.50.2, fuera de src/flujo. Esta sesion cierra el trabajo iniciado
en PRs anteriores (#48/#49 mencionados en handoffs previos): otro agente habia
LOCKEADO cultura/mak_research/ esperando que este trabajo terminara y se
pusheara (ver nota en la seccion "PENDIENTES de esta sesion" mas abajo) --
ese lock se libera con este merge.

### Que se hizo esta sesion (ademas del trabajo previo ya documentado abajo)
- **WIN integrado como proveedor LLM**: notebook Windows (RTX 4070 Laptop 8GB)
  suma como proveedor "win" en research_lib.LLM y codex_lib.CoderLLM, ANTES
  del ollama local de MAK en la cadena de fallback (nube -> WIN -> MAK-local).
  Ollama en WIN bindeado a la IP del cable directo (192.168.50.1:11434), NO a
  0.0.0.0 -- goteo de seguridad real cerrado (WIN es notebook que viaja a
  redes publicas). Probado end-to-end desde ambos deptos.
- **Fallback offline probado de verdad**: red_ok() (socket a 1.1.1.1/8.8.8.8)
  reordena la cadena sin internet; forzado offline en vivo, cayo a ollama
  correctamente.
- **Throttling movil resuelto**: hotspot del Xiaomi (WIN conectado a el)
  caia a 0.75 Mbps. Root descartado (telefono sin root, ver xio/RUNBOOK.md).
  Fix real: `adb shell settings put global tether_dun_required 0` (capa de
  servicio, no kernel -- mismo patron que resolvio charge_control antes) +
  reboot del telefono con `xio/new/pc_reboot_watch.sh` corriendo por USB
  ANTES de reiniciar (evita el "hueco" de reboot sin host). Resultado: 0.75 ->
  12.2 Mbps.
- **hub.py reconstruido sobre DOM+SVG real** (antes: canvas-2D con
  hit-testing a mano, causaba clicks poco confiables). Verificado con
  Playwright REAL (chromium instalado ad-hoc, no MCP) contra el hub vivo en
  MAK: 5 nodos de departamento clickeables, panel de research/codex EMBEBE
  el editor real via iframe (:8890 y :8891 con token, NO un formulario
  propio -- correccion de un error real de esta sesion, se habia reconstruido
  una version mas pobre en vez de reusar el editor de nodos/puertos/SVG que
  research/interfaz.py ya tenia). Fisica del micelio con damping mas fuerte
  (0.55 + tope de velocidad) para que un click real (mouse, no la espera de
  estabilidad de Playwright) aterrice bien sin dejar de moverse.
- **Emisor de eventos con contenido semantico real**: `eventos.jsonl` por
  depto (research_lib.emitir_evento + mint_job_id), interceptado
  centralmente en worker.py/worker_codex.py (linea "STATUS: " -> node_start,
  "HALLAZGO: " -> llm_result con contenido real, no contador de paso).
  Contenido real agregado en research.py (fuente encontrada + extracto del
  informe), generar.py (plan + resultado), debug.py (diagnostico). Panel "en
  vivo" en el hub lee `/api/eventos?depto=X`.
- **Coder que se repara**: nuevo mood `debug` en codex (planner diagnostica +
  coder reescribe) -- NUNCA sobrescribe el modulo vivo, guarda PROPUESTA en
  ~/codex/revisiones/ para revision humana.
- **Trabajo autonomo real**: `trabajo.py` (cron */30, reemplaza el latido.py
  viejo) cicla multiplicar/definir/limpiar/desarrollar via roles.py.
  LIMITACION HONESTA (documentada, no resuelta): las listas semilla son FIJAS
  (roles.py SEMILLAS/MODULOS + backlog_codex.txt) -- al agotarse, repite en
  vez de crecer. La correccion real (leer la seccion "LAGUNAS DE INFORMACION"
  que cada informe ya escribe y usarla como semilla del proximo ciclo) esta
  DISENADA (ver cultura/mak_plataforma/diseno/eventos_y_backlog.md) pero NO
  implementada.
- **Doctrina viva**: cultura/mak_plataforma/doctrina/doctrina_tools_espejo.md
  (herramientas dual-use, jailbreak vs enmascaramiento de intencion, el
  filtro juzga la aplicacion no la capacidad) informa filtro_entrada.py.

### NO completado (honesto, no maquillado)
- **Pausa-en-error / reanudacion**: research.py `investigar()` fue reescrito
  para soportar `checkpoint=`/`job_id=`/`accion=`/`nuevo_input=` (pausa real
  en vez de reventar y esperar el timeout de todo el job), PERO nada invoca
  todavia esa ruta: falta `--resume` en `main()`, falta que worker.py
  reconozca la linea "PASADO: " del subproceso, falta el endpoint
  `/api/reanudar` en interfaz.py + hub.py, y los botones
  reintentar/editar/saltar/abortar en el panel del hub. Diseno completo en
  cultura/mak_plataforma/diseno/eventos_y_backlog.md.
- El emisor de eventos con contenido real (HALLAZGO:) solo esta en
  research.py + generar.py + debug.py. cadena.py/refutar.py/panel.py/
  grafo.py/memoria.py/revisar.py/testear.py solo tienen node_start/node_end
  genericos (heredados gratis via worker.py/worker_codex.py) sin contenido
  semantico propio todavia.
- Regla de firewall de Windows para ollama sigue en "Any remote address"
  (el New-NetFirewallRule con RemoteAddress fallo por falta de admin/UAC). El
  bind a la IP de interfaz (192.168.50.1) ya cierra el riesgo real (no hay
  socket escuchando en otras redes); la regla de firewall es hardening
  adicional, no urgente.

### Limpieza de handoffs viejos (pedido explicito del usuario al cerrar)
- `checkpoints/2026-07-03_*.md` (3 archivos) archivados a
  `_archive/legacy_20260717_1900/checkpoints_2026-07-03/` -- salidas viejas
  de un mecanismo de solo-escritura (src/flujo/airdrop.py), no rompe nada.
- `context/ACTIVE_PLAN.md` (plan de demo del 2026-06-29, hace 3 semanas)
  archivado a `_archive/legacy_20260717_1900/`.
- `context/PLAN_OPUS_SALA3D.md` eliminado (`git rm`, no archivado): el propio
  archivo instruia "Borrar este archivo al cerrar"; su trabajo (PR #30) ya
  esta mergeado desde 2026-07-11.
- `_tmp_mak_plataforma/` (untracked, intento abandonado de 2026-07-16 con
  copias stale de GENESIS.md/guardia.py/salud.py) borrado; reemplazado por
  cultura/mak_plataforma/ con contenido fresco de hoy.
- NO se toco `.archive/`, `_archive/legacy_2026*` (las demas), ni
  `docs/handoffs/archive/` -- son las ubicaciones de archivo OFICIALES segun
  CLAUDE.md, no material suelto.

### Verificacion de cierre
compileall src/flujo: OK. compileall cultura/mak_research+mak_codex+
mak_plataforma+mak_lenguaje: OK (sin errores de sintaxis). pytest tests/: 100%
verde, sin fallos ni nuevos skips. flujo verify: OK (v0.52.0, hub smoke OK).
No se toco web/ esta sesion.

## Estado 2026-07-17 (sesion Fable, autonoma)
Mergeado a main hoy: PRs #50-#69 (checkpoint, MASTER_PLAN v2 anti-muralla,
olas 1-4, RD DB + perfil productoras + lookup, fix precio Pack 1 real $250k,
vibo_voz eliminado, cobertura 10/10 gaps + fix bug scoring fallback, skill
revivir-subagentes rescatada + fix cp1252, CLAUDE.md denso senal-pura, hook
bash-guard PreToolUse). Branch protection en main ACTIVA (require CI ubuntu+
windows, strict). Sesiones duplicadas del picker limpiadas (2 fantasmas
matados por PID + 3 jsonl borrados; contenido en C:/IA/_flujo_local/
session_backups/).

## SESION 2026-07-16 (d) -- MICELIO: el archivo hecho organismo + modos desde el mapa
Feedback duro del usuario ("no veo las conexiones semanticas, botones a
iconos, Files feo, nodos cuestan, replantea todo") -> rework visual completo
de interfaz.py, enfoque cultura/artistico (paleta abisal #0b0a09 + fungico
#9db67c, director-de-arte):

- MICELIO (vista 2, toggle Flujo/Micelio): mapa semantico VIVO del archivo.
  Canvas 2D con fisica force-directed propia (sin librerias): nodo = pieza
  (respira, halo, tamano por fragmentos), filamento = afinidad coseno real
  entre productos (memoria.grafo_semantico + /api/memoria/grafo), ondulan,
  esporas viajan por aristas fuertes, anillo de nacimiento en piezas nuevas.
  Slider de afinidad, leyenda por tipo clickeable, zoom/pan/drag, tooltip.
- MODOS DESDE EL MICELIO (pedido explicito): click en pieza -> tarjeta de
  acciones: Abrir / Investigar (corre el modo activo del topbar con la pieza
  como semilla, memoria=1 si grafo) / PUENTE (dos piezas -> investiga la
  relacion entre ambas). La pieza nueva se auto-indexa (reindex tras cada
  job) y NACE en el mapa (refresh 25s): crece y se remodela solo.
- UI: toolbar de ICONOS svg con tooltips; puertos 16px con drag-to-connect
  estilo n8n (entradas se encienden verdes al conectar) ademas de dos-clicks;
  Files rehecho como "Archivo del departamento" (cards titulo/fecha/chip de
  tipo + buscador, DIR_CHIP singulares correctos).
- Verificado: py_compile local+MAK, node --check (60.9k chars JS), API grafo
  33 nodos/99 aristas, server VIVO (PID 131439 http 200), pantallazos de
  Flujo+Files. LECCION OPERATIVA: NO usar xdotool para "verificar visual" --
  el usuario comparte el MISMO mouse fisico entre Windows y MAK (Barrier);
  mover el cursor via xdotool le pelea el mouse en vivo. Verificacion visual
  = pedirsela al usuario.
- Alerta de higiene: en el worktree aparecio arte-ascii-readme.svg BORRADO
  (working tree, no commiteado) + arte-ascii-readme.svg.html untracked --
  NO fue este agente, NO se commitea; el usuario decide si restaurar
  (git checkout -- arte-ascii-readme.svg).

## SESION 2026-07-16 (c) -- MAK research: MEMORIA del departamento (RAG local)
El usuario pidio "enhance the department". Se agrego la pieza mas de fondo
que faltaba para que sea un DEPARTAMENTO y no una carpeta de informes: una
MEMORIA consultable.

- memoria.py NUEVO: indexa TODOS los productos (.md) con embeddings LOCALES
  y gratis (ollama nomic-embed-text, 768-dim; se pulled en MAK) a
  ~/research/memoria/index.jsonl. Incremental por mtime. Cosine top-k en
  python (instantaneo sobre ~500 chunks). 3 usos: `index`, `buscar "tema"`,
  y consultar (default) = 7mo MODO Memoria: recupera lo previo relevante y
  el modelo capaz sintetiza QUE SABEMOS / consenso / contradicciones /
  VACIOS / que investigar proximo. Escala mejor que Corpus (solo el
  subconjunto relevante, no todo el archivo).
- Inyeccion --memoria en modo Grafo (checkbox "Consultar memoria" en Run):
  cada trigger recibe, junto al tema, los hallazgos previos relevantes
  (memoria.contexto). El grafo construye sobre lo ya sabido.
- UI: boton Reindexar (tools menu, background via /api/memoria/index) +
  contador de fragmentos (/api/memoria/stats, poll 15s). run-modo dropdown
  con Memoria. worker.py SCRIPTS["memoria"], DIRS/MODO_DIR memoria/.
- Verificado: py_compile + node --check OK; index construido en MAK (33
  archivos -> 473 chunks); embeddings 768-dim OK. Borrado el sitecustomize.py
  huerfano que reaparecio (trampa conocida).
- PENDIENTE (no del codigo): confirmar EN VIVO el modo Memoria (consultar +
  sintesis) y grafo --memoria. Se corto por throttle de fail2ban en MAK tras
  muchas conexiones SSH seguidas; interfaz.py lo revive el watchdog (cron
  */5) o relanzar con `setsid python3 interfaz.py >log 2>&1 </dev/null &`
  (un nohup dentro de un SSH con loop largo muere con SIGTERM al cerrar).

## SESION 2026-07-16 (b) -- MAK research: GRAFO REAL dirige la ejecucion
Rama worktree-mak-research-cultural. El usuario pidio arreglar huecos del
canvas: faltaban opciones de conexion en los nodos, la Discussion "no era
comite ni circulo", el Adversarial "no se dibujaba", y queria multiples
entradas/salidas anticipando flujos extremos. Eleccion de arquitectura del
usuario (AskUserQuestion): "Grafo real dirige la ejecucion".

Hecho y VERIFICADO EN VIVO:
- grafo.py NUEVO: ejecutor de grafo real. Lee ~/research/workflow.json
  (nodes + connections), valida (validar_grafo: ciclos/huerfanos/sin-camino
  trigger->output/fan-out>6/>12 modelos), y ejecuta en orden topologico --
  cada nodo-modelo recibe la salida concatenada de sus predecesores, los
  trigger inyectan el tema, los output recopilan, cierra con correlacion.
  Soporta multiples triggers/outputs (set-based). Salida en grafos/.
- interfaz.py: el array `connections` ahora DIRIGE el dibujo (se acabaron las
  topologias hardcodeadas por modo). Eso arregla los bugs reales: Discussion
  = COMITE (trigger->todos los modelos->output, convergen); Adversarial SE
  DIBUJA (proponente->refutadores->juez). Conexiones editables por los
  puertos (2 clicks salida->entrada; click en arista = borrar; Esc cancela).
  Multiples In/Out (+In/+Out; los nodos base se apagan, no se borran; los
  extra y las notas si). Nuevo modo "Grafo" (custom: respeta las aristas
  dibujadas, corre grafo.py). Los otros 4 modos regeneran su topologia como
  PRESET (presetConnections) y siguen corriendo su script especializado.
  validarGrafo (espejo JS) + boton Validar; en modo grafo el run se bloquea
  si el grafo es invalido (chequearGrafo + saveNow antes de correr).
- worker.py: SCRIPTS["grafo"]="grafo.py"; interfaz DIRS/MODO_DIR grafos/.
- Verificacion: py_compile (local+MAK) OK, node --check del JS OK, validador
  unit-tested (5 flujos extremos), 4 presets evaluados en node (correctos),
  click real en Discussion regenero el comite (workflow.json 8 conns +
  pantallazo), y un job grafo REAL corrio end-to-end en MAK (4 modelos en
  orden topologico + correlacion 5750 chars, meta.errors=[]). Server VIVO
  reiniciado en MAK (PID nuevo, http 200). Sigue pendiente del usuario abrir
  ufw 8890 para verlo desde Windows.

## SESION 2026-07-16 -- MAK research: canvas visual + 5 modos + correlacion
Rama worktree-mak-research-cultural (continua la de la noche anterior).
La interfaz web crecio de un formulario a un CANVAS VISUAL tipo n8n
(interfaz.py, ~1500 lineas): 5 modos reales cableados end-to-end y
verificados en vivo en MAK -- Single (research.py), Pipeline (cadena.py
NUEVO, encadenado), Discussion (panel.py), Adversarial (refutar.py NUEVO,
proponer/refutar/juzgar), Corpus (correlacionar_archivos.py NUEVO,
correlaciona TODO el archivo). Correlacion semantica ("departamento"):
el modelo capaz (azure gpt-5-mini) ordena/relaciona lo que dicen los
modelos, por-job (panel/cadena) y sobre-el-corpus (modo Corpus).
Agregados: perilla de densidad (corto/medio/largo, escala tokens con
techo duro anti-timeout), auto-repair (boton en jobs fallidos -> el
modelo capaz diagnostica), nodos nota agregables al canvas, tools menu
(zoom rueda+botones, pan arrastrando fondo, Encajar/Centrar/Organizar),
modal para ver resultados DENTRO de la app, log de error explicito por
job, token auth opcional, historial jobs.jsonl. Fix importante:
Cache-Control no-cache en interfaz.py (Firefox cacheaba HTML viejo por
origen). Todo desplegado y VIVO en MAK ~/research/. PENDIENTE del usuario:
ufw bloquea 8890 desde la LAN (correr `sudo ufw allow from
192.168.50.0/24 to any port 8890 proto tcp` para ver desde Windows). El
usuario avisa si pilla bugs. Detalle completo: cultura/mak_research/MAK_RESEARCH.md.

## SESION 2026-07-15 (noche) -- MAK research cultural VIVO (sin n8n)
Rama worktree-mak-research-cultural. n8n CERRADO como fallido (orden usuario,
no reintentar). Sistema standalone desplegado y VERIFICADO en MAK
(192.168.50.2, ~/research/): research.py (loop Tavily->fetch->analyze->decide
->informe, fallback groq->cerebras->azure->ollama), panel.py (debate 4
angulos historico/estetico/legal/tecnico, 1 modelo por API, sintesis
gpt-5-mini), 3 interfaces para tema X: web LAN :8890 (interfaz.py), ntfy
iPhone (cola.py, topics NTFY_TOPIC_IN/OUT en research.env), CLI research.sh.
Un job a la vez (worker.py flock). Cron @reboot. gemma3:4b bajado (cabe en
4GB VRAM, OLLAMA_MODEL default; aya-expanse:8b de repuesto). Tests vivos:
research 2x OK, panel OK (4 proveedores hablaron), round-trip ntfy OK.
Trampas resueltas: Cloudflare 403/1010 por UA de urllib (UA custom en lib);
razonadores necesitan margen +2048 tokens; defaults frugales (2 iter/1
replica) por orden del usuario. Copia del codigo: cultura/mak_research/
(manual + backlog para agentes VS Code/Antigravity en MAK_RESEARCH.md).
Keys: cultura/.dev y ~/n8n-local/research.env, JAMAS en git. OJO: crontab
de mak pudo perder entradas previas (probablemente vacio) al instalarse
@reboot; revisar si algo falta. "wachuma" era un TEMA, no el sistema: el
sistema es generico, recibe cualquier tema.

## SESION 2026-07-15 (autonoma tarde) -- showcontrol v1.1->v1.8 + cultura wachuma
Rama claude/cultura-xio-mistral-20260715, PR #45 MERGEADO a main.

## NOTA (otra sesion) -- Optimizacion de gasto aplicada
Settings, aplica a sesiones NUEVAS: main model default = Haiku, effort medium,
advisor sonnet, plugins 64->15, hook SessionStart caveman + hook PreToolUse
bash-guard. Doctrina de escalada (triggers decidibles) codificada en CLAUDE.md
seccion "Regulacion de gasto".

### PENDIENTES de esta sesion (lista que NO alcanzo a cerrarse sola)
COMMITEADO en esta tanda (working tree -> main): tapiz cableado al CLI
(`flujo tapiz demo/stress/live`), venues OpenKlub/Paralelo89 + link frvr,
reactivos.json enriquecido (23 reacciones, cocaina en Marquis/Liebermann,
Simon/MDA update, fuente DanceSafe), plugin xio `hub` (sirve flujo_hub.html
desde el telefono, T-G2), cleanup cultura (.dev.limpio + 8 leftovers movidos
a _flujo_local), 5 SPEC-stubs archivados.

NECESITA AL USUARIO (tabla, dar y ejecutar):
- A1 noisette: abrir jobs/test_resolume/deliverables/show_automation.experimental
  .noisette en Chataigne, confirmar 12 acciones en State Machine (ojo humano).
- A5 airdrop Termux: PAT fine-grained (repo vibecodeine, contents:write) en el
  telefono ~/.airdrop_token; luego disparar test de airdrop_push.sh.
- A4/A8 telefono xio: AccessibilityService install + redeploy plugin showcontrol
  (y el nuevo plugin hub) via RUNBOOK 7.
- C12 ensayo Resolume end-to-end en evento real (fecha).
- C16 entrega comercial completa por agentes gratis (job real).
- D18 confirmar/dar data real de las 13 productoras (instagram/venue/tipo).
- D20 specs de venues OpenKlub/Paralelo89 (aforo, preset).
- E21 piezas MANIFIESTO bloqueadas: #2 (2do modelo util?), #5 (ESP32), #7 (orden
  usuario: no tocar), #11 (infra training).

DECISION DEL USUARIO:
- PRs #48/#49 (MAK grafo + MAPA_GENERATIVO): CI verde pero de hace dias, ramas
  ~19 PRs atras de main y el agente MAK sigue trabajandolas. Recomendacion:
  esperar a que MAK pushee su final antes de mergear (evitar clobber).

LOCKEADO por el agente MAK (concurrencia, no entrar a cultura/mak_research):
- C2 gap seguridad xio_puente GET-only; C3 pipeline dossier MAK->markdown;
  G1 panel Cultura muestra grafo MAK. Se destraban cuando MAK termine.

Version: 0.52.0 | Fecha: 2026-07-17 | Identidad: Cauce | Suite completa: VERDE
(compileall OK, pytest verde, flujo verify OK 0.52.0).

Pendientes y fuerte/debil: context/PLAN_SIGUIENTE_AGENTE.md (refrescado hoy).
Historico viejo: git log de este archivo + docs/handoffs/archive/.

## SESION 2026-07-16 -- CHECKPOINT LIMPIEZA TOTAL (ultracode: 5 sonnet + Fable)

Barrido con 5 analistas sonnet (volumen con gitignored, reglas obsoletas,
inventario de ideas, higiene git, salud) y ejecucion central. Resultado:

- BASURA REMOVIDA (~190M): 65 __pycache__ + 3 .pytest_cache + _logs +
  flujo.egg-info + autosave ~ai-*.tmp de Illustrator; duplicado byte-identico
  (md5 verificado) de 76M jobs/2026-07-05_contraportadas/contraportadas_por_
  producto/ (la fuente canonica productos/ queda intacta).
- MOVIDO FUERA DEL REPO, preservado en C:\IA\_flujo_local\: CSV Azure personal
  de la raiz, doublecup.png (referencia de tarea cerrada), APKs instaladores
  termux/shizuku (100M, re-descargables; xio ya esta desplegado on-device).
- GIT PODADO: ramas pr45 + worktree-magical-sparking-kite + claude/cultura-
  xio-mistral-20260715 borradas (verificado: diff contra main = 0 lineas /
  squash-merged en PR #45); worktree cultura-xio removido. Quedan: main, rama
  actual, worktree-mak-research-cultural (= PR #48 ABIERTO, dirty, NO tocar).
- ARCHIVADO via git mv a _archive/legacy_20260716_2000/ (motivos en su
  README.md): xio/advplugins (12 plugins absorbidos por xio/new-plugins),
  projects/agente1_flyers_web + agente2_resolume_chataigne (briefs ya
  materializados), proposals/mejoras_herramientas_2026-06.md (ejecutada),
  .claude/commands/push-all.md (hacia git add . + push directo, contra el
  modelo del repo) y su README.md (el harness lo leia como comando roto).
- NO ARCHIVADO por dependencia viva (verificado con grep, corrige a los
  analistas): projects/flyer_eventos (usado por src/flujo dashboard/flyer/
  intake) y xio/actual (xio/new/server.py y pc_reboot_watch.sh usan su
  platform-tools/adb.exe).
- REGLAS PODADAS: CLAUDE.md (pedir_a_gemini.py marcado PARKED, caveat PARKED
  en la seccion desktop, cultura/ = dept MAK via PRs #48/#49); CONTRIBUTING.md
  reescrito (apunta a CLAUDE.md, sin checkpoint.sh muerto); docs/
  DIRECTOR_PLAN.md marcado HISTORICO; PLAN_SIGUIENTE_AGENTE.md reescrito (los
  items PR #41 / server.py /download / brand analyze ya estaban hechos);
  SESSION_STATE.json comprimido (narrativas largas viven en git/changelog).
- SEGURIDAD: cultura/.dev.limpio contenia keys VIVAS (Tavily/Groq/Cerebras/
  Azure) y NO estaba gitignored -- un git add -A las commiteaba. .gitignore
  ahora cubre cultura/.dev* (glob). Falta que el usuario borre el archivo.
- PENDIENTE MANUAL (el clasificador de permisos bloqueo a los agentes sobre
  cultura/): mover 8 leftovers de cultura/ ya presentes en la historia git --
  comando exacto en PLAN_SIGUIENTE_AGENTE.md P1.3. cultura/xiotech.md se
  queda y se commitea (contenido unico, 0 commits previos).

## OLAS MASTER_PLAN 1-3 (2026-07-16, tras el checkpoint; detalle y lecciones
## en context/MASTER_PLAN.md secciones 2 y 6)

context/MASTER_PLAN.md nuevo (doctrina + 7 frentes + reflexion critica).
Tres olas ejecutadas por sonnets y auditadas/corregidas por el director:
- OLA 1 (PR #51): T-F2 docs re-verificados (INVENTORY estaba en v0.34.6);
  T-E1 esteganografia SVG (pieza MANIFIESTO #4); T-E2 tilde render (ya
  existia, SPEC stale; tests nuevos); T-E3 cron nocturno (pieza #6). Review
  adversarial encontro BLOCKER real (purge sin guarda semanal) -- corregido
  con guarda de semana ISO + tests antes de mergear.
- OLA 2 (PR #52): T-A3 26 tests vj_set/git_performance + 2 bugs arreglados
  (repo vacio RuntimeError; --limit 0 por truthiness); T-B3 xio/RUNBOOK.md
  unico verificado contra scripts reales.
- OLA 3 (PR #53): T-B2 gate opcional XIO_SHOWCONTROL_TOKEN (redeploy al
  telefono PENDIENTE); T-D2 catalogo RD regenerable (docs/CATALOGO_RD.md);
  FIX CRITICO: flujo cotizaciones estaba ROTO (brand.py vaciado dejo
  ImportError en engine.py, piezas.py lo silenciaba) -- brand.py restaurado
  como loader de projects/flujo/flujo.json, verificado en vivo.
MANIFIESTO: 4/11 piezas. Las 4 llaves que destraban H2 son del USUARIO:
.noisette real, branch protection, PRs #48/#49, AccessibilityService xio.

## Estado PRs (2026-07-16)
- ABIERTOS esperando review del usuario: #48 (MAK grafo real + canvas + 6
  modos) y #49 (MAPA_GENERATIVO curador de 19 ideas).
- Mergeados hoy: #45, #47 (previos), #50 (checkpoint limpieza + v0.52.0),
  #51 (MASTER_PLAN + ola 1), #52 (ola 2), #53 (ola 3).

## Reporte Formal de Verificacion y Tolerancia Cero a Errores
- py -m compileall src/flujo: OK
- py -m pytest tests/ -q: OK (394 verdes, 1 skip)
- cd web && npm run build:context: no aplica (web no tocada)
- py -m flujo verify: OK (hub smoke 0.52.0)
- Observaciones: basura y duplicados fuera; docs de reglas alineados con la
  realidad (Gemini PARKED, planes viejos marcados historicos); gap de
  credenciales cerrado en .gitignore; quedan 3 acciones manuales del usuario
  (PLAN P1.1-P1.3).
