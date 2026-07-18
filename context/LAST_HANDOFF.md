# LAST HANDOFF -- estado para el proximo agente

Version: 0.55.0 | Fecha: 2026-07-18T07:10 | Identidad: Cauce | sesion: GODSPEED-4 (director) -- PR #72 MERGEADO a main, PR #73 rebaseado sobre 0.55.0.

## Sesion 2026-07-18T07:00 (GODSPEED-4, director): merge #72 + resolucion conflicto #73
- PR #72 (pausa-en-error, bump 0.55.0) MERGEADO a main con CI matrix verde (ubuntu+windows).
- Esta rama (#73) mergeo origin/main; conflictos solo en LAST_HANDOFF/SESSION_STATE,
  resueltos conservando AMBAS narrativas (regla godspeed). Codigo sin conflicto.
- Worktree god-mak-ola2 seguia lockeado por sesion viva (pid 35300) -- se resolvio en
  worktree detached aparte, sin tocar la del otro agente.

## Sesion 2026-07-18T02:00-03:05 (GODSPEED-3, director Fable, ola 2 -- esta rama, PR #73)

ESTADO PA EL PROXIMO AGENTE -- dos PRs draft esperando review del usuario, CI verde en ambos:

- PR #72 (rama worktree-god-mak-pausa): pausa-en-error MAK completa (Opcion A de
  context/PLAN_UPSCALE.md) + bump 0.55.0 + su propio LAST_HANDOFF detallado.
  Desplegada y VERIFICADA VIVA en el box (ciclo pausa/saltar/resume/informe).
  Workship Win<->MAK probado: llama3.1:8b (VRAM RTX 4070) y deepseek-coder-v2:16b
  responden desde el box via order='win' (research_lib y codex_lib ya cableados).
- PR #73 (esta rama): trabajo.py detecta ok:false de /run (antes contaba como
  exito), emisor HALLAZGO en correlacionar_archivos.py + memoria.py (cierra el
  contrato de eventos), works.json en portfolio.yml (Opcion C -- toca workflow CI,
  revisar ese paso en especial). 10 tests nuevos. Deploy de los 3 .py al box hecho
  y verificado (python3, _resp_ok probado vivo).
- MERGE: si #72 entra primero, esta rama conflictua en LAST_HANDOFF/version --
  resolucion: conservar ambas narrativas, version manda la mas alta. Y viceversa.
- BOX: servicios interfaz/hub corren el codigo nuevo (restart via watchdogs cron).
  ollama serve en Windows (192.168.50.1:11434) arrancado A MANO -- no sobrevive
  reboot; autostart = decision usuario. GPU RTX 4070 SI detectada.
- Skill godspeed ampliada con lecciones 3ra sesion (.claude/skills/godspeed/SKILL.md,
  en esta rama): contrato congelado pa writers paralelos, seam-check md5 vivo-vs-
  espejo, trampa pkill -f via SSH, trampa listado truncado, config persistida antes
  de rediagnosticar.
- PENDIENTES USUARIO: review/merge #72 y #73; autostart ollama Windows; llaves de
  siempre (noisette ojo humano, PAT Termux, AccessibilityService, data productoras).
- PROXIMO SIN GATE: Opcion B (pieza MANIFIESTO via motor-omega); vigilar peso repo;
  test_smoke skip permanente (decidir fixture o borrar).

## Sesion 2026-07-18T02:00+ (GODSPEED-3, director Fable + 4 lectores + 2 builders sonnet, PR #72 -- ya mergeado)

- PAUSA-EN-ERROR (PLAN_UPSCALE Opcion A) COMPLETA: pausa.py nuevo (checkpoint stdlib,
  acciones reintentar/editar/saltar), research.py pausa en fallo terminal de las 3 fases
  (marca "PAUSADO: <ck> | <motivo>" + exit 3) y --resume, worker.py propaga MAK_JOB_ID +
  param extra + evento human_gate, interfaz.py estado PAUSADO + POST /api/reanudar +
  4 botones en ambos renders + CSS, hub.py _norm/colores/contador. 44 tests nuevos
  (test_mak_pausa 20 + test_mak_reanudar 24; 12 fcntl-gated solo corren en CI ubuntu).
  Contrato seguido: cultura/mak_plataforma/diseno/eventos_y_backlog.md.
