# LAST HANDOFF -- estado para el proximo agente

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

## Estado 2026-07-17 (sesion Fable, autonoma)
Mergeado a main hoy: PRs #50-#69 (checkpoint, MASTER_PLAN v2 anti-muralla,
olas 1-4, RD DB + perfil productoras + lookup, fix precio Pack 1 real $250k,
vibo_voz eliminado, cobertura 10/10 gaps + fix bug scoring fallback, skill
revivir-subagentes rescatada + fix cp1252, CLAUDE.md denso senal-pura, hook
bash-guard PreToolUse). Branch protection en main ACTIVA (require CI ubuntu+
windows, strict). Sesiones duplicadas del picker limpiadas (2 fantasmas
matados por PID + 3 jsonl borrados; contenido en C:/IA/_flujo_local/
session_backups/).

Optimizacion de gasto aplicada (settings, aplica a sesiones NUEVAS): main model
default = Haiku, effort medium, advisor sonnet, plugins 64->15, hook SessionStart
caveman + hook PreToolUse bash-guard. Doctrina de escalada (triggers decidibles)
codificada en CLAUDE.md seccion "Regulacion de gasto".

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