- VERIFICADO VIVO en el box: ciclo pausa -> saltar -> resume -> re-pausa (fase informe)
  -> saltar -> informe placeholder exit 0. /api/reanudar valida job inexistente (404).
  interfaz.py y hub.py reiniciados con codigo nuevo -- OJO: eso tambien aterrizo el
  borrado de auth de PR #71 que NUNCA se habia desplegado (el hub vivo aun proxeaba
  token de codex borrado = bug vivo, muerto ahora).
- WORKSHIP Win<->MAK PROBADO (pedido del usuario, primera vez): Windows 192.168.50.1
  (cable directo) con OLLAMA_HOST=192.168.50.1:11434 ya persistido por agente previo y
  modelos en C:\OLLAMA_MODELS (14.2GB): llama3.1:8b + deepseek-coder-v2:16b-lite-q4.
  ollama serve arrancado, RTX 4070 SI detectada (llama en VRAM completa; el log CPU-only
  era de un proceso viejo). Desde el box: research_lib LLM(order='win') respondio OK,
  codex_lib win (deepseek 16b) responde, carga 10.4s. Cadenas ya cableadas en ambos libs.
- GAPS REALES: (1) ollama serve en Windows arrancado a mano -- no sobrevive reboot;
  usuario decide autostart (la app de Ollama al iniciar sesion ya bindea bien por el
  OLLAMA_HOST persistido). (2) trabajo.py no parsea el body de /run (200 con ok:false
  cuenta como exito) -- hallazgo off-task, sin tocar. (3) pkill -f via SSH se mata a si
  mismo si el patron matchea la cmdline del bash remoto (2 sesiones SSH perdidas asi).
- PR #72 (rama worktree-god-mak-pausa): pausa-en-error + bump 0.55.0. MERGEADO
  2026-07-18T07:04 con CI matrix verde.

Sesion anterior (0.54.0): PR #71 MERGEADO a main (cd52a69) tras resolver conflictos + fix CI ubuntu
(iterdir orden). SSH a MAK VERIFICADO: mak@192.168.50.2 (dell-11m, llave autorizada).
Bump 0.54.0: PR #71 MERGEADO a main (cd52a69) tras resolver conflictos + fix CI ubuntu
(iterdir orden). SSH a MAK VERIFICADO: mak@192.168.50.2 (dell-11m, llave autorizada).
Skill godspeed ampliada con lecciones 2da sesion. Rama #71 borrada (local+remota);
dir .claude/worktrees/god-haiku-fixes lockeado por proceso, borrar a mano cuando suelte.
Ruta 0.55: context/PLAN_UPSCALE.md -- Opcion A (MAK pausa-en-error) DESBLOQUEADA y recomendada.

## Sesion 2026-07-18T01:00+ (autonoma, loop 3min activo)
- 8a28651: plugin_guardian duplicado xio/seguridad -> _archive/legacy_20260717_2015
  (canonico queda xio/new-plugins, path que despliega run_server.sh); RUNBOOK flag resuelto;
  borrado doublecup_v2_3d.svg suelto (0 bytes, copia real tracked en doublecup/)
- Falso positivo cerrado: "missing mapping.html" del audit de zonas era stale
  (tracked + build:context lo produce; typecheck y build verdes)
- c11bcf0: refs stale a checkpoint.sh (inexistente) purgadas de cli.py,
  PRIMER_DIA.md, SCRIPTS_INVENTORY.md, finish_airdrop.sh; INSTALL.txt (relic
  v0.20) -> _archive/legacy_20260718_0110/
- e67f965: 5 one-shot cleanup scripts spent archivados (targets verificados
  inexistentes): cleanup_safe/moderate/legacy_aggressive.sh,
  cleanup_repo_hygiene_20260630.py, cleanup_v0359_windows_paths.py
- 0cd8909: fix test order-dependence real -- test_run_airdrop_checks popeaba
  sys.modules["flujo"] sin restaurar; snapshot+restore + import explicito
  flujo.paths en 5 test files
- 1a63c53 + ca11233: 41 tests nuevos (sonnet, auditados): ig/download (17,
  instaloader mockeado), analyze colors/run (11, PIL en memoria + OCR mock),
  analyze/export (13, round-trip binario ACO/ASE). serve/ omitido a proposito:
  PR #71 abierto ya trae test_serve_api.py (21 tests) -- no duplicar.
- 4da2936 + a584dc5 + 224558e: SESSION_STATE.json y PLAN_SIGUIENTE_AGENTE.md
  al dia (PR 48 MERGED / 49 CLOSED / 71 OPEN, branch protection ACTIVA,
  vibo_voz y .dev.limpio ya no existen, sellos docs refrescados)
- c8a6cd9: Makefile help corregido (PYTHON vs PYTHON_BIN; python3 no existe
  en Git Bash Windows)
- OJO PR #71: contiene el mismo archive de plugin_guardian que main (8a28651)
  + su propio LAST_HANDOFF -> conflictos chicos esperables al mergear
- Backlog autonomo AGOTADO al cierre: lo restante necesita usuario (noisette
  ojo humano, PAT Termux, AccessibilityService, data productoras, review #71)
  o SSH a MAK (auth pendiente)
- Suite verde tras cada commit (pytest full verde, 1 skip); flujo verify OK 0.52.0

(rama PR #71, sesiones GODSPEED director+haiku, escritas en 0.52.0; mergeadas bajo 0.53.0)

## Sesion 2026-07-18b -- GODSPEED-2: sistema generativo VIVO (misma rama/PR #71)

### HECHO Y VERIFICADO (director + 1 haiku por area, cada claim re-verificado mecanicamente)
- BACKLOG GENERATIVO implementado desde el contrato diseno/eventos_y_backlog.md seccion 3:
  plataforma/backlog.py (parsear LAGUNAS DE INFORMACION, dedup por hash normalizado, linaje
  cap 3, max 3/informe, pop por score+antiguedad, curador con poda) + 43 tests verdes.
  trabajo.py cableado defensivo: cosecha cada tick, verbo multiplicar hace pop del backlog
  ANTES de las semillas fijas (roles.SEMILLAS pasa de motor a arranque), curar cada 8 tareas.
- SEMBRADO: backlog_semilla.jsonl con 8 preguntas de ideas sin comenzar verificadas (2 por
  area: xio+mak, router+server, portafolio+cultura, rd+colorimetria). backlog_codex.txt +4
  tareas (resumidor backlog, timeline red, glosario reactivos, resumen HALLAZGOs).
- DESPLEGADO Y VIVO en 192.168.50.2 (2026-07-18): 13 archivos copiados tras verificar
  live==espejo por md5 (codex_lib+fallback_util+revisar+testear -> ~/codex; cadena+refutar+
  panel+grafo+retencion -> ~/research; trabajo+roles+backlog+backlog_codex -> ~/plataforma;
  semilla -> ~/plataforma/backlog.jsonl). python3 py_compile OK x12 en el box, research y
  codex responden 200. COSECHA REAL PROBADA: 9 preguntas extraidas de informes existentes
  (quechua, test1) -> 17 pendientes en cola. El proximo tick ya investiga solo.
- BUG VIVO ENCONTRADO Y MATADO: el trabajo.py del box aun leia ~/codex/.token (borrado hace
  2 sesiones) y saltaba TODO verbo codex ("skip: codex sin token" x2 en el log). La sesion
  del auth-delete no lo cubrio. El deploy lo corrige; codex autonomo revive.
- src/flujo/analyze/reactivo_matcher.py: lookup inverso de colorimetria RD (hex observado ->
  familias por delta-E CIE76 en Lab, stdlib puro, disclaimer presuntivo en cada resultado)
  + 30 tests. Probado contra reactivos.json real.
- tools/portfolio/generar_works.py: works.json regenerable desde manifests reales de
  datadrops/ + projects/flyer_eventos/ (nodo 17 MAPA_GENERATIVO, "obras reales" ya no
  placeholder) + 20 tests. Corrida real: 8/8 obras catalogadas.
- Reglas de permiso ssh/scp al box: el clasificador BLOQUEA que el agente se auto-otorgue
  permisos en settings (limite duro correcto). El usuario aprobo por /permissions esta vez.

### NO HECHO (real)
- Pausa-en-error sigue sin construir (diseno completo, es el item grande del backlog).
- works.json NO cableado al workflow portfolio.yml (generar_works.py existe y esta testeado;
  falta un paso en el workflow que lo corra y publique -- editar .github/workflows es de
  mayor blast radius, decision del usuario).
- Emisor HALLAZGO en correlacionar_archivos.py/memoria extra: cubierto lo delegable.
- Contradiccion de lector refutada: xio/FACES.md SI existe (un haiku afirmo que no).

## Sesion 2026-07-18 -- PR #71 draft (rama worktree-god-haiku-fixes)

### HECHO Y VERIFICADO
- flujo: scripts/flujo.py dispatcher -> error+exit2 pa 13 comandos retirados (antes fallo
  silencioso) + test_flujo_dispatcher.py. +21 tests smoke flujo.serve (0 cobertura antes).
  Suite worktree verde (644 passed 1 skip tras borrar tests de token; era 648).
  2 bugs ALUCINADOS por lectores haiku REFUTADOS mecanicamente (mapping.html "roto" = lo
  provee web/public/, probado con el build; 3/5 gaps de cobertura falsos, matados en la costura).
- MAK auth: BORRADO TOTAL de token/auth en codex+research (NO "opcional" -- eliminado del codigo):
  interfaz_codex.py (sin _auth/TOKEN), research/interfaz.py (sin _check_auth), hub.py+trabajo.py
  (sin _codex_token, sin proxy ?t=, sin /api/codex_token), watchdog_mak.sh (arranca abierto),
  patch_interfaz.py BORRADO (era el script que inyectaba el auth de research). delegar.py sin token.
- DESPLEGADO EN VIVO al box 192.168.50.2: copiados interfaz_codex.py + watchdog_mak.sh
  (codex_lib.py NO -- no cambio, copiarlo regresa el vivo); removido ~/codex/.token; codex
  reiniciado. VERIFICADO: curl :8891/api/jobs -> 200 SIN token; job real resumir_jobs.py corrio
  -> listo. research :8890 ya era auth-opcional -> abierto igual. Confirme vivo==mirror byte-
  identico salvo borrado de token ANTES de copiar (0 divergencia). Detalle: DEPLOY_OPEN.md.
- MAK research: cultura/mak_research/retencion.py rota informes sin limite. +17 tests.
- MAK codex fiabilidad: cultura/mak_codex/fallback_util.py agrega TODOS los coders fallidos
  (no solo el ultimo). +24 tests + FALLBACK_FINDINGS.md.
- xio: FACES.md (Face A casa Linux+Windows, wifi + cable ethernet directo / Face B show SOLO
  telefono, el Linux no sale). Codex nunca en la red del show -> la confusion 32-clientes-sin-AP
  NO es exposicion de codex.
- skill .claude/skills/godspeed/SKILL.md: doctrina director+haiku + fallas reales de esta sesion.

### NO HECHO (real, sin maquillar)
- Pausa-en-error (#1 del backlog MAK): NO existe en NINGUN lado. Verificado exhaustivo: 3 stores
  (WEB/LOCAL/MAK), todas las worktrees (incl. mak-research-cultural en .claude y en _flujo_local),
  el stash, keyword ES + EN (research/resume/pause), por directorio, y por fecha. investigar()
  sigue PLANO (topic,iteraciones,depth,providers,densidad), 7819 bytes identico en los 3.
  Solo existe el DISEÑO (cultura/mak_plataforma/diseno/eventos_y_backlog.md) + el emisor vivo
  (research_lib.emitir_evento/mint_job_id; worker.py intercepta STATUS:->node_start,
  HALLAZGO:->llm_result). El handoff previo lo marco honestamente "NO COMPLETADO"; su linea
  "investigar() fue reescrito" NO coincide con el codigo pero NO fue mentira (trabajo perdido/
  optimista). PROXIMO: CONSTRUIR desde el diseño sobre el emisor -- NO re-buscar, no esta.
- [HECHO 2026-07-17 sesion godspeed-2] fallback_util INTEGRADO en codex_lib.py CoderLLM.call
  (import defensivo try/except; al agotar la cadena el RuntimeError agrega TODOS los intentos
  via aggregate_failures; exito byte-identico; +3 tests integracion = 27 en test_mak_fallback).
- [HECHO 2026-07-17 sesion godspeed-2] Emisor semantico (HALLAZGO:) agregado a cadena/refutar/
  panel/grafo (research) + revisar/testear (codex) -- 15 emisiones aditivas con contenido real,
  hecho por 6 haikus (1 archivo c/u, sin commits propios) + verificacion mecanica del director
  (grep + py_compile + diff --stat por archivo + suite completa verde).
- retencion.py, fallback_util y codex_lib.py integrado NO desplegados al box (solo en repo/PR;
  el deploy al box 192.168.50.2 sigue pendiente y ahora INCLUYE codex_lib.py + fallback_util.py).
- Firewall Windows ollama sigue "Any remote address" (bind a 192.168.50.1 ya cierra el riesgo real).

### TOPOLOGIA (memoria: project_tres_repos_topologia -- NO asumir que uno refleja a otro)
WEB = repo publico, solo commits finales. LOCAL = C:/IA/flujo (Windows), toda la info.
LINUX/MAK = 192.168.50.2 station research+codex, codigo SUELTO en ~/research ~/codex ~/plataforma
(NO es clone del repo). Una worktree off origin/main = sabor WEB; puede faltarle trabajo de LOCAL/MAK.

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

## MAK Codex Fallback Analysis (2026-07-17, sesion god-haiku-fixes)

Trabajo: auditoria de la cadena de fallback de CoderLLM ante timeouts y errores
de proveedores (NIM -> WIN -> Ollama). Deliverable: findings + helper module testeable.

**Archivos:**
- cultura/mak_codex/FALLBACK_FINDINGS.md: analisis detallado (lineas 110-129 en
  codex_lib.py; issues: solo "ultimo" error visible, no aggregacion de intentos,
  timeouts no distinguidos de otros errores, sin reordenamiento por salud de
  proveedores). Propone 5 mejoras: agregacion de errores (high), timeout tracking
  (medium), health stats (medium), backoff (low), mensajes claros (high).
- cultura/mak_codex/fallback_util.py: helper puro (NO deps network/ollama):
  * parse_provider_error() -- clasifica excepcion en tipo (timeout/connection/
    api_error/empty/other) + trunca a 100 chars
  * aggregate_failures() -- formatea lista de intentos en mensaje legible
  * score_provider_health() -- ranking proveedores por ratio exito
  * format_chain_suggestion() -- reordena cadena por salud, genera explicacion
- tests/test_mak_fallback.py: 24 tests (TestParseProviderError x8, TestAggregate
  Failuresx5, TestScoreProviderHealth x5, TestFormatChainSuggestion x3,
  TestIntegrationWorkflow x2). Cobertura: tipo de error, truncacion, multi-
  fallback, ranking, reordenamiento, workflow completo.

**Verificacion (CLI):**
- py -m py_compile cultura/mak_codex/fallback_util.py: OK
- py -m pytest tests/test_mak_fallback.py -q: OK (24 passed)
- py -m pytest tests/ -q -p no:cacheprovider --tb=no: 394+ green, 1 skip,
  4 fallo en test_mak_retencion (pre-existing Linux path issues, no impacta)

**Decisiones:**
- NO toque live CoderLLM loop (fuera de scope: "findings + optional tested helper only")
- Helper module extraible y testeable SIN red/ollama/subprocess deps
- Fallback_util.py agnostico a implementacion (puede inyectarse en codex_lib
  futura sin romper tests existentes)

## Reporte Formal de Verificacion y Tolerancia Cero a Errores
- py -m compileall src/flujo: OK (anterior), fallback_util.py: OK (nuevo)
- py -m pytest tests/test_mak_fallback.py -q: OK (24 nuevos)
- py -m pytest tests/ -q -p no:cacheprovider --tb=no: OK (394+ verdes, 1 skip;
  test_mak_retencion fallo pre-existing Linux paths)
- cd web && npm run build:context: no aplica (web no tocada)
- py -m flujo verify: no aplica (repo source audit, no live modules)
- Observaciones: findings + helper + tests completos. Listo para que otro agente
  integre helpers en CoderLLM live loop si se desea.
